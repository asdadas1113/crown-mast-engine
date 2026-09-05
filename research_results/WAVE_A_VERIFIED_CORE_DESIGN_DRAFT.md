# Crown–Mast Wave A verified-core 탐색 설계 초안 — 2026-09-05

상태: **설계 초안 / 실행 금지**

이 문서는 전면 재검증 이후 첫 탐색 batch의 후보 공간을 정리한다. 아직 study ID를 동결하지 않았으며, 사용자 명시 승인 전에는 batch를 실행하지 않는다.

## 1. 목적

Wave A는 보편 최적 운용 규칙을 증명하지 않는다.

목적은 검증된 범위 안에서 다음을 빠르게 찾는 것이다.

- Crown/Mast 상대 손익에 큰 영향을 주는 변수
- Main / Secondary / 성장 / core / 우월 / DEF 상호작용
- 조건에 따라 정책 방향이 뒤집히는 roster
- 반복되는 이상치 후보
- full-grid 또는 별도 기전 연구로 확대할 가치가 있는 조건

미해결 캐릭터를 섞어 coverage를 늘리는 것보다 **verified-core 내부의 해석 가능성**을 우선한다.

## 2. 전투 통제조건

- timeline: RAID14 180초
- baseline rotation: M1 opener를 포함한 현행 연구 기준
- Crown / Mast: 고정 B2 build
- boss pattern loss: OFF
- 기본공격: 큰 단일 보스에 모든 일반탄이 명중하는 ideal-hit 통제조건
- core는 실제 명중확률이 아니라 0% / 100% 민감도 극단값
- Main advantage는 Main의 실제 속성관계에 따라 보스 속성을 선택
- DEF는 발생확률이 아니라 low / representative / high sensitivity anchor

따라서 Wave A 결과는 실제 특정 Solo Raid 보스의 절대 총딜을 재현하는 결과가 아니다.

## 3. B1 후보 — 4명

```text
liter
anis-star
little-mermaid
rapi-red-hood
```

보류:

```text
moran-favorite-item
```

Moran FI는 current display reload와 기존 pinned timing이 충돌하므로 독립 근거 확보 전에는 verified-core에서 제외한다.

Rapi: Red Hood를 B1으로 사용하는 경우 동일 Rapi를 Main B3로 동시에 배치하지 않는다.

## 4. Main B3 후보 — 6명

```text
rapi-red-hood
cinderella
cinderella-crystal-wave
neon-vision-eye
phantom
bready
```

### Bready 재편입 이유

과거 superseded study에서는 대표성 우선순위 때문에 Bready를 공식 Main 표본에서 제외했다.

새 Wave A는 이상치와 상호작용 탐색이 목적이므로 그 이유가 더 이상 제외 근거가 되지 않는다. Bready는 Recommended Taste에서 distributed damage를 중심으로 Mast와 직접 상호작용하며, 현재 데이터는 Prydwen / NIKKE.gg 계열과 재장전 timing audit을 통해 다시 확인됐다.

따라서 특수 상호작용 자체가 제외 이유가 아니라 **탐색 가치가 높은 구조**로 취급한다.

### Main 보류

```text
scarlet-black-shadow
liberalio
raven
quency-escape-queen
```

- SBS / Liberalio / Raven: 특수 reload/recovery timing unresolved.
- Quency: 스킬 수치와 1초 reload는 NIKKE.gg / Prydwen / CannedJar / NIKKE-Sim 계열에서 교차 일치한다. 그러나 Hit Rate와 산포가 실제 normal/core DPS를 크게 움직이는 캐릭터인데 현행 엔진은 weapon spread/body miss를 모델링하지 않는다. 따라서 ideal-hit diagnostic은 가능하지만 첫 canonical Wave A aggregate에서는 제외한다.

Milk: Blooming Bunny는 AUTO-only 구현이므로 이번 후보군 밖이다.

## 5. Secondary B3 anchor — 3명

```text
epinel
helm
snow-white-heavy-arms
```

역할은 기존과 동일하게 유지한다.

- Epinel: 낮은 opportunity-cost 쪽 기준점
- Helm: 중앙 실전형 기준점
- Snow White: Heavy Arms: 높은 opportunity-cost stress anchor

이 라벨은 확률분포가 아니며 최종 해석에서는 실제 계산된 Secondary 총딜/지분을 우선한다.

## 6. 유효 roster 수

Raw roster:

```text
4 B1 × 6 Main × 3 Secondary = 72
```

중복 제외:

```text
Rapi B1 + Rapi Main × 3 Secondary = 3
```

유효 roster:

```text
72 - 3 = 69
```

## 7. 성장 screening — 16점 pairwise orthogonal array

기존 realistic-v3는 B1 / Main / Secondary 각각 4수준을 완전교차해 64점을 사용한다.

```text
g1-base5-none
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

Wave A의 1차 screening에서는 64점 전부를 사용하지 않고 **4수준 3축의 16점 pairwise orthogonal array**를 사용한다.

프로필 인덱스를 `0..3`으로 두고 다음 규칙으로 만든다.

```text
B1 = i
Main = j
Secondary = (i + j) mod 4

for i in 0..3
for j in 0..3
```

성질:

- B1 × Main의 4×4 조합이 정확히 한 번씩 등장
- B1 × Secondary의 4×4 조합이 정확히 한 번씩 등장
- Main × Secondary의 4×4 조합이 정확히 한 번씩 등장
- 64점 완전교차의 1/4 비용으로 모든 2축 성장 조합을 균형 있게 screening

제한:

- 3축 성장의 순수한 three-way interaction은 완전히 식별할 수 없다.
- 따라서 sign reversal / boundary / 이상치가 나온 roster는 후속 단계에서 64점 full growth grid로 확대한다.

Favorite Item 캐릭터는 현행 growth builder 규칙대로 collection을 SR15로 강제하고 나머지 gear/OL 성장만 적용한다.

## 8. 환경축

### DEF — 3수준

```text
140
12,000
31,784
```

해석:

- 140: low / training-range 계열 통제 anchor
- 12,000: 현재 generic raid representative baseline
- 31,784: current DILDORO Solo Raid 설정에서 확인되는 high/Solo-style sensitivity anchor

세 값 모두 '실전 발생확률'을 의미하지 않는다. 특히 31,784를 모든 Solo Raid 보스의 universal exact DEF라고 주장하지 않는다.

### Core — 2수준

```text
0%
100%
```

실제 보스의 코어 크기/산포 확률이 아니라 no-core와 ideal full-core의 양 끝 민감도다.

### Main advantage — 2수준

```text
off
on
```

`on`에서는 Main에게 실제 우월을 주는 보스 속성을 선택하며 같은 속성 관계를 가진 다른 아군도 실제 규칙대로 우월을 받는다.

### 환경 완전교차

```text
3 DEF × 2 core × 2 advantage = 12 conditions
```

환경축은 screening에서 줄이지 않는다. DEF/core/우월 간 상호작용은 이번 연구 목적의 핵심이기 때문이다.

## 9. Wave A1 예상 scenario 수

한 roster당:

```text
16 growth OA × 12 environment = 192 scenarios
```

전체:

```text
69 valid rosters × 192 = 13,248 scenarios
```

이는 기존 superseded 29,952-point 설계보다 작지만, 환경축은 오히려 DEF를 추가해 더 넓고 성장축은 pairwise-balanced screening으로 압축한 구조다.

## 10. Wave A2 확대 조건

Wave A1 결과 중 아래 조건을 만족하는 roster/환경을 64-point full growth grid로 확대한다.

1. 16 growth point 사이에서 Conventional/Funnel 방향이 실제로 뒤집힘
2. DEF 수준 변화로 정책 방향이 뒤집힘
3. core 또는 advantage 변화로 정책 방향이 뒤집힘
4. 상대 변화량 절대값이 0.5% 이내인 close-call 점이 존재
5. 같은 Main/Secondary 계열 대비 반복적으로 튀는 이상치
6. pairwise screening으로 설명되지 않는 비선형 패턴이 의심됨

0.5% close-call 기준은 승패 임계값 그 자체가 아니라, 현재 Mast hit-loss sensitivity 진단에서 관측된 약 0.2 percentage point 수준의 모델 불확실성보다 넓게 잡는 보수적 재검증 트리거다.

Wave A2의 추가 scenario 수는 Wave A1 결과를 본 뒤 결정한다. 사전에 무조건 64점 전체를 실행하지 않는다.

## 11. 별도 diagnostic lane

verified aggregate와 섞지 않고 다음을 별도로 유지한다.

```text
Quency: Escape Queen -> hit/spread sensitivity 필요
SBS                  -> special reload timing 필요
Liberalio            -> 2.0s reload body + 0.5s post-delay decomposition 필요
Raven                 -> RL reload/recovery decomposition 필요
Moran FI              -> current reload source conflict 해결 필요
Milk: Blooming Bunny  -> manual/special reload route 필요
```

이 캐릭터는 diagnostic 결과가 흥미롭더라도 재검증 통과 전에는 Wave A aggregate의 변수 효과나 승패 비율에 합치지 않는다.

## 12. preflight gate 초안

새 generator를 구현할 때 최소 다음을 fail-closed로 검사한다.

- 후보가 verified-core allowlist에 속하는가
- B1/Main 동일 actor 중복이 없는가
- unresolved actor가 aggregate case에 들어오지 않았는가
- scenario의 modeled reload speed가 100%를 넘지 않는가
- DEF/core/advantage label과 실제 CombatSettings가 일치하는가
- 16-point growth OA가 각 역할 쌍의 4×4 조합을 정확히 한 번씩 포함하는가
- case ID가 유일한가
- 모든 case가 RAID14 timeline과 동일 engine/hook/catalog revision을 사용하는가

## 13. 아직 동결하지 않는 것

이 문서는 실행 승인용 최종 design이 아니다.

아직 동결하지 않는다.

- 최종 study ID
- Wave A1 exact run ID
- raw 저장 디렉터리
- 0.5% close-call 트리거의 최종 명칭/표시 방식
- Wave A2 확대량
- Quency 및 unresolved actor 재진입 순서

다음 구현 단계는 이 초안의 **69-roster allowlist + 16-point OA + 12-condition environment + fail-closed preflight**를 코드로 표현하고, scenario 생성 수와 균형성만 테스트하는 것이다.

공식/대규모 계산은 그 이후 사용자 명시 승인 전까지 실행하지 않는다.
