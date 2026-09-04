# RAID14 패턴 대응형 Mast2 선사용 후속연구 설계 — 2026-09-01

## 상태

이 문서는 `RESEARCH_HANDOFF_V6_LEGACY_FULL.md` §25의 12버스트 시절 패턴손실 후속연구 설계를 현재 RAID14 연구 방향에 맞게 갱신한 **현행 설계 문서**다.

기존 §25는 역사적 기록으로 보존한다. 실제 구현·실험에서는 이 문서를 우선한다.

이 후속연구는 다음 연구와 분리한다.

```text
본 연구
- 패턴 OFF
- 현실적인 성장범위에서 크크메 vs 지속 몰아주기 비교
- 목적: 평상시 기본 회전 결정

첫 버스트 후속연구
- Crown opener vs M1 opener
- 목적: 첫 사이클의 관습 검증과 캐릭터별 예외 확인

패턴손실 후속연구 — 이 문서
- 평상시 기본 회전은 유지
- 예정된 M3 구간에 예측 가능한 유효피해 손실이 있을 때만 해당 한 주기에서 M2를 앞당김
- 목적: 기본 회전을 깨야 할 실전 판단기준 생성
```

즉 이 연구는 기존 관습을 검증하는 단계보다 한 단계 더 나아가, **평상시 기본값을 언제 의도적으로 깨야 하는가**를 수치화하는 실전 의사결정 연구다.

---

# 1. 연구 질문

Mast가 3스택 Burst를 사용한 뒤 reset/Hangover를 거쳐 다시 다음 M3까지 가는 한 주기를 생각한다.

직전 M3의 Hangover 때문에 이 주기의 첫 번째 B2는 Crown으로 고정된다. 따라서 실제 선택지는 뒤의 두 번뿐이다.

```text
기본:
Crown → Crown → Mast3
C,C,M3

패턴 대응:
Crown → Mast2 → Crown
C,M2,C
```

질문은 다음과 같다.

> 세 번째 Full Burst, 즉 원래 M3가 예정된 구간에 보스의 무적·이동·저지·강제기믹 등으로 사전에 예상 가능한 유효피해 손실이 충분히 클 때, 두 번째 B2에서 Mast2를 앞당기고 세 번째 B2를 Crown으로 바꾸는 것이 언제부터 유리한가?

비교는 해당 한 M3 주기에서만 수행한다. 그 이후 회전은 다시 동일하다고 가정한다.

이것은 특정 Main B3에게 Mast를 반복적으로 주는 지속 몰아주기가 아니라:

```text
곧 올 M3의 실현가치가 패턴 때문에 크게 훼손될 때
해당 한 주기만 Mast2를 앞당기는 일회성 패턴 대응
```

이다.

---

# 2. 판정모델은 180초 전체가 아니라 3-FB 국소 사이클

패턴 대응 선택은 한 M3 주기 안에서 국소적으로 발생한다.

비교와 무관한 나머지 180초를 매번 다시 stateful하게 계산하는 것은:

```text
동일한 구간이 대부분을 차지해 연구 질문을 희석하고
캐릭터 수 × 64성장점이 늘어날수록 계산량만 크게 증가시킨다.
```

따라서 primary 판정은 전용 `3-FB local cycle` 기능으로 수행한다.

다만 국소적으로 큰 차이가 나더라도 180초 전투에서 한 번만 발생하는 선택이라면 실제 전체 점수 차이는 작을 수 있다. 그래서 **180초 총딜 관점의 효과크기는 별도로 반드시 보여준다.**

```text
언제 바꿀 것인가?     → 3-FB 국소 사이클의 L*
바꾸는 게 중요한가?   → 180초 normalized delta
```

---

# 3. RAID14에서 사용할 반복 주기

현재 M1 opener를 고정한 conventional RAID14 구조는:

```text
M1,C,M3 / C,C,M3 / C,C,M3 / C,C,M3 / C,M2
```

이다.

첫 묶음은 opener 구조가 다르고 마지막은 3버스트 묶음이 완성되지 않으므로, 반복 가능한 정상 `C,C,M3` 표본은:

```text
block A = c4~c6
block B = c7~c9
block C = c10~c12
```

세 묶음이다.

이 세 묶음은 구조는 같지만 실제 피해는 ammo/reload, proc counter, carryover buff 등의 상태차이 때문에 조금씩 달라질 수 있다.

따라서 특정 한 묶음을 대표값으로 고정하지 않는다.

---

# 4. 핵심 집계 방식 — 상태가 아니라 버스트 위치별 피해를 평균

## 4.1 상태를 평균내지 않는다

`c4`, `c7`, `c10`의 실제 시작상태를 각각 그대로 사용한다.

각 block 시작점에서 상태를 snapshot한 뒤 같은 상태에서 두 정책으로 fork한다.

```text
block A start state → C,C,M3 / C,M2,C
block B start state → C,C,M3 / C,M2,C
block C start state → C,C,M3 / C,M2,C
```

snapshot에는 최소 다음을 포함한다.

```text
Mast Drunken / Hangover state
캐릭터별 ammo / reload / charge state
active buffs와 남은 지속시간
skill proc counter
지연피해 / duration-shot 관련 상태
boss condition
```

중요:

> ammo, proc counter, buff duration 같은 상태값 자체를 세 block 평균으로 합쳐 하나의 가상 시작상태를 만들지 않는다.

비선형 상태를 평균하면 실제 어느 사이클에도 존재하지 않는 상태가 생길 수 있다. **실제 상태에서 각각 실행하고, 최종 피해 결과만 평균한다.**

## 4.2 한 block은 1·2·3버스트 구조를 유지한다

각 local run의 피해를 다음 네 구간으로 나눈다.

```text
D1   = 1번째 burst-cycle 구간
D2   = 2번째 burst-cycle 구간
D3   = 3번째 burst-cycle 구간
Tail = 3번째 Full Burst 종료 뒤, 그 선택이 만든 직접 공격효과가 소진되는 구간
```

권장 시간경계는 burst chain의 B1 시작을 기준으로 연속적으로 자른다.

```text
D1: 1st B1 start → 2nd B1 start
D2: 2nd B1 start → 3rd B1 start
D3: 3rd B1 start → 3rd Full Burst end
Tail: 3rd Full Burst end → 직접 공격 관련 tail 종료
```

이렇게 하면 Full Burst 사이의 일반사격 피해도 빠지지 않는다.

버프의 원인을 어느 burst에 귀속시키는 인과분해는 하지 않는다. 첫 Crown의 15초 buff가 두 번째 구간까지 남아 있더라도 실제 피해가 D2 시간대에 발생했다면 D2로 집계한다.

## 4.3 같은 위치의 버스트끼리 먼저 평균한다

각 block `k`에서 baseline 피해를 `C_{k,1}`, `C_{k,2}`, `C_{k,3}`, `C_{k,t}`라 하고 pattern-response 피해를 `P_{k,1}`, `P_{k,2}`, `P_{k,3}`, `P_{k,t}`라 한다.

세 block의 **같은 위치끼리** 평균한다.

\[
\bar C_1=\frac{C_{A,1}+C_{B,1}+C_{C,1}}{3}
\]

\[
\bar C_2=\frac{C_{A,2}+C_{B,2}+C_{C,2}}{3}
\]

\[
\bar C_3=\frac{C_{A,3}+C_{B,3}+C_{C,3}}{3}
\]

\[
\bar C_t=\frac{C_{A,t}+C_{B,t}+C_{C,t}}{3}
\]

`P`도 동일하게 계산한다.

그 뒤 평균 버스트 세 개를 다시 합쳐 **대표 3버스트 사이클**을 만든다.

\[
C_0=\bar C_1+\bar C_2+\bar C_3+\bar C_t
\]

\[
P_0=\bar P_1+\bar P_2+\bar P_3+\bar P_t
\]

즉 연구의 대표값은:

```text
평균적인 1번째 Crown 구간
+ 평균적인 2번째 Crown/M2 구간
+ 평균적인 3번째 M3/Crown 구간
+ 평균적인 직접 tail
```

이다.

이 방식은 **1→2→3이라는 실제 운용 구조는 유지하면서, 특정 c6/c9/c12의 우연한 피해편차가 결과를 지배하는 것을 줄인다.**

---

# 5. 평가 구간과 패턴손실 적용 구간은 분리

전체 local value에는 `D1 + D2 + D3 + Tail`을 모두 넣는다.

특히 `C,M2,C`의 세 번째 Crown Burst는 15초이므로 Full Burst 10초 종료 뒤에도 약 5초의 공격대미지 buff가 남을 수 있다. 이 직접 잔여가치는 Tail에 포함한다.

반면 패턴손실 `L`은 **세 번째 Full Burst의 실질 유효타격 시간창에만 적용**한다.

```text
loss window:
3rd Full Burst start → 3rd Full Burst end
```

따라서 세 번째 Crown의 FB 종료 후 남는 tail은 전체 가치에는 들어가지만 M3 예정구간 손실에는 포함하지 않는다.

B3 cast 순간부터 이미 보스가 사라지는 특수패턴은 2차 시간마스크 검증에서 별도로 다룬다.

---

# 6. 패턴손실 변수 L

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

`L`은 시간 그 자체가 아니라 피해손실률이다.

```text
5초를 못 때림 = 항상 L 0.50
```

으로 정의하지 않는다.

즉발 nuke, proc, reload, 지속피해 등의 시간분포 때문에 같은 5초라도 어느 부분이 잘리는지에 따라 실제 피해손실은 달라질 수 있다.

\[
t_{loss}\approx10L\text{ seconds}
\]

은 실전 설명용 근사치로만 사용한다.

1차 연구의 `L`은 damage-only availability loss다.

```text
공격 동작과 내부 무기상태는 정상 진행
세 번째 Full Burst 유효구간에서 일정 비율의 피해만 실현되지 않음
```

사격 자체가 멈추거나 강제엄폐로 ammo/reload/charge 상태까지 변하는 패턴은 2차 stateful pattern 검증으로 분리한다.

---

# 7. 대표 M3 유효구간 피해도 위치별 평균으로 만든다

각 block의 세 번째 Full Burst **10초 유효구간만** 따로 집계한다.

baseline:

\[
C_{w,k}=\text{block k의 3rd Full Burst window 피해}
\]

response:

\[
P_{w,k}=\text{block k의 동일 3rd Full Burst window 피해}
\]

대표 loss-window 피해는:

\[
\bar C_w=\frac{C_{w,A}+C_{w,B}+C_{w,C}}{3}
\]

\[
\bar P_w=\frac{P_{w,A}+P_{w,B}+P_{w,C}}{3}
\]

으로 계산한다.

여기서도 특정 block의 `L*`을 먼저 구해 세 값을 단순평균하지 않는다.

**피해 구성요소를 먼저 평균한 뒤 마지막에 하나의 대표 threshold를 계산한다.**

---

# 8. 핵심 threshold 계산

대표 사이클에서:

- `C0` = 평균 `C,C,M3` local total + tail
- `P0` = 평균 `C,M2,C` local total + tail
- `Cw` = `\bar C_w`, 평균 M3 예정 Full Burst 유효구간 피해
- `Pw` = `\bar P_w`, response에서 같은 위치의 평균 유효구간 피해

uniform proportional loss `L`을 적용하면:

\[
C(L)=C_0-LC_w
\]

\[
P(L)=P_0-LP_w
\]

손익분기:

\[
\boxed{L^*=\frac{C_0-P_0}{C_w-P_w}}
\]

현재 damage-only proportional-loss 정의에서는 이 식이 직접 계산식이다.

### 중요한 금지사항

다음처럼 block별 threshold를 먼저 구해 평균하지 않는다.

\[
\frac{L_A^*+L_B^*+L_C^*}{3}
\]

`L*`은 비율이므로 이 방식은 대표 피해구조와 다른 값을 만들 수 있다.

대신:

```text
1. block별 실제 상태에서 두 정책 실행
2. 1번째 위치끼리 피해 평균
3. 2번째 위치끼리 피해 평균
4. 3번째 위치끼리 피해 평균
5. tail 평균
6. 3rd FB loss-window 피해 평균
7. 평균된 피해 구성요소로 L*를 한 번 계산
```

한다.

---

# 9. 위치편차는 버리지 않고 진단값으로 보존

대표 판정값은 burst-position average로 계산하지만, block별 값도 진단용으로 남긴다.

예:

```text
representative L* = 0.47
block A implied L* = 0.45
block B implied L* = 0.48
block C implied L* = 0.49
```

세 위치가 비슷하면 대표 threshold를 일반 판단선으로 써도 된다는 근거가 된다.

반대로 위치별 차이가 크게 벌어지면:

```text
전투 시점 / state 의존성이 큰 조합
```

으로 표시하고 평균 하나를 universal rule처럼 쓰지 않는다.

즉 평균은 위치효과를 숨기기 위한 것이 아니라 **대표 판단값을 안정화하기 위한 primary estimator**이며, 개별 위치값은 robustness diagnostic이다.

---

# 10. L* 예외 케이스

다음을 둔다.

\[
D_0=C_0-P_0
\]

\[
D_w=C_w-P_w
\]

일반적인 기대상황은:

```text
D0 > 0 → 패턴이 없으면 C,C,M3 우세
Dw > 0 → M3 예정구간이 사라질수록 baseline 우세가 감소
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

그 외는 숫자를 억지로 threshold처럼 출력하지 않는다.

```text
D0 <= 0
→ 패턴이 없어도 C,M2,C가 동급 이상. 패턴 threshold가 아닌 별도 예외.

D0 > 0, Dw <= 0
→ loss window를 지워도 baseline 우위가 줄지 않음. 정상 양의 역전점 없음.

L* > 1
→ M3 예정구간 피해를 100% 잃어도 response가 역전하지 못함.

Dw ≈ 0
→ 수치적으로 불안정. dominance/no-crossing 처리.
```

---

# 11. 180초 총딜 환산

`L*`은 언제 바꿀지를 알려주지만, 그 선택이 한 판 전체에서 얼마나 중요한지는 알려주지 않는다.

- `T180` = 같은 roster / growth / boss condition의 평상시 RAID14 180초 baseline 총피해
- `Δlocal(L)` = 대표 3버스트 사이클에서 한 번 패턴 대응했을 때의 피해차

\[
\Delta_{local}(L)=P(L)-C(L)
\]

나머지는 동일하다는 본 연구의 국소 가정 아래:

\[
T_{180,response}(L)=T_{180}+\Delta_{local}(L)
\]

\[
\boxed{\Delta_{180\%}(L)=\frac{\Delta_{local}(L)}{T_{180}}\times100}
\]

으로 180초 효과크기를 환산한다.

이 값은 모든 표본에서 180초 intervention run을 다시 돌린 결과가 아니라, **평균적인 한 번의 국소 선택 손익을 기존 180초 baseline에 얹은 실전 중요도 지표**다.

결과에는 반드시:

```text
local delta %
180s normalized delta %
```

를 같이 표시한다.

`L*`에서는 두 정책이 동률이므로 180초 delta도 0이다. 따라서 실전 중요도는 `L*`보다 명확히 큰 대표 손실값에서도 함께 본다.

대표 표본 몇 개만 실제 RAID14 전체 intervention run으로 재검증해 환산오차를 확인할 수 있다.

---

# 12. 성장점 — 64점 realistic grid 유지

이 후속연구도 출발점은 실전 적용이다.

본 연구의 64점 realistic growth grid를 그대로 기본 단위로 사용한다.

```text
g1-base5-none
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

B1 × B3-A × B3-B의 상대성장을 `4×4×4 = 64`점으로 교차한다.

목적은:

```text
ATK 한 줄이 L*를 정확히 몇 %p 움직이는가
```

가 아니라:

```text
실제 계정에서 나타날 법한 성장격차를 넓게 넣어도
패턴 대응 판단선과 180초 실전효과가 비슷한 범위에 모이는가?
```

를 보는 것이다.

정밀한 스탯별 인과분해나 연속 crossover는 연구 종료 후 별도의 stat parameter model로 진행한다.

36점 orthogonal grid는 anomaly 진단용으로만 보존한다.

---

# 13. B3 표본 선정

구형 §25의 `실질 DPS가 비슷한 B3 둘`은 필수조건으로 두지 않는다.

우선순위는:

```text
실제로 Crown + Mast와 함께 사용할 수 있는 B3 조합
실제 보스전에서 교대 B3로 사용할 이유가 있는 조합
서로 다른 Mast 반응구조를 대표하는 조합
```

이다.

대표군:

```text
1. 두 B3 기여도가 비교적 비슷한 조합
2. Main B3 기여도가 더 큰 현실적인 조합
3. 분배딜 비중이 높은 B3가 포함된 조합
4. 실사용 하단부 Secondary가 포함된 조합
```

극단적인 저DPS 캐릭터는 practical threshold의 대표 표본이 아니라 positive-control/stress test로 분리한다.

---

# 14. Boss condition

기본적으로 realistic grid 철학을 이어간다.

```text
neutral
Main B3 natural elemental advantage
```

를 기본 후보로 둔다.

실제 특정 보스에 적용할 때는 해당 보스의 속성조건을 그대로 넣을 수 있다.

`L` 외의 조건은 baseline/response에서 동일해야 한다.

---

# 15. 1차 출력

각 roster / boss condition / growth point마다 최소 다음을 기록한다.

```text
[burst-position representative cycle]
C1 / P1 = 평균 1번째 burst-cycle 피해
C2 / P2 = 평균 2번째 burst-cycle 피해
C3 / P3 = 평균 3번째 burst-cycle 피해
Ct / Pt = 평균 tail 피해
C0 / P0 = 대표 3버스트 local total

[loss window]
Cw / Pw = 평균 3rd Full Burst 10초 유효구간 피해
Dw = Cw-Pw
L* 또는 no-crossing 판정
10L*초 단순 환산값(참고용)

[robustness]
block A/B/C의 개별 위치 결과
필요하면 implied L* 범위

[practical effect]
T180 = 평상시 180초 baseline
대표 L에서 Δlocal
동일 L에서 180s normalized delta
180s response-equivalent total
```

집계 요약에서는:

```text
정상 threshold 존재 비율
대표 L* 최소 / 중앙 / 최대
필요하면 10~90 percentile
roster별 / boss condition별 분포
위치편차가 큰 표본 비율
대표 L에서 local delta 분포
대표 L에서 180s normalized delta 분포
```

를 본다.

64점은 실제 계정 분포 확률을 뜻하지 않는다. 평균/중앙값을 현실의 발생확률이나 기대값처럼 해석하지 않는다.

---

# 16. 2차 검증 — 실제 시간마스크

64점 전체에서 실제 보스패턴을 프레임 단위로 재현하지 않는다.

먼저 위의 대표 `L*`로 practical range를 구한 뒤 대표 성장점만 실제 time mask로 확인한다.

예:

```text
Full Burst 앞부분 3초 손실
중간 3초 손실
뒷부분 3초 손실
앞/뒤 5초 손실
실제 특정 보스의 관찰 가능한 무적·이동 패턴
```

목적은:

> 피해손실률 `L*`를 `대략 몇 초를 못 때리면 되는가`라는 실전 언어로 번역했을 때 오차가 허용 가능한가?

를 보는 것이다.

### damage-only time mask

사격/탄약/차지 상태는 정상 진행하고 피해만 실현되지 않는 패턴이면 damage event timestamp에 mask를 적용한다.

### state-changing pattern

강제엄폐나 사격정지로 ammo/reload/charge state까지 달라지면 대표 표본만 별도의 stateful pattern run을 사용한다.

---

# 17. 실전 가이드로 변환

최종 결과는 소수점 단위의 정밀도보다 **판단 가능한 범위와 실제 영향 크기**를 우선한다.

가상의 예:

```text
대표 L*가 대부분 0.42~0.51
block 위치편차도 작음
실제 time mask에서도 대략 4~6초 부근에서 전환

L=0.60에서 local 이득 +2~3%
180초 normalized 이득 +0.1~0.3%
```

이라면:

```text
M3 구간의 절반 가까이를 날릴 것이 명확하면 그 한 주기는 M2 선사용을 고려.
다만 한 번의 대응이 180초 전체에 주는 이득은 작을 수 있으므로
경계 근처라면 운용 난이도나 다른 택틱을 희생하면서까지 강제하지 않는다.
```

처럼 표현한다.

roster별 threshold가 크게 흩어지면 universal threshold를 만들지 않고 조합군별 범위를 제시한다.

---

# 18. 구현 순서

패턴손실 연구 기능은 본 연구용 180초 비교기와 분리된 국소 분석 모듈로 추가한다.

권장 구현 순서:

```text
1. RAID14 run에서 c4/c7/c10 실제 시작상태 snapshot 또는 재현 기능
2. 같은 snapshot에서 C,C,M3 / C,M2,C local fork
3. damage event를 D1 / D2 / D3 / Tail로 연속 분할
4. 3rd Full Burst loss-window 피해 별도 집계
5. block A/B/C 결과를 burst-position별 평균
6. 대표 3-FB cycle 조립
7. 대표 L* 계산 + no-crossing 판정
8. 기존 T180을 이용한 180s normalized delta
9. 대표 표본용 실제 time mask 기능
```

이 기능을 만들기 전에는 표본 캐릭터 구현과 본 연구 검증을 우선 진행해도 된다.

---

# 19. 이 연구에서 하지 않는 것

1차 후속연구에서는 다음을 하지 않는다.

```text
모든 B3 전수조사
모든 보스패턴 프레임 재현
개별 계정 Actual Account Mode
ATK/우월/장탄 한 줄 단위 인과분해
정확한 캐릭터 간 연속 crossover 탐색
첫 버스트 Crown/M1 연구와 결합
실측 점수에 엔진 값을 억지로 calibration
모든 표본에서 180초 전체 stateful intervention 재실행
상태값 자체를 평균해 가상 사이클 생성
block별 L*의 단순평균을 대표 threshold로 사용
```

필요한 세부 임계점이나 인과가 생기면 연구 종료 후 연속 stat parameter model로 별도 연구한다.

현재 목표는:

> **실제 여러 사이클의 상태차이는 보존하되 같은 버스트 위치의 결과를 평균해 대표 3버스트 사이클을 만들고, M3 예정구간의 손실이 어느 정도일 때 한 번의 M2 선사용이 유리한지와 그 선택이 180초 총점에서 얼마나 중요한지를 함께 제시하는 것.**
