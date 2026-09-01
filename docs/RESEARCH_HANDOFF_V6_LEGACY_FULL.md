# v6 크라운–메스트 운용 연구

> **Source-policy note (2026-09-02):** any `nikke-sim` reference below is provenance/secondary-reference only, not the authority priority. Current mechanics work must prefer Moris calculator / NIKKE.gg (and direct evidence when available) and must be independently cross-validated. See `docs/SOURCE_VALIDATION_POLICY.md`.

## 손익분기 연구 복원·검산용 마스터 노트

- 작성 기준: **2026-08-29 (v6 정리)**
- 본 연구 대상: **NIKKE Crown / Mast B2 운용에서 `크크메`와 `지속 몰아주기`의 순수 피해 손익**
- 후속 연구 대상: **정상 `C,C,M3`의 M3 구간에 예측 가능한 타격손실이 있을 때, 해당 3사이클 묶음만 `C,M2,C`로 바꾸는 패턴 대응형 2스택 선사용의 손익분기**
- 목적: 새 채팅으로 이동해도 기존 연구를 최대한 동일하게 복원하고, 수식·가정·결과·시행착오를 다시 검산할 수 있도록 한다.
- 핵심 원칙: **실측 보스의 패턴을 본 연구의 이론식에 맞추지 않는다. 변수 통제가 가능한 이론을 본 분석으로 삼고, 이론의 기반이 되는 계산 규칙만 독립 자료로 교차검증한다. 패턴은 후속 연구에서 별도의 통제변수로만 다시 도입한다.**

---

# 0. 이 문서에서 가장 먼저 읽어야 할 내용

이 연구가 답하려는 질문은 다음과 같다.

> **보스 점프/무적/부위/코어/사거리/우월/강제엄폐 등의 외생변수를 제거하고, 동일한 파티·스펙·시간축에서 Crown과 Mast의 B2 배치만 바꿨을 때 `크크메`와 `몰아주기` 중 어느 쪽의 5인 총피해가 높은가? 그리고 메인캐리의 상대적 딜 비중이 얼마일 때 손익이 뒤집히는가?**

따라서 이론값은 특정 보스 실전의 점수를 예측하는 값이 아니다.  
이론값은 **Intrinsic Rotation Value = 순수 운용 가치**이다.

이 문서는 연구축을 두 개로 분리한다.

```text
본 연구:
외생변수 OFF
→ 크크메 vs 지속 몰아주기의 intrinsic rotation value 비교

후속 연구:
본 연구의 기본 회전을 전제로, 예측 가능한 M3 구간 타격손실 L만 의도적으로 추가
→ 해당 3사이클만 C,C,M3 → C,M2,C로 바꿀 손익분기 탐색
```

**후속 연구의 `C,M2,C`는 지속 몰아주기와 같은 개념이 아니다.**  
특정 M3 구간의 실현가치가 패턴 때문에 떨어질 때만 한 묶음을 바꾸고, 다음 묶음부터 다시 기본 회전으로 복귀하는 패턴 대응형 운용이다.

반드시 기억할 핵심:

1. **딜러 둘만 비교하면 안 된다. 5인 총피해 기준으로 봐야 한다.**
   - 몰아주기로 Rapi가 얻는 피해 증가만 보면 안 된다.
   - Helm, B1, Crown, Mast가 동시에 잃거나 얻는 피해를 전부 합산해야 한다.
   - 최종 판정은 항상 `Rapi 이득 vs 나머지 4인 총손실`이다.

2. **“Rapi 딜비중이 X%면 무조건 몰아주기” 같은 보편적 상수는 현재 도출되지 않았다.**
   - B1이 바뀌면 Rapi가 받는 상대이득 `g`와 나머지 4인의 평균손실 `l`이 바뀐다.
   - 따라서 손익분기 비중은 **조합·스펙·시간축별 국소값**이다.

3. **실측은 현재 본 계산의 보정자료로 사용하지 않는다.**
   - 실측에 사용한 보스가 Mast 3스택 주기마다 고정적으로 점프하여 약 2~3초 딜로스를 만들었다.
   - 이 딜로스가 어느 Mast 스택, 어느 B3, 어느 캐릭터의 피해를 잘랐는지 전부 추적하지 않으면 순수 운용 효과와 분리할 수 없다.
   - 그 작업비용이 이론 연구의 목적에 비해 지나치게 높다.
   - 따라서 기존 실측은 역사적 sanity check 또는 “실전 패턴이 이론값을 크게 흔들 수 있다”는 사례로만 보존한다.
   - 단, 이 상관된 타격손실 자체는 버리는 정보가 아니다. 본 연구의 보정값으로 사용하지 않을 뿐, 후속 연구에서는 `예상 M3 타격손실률 L`이라는 별도 통제변수로 추상화해 다시 다룬다.

4. **NIKKE Sim 전체가 완벽할 필요는 없다.**
   - 현재 파티에서 실제로 결과에 들어오는 계산 경로만 맞으면 된다.
   - 예: 현재 테스트 캐릭터에 분배 피해가 없다면 Mast의 `Distributed Damage` 공식이 틀려도 이번 결과에는 영향이 없다.
   - 반대로 ATK%, caster-ATK, Attack Damage, Crit, Charge, Reload, Crown/Mast 지속시간·스택·타겟팅 등은 실제 결과에 들어오므로 검증 우선순위가 높다.

5. **계산기에서는 c5/c6/c11/c12만 독립적으로 떼면 안 된다.**
   - 직접 B2 선택이 바뀌는 사이클은 네 곳이 맞다.
   - 하지만 Crown 15초 버프, reload, ammo, durationShots 등이 다음 사이클로 상태를 전파한다.
   - 따라서 최소 c1→c12 전체 시간축을 stateful하게 진행해야 한다.

---

# 1. 운용 정의

## 1.1 B3 고정 순서

12회의 B3는 다음과 같이 고정한다.

| Cycle | B3 |
|---|---|
| c1 | Rapi |
| c2 | Helm |
| c3 | Rapi |
| c4 | Helm |
| c5 | Rapi |
| c6 | Helm |
| c7 | Rapi |
| c8 | Helm |
| c9 | Rapi |
| c10 | Helm |
| c11 | Rapi |
| c12 | Helm |

---

## 1.2 `크크메`

B2 순서:

```text
C, C, M / C, C, M / C, C, M / C, C, M
```

즉:

| Cycle | B2 | B3 |
|---|---|---|
| c1 | Crown | Rapi |
| c2 | Crown | Helm |
| c3 | Mast | Rapi |
| c4 | Crown | Helm |
| c5 | Crown | Rapi |
| c6 | Mast | Helm |
| c7 | Crown | Rapi |
| c8 | Crown | Helm |
| c9 | Mast | Rapi |
| c10 | Crown | Helm |
| c11 | Crown | Rapi |
| c12 | Mast | Helm |

Mast는 `c3, c6, c9, c12`, 전부 **3스택**으로 사용한다.

---

## 1.3 `몰아주기`

B2 순서:

```text
C, C, M / C, M, C / C, C, M / C, M, C
```

즉:

| Cycle | B2 | B3 |
|---|---|---|
| c1 | Crown | Rapi |
| c2 | Crown | Helm |
| c3 | Mast | Rapi |
| c4 | Crown | Helm |
| c5 | Mast | Rapi |
| c6 | Crown | Helm |
| c7 | Crown | Rapi |
| c8 | Crown | Helm |
| c9 | Mast | Rapi |
| c10 | Crown | Helm |
| c11 | Mast | Rapi |
| c12 | Crown | Helm |

Mast는 `c3, c5, c9, c11`.

- c3/c9 = 3스택, `크크메`와 공통.
- c5/c11 = **2스택 Mast를 Rapi에 사용**.

직접적으로 B2가 달라지는 곳은:

```text
c5, c6, c11, c12
```

하지만 “차이가 발생하는 사이클”과 “그 차이의 영향이 남아 있는 시간범위”는 같지 않다.

---

## 1.4 NIKKE Sim 적용 후보와 본 연구 baseline의 구분

현재 NIKKE Sim 개선 논의에서는 Mast의 실제 Drunken state를 구현한 뒤 다음과 같은 **기본 burst eligibility**가 후보로 논의되고 있다.

```text
1) Mast가 아직 한 번도 Burst II를 쓰지 않았다면 첫 B2는 Mast 우선
2) 이후 Drunken 3 stack이면 Mast 우선
3) 1~2 stack에서는 다른 B2가 사용 가능하면 Mast가 양보
4) 다른 B2가 사용 불가능하면 Burst chain 유지를 위해 Mast 사용
```

20초 B2 + Mast라면 이 규칙은 대략:

```text
M1 → B2 → M3 / B2 → B2 → M3 / ...
```

형태가 된다.

이것은 **시뮬레이터의 향후 기본 Mast 정책 후보**이며, 현재 §1.2~1.3의 legacy/provisional 연구 회전을 소급해서 바꾸는 규칙이 아니다.
현재 수치들은 기존 `C,C,M3` 시작 baseline으로 계산되었으므로 그대로 regression reference로 보존한다.
새 stateful calculator에서 최종 재계산할 때는:

```text
A. 기존 연구 baseline을 재현하는 regression run
B. 실제 기본정책 후보인 M1 opener를 공통으로 적용한 C/F run
```

을 구분할 수 있다.
두 run의 결론 방향이 같다면 opener 선택에 robust한 근거가 되고, 다르면 opener 자체를 별도 변수로 취급한다.

---

# 2. 고정 시간축

원본 업로드 파일:

```text
7f78a268-411a-408a-b0b4-de4e46ebc588.txt
conversation file id:
file_000000004fcc8230ab50a366c63458c1
```

새 채팅에서는 원본 파일이 자동으로 존재하지 않을 수 있으므로 아래 값을 문서에 완전히 복사한다.

| Cycle | B1 | B2 | B3 | Full Burst |
|---|---:|---:|---:|---|
| c1 | 3.9 | 4.3 | Rapi 4.8 | 5.1–15.1 |
| c2 | 18.3 | 18.7 | Helm 19.3 | 19.6–29.6 |
| c3 | 32.7 | 33.3 | Rapi 33.9 | 34.3–44.3 |
| c4 | 47.4 | 48.0 | Helm 48.5 | 48.9–58.9 |
| c5 | 61.3 | 61.6 | Rapi 62.2 | 62.6–72.6 |
| c6 | 76.0 | 76.4 | Helm 77.0 | 77.4–87.4 |
| c7 | 89.7 | 90.3 | Rapi 90.8 | 91.2–101.2 |
| c8 | 104.7 | 105.1 | Helm 105.6 | 106.0–116.0 |
| c9 | 118.3 | 118.8 | Rapi 119.3 | 119.6–129.6 |
| c10 | 132.1 | 132.4 | Helm 132.8 | 133.2–143.2 |
| c11 | 147.6 | 148.0 | Rapi 148.6 | 149.0–159.0 |
| c12 | 161.8 | 162.1 | Helm 162.7 | 163.0–173.0 |

c13은:

```text
B1 177.6 / B2 178.2 / B3 178.5 / FB 178.9...
```

현재 12버스트 비교에서는 c13의 Burst 선택과 효과를 모두 제외한다.
다만 c12까지 발생한 버프·탄수형 효과·무기 상태의 후속 피해는 180초까지 집계한다.
즉 본 연구의 기본 시간범위는 다음과 같다.

```text
Burst decision horizon: c1~c12
Damage evaluation horizon: 0~180초
c13: 발생시키지 않음
```

이는 실제 Burst Gauge 기반 180초 전투의 완전 재현이 아니라, **12회의 운용 선택이 만든
terminal value를 동일한 고정 종료시점까지 평가하는 연구용 시간축**이다.

## 시간축에서 중요한 것

- B2 → FB start 지연은 대략 0.8~1.0초.
- B3 burstCast와 Full Burst 진입은 같은 순간이 아니다.
- 예: c12 Helm B3 = 162.7초, Full Burst start = 163.0초.
- Crown Burst는 15초이므로 다음 cycle에 carryover될 수 있다.
- 예: c11 Crown B2 = 148.0초라면 Crown Burst AD +36.24%는 163.0초까지 유지된다.
  - 따라서 c12 Helm B3 162.7초에는 아직 살아 있다.
- Crown S1은 `fullBurstEnter`에서 적용된다. BurstCast 즉발 피해와 순서를 혼동하지 않는다.
- c12 크크메의 Mast Burst/S2는 각각 172.1/172.7초에 끝나지만, 몰아주기의 Crown Burst는
  177.1초, 양쪽의 Crown S1은 178.0초까지 남는다.
- Helm c12 Burst의 다음 10발 Charge Damage Multiplier도 177.867초의 열 번째 탄까지 이어진다.
- 따라서 173초 종료는 c12에서 생성된 효과를 비대칭으로 절단하므로 본 결과가 아니라
  경계 민감도 보조값으로만 사용한다.

---

# 3. 이론 테스트의 기본 Scope-lock

기존 통합 가상테스트의 기본 조건:

```text
Sync 400 / Level 400
Base-5 gear
Skill 10/10/10
Cube 없음
OL line 없음
Doll 없음
core7 progression basis
Boss DEF = 140

Core hit OFF
Range bonus OFF
Element advantage OFF
Part damage OFF
보스 점프/무적/부위 변화 OFF
고정 12버스트 타이밍
c13 Burst 비활성
180초까지 c12 잔여 효과와 후속 피해 계산
```

Static ATK:

| Class | Static ATK |
|---|---:|
| Attacker | 118,027 |
| Supporter | 98,367 |
| Defender | 78,707 |

고정 시간축 연구에서는 CDR 및 Burst Gauge 증가는 스케줄을 변화시키지 않는 것으로 처리했다.  
즉 해당 효과가 “피해 자체”를 바꾸지 않는다면 현재 모델에서는 inert로 취급한다.

### 연구용 강제 시간축의 의미

이 고정 시간축은 실제 파티가 해당 회전을 자연스럽게 성립시키는지 검증하기 위한 것이 아니다.
본 연구에서 B1은 **서로 다른 버프 구조 / 자체딜 구조를 가진 비교군**이고, 질문은 그 B1 환경에서 `g / l / s*`의 방향이 반복되는지 여부다.

따라서:

```text
- 특정 B1의 실제 CDR / Burst Gauge만으로 연구 회전이 성립하는가? → 본 연구의 판정변수 아님
- 필요하면 C/F 양쪽이 동일한 비교 시간축을 갖도록 burst cadence를 강제/정규화
- B1의 CDR / Burst Gauge는 그 강제 시간축을 깨지 않으며, 직접 피해경로가 없으면 inert
- 목적은 현실 파티의 rotation feasibility가 아니라 B1 buff environment를 바꾼 controlled A/B
```

즉 Liter 등 특정 B1에서 회전을 성립시키기 위해 시간축을 강제하더라도 연구 설계 위반이 아니다.
오히려 실제 회전 가능성을 별도의 독립변수로 섞으면 `B1 버프 구조가 Crown/Mast 교환비에 미치는 영향`이라는 질문이 흐려질 수 있다.

### 12버스트 terminal-tail과 173초 경계값

173초는 c12 Full Burst가 끝나는 깔끔한 상태 관측점이지만, c12에서 시작한 Crown의 15초
버프와 Helm의 다음 10발 효과를 끝까지 평가하지 못한다. 현재 기본 편성에서는:

```text
종료    몰아주기 total delta    break-even Main B3 share
173초   -1.3089%                72.4865%
178초   -1.2148%                71.3384%
180초   -1.2130%                71.3343%
```

주요 c12 효과는 178초까지 소진되며, 178→180초 추가 구간이 break-even을 움직이는 폭은
약 0.004%p다. 따라서 180초를 기본 결과로 사용하고 173초는 endpoint sensitivity로 함께
보존한다. 이 180초 결과를 `stock NIKKE Sim의 실제 180초 회전`이라고 표현하지 않는다.

---

# 4. 가장 중요한 연구용 수식

이 절은 **NIKKE의 개별 피해공식이 아니라, 크크메 vs 몰아주기 가설을 검증하기 위해 우리가 세운 비교식**이다.

이 식들의 대수적 타당성은 현재 검토 완료 상태다.

---

## 4.1 5인 총피해 비교식

정의:

- `C` = 크크메
- `F` = 몰아주기(funnel)
- `R_C` = 크크메에서 Rapi 피해
- `R_F` = 몰아주기에서 Rapi 피해
- `O_C` = 크크메에서 Rapi를 제외한 4인 피해 합
- `O_F` = 몰아주기에서 Rapi를 제외한 4인 피해 합

따라서:

\[
T_C = R_C + O_C
\]

\[
T_F = R_F + O_F
\]

몰아주기와 크크메의 차이:

\[
\Delta T = T_F - T_C
\]

전개하면:

\[
\Delta T = (R_F - R_C) + (O_F - O_C)
\]

몰아주기 우위 조건:

\[
R_F - R_C > O_C - O_F
\]

### 이 식이 의미하는 것

몰아주기는 단순히 “Rapi가 더 세지는 운용”이 아니다.

정확한 경제구조:

```text
Rapi가 추가로 얻는 피해
VS
Rapi를 제외한 4인이 합쳐서 잃는 피해
```

따라서 **5인 전체 딜 기준이 필수**다.

---

## 4.2 Rapi만 추상적으로 강하게 만들었을 때 손익분기: λ 식

Rapi의 “최종 계산된 피해 패킷”만 추상적으로 `λ`배 가중한다.

\[
T_C(\lambda)=\lambda R_C + O_C
\]

\[
T_F(\lambda)=\lambda R_F + O_F
\]

손익분기:

\[
T_C(\lambda_*) = T_F(\lambda_*)
\]

따라서:

\[
\lambda_*R_C + O_C = \lambda_*R_F + O_F
\]

정리:

\[
\lambda_*(R_F-R_C)=O_C-O_F
\]

결론:

\[
\boxed{
\lambda_* =
\frac{O_C-O_F}{R_F-R_C}
}
\]

### λ의 정확한 의미

**λ는 Rapi의 Static ATK 배율이 아니다.**

λ는:

> “현재 두 운용에서 계산된 Rapi의 반응률을 유지한 상태로, 최종 Rapi 피해 패킷의 상대적 중요도만 가중하는 추상적 스케일”

이다.

왜 Static ATK 배율로 해석하면 안 되는가?

실제 Rapi Static ATK를 변경하면:

- caster-ATK flat buff의 상대가치가 달라짐
- DEF 차감의 상대가치가 달라짐
- 여러 ATK bucket의 희석 정도가 달라짐
- 결과적으로 `R_F/R_C` 자체가 변할 수 있음

즉 λ 식은 **local break-even 분석용**이다.

---

## 4.3 λ를 “크크메 기준 Rapi 팀딜 비중”으로 변환

손익분기 시점의 크크메 기준 Rapi 비중:

\[
s_C^*=
\frac{\lambda_*R_C}
{\lambda_*R_C+O_C}
\]

이 값이 우리가 흔히 말한:

> “크크메 기준 손익분기 Rapi 딜비중”

이다.

반드시 **크크메 기준**이라고 써야 한다.

몰아주기에서의 비중은 별도:

\[
s_F^*=
\frac{\lambda_*R_F}
{\lambda_*R_F+O_F}
\]

이며 두 값은 동일하지 않다.

---

## 4.4 더 중요한 형태: `g`와 `l`

정의:

Rapi의 몰아주기 상대이득:

\[
g=
\frac{R_F}{R_C}-1
\]

즉:

\[
R_F=R_C(1+g)
\]

나머지 4인의 평균 상대손실:

\[
l=
1-\frac{O_F}{O_C}
\]

즉:

\[
O_F=O_C(1-l)
\]

손익분기식:

\[
\lambda R_C(1+g)+O_C(1-l)
=
\lambda R_C+O_C
\]

따라서:

\[
\lambda R_C g=O_C l
\]

이를 크크메 기준 비중식에 대입하면:

\[
\boxed{
s_C^*=
\frac{l}{g+l}
}
\]

### 이 식이 주는 가장 중요한 결론

손익분기를 설명하는 핵심은:

```text
g = Rapi가 몰아주기로 몇 % 강해지는가
l = 나머지 4인이 가중평균으로 몇 % 약해지는가
```

이다.

**단순한 Rapi 절대딜이 아니다.**

---

## 4.5 손익분기 이후의 실제 이득 크기

손익분기 `s*`만 보면 “언제 부호가 뒤집히는가”는 알 수 있지만,
**손익분기를 넘은 뒤 몰아주기가 실제로 얼마나 이기는가**는 바로 보이지 않는다.

크크메 기준 Main B3 팀딜 비중을:

\[
s=\frac{R_C}{T_C}
\]

라고 두면, 현재 `g / l`을 고정한 local model에서:

\[
\frac{T_F-T_C}{T_C}
=sg-(1-s)l
\]

이고, `s_C^*=l/(g+l)`를 대입하면:

\[
\boxed{
\frac{T_F-T_C}{T_C}
=(g+l)(s-s_C^*)
}
\]

이다.

### 해석

```text
s_C*      = 몰아주기와 크크메의 부호가 뒤집히는 지점
g + l     = 그 지점을 넘은 뒤 local total-delta가 커지는 기울기
g         = 같은 local 반응률을 고정했을 때 s=1 극단에서의 몰아주기 최대 우위
```

특히 `s=1`이면:

\[
\frac{T_F-T_C}{T_C}=g
\]

이므로, **현재 조합에서 측정된 `g`가 작다면 손익분기점을 넘더라도 몰아주기의 기대이득이 구조적으로 작을 수 있다.**

단 이 식 역시 `g,l`을 현재 조합에서 고정한 **local extrapolation**이다.
실제로 Main B3의 스펙이나 캐릭터를 크게 바꾸면 ATK bucket 희석, caster-flat 상대가치, DEF 영향 등으로 `g,l` 자체가 변할 수 있으므로, `s`만 임의로 움직인 값을 새로운 실제 파티의 예측값으로 해석하지 않는다.

현재 legacy/provisional 네 케이스의 `g`는 약 +1.07~+1.47% 범위다.
따라서 이 **구형 local model 내부에서만** 보면 극단적으로 Main B3 비중을 100%까지 가중해도 몰아주기 우위는 약 `g` 수준에 머문다.
이 수치는 수정 계산기 재계산 전 최종 결론으로 사용하지 않고, “threshold뿐 아니라 upside magnitude도 같이 봐야 한다”는 분석축의 예시로만 보존한다.

---

# 5. “딜러 기준이 아니라 5인 전체를 봐야 한다”의 정확한 의미

나머지 4인 각각을 `i`라고 하자.

크크메 피해:

\[
D_{i,C}
\]

몰아주기 손실률:

\[
l_i =
1-\frac{D_{i,F}}{D_{i,C}}
\]

그렇다면 비Rapi 전체 손실률 `l`은 단순 평균이 아니다.

\[
\boxed{
l=
\frac{
\sum_i D_{i,C}l_i
}{
\sum_i D_{i,C}
}
}
\]

즉 **크크메 피해량을 가중치로 한 가중평균**이다.

이것 때문에 B1의 자체딜도 중요하다.

예:

- Helm은 몰아주기에서 -6%를 잃음.
- B1은 몰아주기에서 -1%만 잃음.
- B1 자체딜이 매우 크다면, 비Rapi 전체에서 Helm의 -6% 손실이 희석됨.
- B1 자체딜이 매우 작다면 Helm 손실이 비Rapi `l`에 더 크게 반영됨.

따라서:

> “B1은 메인딜러가 아니니 B1 자체딜은 무시해도 된다”

는 결론은 틀리다.

B1 자체딜은 **팀 총딜에 직접 들어갈 뿐 아니라 비Rapi 평균손실 `l`의 가중치**를 바꾼다.

---

# 6. 손익분기식의 예외 케이스

기존 네 사례는 보통:

```text
R_F > R_C
O_F < O_C
```

즉 Rapi는 이득, 나머지는 손해라 정상적인 양의 손익분기가 생긴다.

그러나 일반 계산기는 다음 경우를 검사해야 한다.

편의를 위해:

\[
\Delta R=R_F-R_C
\]

\[
\Delta O=O_F-O_C
\]

Rapi 최종 피해 packet을 추상적으로 \(\lambda\)배 할 때:

\[
\Delta T(\lambda)=\lambda\Delta R+\Delta O
\]

### Case A
\[
\Delta R>0,\quad \Delta O<0
\]

정상적인 양의 손익분기 존재.

\[
\lambda^*=-\frac{\Delta O}{\Delta R}
\]

\(\lambda>\lambda^*\)이면 몰아주기 우위.

### Case B
\[
\Delta R\ge0,\quad \Delta O\ge0
\]

적어도 하나가 양수이면 **몰아주기 지배우위**.

### Case C
\[
\Delta R\le0,\quad \Delta O\le0
\]

적어도 하나가 음수이면 **크크메 지배우위**.

### Case D
\[
\Delta R<0,\quad \Delta O>0
\]

반대 방향의 양의 손익분기 존재.

\[
\lambda^*=-\frac{\Delta O}{\Delta R}
\]

이 경우는 Case A와 반대로 \(\lambda<\lambda^*\)일 때 몰아주기 우위.

경계값에서 \(\Delta R=0\)이면 \(\Delta O\)의 부호로 직접 판정하고,
\(\Delta O=0\)이면 \(\Delta R\)의 부호로 직접 판정한다.

따라서 계산기는 무조건 손익분기 %를 출력하면 안 된다.

---

# 7. “보편적인 60% 법칙”이 성립하지 않는 이유

초기 실측에서는 약 60~63% 부근이 손익분기처럼 보였다.

하지만 일반식:

\[
s_C^*=\frac{l}{g+l}
\]

에서 B1/조합이 바뀌면 `g`와 `l`이 달라진다.

따라서 동일한 Rapi 비중이라도:

- Anis: Star의 team Attack Damage +34%
- Liter의 ATK +66%
- Moran의 caster-ATK
- Little Mermaid의 Damage Taken / Attack Damage
- B1 자체딜
- 각 버프의 지속시간

등 때문에 Crown vs Mast의 상대가치가 달라진다.

정확한 표현:

> **같은 조합·스펙·시간축에서 다른 조건을 고정하면 Rapi의 상대적 팀딜 중요도가 손익을 좌우한다. 그러나 서로 다른 B1/버프 환경을 하나의 보편적 Rapi 비중 컷으로 묶을 수는 없다.**

---

# 8. NIKKE Sim에서 현재 사용한 관련 피해식

이 절은 “가설 비교식”이 아니라 **각 캐릭터의 피해를 산출하는 기반식**이다.

Repo:

```text
Infernal-Crack-LED/nikke-sim
```

주요 코드:

```text
src/engine/sim.ts
scripts/blind-rebuild/code-bundle/sim-core-a.ts
src/skills/overrides/crown.json
src/skills/overrides/helm.json
각 캐릭터 override 파일
```

검색 결과 중 일부는 commit:

```text
43308bd02276a476660e44af730785c2ae91eea3
```

를 가리켰고, 일부 최신 fetch는 `main`을 읽었다.  
향후 공식 교차검증 때는 **사용한 repo revision을 한 버전으로 고정**하는 편이 좋다.

---

## 8.1 Effective ATK

NIKKE Sim 구조:

\[
EffectiveATK
=
StaticATK
\left(
1+\frac{ATK\%}{100}
\right)
+
CasterATKFlat
+
기타\ 특수ATK
\]

현재 조합에서 가장 중요한 부분은 앞의 두 항이다.

Boss DEF 반영:

\[
BaseATK=
\max(0, EffectiveATK-BossDEF)
\]

현재 scope-lock:

```text
Boss DEF = 140
```

---

## 8.2 `casterAtkPct`의 의미

이것은 대상 자신의 ATK%가 아니다.

시전자의 Static ATK 기준으로 buff 적용 순간 flat 값으로 변환한다.

\[
CasterATKFlat
=
StaticATK_{caster}
\times
\frac{p}{100}
\]

그 뒤 대상의 Effective ATK에 **고정값으로 더한다**.

예: Treasure Moran

\[
78,707\times0.4257
\approx33,506
\]

즉 팀원 각각에게 약 `+33,506 ATK`를 주는 형태.

중요:

- 시전자의 전투 중 일반 ATK% 버프가 이 값을 재귀적으로 증폭하지 않는 것으로 현재 NIKKE Sim은 처리.
- 대상 자신의 ATK%에도 곱해지지 않고 별도 flat 가산.
- Anis: Star도 같은 종류의 caster-ATK 버프를 가진다.
- 따라서 “Moran만 caster-flat 구조라 threshold가 높다”는 해석은 폐기.

---

## 8.3 기대 피해식의 관련 부분

현재 NIKKE Sim의 핵심 구조:

\[
Damage
=
BaseATK
\times
\frac{AtkPct}{100}
\times Major
\times Element
\times Charge
\times DamageUp
\times Taken
\times Distributed
\]

Projectile Attachment / Explosion은 별도 곱셈 factor가 아니라,
해당 flavor에 적용될 때 `DamageUp` bucket에 가산한다. (§8.7)

현재 scope-lock에서는:

```text
Element = 1
Range bonus = OFF
Core = OFF
Part = OFF
```

이라 많은 항이 제거된다.

---

## 8.4 Major: Full Burst / Crit

대략적 구조:

\[
Major =
1
+
FBBonus
+
RangeBonus
+
ExpectedCritBonus
+
CoreBonus
\]

현재:

```text
Range OFF
Core OFF
```

Full Burst가 적용되는 피해라면:

\[
FBBonus=0.5
\]

즉 +50%가 major에 additive.

기대값 모드의 Crit:

\[
ExpectedCritBonus
=
CritRate
\times
CritBonus
\]

여기서 `CritBonus`는 기본 Crit Damage와 Crit Damage 버프의 증가분.

주의:
- 모든 피해가 crit 가능한 것은 아니며 source별 규칙 확인 필요.
- `burstCast` 즉발 B3 nuke는 Full Burst가 시작되기 전에 발생할 수 있다.
- Helm 8236.8% nuke는 현재 NIKKE Sim에서 FB +50% 제외로 검증되어 있다.

---

## 8.5 Charge

NIKKE Sim 구조:

기본 charge multiplier:

\[
BaseCharge=
\frac{ChargeMultiplier}{100}
\]

Helm 같은 multiplier-class:

\[
Charge
=
BaseCharge
+
BaseCharge
\times
\frac{ChargeDamageMultPct}{100}
+
\frac{ChargeDamagePct}{100}
\]

즉 `Charge Damage Multiplier` 계열과 일반 `Charge Damage ▲`를 구분한다.

Helm Treasure Burst의 +158.4%는 multiplier-class로 현재 모델링.

---

## 8.6 Attack Damage

Attack Damage는 ATK%와 별도 Damage-Up bucket.

대략:

\[
DamageUp=
1+
\frac{
AttackDamagePct
+
해당\ flavor\ 추가값
}{100}
\]

Projectile Explosion / Attachment도 해당 hit flavor에 적용될 때 이 `DamageUp` bucket에 가산된다.
따라서 이미 큰 Attack Damage가 깔려 있으면 같은 bucket의 추가 Attack Damage는 상대적으로 희석된다.

예:
공통 AD가 없을 때 Crown +36.24%:

\[
1 \rightarrow 1.3624
\]

이미 Anis: Star +34%가 있다면:

\[
1.34 \rightarrow 1.7024
\]

절대 +0.3624는 동일하지만 상대증가율은 작아진다.

이런 bucket interaction이 Crown vs Mast 상대가치를 바꾼다.

---

## 8.7 Projectile Attachment / Explosion

정정: 현재 고정 기준 commit

```text
43308bd02276a476660e44af730785c2ae91eea3
```

의 NIKKE Sim에서는 Projectile Attachment / Explosion을 **별도 multiplicative bucket으로 곱하지 않는다.**
해당 flavor에 적용될 때 Attack Damage와 같은 `DamageUp` bucket에 additive로 합성한다.

대략:

\[
DamageUp
=
1+
\frac{
AttackDamagePct+
ProjectileExplosionPct+
ProjectileAttachmentPct+
해당\ flavor\ 추가값
}{100}
\]

source의 `projFactor`는 event/report용 marker로 남아 있을 수 있으나 최종 damage product에 별도 factor로 곱하지 않는다.

현재 관련 캐릭:
- Rapi: Red Hood
- Anis: Star

따라서 전용 계산기에서는 **별도 Projectile multiplier를 만들지 않는다.**
RL normal attack 등은 해당 source/flavor가 Projectile Explosion을 받는지 판정한 뒤 그 값을 `DamageUp`에 주입한다.

기존 event-model 코드가 실제로 별도 Projectile factor를 곱했는지는 이 handoff 문서만으로 확인할 수 없으므로,
기존 수치 재사용 전 구현 확인 또는 수정된 계산기로 재계산한다.

---

## 8.8 Damage Taken

Enemy Damage Taken:

\[
Taken=
1+\frac{DamageTakenPct}{100}
\]

Little Mermaid의 상시 +5.05% Damage Taken은 현재 파티 전체 피해에 공통으로 걸리는 것으로 취급.

같은 LM 케이스 안에서 C/F 모두 모든 캐릭에 동일하게 곱해지면:
- 각 캐릭 C→F 변화율
- 팀 share
- `g`
- `l`
- break-even

에는 공통 스칼라라 상쇄된다.

절대 피해량에는 곱해진다.

---

## 8.9 Distributed

Distributed source일 때만:

\[
Distributed=
1+\frac{DistributedDamagePct}{100}
\]

현재 테스트 캐릭의 핵심 피해원에는 사실상 적용되지 않는 것으로 보고 있으므로,
Mast S2의 distributed +15.03%×stack은 **현재 연구의 비활성 경로**로 분류 가능.

즉 이 공식이 완벽하게 맞는지 검증할 필요는 현재 없다.

---

# 9. 현재 캐릭터별 핵심 스킬 모델

숫자는 현재 연구에 사용한 10/10/10 기준.

---

## 9.1 Crown

핵심:

### S1 — Full Burst Enter

이번 burst chain에서 **Burst Skill을 사용한 캐릭터들**:

- caster-ATK +64.51% of Crown Static ATK
- Reload +44.35%
- 15초

non-burst-casters:

- DEF
- Reload +44.35%
- 15초

즉 caster와 noncaster는 disjoint.

### S2 — Recovery trigger

Crown이 recovery를 받을 때:

- Team Attack Damage +20.99%
- 7초

Helm의 full-charge heal이 자주 들어오므로 거의 상시 refresh되는 구조로 현재 처리.

### Burst

- Team Attack Damage +36.24%
- 15초
- shield는 현재 공격 계산에 직접 inert

중요:
Crown Burst 15초 때문에 다음 cycle로 carryover가 생길 수 있다.

---

## 9.2 Mast

Mast: Romantic Maid.

핵심 상태: Drunken stack, 최대 3.

### Drunken / S1 계열

Drunken 상태 중:
- Team Crit Rate +20.05%
- caster-ATK +35.02% of Mast Static ATK
- max 3 stack state의 운용 및 reset을 정확히 추적

### B3-stage 관련 S2

B3 진입 시 stack 수에 따라:
- Distributed Damage +15.03% × stack
- Reload +15.04% × stack
- 10초

현재 연구에서 distributed는 비활성에 가깝고,
reload는 실제 발사 횟수에 영향을 줄 수 있으므로 활성.

### Mast Burst

- Crit Damage +40.04%
- Attack Damage +15.04%
- caster-ATK +(20.06% × stack) of Mast Static ATK
- 10초

따라서:
- 2stack Burst caster-ATK = +40.12% of Mast static
- 3stack Burst caster-ATK = +60.18% of Mast static

max stack Full Burst 종료 시:
- stack reset
- Hangover stun 10초

이 reset/stun과 stack progression을 event model이 literal하게 추적.

---

## 9.3 Rapi: Red Hood

현재 모델 핵심:

- B1 ally가 있는 Full Burst enter:
  - self ATK +95.04%, 10초
- passive:
  - Projectile Attachment +150.72%
  - Projectile Explosion +100.6%
- rocket meter:
  - 120 attacks 기준
  - own Stage3 window에서는 60
- proc:
  - attachment 88.11
  - explosion 88.11
- B3 missile:
  - 2808%
  - 약 0.4초 delay
- own B3:
  - Projectile Attachment +421.2%, 10초

Core OFF 조건.

Rapi가 `몰아주기`에서 얻는 핵심은 c5/c11의 2stack Mast 패키지를 받는 구조.

---

## 9.4 Helm (Treasure)

현재 10/10/10 sim override:

- SR normal 69.04%
- ammo 6
- reload 141f
- charge 60f
- universal bolt recovery 22f
- base charge multiplier 250%

### S1
last bullet:
- normal attack Crit Rate +14.64%
- 5초

full charge:
- heal → Crown S2 recovery trigger 갱신

### S2
Full Burst enter:
- Team Attack Damage +27.87%
- 10초

full charge:
- additional hit 178.98%

### Burst
- nuke 8236.8%
- burstCast 즉발
- Full Burst +50% 미적용
- own Charge Damage Multiplier +158.4%
- next 10 rounds

현재 연구에서 **몰아주기의 가장 큰 비용이 대체로 Helm의 c6/c12 3스택 Mast Burst 미사용 구간 손실**로 나타났다.

주의:
현재 Helm Treasure override는 최대치가 고정된 형태라 실제 7/6/7 같은 저레벨 Treasure scaling을 그대로 재현하지 못할 가능성이 있다.
그러나 현재 본 연구를 **표준 10/10/10 이론모드**로 제한하면 이 문제는 직접적인 장애가 아니다.
“실제 계정 모드”를 만들 때는 별도 해결 필요.

---

## 9.5 Anis: Star (`돌니스`)

“다른 B1이 없을 때 My Own Star” 조건:

- self ATK +40.01% continuous
- FB enter:
  - team caster-ATK +35.01% of Anis static
  - Team Attack Damage +34%
  - Projectile Explosion +92.03%
  - 10초
- self BurstCast:
  - Attack Damage +35.2%, 10초
- full charge additional 120.13%
- Shooting Stars:
  - 40.01% every 0.25s for 10s
  - projectileExplosion
- charge time clamp 0.7s, 10초
- RL 61.3%, ammo6, reload141f, charge60f, charge250%
- autofire charge로 22f recovery 없음

중요:
Anis도 **caster-ATK based buff**를 가진다.

\[
78,707\times0.3501
\approx27,555
\]

따라서 Moran만 caster-flat이라는 해석은 틀림.

---

## 9.6 Liter

- SMG normal 8.73%
- ammo120
- reload111f
- 24/s

BurstCast 5초 계열:
- maxAmmo +45.17%
- 2회차부터 Crit Damage +12.46%
- 3회차부터 ATK% +14.42%

Burst:
- Team ATK +66%
- 5초

고정 시간축에서는 escalating CDR은 스케줄에 반영하지 않음.

B1/B2/B3→FB 지연 때문에 5초 버프는 Full Burst 전체가 아니라 약 3.6~3.8초 정도를 덮는 구간이 생김.

---

## 9.7 Treasure Moran (`애장품 목단`)

- Defender static = 78,707
- AR normal 14.71%
- ammo60
- reload111f
- base 12/s

BurstCast:
- Team caster-ATK +42.57% of Moran static
- 10초

따라서:

\[
78,707\times0.4257
\approx33,506
\]

Full Burst 시작보다 B1 cast가 앞이므로 실제 FB overlap은 대략 8.6~8.8초.

self:
- weaponSwap 14.7%/shot
- unlimited ammo 10초
- every 5 normal hits: 47.18% additional

중요 caveat:
NIKKE Sim source 자체가 Moran swap throughput을 unresolved/cold로 표시한 적 있음.
sim 약 217M vs real 약 288M 수준의 차이를 기록했고,
per-shot보다 swap fire-rate/bullets-per-pull 문제 가능성을 언급.

현재 **순수 이론모드에서는 임의 실측 보정하지 않는다.**

---

## 9.8 Little Mermaid

- Supporter static = 98,367
- SMG 10.12%
- ammo120
- reload81f
- 24/s

continuous:
- enemy Damage Taken +5.05%

Full Burst enter:
- Team Attack Damage +4%, 10초

Burst:
- Team Attack Damage +10.13%, 10초
- instant reload 0.3326
- self caster-ATK +17.28%, 10초

Full Burst:
- every 1s 63.36% ×4 = 253.44%/s
- 10초 sequential DoT

teamAmmo500:
- Bubble Barrage 85%×10 = 850% sequential

고정 schedule에서는 CDR/gauge effects 제외.

LM을 최종 계산기에 포함한다면:
- DoT crit rule
- sequential damage rule
은 활성 경로이므로 외부 교차검증 대상에 포함해야 한다.

---

# 10. 기존 통합 event-model 구현 요약 — legacy 기록

NIKKE Sim damage-engine semantics와 literal state tracking을 결합해 수동 재구현한 deterministic hybrid reduced/event model.

핵심:

```text
60 fps
위의 실측 B1/B2/B3/FB 타이밍 고정
c1~c12, 173초 종료를 사용했던 legacy 기준
normal firing
ammo
dynamic reload
charge
Helm 22f bolt recovery

Crown S1 targeting
Crown S2 recovery refresh
Mast exact 2/3 stack
Mast reset/stun
Rapi rockets/stored explosion/B3 delayed missile
Helm B3 nuke
Helm next-10-charge enhancement
각 B1의 own damage packet
```

CDR/gauge fill은 fixed cadence이므로 스케줄에 미반영.

이 모델은 stock NIKKE Sim executable을 그대로 실행한 것이 아니다.
GitHub의 damage-engine rule을 참고하되, Mast exact stack/reset 등 연구에 필요한 상태는 literal하게 추적한 **hybrid reduced manual implementation**이다.

따라서 표현:

```text
“nikke-sim을 직접 돌렸다”
```

보다는:

```text
“nikke-sim damage-engine semantics + literal state tracking 기반의 deterministic hybrid reduced/event model”
```

이 정확하다.

---

# 11. 현재 통합 event-model 결과

**중요: 아래 값은 현재 모델 내부에서 재현되는 표준 10/10/10 scope-lock 이론값이다.**
향후 외부 계산기/공식자료로 기반 피해식을 교차검증한 뒤 최종 신뢰도 판정을 한다.

추가 정정:
§8.7의 Projectile bucket 문서식이 수정되었다. 기존 manual event-model 코드가 실제로 별도 Projectile multiplier를 사용했는지는 이 문서만으로 확인할 수 없다.
따라서 아래 raw 결과와 threshold는 **legacy regression reference / provisional 값**으로 보존하고, 수정된 계산기 재계산 전에는 최종 정량값으로 확정하지 않는다.

---

## 11.1 Anis: Star

### 크크메

| Unit | Damage M |
|---|---:|
| Anis | 757.7121 |
| Crown | 252.4109 |
| Rapi | 1370.5937 |
| Helm | 527.5504 |
| Mast | 117.6163 |
| Total | 3025.8834 |

### 몰아주기

| Unit | Damage M | C→F |
|---|---:|---:|
| Anis | 749.4209 | -1.094% |
| Crown | 246.7661 | -2.236% |
| Rapi | 1387.6950 | +1.248% |
| Helm | 494.8361 | -6.201% |
| Mast | 118.4741 | +0.729% |
| Total | 2997.1923 | -0.948% |

크크메 Rapi share:

\[
45.30\%
\]

Break-even:

\[
\lambda_*=2.6777
\]

\[
\boxed{s_C^*=68.92\%}
\]

---

## 11.2 Liter

### 크크메

| Unit | Damage M |
|---|---:|
| Liter | 185.2515 |
| Crown | 228.6754 |
| Rapi | 1202.6429 |
| Helm | 593.6247 |
| Mast | 107.0146 |
| Total | 2317.2091 |

### 몰아주기

| Unit | Damage M | C→F |
|---|---:|---:|
| Liter | 182.6732 | -1.392% |
| Crown | 224.2758 | -1.924% |
| Rapi | 1220.3703 | +1.474% |
| Helm | 560.5846 | -5.566% |
| Mast | 109.0385 | +1.891% |
| Total | 2296.9424 | -0.875% |

크크메 Rapi share:

\[
51.90\%
\]

\[
\lambda_*=2.1432
\]

\[
\boxed{s_C^*=69.81\%}
\]

---

## 11.3 Treasure Moran

### 크크메

| Unit | Damage M |
|---|---:|
| Moran | 246.6405 |
| Crown | 220.7502 |
| Rapi | 1096.5315 |
| Helm | 516.2841 |
| Mast | 101.8346 |
| Total | 2182.0409 |

### 몰아주기

| Unit | Damage M | C→F |
|---|---:|---:|
| Moran | 243.1934 | -1.398% |
| Crown | 215.9521 | -2.174% |
| Rapi | 1108.3125 | +1.074% |
| Helm | 484.8107 | -6.096% |
| Mast | 102.5841 | +0.736% |
| Total | 2154.8529 | -1.246% |

크크메 Rapi share:

\[
50.25\%
\]

분해:

\[
R_C=1096.53
\]

\[
R_F=1108.31
\]

\[
O_C=1085.51
\]

\[
O_F=1046.54
\]

\[
\Delta R=+11.78
\]

\[
O_C-O_F=38.97
\]

\[
\lambda_*=3.3078
\]

\[
\boxed{s_C^*=76.97\%}
\]

현재 모델 내부에서는 이 값이 대수적으로 재검산됨.

---

## 11.4 Little Mermaid

표시된 절대값에는 common Damage Taken +5.05% scalar 포함.

### 크크메

| Unit | Damage M |
|---|---:|
| Little Mermaid | 694.6430 |
| Crown | 223.6031 |
| Rapi | 1184.8595 |
| Helm | 507.5657 |
| Mast | 100.9402 |
| Total | 2711.6115 |

### 몰아주기

| Unit | Damage M | C→F |
|---|---:|---:|
| LM | 686.9049 | -1.114% |
| Crown | 218.7691 | -2.162% |
| Rapi | 1201.5296 | +1.407% |
| Helm | 473.0521 | -6.800% |
| Mast | 102.5896 | +1.634% |
| Total | 2682.8454 | -1.061% |

크크메 Rapi share:

\[
43.70\%
\]

\[
R_C=1184.86,\quad R_F=1201.53
\]

\[
O_C=1526.75,\quad O_F=1481.32
\]

\[
\Delta R=+16.67
\]

\[
O_C-O_F=45.43
\]

\[
\lambda_*=2.7256
\]

\[
\boxed{s_C^*=67.90\%}
\]

---

# 12. 네 B1의 `g / l` 요약

| B1 | Rapi gain `g` | non-Rapi loss `l` | `l/g` | Break-even `s_C*` |
|---|---:|---:|---:|---:|
| Anis: Star | +1.248% | 2.766% | 2.217 | **68.92%** |
| Liter | +1.474% | 3.409% | 2.313 | **69.81%** |
| Treasure Moran | +1.074% | 3.590% | 3.341 | **76.97%** |
| Little Mermaid | +1.407% | 2.976% | 2.115 | **67.90%** |

이 표가 현재 인과해석에서 가장 안전하다.

Treasure Moran이 높은 이유를 현재 모델 결과 자체로만 표현하면:

```text
1) Rapi의 몰아주기 상대이득 g가 네 케이스 중 가장 작고
2) 나머지 4인의 평균손실 l이 가장 크다.
```

그보다 더 세부적인 “어떤 버프가 몇 %p를 만들었다”는 설명은
통제 ablation이 끝나기 전까지 확정하지 않는다.

---

# 13. 비Rapi 손실의 구조

현재 결과에서 Helm은 대부분의 경우 가장 큰 비용이다.

대략 gross loss 기준:

### Anis
- Anis loss ≈ 8.29M
- Crown loss ≈ 5.64M
- Helm loss ≈ 32.71M
- Mast gain ≈ +0.86M
- net non-Rapi loss ≈ 45.79M

Helm이 gross loss의 약 71%.

### Liter
- Liter loss ≈ 2.58M
- Crown loss ≈ 4.40M
- Helm loss ≈ 33.04M
- Mast gain ≈ +2.02M
- net ≈ 37.99M

Helm 비중 매우 큼.

### Moran
- Moran loss ≈ 3.45M
- Crown loss ≈ 4.80M
- Helm loss ≈ 31.47M
- Mast gain ≈ +0.75M
- net ≈ 38.97M

### Little Mermaid
- LM loss ≈ 7.74M
- Crown loss ≈ 4.83M
- Helm loss ≈ 34.51M
- Mast gain ≈ +1.65M
- net ≈ 45.43M

따라서 순수 운용 경제는 크게 보면:

```text
c5/c11: Rapi가 Mast2를 받아 얻는 것
VS
c6/c12: Helm이 Mast3를 잃는 것
```

의 경쟁이고,
B1/Crown/Mast의 변화가 그 주변을 보정한다.

---

# 14. 현재 실측자료의 취급

과거 참고값:

- Anis empirical:
  - 크크메 Rapi share 약 56.06%
  - 몰아주기 total 약 -0.714%

- Treasure Moran:
  - 크크메 Rapi share 약 62.97%
  - 몰아주기 약 +0.153% (사실상 tie)

- low-invest Liter:
  - 과거 raw를 재검토하여 대략 +0.106% 수준으로 수정
  - 초기 +0.57% 기억값은 신뢰하지 않음

그러나 현재 연구에서는 위 실측을 **모델 파라미터 보정에 쓰지 않는다.**

이유:
실측 보스는 Mast 3스택 주기에 고정적으로 점프하여 약 2~3초 타격로스가 발생.

이것은 랜덤노이즈가 아니라 운용 스택과 상관된 외생변수다.

정확히 쓰려면 매 run마다:

```text
Mast 몇 stack?
누가 B3?
보스 점프 시작/끝?
Rapi/Helm의 nuke가 잘렸는가?
normal firing 몇 초 손실?
Crown/Mast carryover 동안 실제 타격 가능했는가?
```

를 전부 복원해야 한다.

비용이 지나치게 크므로 중단.

현재 방침:

> **이론 계산을 본 연구로 하고, 실측은 필요 시 완전히 통제 가능한 보스/환경에서만 sanity check.**

중요한 구분:

- 위 판단은 `패턴 타격손실을 연구하지 않는다`는 뜻이 아니다.
- 기존 실측의 2~3초 점프값을 본 연구의 threshold 보정에 직접 넣지 않는다는 뜻이다.
- 후속 연구에서는 미스/크리/조준편차/진입 HP 같은 비통제 잡음은 제외하고, **`Mast3가 예정된 10초 Full Burst 구간에서 얼마만큼의 유효피해가 사라지는가`만 독립변수로 둔다.**
- 따라서 기존 실측은 후속 연구의 동기를 제공하지만, 후속 연구의 숫자를 calibration하는 자료는 아니다.

---

# 15. 전용 계산기 설계안

목표:

```text
Crown–Mast Rotation Calculator
```

NIKKE Sim 전체 복제품이 아니라
**Crown/Mast 운용 상대비교에 필요한 부분집합 engine**.

## 15.A 2026-08-29 현재 구현 상태

현재 Python 전용 엔진에는 다음이 구현되어 있다.

```text
고정 c1~c12 타임라인과 180초 terminal-tail
크크메 / 지속 몰아주기 강제 B2 정책
live Drunken 0..3
Mast S1 gate, S2/Burst stack snapshot, FB-end reset/Hangover
Mast live Drunken별 자기 평타 기대 적중 손실과 Hangover 무기 상태 정지
Crown S1/S2/Burst
Liter / Rapi: Red Hood / Helm (애장품) 캐릭터 모듈
Base-5 / OL0 / OL5 슬롯별 장비 기반
Boss DEF와 공통 피해 bucket
MG / SMG / SR cadence, ammo, reload, charge, durationShots
캐릭터·피해 종류·발생원·개별 Burst·3버스트 macro-cycle별 집계
ΔR/ΔO 부호 case, g, l, lambda*, s*, 실제 승패 판정
local slope g+l와 local extreme upside g
Secondary B3의 3스택 Mast Burst 미사용 구간 자동 검출 및 운용 간 피해 집계
Mast 자기 평타 기대손실 0/18/20/22% per stack 민감도 sweep
Scarlet: Black Shadow 완충 3단계 S1·분배 대미지·S2·Burst 모듈
```

Mast의 Hit Rate 감소는 탄착 원뿔을 직접 시뮬레이션하지 않는다. pinned NIKKE Sim이
실측 표본에 맞춘 `평균 2스택 = 자기 평타 -40%` 근사를 live state로 확장하여,
`normal_attack_pct = -20% × 현재 Drunken`을 Mast 자신의 일반 공격에만 적용한다.
공통 `core_hit_rate_pct`에는 영향을 주지 않는다.

현재 민감도 sweep:

```text
기대손실/stack   몰아주기 delta   현재 Main share   break-even share
0%               -1.4105%         45.5936%          72.3234%
18%              -1.2335%         47.3248%          71.4437%
20%              -1.2130%         47.5253%          71.3343%
22%              -1.1923%         47.7275%          71.2222%
```

명중 손실을 완전히 제거한 0% 극단과 기준값 ±10% 범위 모두 크크메 우세가 유지된다.

아직 남은 연구용 기능:

```text
Liter 외 B1 표본
흑련 외 추가 Main·Secondary B3 표본
Boss DEF 자동 sweep
M1 opener robustness run
패턴 대응형 2스택 손익분기
```

고정 commit `43308bd02276a476660e44af730785c2ae91eea3`과의 순수 무기 교차검증에서는
스킬·Burst·보스 이동을 끄고 동일한 Static ATK, Base-5, Boss DEF 140, Core/Range/Element
OFF 조건을 사용했을 때 양쪽 팀 피해가 다음과 같이 일치했다.

```text
전용 엔진    144,674,000.646097
NIKKE Sim    144,674,000.646096
```

캐릭터별 피해와 발사 횟수도 일치했다. 이는 Static ATK, Boss DEF, 평타 계수, 기대 치명타,
장탄·재장전, MG/SMG/SR 기본 cadence 경로의 parity를 확인한 결과다. 전체 스킬 및 회전
결과의 parity를 뜻하지 않는다. Stock Team Sim은 같은 편성에서 Crown 11회, Mast 0회로
동작했으므로 연구의 강제 B2 정책 총딜과 직접 비교하지 않는다.

## 15.0 고정/교체 구조

계산량과 검증범위를 줄이기 위해 다음 구조로 고정한다.

본 연구 baseline 고정:
```text
Crown
Mast: Romantic Maid
Helm (Treasure)
12-cycle timeline
크크메 / 지속 몰아주기 B2 rotation
Standard Theory scope-lock (Boss DEF는 기본 140, DEF sweep에서만 변경)
```

본 연구 교체/가변:
```text
B1
Main B3 dealer
Boss DEF (default 140)
```

Boss DEF는 캐릭터 스펙 커스터마이징과 달리 **단일 외부환경 축**으로만 허용한다.
일반 보스 연구에서는 140을 기본값으로 고정하고, 하드 스테이지/고DEF처럼 `EffectiveATK - BossDEF` 여유가 작아지는 환경을 볼 때만 입력값 또는 sweep 축으로 변경한다.

Helm은 `실사용 가능한 B3 중 상대적으로 낮은 딜 기준점`이라는 연구 설계상의 역할을 가진다.
정확히 몇 위인지 자체가 핵심은 아니며, 상위권 메인 B3보다 충분히 낮은 딜 기여도를 가져 메인캐리 비중을 크게 만들기 쉬운 비교조건이라는 점이 중요하다.

후속 연구에서는 질문이 달라지므로 Helm 고정을 해제할 수 있다.  
패턴 대응형 2스택 선사용의 임계점을 볼 때는 **동등한 성장 기준에서 실질 DPS가 비슷한 B3 두 명**을 우선 사용해, `한쪽이 원래 훨씬 강해서 M2를 주는 효과`와 `M3 구간 패턴손실 효과`가 섞이지 않게 한다.

기존 수식의 `R`은 baseline에서는 Rapi: Red Hood를 뜻하지만,
전용 계산기에서는 **현재 선택된 Main B3 dealer**를 뜻하는 변수로 사용한다.

권장 구조:

```text
Engine
- time / buff / ammo / reload / charge / fire
- Crown
- Mast
- 공통 damage formula
- damage flavor routing (normal / distributed 등)
- Distributed Damage bucket (해당 source가 있을 때만 활성)
- Boss DEF input / DEF sweep

Character modules
- B1 module
- Main B3 module
- Secondary B3 module (본 연구 baseline은 Helm)
- Scarlet: Black Shadow(흑련) B3 module — 구현 완료, 규칙 민감도 검증 대기

Analysis
- C run / F run
- unit별 damage
- damage source / flavor별 damage split
- total delta
- g / l / s*
- Distributed Damage 기여분 / C-F 변화
- DEF sensitivity
```

캐릭터 모듈은 해당 캐릭터가 실제로 사용하는 damage source만 구현한다.
현재 scope에서 비활성인 Core / Element / Part / Range / Burst gauge / CDR 등의 경로는 필요해질 때 추가한다.

### 흑련(Scarlet: Black Shadow) / Distributed Damage 확장

흑련은 계산기 초기 B3 확장 대상에 **우선 포함한다.**
이유는 단순히 강한 B3 대표이기 때문만이 아니라, 흑련이 들어오면 지금까지 baseline에서 사실상 비활성이었던 **Distributed Damage 경로가 실제 결과에 들어오기 때문**이다.

특히 Mast의 stack-scaled Distributed Damage buff가 흑련의 distributed-flavor damage source에 직접 작용하므로,
흑련 case는 `Secondary B3가 강해질수록 크크메가 유리한가`만 보는 샘플이 아니라 다음 질문을 함께 검증한다.

```text
Mast2 / Mast3의 Distributed Damage 차이가
크크메 vs 지속 몰아주기 손익을 얼마나 바꾸는가?
```

구현 원칙:

```text
- Distributed Damage를 흑련 전용 예외식으로 하드코딩하지 않는다.
- 공통 damage engine에 distributed flavor와 distributedDamagePct 경로를 추가한다.
- distributed flavor가 붙은 damage instance에만 해당 modifier가 적용되게 한다.
- Mast의 1/2/3 stack 실제 값과 duration을 stateful하게 연결한다.
- 흑련 외에 향후 distributed source를 가진 B3를 추가해도 같은 경로를 재사용한다.
```

흑련 모듈의 세부 proc cadence / damage source / crit·Full Burst 적용 여부 등은 계산기 구현 시 선택한 NIKKE Sim 고정 revision과 독립 자료로 검증한 뒤 pin한다.
현재 문서 단계에서는 숫자를 미리 확정하지 않고 **`흑련 추가 시 Distributed Damage가 활성 검증항목으로 승격된다`**는 설계 요구만 고정한다.

흑련 case에서는 결과표에 최소한 다음을 별도 출력한다.

```text
흑련 total damage C/F
흑련 distributed damage C/F
흑련 non-distributed damage C/F
Mast2 vs Mast3에 의해 달라진 distributed bonus 기여분
team total에서 distributed 경로가 만든 delta
```

이렇게 해야 흑련에서 결과가 예상과 다르게 나와도 `강한 B3 자체의 효과`와 `Mast Distributed Damage 시너지`를 분리해서 해석할 수 있다.

---

## 15.1 표준화 연구 모드만 사용

현재 계산기는 사용자 계정 최적화 도구가 아니라 **통제된 비교실험 도구**로 설계한다.

기준:

```text
Sync400
Base5
Skill 10/10/10
no OL
no cube
no core/range/element/part
Boss DEF = 140 (default; optional DEF sweep)
fixed 12-cycle timeline
```

`동등한 성장`은 모든 캐릭터의 ATK를 같은 숫자로 강제한다는 뜻이 아니다.  
동일한 투자 규칙을 적용하되 class / weapon / skill에서 생기는 캐릭터 고유 스탯 차이는 그대로 유지한다.

### Boss DEF만 예외적으로 가변 허용

Boss DEF는 현재 계산기에서 **스펙 외 유일한 추가 가변축**으로 둔다.

이유:

- 일반적인 동등성장 스케일링에서는 C/F 양쪽 피해가 함께 변해 `g/l/s*`가 비교적 안정적일 가능성이 높다.
- 반면 Boss DEF가 높아져 `EffectiveATK - BossDEF` 여유가 작아지면 ATK / caster-ATK 계열 버프의 실효가 커지고, 캐릭터별 상대딜·메인캐리 비중·`g/l` 자체가 크게 달라질 수 있다.
- 따라서 일반 보스에서 얻은 `크크메 vs 몰아주기` 결론을 고DEF 하드 환경에 그대로 이식하지 않고, 같은 계산기에서 DEF만 바꿔 별도 local result를 낸다.
- 구현비용은 §8.1의 `BaseATK=max(0, EffectiveATK-BossDEF)`에 입력값 하나를 연결하는 수준이라 낮다.

권장 사용:

```text
General / baseline mode:
Boss DEF = 140

High-DEF mode:
Boss DEF 사용자 입력 또는 일정 구간 sweep
```

DEF sweep은 **고DEF라는 한 변수의 효과를 분리해서 보는 통제실험**이다.
실제 고결손 하드 스테이지의 모든 전투력 페널티·스탯 감소를 자동 재현하는 모드는 아니며, 필요하다면 그 문제는 별도 연구로 둔다.

### 스펙 커스터마이징 / Actual Account Mode

현재 연구 범위에서는 **구현하지 않는다.**

이유:

- 메인캐리만 고돌파/고OL/고우월 등으로 크게 앞서는 비대칭 육성은 몰아주기 가치에 영향을 줄 수 있지만, 이는 `일반적인 동등성장 환경에서 운용 자체가 유효한가`라는 본 질문과 다른 변수다.
- 개별 계정 입력을 허용하려면 OL / 우월 / 장탄 / 차속 / 소장품 / 큐브 / 스킬 투자차 등 경우의 수가 급격히 늘어난다.
- 구현·검증 비용에 비해 얻는 정보는 주로 `극단적인 육성 편중에서는 몰아주기가 유효할 수 있다`는 예외 확인에 가깝다.
- 따라서 먼저 표준화 조건에서 구조적 경향을 확정하고, 필요하면 전체 성장점 자체를 일괄 스케일하는 간단한 민감도 검사만 한다.

## 15.2 계산기는 stateful이어야 함

각 frame 또는 충분히 세밀한 event time마다 유지할 상태:

```text
active buffs
buff start / expiry
caster identity
burstCasters / nonBurstCasters
Mast stack
Mast hangover/stun
ammo
reload state/progress
charge progress
durationShots
weapon swap
Rapi rocket meter / stored hits
```

c5/c6/c11/c12만 계산하는 방식은 위험.

---

## 15.3 추천 출력

### 1차: 실제 총피해 판정

| Unit | 크크메 | 몰아주기 | Δ% |
|---|---:|---:|---:|

그리고:

\[
\Delta T=T_F-T_C
\]

현재 조건에서 누가 이기는지 직접 판정.

### 2차: 구조 분석

\[
g=R_F/R_C-1
\]

\[
l=1-O_F/O_C
\]

일반적인 `g>0, l>0` tradeoff case에서는:

\[
s_C^*=\frac{l}{g+l}
\]

또한 현재 실제 Main B3 share를 `s=R_C/T_C`라 하면:

\[
\frac{T_F-T_C}{T_C}=sg-(1-s)l=(g+l)(s-s_C^*)
\]

출력:

```text
Boss DEF
Main B3 funnel gain g
non-main weighted loss l
현재 크크메 기준 Main B3 share s
크크메 기준 Main B3 break-even share s*
현재 total delta / delta %
local slope g+l
local extreme upside g (해석용; s=1 local extrapolation)
각 캐릭터의 C/F 절대손익
Secondary B3의 3스택 Mast Burst 미사용 구간 피해 차이
```

### threshold 출력 전 부호 판정

계산기는 무조건 `s*`를 숫자로 출력하지 않는다. 먼저 §6의 `ΔR / ΔO` case를 판정한다.

```text
ΔR>0, ΔO<0  → 정상적인 양의 break-even; s* 출력
ΔR≥0, ΔO≥0  → Funnel dominance
ΔR≤0, ΔO≤0  → CCM dominance
ΔR<0, ΔO>0  → 반대 방향 break-even; 방향을 명시해서 출력
ΔR≈0 또는 g+l≈0 → 수치 threshold 대신 직접 부호판정
```

`Secondary B3의 3스택 Mast Burst 미사용 구간 피해 차이`는 Helm보다 강한 B3를 붙였을 때 운용 결과가 어떻게 이동하는지 확인하는 보조지표다.
몰아주기에서도 Mast S2는 현재 Drunken 3스택을 읽으므로, 빠지는 것은 Mast3 전체가 아니라 3스택 Mast Burst 버프다. 또한 이 값은 해당 버프만 제거한 반사실 인과효과가 아니라 c6/c12의 운용 간 관측 피해 차이다.

### 현재 Liter baseline 결과

현재 구현된 Liter / Crown / Mast: Romantic Maid / Rapi: Red Hood / Helm (애장품),
Base-5, Boss DEF 140, Core/Range/Element/Part OFF, 180초 terminal-tail 결과는 다음과 같다.

```text
크크메 total                    2,096,368,373.67
지속 몰아주기 total            2,070,939,773.66
total delta                    -25,428,600.01
total delta %                  -1.2130%
Rapi funnel gain g             +1.4604%
non-main weighted loss l        3.6342%
현재 크크메 Rapi share s       47.5253%
break-even Rapi share s*       71.3343%
local slope g+l                 5.0946%
local extreme upside g         +1.4604%
lambda*                         2.7476
Helm c6/c12 3스택 Mast Burst 미사용 구간 피해 차이  36,628,355.73 (19.3738%)
판정                            크크메 우세
```

이는 현재 전용 엔진의 첫 활성 baseline 결과이며 연구 전체의 최종 결론은 아니다. B1/Main B3/
Secondary B3 표본과 DEF 민감도를 확장한 뒤 방향의 반복성을 판정한다. `lambda*`는 Rapi의
최종 damage packet을 국소적으로 가중하는 추상값이며 Static ATK 배율이나 실제 육성 권고가 아니다.

### Scarlet: Black Shadow Secondary B3 provisional 표본

동일한 Liter / Crown / Mast / Rapi 편성에서 Secondary B3만 흑련으로 교체한 결과:

```text
크크메 total                    2,004,495,344.74
지속 몰아주기 total            2,000,134,867.01
total delta                    -4,360,477.74
total delta %                  -0.2175%
Rapi funnel gain g             +1.5107%
non-main weighted loss l        1.3298%
현재 크크메 Rapi share s       39.1579%
break-even Rapi share s*       46.8162%
흑련 share                      43.2751%
c6/c12 3스택 Mast Burst 미사용 구간 피해 차이  12,145,754.40 (4.5844%)
판정                            크크메 근소 우세
```

흑련의 분배 추가타 합계는 크크메 `581,969,242.84`, 몰아주기 `573,264,337.88`이다.
다만 pinned NIKKE Sim이 사용하는 일반 구간 `3회/phase`, 본인 B3 구간 `1회/phase`의
scalar cadence는 원본에서도 측정 대기 규칙이다. 분배 추가타의 치명타·Full Burst·속성
적용도 disputed이므로 이 표본은 해당 규칙 민감도 검증 전까지 provisional이다.

### 3차: DEF sensitivity (선택)

대표 조합에서는 Boss DEF를 sweep하여 다음을 함께 출력한다.

```text
Boss DEF
크크메 total
몰아주기 total
total delta / delta %
Main B3 share
g / l / s*
```

목적은 `몇 DEF에서 반드시 몰아주기` 같은 보편 상수를 만드는 것이 아니라,
**고DEF로 갈수록 일반 보스에서 얻은 결론이 언제부터 유의미하게 흔들리는지** 확인하는 것이다.

운용 우위의 부호가 바뀌는 경우에는 대략적인 `DEF reversal region`을 보조 출력할 수 있다.
경계 부근의 소수점 정밀도보다, 일반 DEF 구간과 고DEF 구간에서 방향성이 달라지는지 여부를 우선한다.

---

## 15.4 본 연구의 권장 테스트 매트릭스

### Phase 1 — B1 환경 sweep

```text
Main B3 + Helm 고정
B1만 여러 타입으로 교체
Boss DEF = 140
```

목적:
- B1 자체딜의 크기
- ATK / caster-ATK / Attack Damage 등 버프구조
- B1이 5인 total과 g/l에 주는 영향

을 바꾸어도 `몰아주기가 높은 메인캐리 비중을 요구한다`는 방향이 반복되는지 확인.

**중요:** 이 Phase의 B1은 현실적인 rotation enabler를 선별하는 것이 아니다.
실제 CDR / gauge만으로 고정 12-cycle 회전이 자연스럽게 성립하지 않는 B1이라도, C/F 양쪽에 동일한 cadence를 강제하여 **버프환경 비교군**으로 사용할 수 있다.
따라서 `이 B1로 실제 그 사이클이 가능한가`는 Phase 1의 탈락조건이 아니다.

### Phase 2 — Secondary B3 강도 sweep

Helm을 기준점으로 두고:

```text
상위권/주류 B3 대표 몇 명
- Scarlet: Black Shadow(흑련) 우선 포함
  - 강한 B3 대표
  - Distributed Damage 활성 대표 case
+ 보스 DPS가 매우 낮은 비주류 B3 1명(극단값 확인용)
Boss DEF = 140
```

정도만 추가한다.

목적:
- Helm보다 강한 B3를 붙였을 때 메인캐리 비중 하락 및 Mast3 포기비용 증가가 실제로 크크메 쪽으로 작용하는지 확인.
- 흑련에서는 Mast의 Distributed Damage buff가 실제 damage source에 들어가므로, 일반 B3와 다른 `Mast2 vs Mast3` 손익이 생기는지 별도 확인.
- 흑련 결과가 일반 case와 다르면 `강한 Secondary B3라서`인지 `Distributed Damage 시너지 때문인지` damage-source split으로 분해.
- 반대로 매우 약한 B3까지 내려갔을 때도 지속 몰아주기의 이득이 작다면, `극단적인 원맨캐리 구조에서도 보상이 제한적`이라는 직관적 상한 예시를 제공.
- 극단값에서 몰아주기가 확실히 강해진다면, `몰아주기는 존재 의미가 없다는 것이 아니라 매우 편중된 조합에서만 의미가 커진다`는 경계를 제시.

이 테스트는 모든 B3를 전수조사하려는 것이 아니다.  
연구 질문에 필요한 경계조건과 대표 구간만 확인한다.

### Phase 3 — Boss DEF sweep

Phase 1/2에서 대표성이 확인된 몇 조합만 선택하여 **캐릭터·성장·시간축은 그대로 두고 Boss DEF만 변경**한다.

```text
B1 고정
Main B3 고정
Secondary B3 고정
Boss DEF: 140 → 고DEF 구간 sweep
```

목적:
- 고DEF에서 ATK / caster-ATK의 가치가 커지면서 메인캐리 비중과 `g/l/s*`가 얼마나 이동하는지 확인.
- 일반 보스에서는 사소했던 `크크메 vs 지속 몰아주기` 차이가 하드형 고DEF 환경에서 확대되거나 역전되는지 확인.
- `일반 보스는 크크메 기본` 같은 가이드에 **고DEF 환경은 local calculation 필요**라는 예외를 어느 정도 강도로 붙여야 하는지 판단.

이 단계에서도 개별 계정 스펙은 바꾸지 않는다.
따라서 DEF 외의 변수가 결과에 섞이지 않는다.

현재 전용 계산기는 Crown/Mast 운용 비교가 목적이므로 `Crown+Helm vs Crown+Mast`처럼 B2 구성 자체를 바꾸는 지원조합 비교는 별도 연구 범위다.

---

## 15.5 공개 자료의 활용 원칙과 현재 연구 gap

현재 검색 가능한 공개 공략에서는 `메인캐리 + Helm이면 Mast를 메인캐리에 더 자주 맞춘다`는 식의 지속 몰아주기 운용 지침을 여러 번 확인했다.
반면 현재까지 찾은 범위에서는 다음을 동시에 만족하는 통제 A/B 연구를 확인하지 못했다.

```text
동일 5인
동일 성장/스펙 기준
동일 시간축
동일 타격조건
크크메 vs 지속 몰아주기만 독립변수
5인 총피해 또는 동일 구간 HP 변화 비교
```

따라서:

- `몰아주기를 자주 쓴다`는 사실은 **사용 관습/실전 휴리스틱의 존재**를 보여주는 자료로 사용한다.
- `해보니 더 센 것 같다`는 단일 체감은 미스/크리/패턴/진입상태가 통제되지 않으므로 intrinsic rotation value의 근거로 사용하지 않는다.
- 공개자료에서 통제연구를 찾지 못했다는 것은 `그런 연구가 존재하지 않는다`는 증명이 아니다. 검색되지 않는 Discord / 영상 내부 / 비공개 sheet 등이 있을 수 있다.
- 본 전용 계산기의 역할은 바로 이 공백을 **표준화 조건의 반복 가능한 비교**로 메우는 것이다.

NIKKE Sim의 standardized DPS ranking 등은 캐릭터 선택을 위한 **상대적 위치 참고자료**로 사용할 수 있다.
정확한 실전 DPS 자체를 증명하는 용도가 아니라, Helm이 상위권 Main B3보다 낮은 딜 기준점인지, 극단값 B3가 어느 정도 떨어져 있는지 등 대표 샘플을 고르는 데 사용한다.

---

# 16. 외부 교차검증 계획

목표는:

> “NIKKE Sim이 완벽함을 증명”이 아니다.

목표:

> **현재 Crown/Mast 파티에서 실제 결론에 들어오는 계산규칙이 다른 독립 계산기/공개 공식/공략 자료와 대체로 일치하고, 남은 오차가 손익분기를 크게 뒤집을 가능성이 낮음을 확인.**

---

## 16.1 최우선 검증 항목

### 매우 중요 / 활성

1. Effective ATK
   - StaticATK × (1 + ATK%)
   - caster-ATK flat의 위치
   - DEF 차감 순서

2. caster-ATK
   - 시전자 Static ATK 기준인가
   - target ATK%와 분리인가
   - 일반 ATK buff가 caster flat을 재귀증폭하지 않는가

3. Attack Damage
   - ATK bucket과 분리된 Damage-Up bucket인가
   - 같은 Attack Damage끼리 additive인가

4. Crit
   - Crit Rate / Crit Damage 기대식
   - skill / nuke / additional damage의 crit 가능 여부

5. Full Burst +50%
   - major additive 구조
   - burstCast 즉발 nuke는 제외되는가

6. Charge
   - ordinary Charge Damage
   - Charge Damage Multiplier의 차이

7. Reload
   - reload buff가 실제 발사 횟수에 미치는 공식
   - 특히 Crown 44.35%, Mast stack reload

8. Buff duration / refresh
   - 같은 buff refresh
   - 다른 caster/skill stack
   - 15초 carryover

9. Crown S1 targeting
   - 현재 chain의 burst casters만 caster-ATK
   - noncasters와 disjoint

10. Mast 2/3stack
    - stack progression
    - Burst caster-ATK
    - reset/hangover

11. Rapi/Anis projectile bucket
    - 교차검증 완료: attachment/explosion은 별도 multiplier가 아니라 DamageUp에 additive
    - RL normal 등 source/flavor별 적용 여부와 구현 regression 확인

12. Helm
    - B3 burstCast ordering
    - 10-round charge enhancement
    - full-charge additional hit

### LM을 포함할 경우 추가

13. Damage Taken
14. DoT crit
15. Sequential damage

---

## 16.2 현재 검증 불필요 또는 낮은 우선순위

현재 scope-lock/현재 damage sources 기준:

- Core formula
- Element advantage
- Part damage
- Range bonus
- Pierce
- Distributed Damage (현재 source가 distributed가 아니면)
- defensive HP/DEF/shield
- CDR
- Burst gauge generation

단, 향후 파티나 조건을 바꾸어 해당 경로가 활성화되면 검증 목록에 추가.

---

# 17. 민감도 분석 계획

외부 자료가 완전히 일치하지 않는 항목이 생기면:

- ±5%
- ±10%

로 rule/value를 흔들어 break-even을 재계산.

예:

```text
기준 break-even 69.0%
의심 coefficient ±10%
결과 68.3~69.8%
```

이면 결론 robust.

반대로:

```text
60~75%
```

처럼 크게 흔들리면 그 공식은 고신뢰 검증이 끝날 때까지 결과 확정 금지.

스펙 민감도는 개별 계정 커스터마이징으로 확장하지 않는다.  
필요할 경우 대표 조합에 한해 표준 성장점을 통째로 ±20~30% 등으로 일괄 이동시켜 `g/l/s*`가 크게 흔들리는지만 확인한다.
동등 성장 스케일링에서 결론이 안정적이면 그 이상 세분화하지 않는다.

민감도 분석에서는 threshold 위치뿐 아니라 **몰아주기 우위의 크기**도 같이 본다.

```text
- s*가 얼마나 이동하는가
- 현재 s에서 total delta %가 얼마나 이동하는가
- g+l(local slope)가 얼마나 이동하는가
- 몰아주기가 이기는 대표/극단 case에서도 실제 upside가 몇 %인가
```

예를 들어 threshold가 다소 움직여도, 몰아주기 우위 영역에서 최대 이득 자체가 계속 매우 작다면
`기본 회전을 단순한 크크메 계열로 두어도 regret이 작다`는 구현 판단에는 여전히 robust한 근거가 될 수 있다.
반대로 threshold는 높아도 특정 조건에서 몰아주기 이득이 크게 확대되면, 해당 조건은 별도 rotation policy의 필요성을 시사한다.

---

# 18. 현재 연구에서 안전하게 말할 수 있는 결론

1. **순수 손익은 반드시 5인 총피해로 계산해야 한다.**
2. 몰아주기 우위는:
   \[
   R_F-R_C > O_C-O_F
   \]
   일 때 발생.
3. local Rapi-share break-even:
   \[
   s_C^*=\frac{l}{g+l}
   \]
4. local `g,l`을 고정하면 현재 Main B3 share `s`에서의 총손익은:
   \[
   \frac{T_F-T_C}{T_C}=sg-(1-s)l=(g+l)(s-s_C^*)
   \]
   로 표현할 수 있다. 따라서 threshold뿐 아니라 **threshold를 넘은 뒤 실제 이득 크기**도 별도 판단축이다.
5. B1/버프환경이 바뀌면 `g,l`이 바뀌므로 보편적인 단일 Rapi 딜비중 컷은 현재 없음.
6. 현재 전용 엔진의 첫 Liter baseline에서는 크크메가 약 1.2130% 우세하고, Rapi의 실제
   크크메 팀딜 비중 47.5253%에 비해 local break-even은 71.3343%다.
   - 이는 단일 표본이므로 `몰아주기는 대부분 비유효`라는 일반 결론으로 확정하지 않는다.
   - 173초 경계에서도 크크메 우세가 유지되며 break-even은 72.4865%다.
7. 기존 event-model에서 산출된 네 threshold는 현재 **legacy/provisional**로 보존:
   - Anis: Star 68.92%
   - Liter 69.81%
   - Treasure Moran 76.97%
   - Little Mermaid 67.90%
   - 현재 71.3343% Liter 결과에 맞추기 위한 목표값이 아니라 과거 모델과의 차이 추적용이다.
8. legacy 네 모델에서 몰아주기의 큰 비용은 대체로 Helm의 3스택 Mast Burst 미사용이었다. 현재 엔진에서는
   c6/c12의 운용 간 피해를 분리해 판정한다. 이는 해당 Burst 버프만 제거한 반사실 비교가 아니다.
9. 실측 목단의 약 63% tie는 현재 이론식을 보정하는 근거로 쓰지 않는다.
   보스의 Mast3 연동 점프 때문에 조건통제가 깨짐.
10. 다음 작업은 “실측과 이론을 맞추기”가 아니라 **현재 전용 엔진의 남은 활성 스킬 경로를
    교차검증하고 B1/Main B3/Secondary B3 표본을 확장하는 것**이다.
11. Helm은 본 연구에서 `몰아주기에 비교적 우호적인 낮은 Secondary B3 기준점`으로 사용하는 설계변수다.
   - 이는 `Helm이 모든 실사용 B3 중 절대 최약`이라는 주장과 다르다.
   - 핵심은 상위권 B3보다 낮은 딜 기여도로 메인캐리 비중을 높이기 쉬우면서도 실제 보스 파훼에서 사용가치가 있는 B3라는 점이다.
12. 본 연구와 후속 연구를 혼합하지 않는다.
   - 본 연구: 패턴 OFF, `크크메 vs 지속 몰아주기`.
   - 후속 연구: 특정 M3 구간의 예측 가능한 타격손실만 ON, 해당 3사이클의 `C,C,M3 vs C,M2,C`.

---

# 19. 아직 확정해서 말하면 안 되는 내용

1. “60%면 몰아주기” 같은 universal rule.
2. “Moran threshold 77%의 원인은 caster-flat 하나다.”
3. “강한 B1은 단순히 분모를 키워 threshold를 낮춘다.”
   - 정확히는 B1의 C→F 상대손실과 절대 가중치가 `l`에 들어감.
4. “실측과 이론 차이는 NIKKE Sim 오류다.”
   - 현재 실측 자체에 큰 외생변수가 있음.
5. “NIKKE Sim 전체가 검증되었다.”
   - 아직 외부 교차검증 단계 전.
6. “현재 source-based event model = stock sim 실행 결과.”
   - 아님. 수동 재구현.
7. “68.92 / 69.81 / 76.97 / 67.90은 최종 확정 threshold다.”
   - 아님. Projectile bucket 구현 확인 및 수정 계산기 재계산 전에는 legacy/provisional.
8. “몰아주기는 대부분의 상황에서 비유효하다는 가설은 이미 확정됐다.”
   - 아님. 현재 대수구조와 legacy 결과는 강하게 시사하지만, 수정 계산기 재계산 + B1/B3 대표 샘플 확장이 필요하다.
9. “Helm보다 총딜이 높은 B3는 무조건 3스택 Mast Burst 미사용 구간 피해 차이도 더 크다.”
   - 아님. 캐릭터별 Mast 반응도가 다르므로 실제 절대손실을 계산해야 한다.
10. “실전 한두 판에서 크메크가 더 높았으니 크메크의 intrinsic value가 더 높다.”
   - 아님. 기대값 차이가 작을 경우 미스/크리/타격가능시간 등의 외부변수로 쉽게 뒤집힐 수 있다.

---

# 20. 폐기된 가설 / 시행착오 / 정정 로그

이 절은 새 채팅에서 과거 오류를 다시 되살리지 않기 위해 의도적으로 자세히 남긴다.

---

## 20.1 초기 “약 60% 보편 손익분기” 가설

초기 실측을 보고:

```text
Rapi가 팀딜 60%를 넘으면 몰아주기
```

처럼 생각.

폐기 이유:
B1별 `g,l`이 달라서 이론 threshold가 67.9~77.0%로 벌어짐.

현재 표현:
**각 조합의 local threshold만 의미 있음.**

---

## 20.2 “딜러가 얼마나 센지가 핵심”이라는 단순 해석

초기에는 Rapi vs Helm 두 딜러의 상대세기만 중요하다고 생각.

정정:
5인 총딜이 기준.

특히 B1/Crown/Mast도 total 및 weighted loss `l`에 기여.

---

## 20.3 구형 compressed model의 77.75% / 83.00%

초기 더 압축된 interval-average/packet model에서:

- Anis ≈ 77.75%
- Liter ≈ 83.00%

도출.

후에 full event/time-series 모델과 기준이 통일되지 않았음이 확인.

**완전 폐기.**

현재 사용:
- Anis 68.92%
- Liter 69.81%

새 채팅에서 77.8 / 83.0을 최종값으로 복구하면 안 됨.

---

## 20.4 “Moran이 caster-flat이라 77%” 가설

Moran의 caster-ATK가 시전자 기준 flat이라 Rapi에 상대적으로 희석된다는 식으로 과도하게 설명.

문제:
Anis: Star도 같은 caster-ATK bucket.

Anis:
\[
78,707\times35.01\%\approx27,555
\]

Moran:
\[
78,707\times42.57\%\approx33,506
\]

따라서 “buff 종류 자체”가 Moran 고threshold의 독점적 원인이 아님.

**폐기.**

안전한 현재 설명:
Moran model case는 `g`가 가장 작고 `l`이 가장 큼.
세부 component attribution은 controlled ablation 필요.

---

## 20.5 “B1 자체딜이 약 70% 원인”이라는 중간 분해

한 번 Anis→Moran을:
- own damage
- AD +34 제거
- caster flat 크기
- duration

등으로 나눠 약 5.6%p가 B1 자체딜이라고 설명한 적 있음.

이 분석은 다른 변수와 곱상호작용이 있고,
완전히 독립적인 ablation suite로 재현·검산되지 않은 상태.

**최종 인과결론으로 사용하지 않는다.**
참고용 시행착오로만 보존.

향후 전용 계산기에서:
- 한 component씩 on/off
- 순서 의존성을 피하기 위해 Shapley-like 또는 양방향 ablation
등으로 다시 검증할 수 있음.

---

## 20.6 “Helm B3에 FB +50%를 잘못 넣었다” 진단

한 시점에:
기존 event model이 Helm 8236.8% nuke에 Full Burst +50%를 잘못 적용했다고 판단하고,
Moran threshold를 76.97% → 약 71%로 보정해야 한다고 말함.

후에 재검산:
기존 통합 event model 자체는 B3 timestamp와 FB start를 이미 분리했고,
Helm burstCast nuke를 FB 이전에 처리하고 있었음.

즉 존재하지 않는 오류를 다시 빼려 한 것.

**완전 폐기.**

따라서:
- `Moran 71.3% 보정값` 폐기.
- 현재 event model 값은 다시 76.97%.

---

## 20.7 Crown S1 carryover 혼동

한 번 Crown 이전 cycle의 +64.51% caster-ATK가 Helm에게 carryover되는 것처럼 해석할 위험이 있었음.

정확한 rule:
Crown S1은 **그 chain의 burst casters**에게 적용.
non-burst caster는 DEF+reload 그룹.

예 c11 B3가 Rapi이면:
- Helm은 c11 burst caster가 아님.
- c11 Crown Burst AD +36.24%는 15초라 c12 Helm B3까지 남을 수 있음.
- 그러나 c11 Crown S1 caster-ATK +64.51%가 Helm에 생기는 것은 아님.

현재 재검산은 이 targeting을 구분.

---

## 20.8 실측 목단 63%를 이론 77%에 억지로 맞추려 한 시도

스펙/Helm OL/skill level 등을 통해 77→63을 설명하려고 추적.

사용자 실제 자료:
Moran:
- 우월코드 1줄
- 명중(거의 의미 없음)
- Crit Damage +16
- Charge Damage +5(AR이라 사실상 의미 낮음)

Helm:
- ATK +11
- Charge Damage +23.6
- Crit Damage +16
- skill 7/6/7

이 차이는 이론 threshold를 어느 정도 움직일 수 있지만
현재 실측 보스 자체가 Mast3마다 점프하여 조건통제가 깨졌다는 사실이 더 중요.

따라서 **실측값과 표준 이론값을 맞추는 작업 자체를 중단.**

실제 스펙 자료는 역사적 참고자료로만 보존.  
현재 전용 계산기에는 Actual Account Mode / 개별 스펙 커스터마이징을 구현하지 않는다.

---

## 20.9 Projectile bucket 정정

기존 §8.7 문서식은 Projectile Attachment / Explosion을 별도 multiplicative factor처럼 기록했다.

고정 commit `43308bd02276a476660e44af730785c2ae91eea3`의 damage-engine semantics를 다시 확인한 결과:

```text
Attack Damage
Projectile Explosion
Projectile Attachment
```

은 해당 flavor에서 `DamageUp` bucket에 additive로 합성되며, 별도 Projectile factor를 최종 damage product에 곱하지 않는다.

따라서 §8.3 / §8.7을 수정.
기존 raw 결과는 삭제하지 않고 regression reference로 보존하되, 구현 확인 및 수정 계산기 재계산 전까지 provisional 처리.

---

## 20.10 일반 손익분기 예외 케이스 정정

기존 Case D의 “둘 다 증가 또는 둘 다 감소” 표현은 Case B/C와 중복되고,
실제 누락된 경우는 다음 반대 tradeoff였다.

\[
\Delta R<0,\quad \Delta O>0
\]

일반식:

\[
\Delta T(\lambda)=\lambda\Delta R+\Delta O
\]

\[
\lambda^*=-\frac{\Delta O}{\Delta R}
\]

따라서 양의 threshold는 \(\Delta R\)과 \(\Delta O\)의 부호가 반대일 때 생기며,
\(\Delta R>0\)이면 threshold 위에서 몰아주기 우위,
\(\Delta R<0\)이면 threshold 아래에서 몰아주기 우위.

§6을 이 일반형으로 수정. 현재 네 baseline case의 기존 대수값에는 영향 없음.

---

# 21. 현재 시점의 권장 작업 순서

### Step 1 — 연구축과 시간범위 고정 — 완료

```text
본 연구 = 패턴 OFF, 크크메 vs 지속 몰아주기
후속 연구 = M3 구간의 예측 가능한 타격손실만 ON, 해당 묶음의 2스택 선사용
Burst 선택 = c1~c12
피해 집계 = 180초 terminal-tail
```

### Step 2 — 전용 stateful baseline 구현 — 완료

Crown / Mast / Liter / Rapi: Red Hood / Helm (애장품), 공통 피해식, 무기 상태,
버프 장부와 운용 비교 분석기가 구현되어 있다. 현재 전체 회귀 테스트는 95개다.

### Step 3 — 활성 기반식 교차검증 — 진행 중

완료:

```text
Projectile Attachment/Explosion의 DamageUp additive 배치
Static ATK / Boss DEF / 평타 계수 / 기대 치명타
MG / SMG / SR 기본 cadence, ammo, reload, charge
Helm B3의 Full Burst +50% 제외와 next-10 multiplier 구조
```

순수 무기 조건은 고정 NIKKE Sim commit과 수치가 일치했다. 다음에는 연구 결과에 직접 들어오는
Crown/Mast/Liter/Rapi/Helm의 buff window와 skill damage를 rule 단위로 교차검증한다.

### Step 4 — 현재 baseline 고정과 legacy 비교 — 진행 중

현재 Liter baseline `s*=71.3343%`, 크크메 `+1.2130%`를 새 기준점으로 보존한다.
기존 68.92 / 69.81 / 76.97 / 67.90은 재현 목표가 아니라 legacy regression reference다.
차이는 unit / damage source / macro-cycle 단위로 추적한다.

### Step 5 — 본 연구 일반화

1. Liter baseline에서 남은 활성 스킬 경로를 검증한다.
2. B1을 여러 buff environment로 교체한다.
3. Main B3와 Secondary B3에 주류 대표 및 저딜 극단값을 추가한다.
4. Scarlet: Black Shadow를 통해 Distributed Damage 활성 경로를 검증한다.
5. 각 case에서 total delta, g, l, s, s*, g+l, local upside, c6/c12 3스택 Mast Burst 미사용 구간 피해 차이를 기록한다.

### Step 6 — DEF 및 불확실성 민감도

Boss DEF sweep, 불확실 rule ±5~10%, 필요 시 표준 성장점 일괄 scaling을 적용한다.

목표:
- `평상시 기본 회전`을 정할 수 있을 정도로 방향이 robust한가?
- 지속 몰아주기가 유효해지는 조건은 일반적인가, 원맨캐리 편중 같은 예외에 가까운가?
- 몰아주기가 이기는 조건에서도 실제 upside가 충분히 큰가?

### Step 7 — 본 연구 결론 및 NIKKE Sim 개선 제보

대표 표본에서 결론 방향을 확인한 뒤, 연구 결과와 별도로 Mast의 live Drunken 및 Burst 정책
개선안을 NIKKE Sim 제작자에게 전달한다. `NIKKE Sim 전체가 틀렸다`가 아니라 기본 피해 경로는
일치하지만 현재 Mast 평균화와 stock B2 선택이 이 운용을 표현하지 못한다는 범위로 제안한다.

### Step 8 — 후속 연구는 §25에서 별도 진행

본 연구가 안정된 뒤 패턴 대응형 2스택 선사용의 손익분기 `L*`를 계산한다.

---

# 22. 빠른 복원용 요약

새 채팅에서 시간이 없으면 이 블록만 먼저 읽는다.

```text
본 연구 목적:
보스 패턴 제거 후 Crown/Mast B2 배치만 바꾼 intrinsic rotation value 비교.

후속 연구 목적:
본 연구의 기본회전을 전제로, Mast3 예정 구간의 예측 가능한 타격손실 L만 추가했을 때
해당 3사이클만 C,C,M3 → C,M2,C로 바꿀 임계점 계산.
지속 몰아주기와 패턴 대응형 2스택 선사용을 혼동하지 않는다.

크크메:
C,C,M / C,C,M / C,C,M / C,C,M
Mast c3,c6,c9,c12 = 모두 3stack.

몰아주기:
C,C,M / C,M,C / C,C,M / C,M,C
Mast c3,c9=3stack, c5,c11=2stack Rapi.

B3:
Rapi/Helm 교대, 12회.

시간범위:
c1~c12까지만 Burst 선택.
c13은 발생시키지 않음.
c12가 생성한 잔여 버프와 durationShots를 포함해 180초까지 피해 집계.
173초는 Full Burst 종료 경계 민감도 보조값.

핵심:
Rapi 증가만 보면 안 됨.
5인 total 기준.

T_C = R_C + O_C
T_F = R_F + O_F

몰아주기 승:
R_F-R_C > O_C-O_F

g = R_F/R_C - 1
l = 1 - O_F/O_C

크크메 기준 local break-even Rapi share:
s* = l/(g+l)

local total delta:
ΔT/T_C = s·g - (1-s)·l = (g+l)(s-s*)
→ threshold뿐 아니라 실제 upside magnitude도 확인

λ:
λ*=(O_C-O_F)/(R_F-R_C)
단 λ는 Static ATK scaling 아님.
최종 Rapi damage packet의 추상적 가중치.

현재 전용 엔진 Liter baseline, Base-5 / Boss DEF 140 / 180초:
크크메 total 2,096,368,373.67
몰아주기 total 2,070,939,773.66
몰아주기 delta -1.2130%
Rapi g +1.4604%
나머지 l 3.6342%
현재 Rapi share 47.5253%
s* 71.3343%
판정 크크메 우세

기존 standard 10/10/10 event-model legacy/provisional:
Anis 68.92%
Liter 69.81%
Moran 76.97%
Little Mermaid 67.90%

Projectile Attachment/Explosion:
별도 multiplier 금지. 해당 flavor의 DamageUp에 additive.
기존 코드 구현 확인 및 수정 계산기 재계산 전 위 threshold는 최종값 아님.

이전 77.75/83.00 = 폐기.
Moran 71% Helm-FB 보정 = 폐기.

실측 보정 중단:
실측 보스가 Mast3마다 2~3초 점프하여 운용과 타격로스가 상관됨.

스펙 정책:
표준화된 동등성장 기준만 사용.
개별 계정 스펙 커스터마이징 / Actual Account Mode는 현재 범위 밖.

B1 sweep 정책:
B1은 rotation feasibility 검증 대상이 아니라 buff environment 비교군.
필요하면 C/F 양쪽의 burst cadence를 동일하게 강제하여 가설의 반복성을 본다.

다음 작업:
남은 Crown/Mast/Liter/Rapi/Helm 활성 경로 교차검증
→ 현재 Liter baseline 고정 + legacy 차이 분해
→ B1/B3 대표 샘플 확장
→ Boss DEF와 불확실 rule 민감도 분석
→ 본 연구 결론 확정 후 §25 패턴 대응형 후속 연구.
```

---

# 23. 원본/소스 재탐색 키워드

GitHub repo:

```text
Infernal-Crack-LED/nikke-sim
```

검색 키워드:

```text
effectiveAtk
dealDamage
casterAtkPct
attackDamagePct
chargeDamageMultPct
crown
mast-romantic-maid
rapi-red-hood
helm
anis-star
liter
moran
little-mermaid
```

특히 확인할 파일:

```text
src/engine/sim.ts
scripts/blind-rebuild/code-bundle/sim-core-a.ts
src/skills/overrides/crown.json
src/skills/overrides/helm.json
data/skill-levels.json
```

그리고 각 캐릭터 override.

---

# 23.1 v5 정리에서 추가된 분석축

2026-08-29 검토에서 다음을 추가/명확화했다.

1. **B1 sweep의 목적 명확화**
   - 실제 CDR/gauge로 해당 회전이 자연스럽게 성립하는지 보는 연구가 아님.
   - B1을 서로 다른 buff environment 비교군으로 두고 필요하면 동일 cadence를 강제한다.
2. **손익분기 이후 이득 크기 공식 추가**
   - `ΔT/T_C = s·g - (1-s)·l = (g+l)(s-s*)`
   - `s*`뿐 아니라 local slope와 실제 upside magnitude를 같이 본다.
3. **계산기 threshold 출력 안전장치**
   - `ΔR/ΔO` 부호 case를 먼저 판정하고 정상 tradeoff case에서만 일반형 `s*`를 출력한다.
4. **패턴손실 근사식 적용조건 추가**
   - `L*≈1-A/B`가 [0,1] 내부의 정상 threshold가 되는 조건과 무교차 case를 명시했다.
5. **NIKKE Sim Mast 기본정책 후보와 연구 baseline 분리**
   - 첫 Mast 우선 + 이후 3stack 우선 정책은 향후 simulator integration 후보로 기록하되, 기존 legacy/provisional 수치를 소급 변경하지 않는다.

---

# 23.2 v6 정리에서 추가·변경된 내용

2026-08-29 현재 구현과 재검토를 반영해 다음을 수정했다.

1. **시간범위 재정의**
   - c1~c12까지만 Burst 선택하고 c13은 발생시키지 않는다.
   - c12가 만든 잔여 버프·durationShots·무기 상태의 후속 피해는 180초까지 집계한다.
   - 173초는 본 결과가 아니라 endpoint sensitivity로 보존한다.
2. **현재 구현 상태 기록**
   - Crown/Mast/Liter/Rapi/Helm baseline, stateful 무기·버프 엔진과 운용 비교 분석기 구현 완료.
   - 전체 95개 회귀 테스트 통과 상태를 기록했다.
3. **NIKKE Sim 순수 무기 parity 기록**
   - 보스 이동을 고정하고 스킬·Burst를 제거한 공통 조건에서 팀 총피해와 캐릭터별
     피해·발사 횟수가 고정 commit과 일치했다.
4. **현재 Liter baseline 추가**
   - 180초 기준 크크메 +1.2130%, 현재 Rapi share 47.5253%, local s* 71.3343%.
   - 단일 표본이며 일반화 결론이 아님을 명시했다.
5. **개발 순서 현행화**
   - 계산기 구축 단계를 완료로 전환했다.
   - 다음 단계는 활성 스킬 경로 검증, B1/B3 표본 확장과 DEF 민감도 분석이다.
6. **NIKKE Sim 개선 제보 시점 분리**
   - 본 연구 표본이 충분히 쌓인 뒤 Mast 메커니즘·정책 개선을 별도 제보한다.

---

# 24. 최종 메모

현재 연구의 가장 중요한 방법론적 변화는:

```text
“실측을 이론에 맞춘다”
→ 폐기

“완전히 통제된 이론 모델을 본 연구로 삼고,
그 모델이 실제로 사용하는 계산식만 독립 자료로 교차검증한다”
→ 현재 채택
```

이 방식의 장점:

- 외생변수 제거
- 동일 조건 반복 가능
- 계산기 regression 가능
- 오차의 출처를 rule 단위로 분해 가능
- 실전 특정 보스 패턴에 과적합하지 않음

실전 적용 목표도 분명히 한다.

본 연구가 여러 B1/B3 환경과 민감도에서 robust하게 끝나면, 사용자가 매 보스마다 `크크메와 크메크 중 무엇이 더 센가`를 단일 실측으로 다시 검증할 필요를 줄이는 것이 목표다.  
기본 회전의 기대값 차이는 계산으로 정하고, 실제 한두 run에서 반대 결과가 나오는 것은 우선 미스/크리/타격가능시간 등 외부변수로 해석한다.  
반대로 **예측 가능한 M3 구간 타격손실**은 외부잡음으로 버리지 않고 §25의 임계값을 이용해 의도적으로 대응한다.

그리고 가장 놓치기 쉬운 결론을 마지막으로 다시 반복한다.

> **몰아주기의 가치는 메인캐리 한 명의 증가율로 판단할 수 없다.**
>
> **5인 총피해에서 메인캐리가 얻는 피해와 나머지 4인이 잃는 피해의 교환비를 봐야 한다.**
>
> 그 교환비를 압축한 값이 `g`와 `l`이고,
> 현재 조건에서의 크크메 기준 local Rapi-share break-even은:
>
> \[
> \boxed{s_C^*=\frac{l}{g+l}}
> \]
>
> 이다.

---

# 25. 후속 연구 — 패턴 대응형 2스택 선사용의 손익분기

이 절은 **본 연구의 `지속 몰아주기`와 완전히 별개의 후속 연구**다.

## 25.1 연구 질문

기본 3사이클 묶음이:

```text
Crown → Crown → Mast3
C,C,M3
```

라고 하자.

다음 Mast3 Full Burst 구간에 보스의 저지 / 무적 / 이동 / 강제기믹 등으로 **예측 가능한 유효타격 손실**이 충분히 크게 발생할 것으로 예상되면,
그 한 묶음만:

```text
Crown → Mast2 → Crown
C,M2,C
```

으로 바꾸는 것이 유리해지는가?

이 경우 다음 3사이클부터는 다시 기본 회전으로 복귀한다.

따라서 이것은:

```text
메인캐리에게 Mast를 반복적으로 맞추는 지속 몰아주기
```

가 아니라:

```text
곧 올 Mast3의 실현가치가 패턴 때문에 크게 훼손될 때
해당 묶음에서만 Mast2를 앞당겨 사용하는 패턴 대응
```

이다.

---

## 25.2 왜 별도 연구로 분리하는가

본 연구는 외생변수를 제거해 `운용 자체의 기대값`을 비교한다.

반면 이 후속 연구는 외생변수 중에서도 **사전에 관찰·예상 가능한 M3 구간 타격손실 하나만 의도적으로 추가**한다.

다음은 threshold 산정변수로 사용하지 않는다.

```text
총알 몇 발 미스
크리티컬 운
조준 편차
run별 진입 HP 차이
우연한 타겟 전환
개별 계정의 비대칭 육성
```

이런 값은 실전 노이즈이거나 별도 연구변수다.

반대로:

```text
다음 Mast3 10초 구간 중 보스를 약 6초 못 친다
족자/저지/무적 때문에 후반 대부분이 비어 있다
고정 패턴상 이 Full Burst의 절반 이상을 사실상 버린다
```

같은 정보는 플레이어가 리트라이 과정에서 비교적 안정적으로 파악할 수 있고,
`몇 % 이상의 손실이면 2스택 선사용이 합리적인가`라는 판단 기준으로 변환할 수 있다.

---

## 25.3 테스트 조합 선정

이 연구에서는 Helm처럼 Main B3와 피해격차가 큰 Secondary B3보다 **실질적으로 동급인 두 B3**가 더 중요하다.

권장 조건:

```text
동일한 표준 성장규칙
비슷한 이론 DPS 구간
둘 다 정상적으로 B3를 교대사용할 가치가 있는 캐릭터
특수한 Mast 상호작용이 없는 일반 case 우선
```

이유:
한쪽 B3가 원래 훨씬 강하면 `M2를 강한 쪽에 주는 효과`와 `M3 구간 패턴손실 효과`가 섞인다.
두 B3의 기본 기여도가 비슷해야 **패턴손실 자체가 C,C,M3 → C,M2,C 변경을 정당화하는 임계점**을 더 깨끗하게 볼 수 있다.

여러 B1 환경에서 반복해 threshold가 얼마나 흔들리는지도 확인한다.

---

## 25.4 패턴손실 변수의 정의

Mast3가 예정된 Full Burst 구간의 유효피해 손실률을:

\[
L\in[0,1]
\]

로 둔다.

```text
L = 0.0  → 손실 없음
L = 0.5  → 해당 10초 구간의 유효피해 약 50% 손실
L = 0.8  → 약 80% 손실
```

1차 연구에서는 `시간손실률 ≈ 피해손실률`로 근사해도 충분하다.

Full Burst 10초 기준 단순 환산:

\[
t_{loss}\approx10L\ \text{seconds}
\]

예:

```text
L*=0.50 → 약 5초 손실이 손익분기
L*=0.70 → 약 7초 손실이 손익분기
```

정확히 어느 5초가 잘렸는지, 즉발 nuke가 살아 있는지 등에 따라 실제 피해손실은 달라질 수 있다.
하지만 이 연구의 목적은 프레임 단위 실전예측이 아니라 **감 대신 사용할 수 있는 근사 판단선**을 제공하는 것이다.

---

## 25.5 계산 방법 — stateful 재실행이 우선

단순 설명식만으로 c2/c3을 완전히 독립 분리하지 않는다.
Crown/Mast 지속시간, ammo/reload, buff carryover 등이 다음 사이클로 전파되기 때문이다.

권장 구현:

1. 동일한 초기 state에서 `C,C,M3`를 실행.
2. 동일한 초기 state에서 `C,M2,C`를 실행.
3. Mast3가 예정된 affected Full Burst 10초에 동일한 `damage availability mask`를 두 run 모두에 적용.
4. `L=0 → 1`을 sweep하거나 binary search하여 5인 총피해 차이가 0이 되는 `L*`를 찾는다.

정의:

\[
\Delta_{pattern}(L)
=
T_{CM2C}(L)-T_{CCM3}(L)
\]

손익분기:

\[
\boxed{\Delta_{pattern}(L^*)=0}
\]

- `L < L*`이면 기본 `C,C,M3` 우위.
- `L > L*`이면 해당 묶음의 `C,M2,C` 우위.
- `L ≈ L*`이면 실전 잡음보다 차이가 작을 가능성이 높으므로 사실상 어느 쪽이든 큰 의미가 없다고 본다.

---

## 25.6 직관용 근사식

상태전파를 무시한 설명용 1차 근사에서는:

```text
A = 앞 사이클에서 Crown → Mast2로 바꿔 얻는 5인 총 추가가치
B = 다음 사이클에서 Crown 대신 정상 Mast3를 유지했을 때의 5인 총 추가가치
```

라고 두면:

\[
\Delta_L\approx A-(1-L)B
\]

따라서:

\[
\boxed{L^*\approx1-\frac{A}{B}}
\]

이 식은 threshold의 직관을 설명하는 용도다.
최종 숫자는 §25.5의 stateful 재실행 결과를 우선한다.

### 근사식의 적용조건

정상적인 `0<L*<1` threshold 해석은 대체로:

```text
B > 0
0 < A < B
```

일 때 성립한다.

- `A >= B`: 패턴손실이 없어도 C,M2,C가 이미 동급 이상일 수 있으므로 `패턴손실 임계점`이라는 해석이 약해진다.
- `A <= 0`: 앞당긴 Mast2 자체가 추가가치를 만들지 못하므로 매우 큰 L이 필요하거나 threshold가 [0,1] 밖으로 나갈 수 있다.
- `B <= 0`: `1-A/B`의 직관적 의미가 깨지므로 근사식 숫자를 쓰지 않고 stateful 결과만 판정한다.
- `L* < 0` 또는 `L* > 1`: 물리적 손실범위 [0,1] 안에 교차점이 없다는 뜻으로 해석하고 dominance/무교차로 표시한다.

과거 계산에서 사용했던 단순 `M2/Crown`, `M3/Crown` 비율식은 이 개념을 먼저 확인하기 위한 근사였으며,
당시 숫자를 새 계산기의 최종 threshold로 재사용하지 않는다.

---

## 25.7 권장 출력

조합별로 최소 다음을 출력한다.

```text
B1
B3-A / B3-B
패턴 없음에서 C,C,M3 vs C,M2,C total delta %
손익분기 유효피해 손실률 L*
10초 기준 단순 환산 t_loss*
민감도 반영 경계구간
```

예시 형식:

```text
손익분기 L* ≈ 0.50
10초 기준 ≈ 5초
민감도 고려 경계 ≈ 4~6초

< 4초 예상 손실: C,C,M3 쪽
4~6초: 사실상 경계, 어느 쪽이든 큰 차이 없을 가능성
> 6초: C,M2,C 쪽을 우선 고려
```

위 숫자는 형식 예시일 뿐 실제 결과가 아니다.
경계폭은 계산기 민감도 분석 후 정한다.

---

## 25.8 이 후속 연구가 실전에서 주는 것

목표는 `이 보스에서 정확히 몇 프레임에 버스트를 눌러라`가 아니다.

목표:

> **두 B3의 육성/기여도가 비슷하고, 다음 Mast3 구간에서 계산된 임계점보다 명확하게 큰 딜로스가 예상되면 그 한 묶음은 2스택 Mast를 앞당겨 쓰는 것이 이득일 가능성이 높다.**

사용자는 이후:

```text
족자/저지 때문에 다음 Mast3에서 약 8초를 못 친다
threshold는 약 5초다
→ 별도 A/B 리트라이 없이 C,M2,C 선택
```

처럼 판단할 수 있다.

반대로 예상 손실이 threshold 근처라면:

```text
4초인지 6초인지 애매하다
→ 두 운용 차이보다 실전 외부변수가 더 클 수 있으므로 굳이 반복검증하지 않는다
```

라고 처리할 수 있다.

이 판단기준이 서면 사용자는 `크메크가 센가 / 크크메가 센가`를 매 보스에서 반복 시험하기보다,
버스트 지연 / 패턴 회피 / 저지 / 엄폐처럼 실제 클리어에 더 큰 영향을 주는 택틱에 리트라이 비용을 집중할 수 있다.

---

## 25.9 본 연구와 후속 연구가 함께 제공할 최종 운용 프레임

본 연구가 가설대로 확정된다는 전제에서 최종 프레임은 다음과 같다.

```text
1. 패턴상 특별한 이유 없음
   → 계산으로 정한 기본 회전 사용.
   → 실전 한두 run의 작은 점수 역전은 우선 외부변수로 해석.

2. 지속 몰아주기
   → Main B3의 g가 나머지 4인의 l을 이길 만큼 원맨캐리 편중이 큰 특수조건인지 확인.
   → 단순히 "한 캐릭이 더 세다"만으로 기본값으로 쓰지 않음.

3. 특정 Mast3 구간에 큰 예상 딜로스 존재
   → 지속 몰아주기와 별개.
   → §25의 L*를 기준으로 그 3사이클만 C,M2,C 사용 여부 판단.
```

즉 목표는:

> **평상시 기본값을 계산으로 정하고, 예외는 `왜 예외인지`를 통제 가능한 변수로 설명하는 것.**

이다.

---

## 25.10 현재 상태와 주의사항

- 이 후속 연구의 **개념과 비교구조는 정리 완료**.
- 실제 `L*` 숫자는 새 stateful calculator에서 다시 계산해야 함.
- 기존 실측의 2~3초 점프값은 calibration target이 아님.
- 기존 스크린샷의 단순 비율계수와 과거 threshold 숫자는 final value로 사용하지 않음.
- 패턴손실을 damage availability로 추상화하는 1차 모델이면 실전 가이드 목적에는 충분할 가능성이 높음.
- 여러 동급 B3 / B1 조합에서 `L*`가 비슷한 범위로 모이면 일반 가이드라인을 제시할 수 있음.
- 크게 흩어지면 universal threshold를 만들지 않고 조합군별 범위로 제시한다.
