# RAID14 패턴 대응형 Mast2 선사용 후속연구 설계 — 2026-09-01

## 상태

이 문서는 `RESEARCH_HANDOFF_V6_LEGACY_FULL.md` §25의 12버스트 시절 패턴손실 후속연구 설계를 현재 연구 방향에 맞게 갱신한 현행 설계 문서다.

기존 §25는 연구 아이디어의 역사적 기록으로 보존한다. 실제 구현·실험에서는 이 문서를 우선한다.

본 후속연구는 다음 두 연구와 분리한다.

```text
본 연구
- 패턴 OFF
- 현실적인 성장범위에서 크크메 vs 지속 몰아주기 비교
- 목적: 평상시 기본 회전 결정

첫 버스트 후속연구
- Crown opener vs M1 opener
- 목적: 첫 사이클 최적화와 캐릭터별 예외 확인

패턴손실 후속연구 — 이 문서
- 평상시 기본 회전은 유지
- 예정된 M3 구간에 예측 가능한 타격손실이 있을 때만 해당 묶음에서 M2를 앞당김
- 목적: 기본 회전을 깨야 할 실전 판단기준 생성
```

즉 이 연구는 기존 관습을 검증하는 단계보다 한 단계 더 나아가, **평상시 기본값을 언제 의도적으로 깨야 하는가**를 수치화하는 실전 의사결정 연구다.

---

# 1. 연구 질문

Mast가 3스택 Burst를 사용한 뒤 reset/Hangover를 거쳐 다시 다음 M3까지 가는 한 주기를 생각한다.

이 주기에서는 첫 번째 B2는 직전 M3 이후의 Hangover 때문에 Crown으로 고정된다.
따라서 실제 선택지는 뒤의 두 번뿐이다.

```text
기본:
Crown → Crown → Mast3
C,C,M3

패턴 대응:
Crown → Mast2 → Crown
C,M2,C
```

질문은 다음과 같다.

> 세 번째 Full Burst, 즉 원래 M3가 예정된 구간에 보스의 무적·이동·저지·강제기믹 등으로 사전에 예상 가능한 유효피해 손실이 충분히 클 때, 두 번째 B2에서 Mast2를 앞당기고 세 번째를 Crown으로 바꾸는 것이 언제부터 유리한가?

이 비교는 해당 한 주기에서만 수행한다.
그 이후 회전은 다시 동일하다고 가정한다.

따라서 이것은 특정 Main B3에게 Mast를 계속 주는 지속 몰아주기가 아니라:

```text
곧 올 M3의 실현가치가 패턴 때문에 크게 훼손될 때
해당 한 주기만 Mast2를 앞당기는 일회성 패턴 대응
```

이다.

---

# 2. 왜 180초 전체 회전을 판정모델로 사용하지 않는가

이 후속연구의 선택은 **한 M3 주기 안에서 국소적으로 발생한다.**

비교와 무관한 나머지 180초 구간까지 stateful하게 다시 계산하면:

```text
동일한 구간이 대부분을 차지해 연구 질문이 희석되고
캐릭터 수 × 64성장점이 늘어날수록 계산량만 크게 증가한다.
```

따라서 primary 판정은 전용 `3-FB local cycle` 모듈로 수행한다.

단, 국소적으로는 큰 차이가 나더라도 180초 전투에서 한 번만 발생하는 선택이라면 실제 전체 점수 차이는 매우 작을 수 있다.
그래서 **180초 총딜 관점의 효과크기는 반드시 별도로 보여준다.**

정리하면:

```text
손익분기 판정      → 3-FB 국소 사이클
실전 중요도 판단   → 180초 총딜 환산치
```

둘을 동시에 출력한다.

---

# 3. 국소 사이클의 시작 상태

두 정책은 완전히 동일한 초기 상태에서 출발해야 한다.

기준점은 직전 M3 Full Burst 종료 직후의 정상 reset 상태를 사용한다.

최소 상태:

```text
Mast Drunken reset
Mast Hangover 시작
동일한 캐릭터별 ammo / reload / charge 상태
동일한 active buff 상태
동일한 스킬 proc counter / duration-shot 상태
동일한 boss condition
```

첫 번째 B2는 양쪽 모두 Crown으로 고정한다.

그 뒤에만 분기한다.

```text
A — baseline
1st: Crown
2nd: Crown
3rd: Mast3

B — pattern response
1st: Crown
2nd: Mast2
3rd: Crown
```

첫 B2 선택을 변수로 만들지 않는다. Crown/M1 opener 연구와도 섞지 않는다.

---

# 4. 평가 구간과 손실 적용 구간을 분리

이 연구에서는 **총가치를 평가하는 시간**과 **패턴손실 L을 적용하는 시간**을 다르게 둔다.

## 4.1 국소 총가치 평가 구간

첫 번째 Crown 사이클 시작부터 세 번째 Burst 선택이 만들어낸 공격 관련 잔여효과가 끝날 때까지를 평가한다.

특히 세 번째가 Crown인 `C,M2,C`에서는 Crown Burst가 15초이므로 Full Burst 10초가 끝난 뒤에도 약 5초의 공격대미지 버프가 남을 수 있다.
이 잔여가치는 반드시 local total에 포함한다.

또한 세 번째 Burst에서 직접 생성된 delayed damage, duration-shot, reload/ammo 차이 등 **그 선택의 직접적인 tail**도 포함한다.

다만 tail 이후의 다음 회전까지 계속 추적하지 않는다.
연구 가정상 그 이후는 다시 동일한 상태/운용으로 복귀한 것으로 취급한다.

## 4.2 패턴손실 적용 구간

패턴손실 `L`은 **세 번째 Full Burst의 실질 유효타격 시간창**에만 적용한다.

기본값:

```text
3rd Full Burst start
→
3rd Full Burst end
```

즉 세 번째 Crown의 FB 종료 후 남는 약 5초 tail은 전체 가치에는 들어가지만, `M3 예정 구간에서 발생한 타격손실`에는 포함하지 않는다.

이 구분은 Crown 15초 잔여가치를 보존하면서도 그것을 M3 구간 손실로 잘못 계산하지 않기 위해 필요하다.

B3 cast 순간부터 이미 보스가 사라지는 특수 패턴은 2차 시간마스크 검증에서 별도로 다룬다.

---

# 5. 패턴손실 변수 `L`

세 번째 Full Burst 유효구간에서 사라지는 **원래 유효피해의 비율**을:

\[
L\in[0,1]
\]

로 정의한다.

```text
L = 0.00 → 손실 없음
L = 0.30 → 해당 구간 원래 피해의 30% 손실
L = 0.50 → 50% 손실
L = 1.00 → 해당 구간 피해 전부 손실
```

중요하게 `L`은 시간 그 자체가 아니라 **피해손실률**이다.

따라서:

```text
5초를 못 때림 = 항상 L 0.50
```

으로 정의하지 않는다.

즉발 nuke, 스킬 proc, 재장전, 지속 피해 등 때문에 같은 5초라도 어느 부분이 잘리는지에 따라 실제 손실피해가 달라질 수 있다.

10초 Full Burst에 대한:

\[
t_{loss}\approx10L\ \text{seconds}
\]

환산은 실전 설명용 근사치로만 사용한다.

---

# 6. 1차 패턴 모델의 범위

1차 연구의 `L`은 damage-only availability loss다.

```text
공격 동작과 내부 무기 상태는 정상적으로 진행
세 번째 Full Burst 유효구간에서 일정 비율의 피해만 실현되지 않음
```

으로 둔다.

이 변수는 다음과 같은 상황을 하나의 실전 판단축으로 추상화한다.

```text
보스 무적
타격 불가능 위치 이동
저지/기믹 처리로 인한 실질 공격손실
특정 M3 Full Burst가 사실상 비는 고정 패턴
```

반대로 다음은 1차 모델과 구분한다.

```text
보스 이탈 때문에 실제 사격 자체가 멈춤
강제 엄폐로 charge/reload/ammo state가 달라짐
타겟 소멸이 캐릭터별 스킬 발동상태까지 바꿈
```

이런 state-changing pattern은 대표 표본의 2차 검증에서만 별도 모델링한다.

---

# 7. 핵심 계산 — 국소 두 run으로 `L*` 직접 계산

각 조건에서 두 국소 사이클을 stateful하게 한 번씩 실행한다.

정의:

- `C0` = 패턴손실이 없을 때 `C,C,M3` local total + 직접 tail
- `P0` = 패턴손실이 없을 때 `C,M2,C` local total + 직접 tail
- `Cw` = baseline의 세 번째 Full Burst 유효구간에 원래 발생한 5인 총피해
- `Pw` = response의 동일한 세 번째 Full Burst 유효구간에 원래 발생한 5인 총피해

uniform proportional loss `L`을 적용하면:

\[
C(L)=C_0-LC_w
\]

\[
P(L)=P_0-LP_w
\]

손익분기:

\[
C(L^*)=P(L^*)
\]

따라서:

\[
\boxed{
L^*=\frac{C_0-P_0}{C_w-P_w}
}
\]

이다.

현재 damage-only proportional-loss 정의에서는 이 식이 직접적인 threshold 계산식이다.

각 성장점마다 `L=0→1`을 반복 sweep할 필요가 없다.

Crown duration, Mast stack/reset, ammo/reload, proc 등 **두 선택이 해당 국소 사이클 내부에서 만든 상태차이와 tail은 두 stateful run에 이미 반영**한다.

---

# 8. 180초 총딜 환산

`L*`은 선택 기준을 알려주지만, 실전에서 그 선택이 얼마나 중요한지는 알려주지 않는다.

예를 들어 국소 3-FB 묶음에서 `C,M2,C`가 3% 이기더라도 180초 동안 이 대응을 한 번만 사용한다면 전체 전투에서는 수십 bp 수준의 차이에 그칠 수 있다.

따라서 각 결과에 **180초 총딜 환산치**를 같이 출력한다.

정의:

- `T180` = 같은 roster / growth / boss condition의 평상시 180초 baseline 총피해
- `Δlocal(L)` = 한 번의 패턴 대응으로 생기는 local total 차이

\[
\Delta_{local}(L)=P(L)-C(L)
\]

연구 가정상 해당 국소 사이클 바깥은 동일하므로, 한 번의 패턴 대응이 발생한 180초 전투의 환산 총피해는:

\[
\boxed{
T_{180,response}(L)=T_{180}+\Delta_{local}(L)
}
\]

이고 180초 기준 상대효과는:

\[
\boxed{
\Delta_{180\%}(L)=\frac{\Delta_{local}(L)}{T_{180}}\times100
}
\]

이다.

이 값은 `180초 전체를 다시 stateful하게 재실행한 값`이 아니라, **나머지는 동일하다는 본 연구의 국소 가정 아래 한 번의 선택 손익을 기존 180초 baseline에 반영한 환산값**이다.

따라서 결과에는 반드시 둘 다 표시한다.

```text
local delta %
180s normalized delta %
```

이렇게 해야:

```text
국소적으로는 차이가 커 보이지만 3분 전체에서는 거의 무시 가능한 선택인지
아니면 한 번의 대응만으로도 실제 총점에 의미 있는 차이를 만드는지
```

를 구분할 수 있다.

필요하면 실제 RAID14 180초 엔진으로 대표 표본 몇 개만 재실행해 이 환산 가정의 오차를 확인한다.

---

# 9. `L*` 판정의 예외 케이스

다음을 둔다.

\[
D_0=C_0-P_0
\]

\[
D_w=C_w-P_w
\]

일반적인 기대상황:

```text
D0 > 0
→ 패턴이 없으면 C,C,M3 우세

Dw > 0
→ 세 번째 유효구간에서 C,C,M3가 더 큰 가치를 가지므로
   그 구간이 사라질수록 baseline 우세가 줄어듦
```

이때:

\[
L^*=\frac{D_0}{D_w}
\]

이고:

```text
0 < L* < 1 → 정상적인 실전 손익분기
L < L*     → C,C,M3 유지
L > L*     → 해당 한 주기만 C,M2,C 고려
```

그 외에는 숫자를 억지로 threshold처럼 출력하지 않는다.

### Case A — `D0 <= 0`

패턴손실이 없어도 `C,M2,C`가 이미 동급 이상이다.
패턴 대응 threshold가 아니라 별도 예외 case로 표시한다.

### Case B — `D0 > 0`, `Dw <= 0`

세 번째 유효구간의 피해를 없애도 baseline 우위가 줄지 않는다.
현재 uniform damage-loss 모델에서는 정상적인 양의 역전점이 없다.

### Case C — `L* > 1`

세 번째 유효구간 피해를 100% 잃어도 `C,M2,C`가 역전하지 못한다.
`이 종류의 패턴손실만으로는 변경 불필요`로 표시한다.

### Case D — `0 < L* < 1`

정상 threshold.

`Dw≈0`이면 수치적으로 불안정한 threshold를 출력하지 않고 dominance/no-crossing으로 판정한다.

---

# 10. 성장점 설계 — 64점 realistic grid 유지

이 후속연구도 출발점은 **실전 적용**이다.

따라서 본 연구에서 채택한 64점 realistic growth grid를 기본으로 재사용한다.

각 가변 슬롯의 성장 상태:

```text
g1-base5-none
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

B1 × B3-A × B3-B의 성장차를 현실적으로 넓게 포함하는 `4×4×4 = 64`점을 한 roster/boss condition의 기본 단위로 둔다.

이 설계의 목적은:

```text
ATK 한 줄이 L*를 정확히 몇 %p 바꾸는가
```

가 아니라:

```text
실제 계정에서 나타날 법한 성장격차를 넓게 넣어도
M3 패턴손실 판단선과 180초 실전효과가 비슷한 범위에 모이는가?
```

를 보는 것이다.

정확한 스탯별 인과분해나 연속 crossover가 필요해지면 본 연구 종료 후 별도의 stat parameter model로 진행한다.

기존 36점 orthogonal grid는 anomaly 진단용으로만 보존한다.

---

# 11. B3 조합 선정

구형 §25의 `실질 DPS가 비슷한 B3 둘` 조건은 필수로 두지 않는다.

현재 우선순위는:

```text
실제로 Crown + Mast와 함께 사용할 수 있는 B3 조합
실제 보스전에서 교대 B3로 채용할 이유가 있는 조합
서로 다른 Mast 반응구조를 대표하는 조합
```

이다.

대표적으로:

```text
1. B3 두 명의 기여도가 비교적 비슷한 조합
2. Main B3의 기여도가 더 큰 현실적인 조합
3. 분배딜 비중이 높은 B3가 포함된 조합
4. 실사용 하단부 Secondary가 포함된 조합
```

을 섞는다.

극단적인 저DPS 캐릭터는 practical threshold의 대표 표본보다 positive-control/stress test로 분리한다.

---

# 12. Boss condition

기본적으로 realistic grid의 철학을 이어간다.

우선:

```text
neutral
Main B3 natural elemental advantage
```

를 사용할 수 있다.

다만 패턴손실 후속연구는 특정 보스의 패턴 대응이 목적이므로 실제 적용 단계에서는 해당 보스의 속성조건을 그대로 넣을 수 있다.

중요한 것은 `L` 외의 조건을 두 정책에서 동일하게 유지하는 것이다.

---

# 13. 1차 출력

각 roster / boss condition / growth point마다 최소 다음을 기록한다.

```text
C0 = C,C,M3 local total + tail
P0 = C,M2,C local total + tail
pattern-free local delta %
Cw = baseline 3rd Full Burst 유효구간 피해
Pw = response 3rd Full Burst 유효구간 피해
Dw = Cw-Pw
L* 또는 no-crossing 판정
10L*초 단순 환산값(참고용)

T180 = 평상시 180초 baseline 총피해
L*보다 충분히 큰 대표 손실값에서 Δlocal
동일 조건의 180s normalized delta %
180s response-equivalent total
```

`L*`에서는 두 정책이 같으므로 180초 delta도 0이다.
따라서 실전 중요도는 threshold 자체보다 **threshold를 명확히 넘어선 대표 손실값**에서도 같이 본다.

예:

```text
L* = 0.45
L = 0.60일 때 local +2.0%
같은 L = 0.60을 180초로 환산하면 +0.18%
```

처럼 출력한다.

집계 요약에서는:

```text
정상 threshold 존재 비율
L* 최소 / 중앙 / 최대
필요하면 10~90 percentile
roster별 분포
boss condition별 분포

대표 L에서 local delta 분포
대표 L에서 180s normalized delta 분포
```

를 함께 본다.

64점은 실제 계정의 발생확률을 반영한 표본이 아니므로 평균/중앙값을 현실의 확률적 기대값처럼 해석하지 않는다.
목적은 현실적인 성장범위에서 판단선과 실전 중요도가 얼마나 흔들리는지 보는 robustness check다.

---

# 14. 2차 검증 — 실제 시간마스크

64점 전체를 프레임 단위 실제 패턴으로 반복실행하지 않는다.

먼저 국소 `L*` 계산으로 realistic grid의 범위를 저비용으로 구한다.

그 뒤 대표 성장점 몇 개만 선택해 실제 시간형 damage availability mask를 적용한다.

예:

```text
Full Burst 앞부분 3초 손실
중간 3초 손실
뒷부분 3초 손실
앞/뒤 5초 손실
실제 특정 보스의 관찰 가능한 무적·이동 패턴
```

목적은:

> `유효피해 손실률 L*`를 `대략 몇 초를 못 때리면 되는가`라는 실전 언어로 번역했을 때 오차가 허용 가능한가?

를 검증하는 것이다.

### damage-only time mask

사격/탄약/차지 상태가 정상적으로 진행되고 피해만 실현되지 않는 패턴은 기존 damage event timestamp에 mask를 적용한다.

### state-changing pattern

사격 자체가 멈추거나 강제엄폐 등으로 ammo/reload/charge state까지 변하면 대표 표본에 한해 별도의 stateful pattern run을 사용한다.

필요하면 이 대표 표본에서 실제 RAID14 180초 재실행도 함께 하여 `180s normalized delta` 환산오차를 확인한다.

---

# 15. 실전 가이드로의 변환

최종 결과는 소수점 단위의 과도한 정밀도보다 **판단 가능한 범위와 실제 영향 크기**를 우선한다.

가상의 예:

```text
64점 대부분의 L*가 0.42~0.51
실제 시간마스크에서도 대략 4~6초 부근에서 전환

L=0.60에서 local 이득은 +2~3%
하지만 180초 normalized 이득은 +0.1~0.3%
```

이라면 최종 가이드는:

```text
M3 구간의 절반 가까이를 날릴 것이 명확하면 그 한 주기는 M2 선사용을 고려.
다만 한 번의 대응으로 180초 전체에서 얻는 이득은 작을 수 있으므로,
경계 근처라면 운용 난이도나 다른 택틱을 희생하면서까지 강제할 필요는 없음.
```

처럼 표현할 수 있다.

반대로 threshold를 넘었을 때 180초 normalized 이득까지 크게 나온 조합은 우선도가 높은 실전 예외로 분류한다.

roster별 L*가 크게 흩어지면 universal threshold를 만들지 않고:

```text
일반 B3군
분배딜 B3군
Main-heavy 조합
```

등 실전적으로 의미 있는 조합군별 범위를 제시한다.

---

# 16. 이 연구에서 하지 않는 것

1차 후속연구에서는 다음을 하지 않는다.

```text
모든 B3 전수조사
모든 보스 패턴 프레임 재현
개별 계정 Actual Account Mode
ATK/우월/장탄 한 줄 단위 인과분해
정확한 캐릭터 간 연속 crossover 탐색
첫 버스트 Crown/M1 연구와 결합
실측 점수에 엔진 값을 억지로 calibration
모든 표본에서 180초 전체 stateful intervention 재실행
```

필요한 세부 임계점이나 인과가 생기면 본 연구 종료 후 연속 stat parameter model을 만들어 별도 연구한다.

그 단계에서는 예를 들어:

```text
Main damage scale
Secondary damage scale
분배딜 비중
Mast 반응도
Boss DEF
M3 effective availability
```

등을 연속 파라미터로 두고 저비용 sweep할 수 있다.

현재 단계의 목표는:

> **국소적으로 언제 C,M2,C로 바꿀 것인가와, 그 선택이 실제 180초 총점에서 얼마나 중요한가를 동시에 제시하는 것.**

이다.
