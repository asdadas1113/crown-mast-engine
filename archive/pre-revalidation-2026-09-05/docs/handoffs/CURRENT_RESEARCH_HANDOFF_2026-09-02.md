# Crown–Mast Engine 연구 Handoff — 2026-09-02

이 문서는 새 채팅에서 현재 연구를 이어가기 위한 최신 인계문서다.

## 0. 새 채팅에서 먼저 읽을 것

```text
docs/CURRENT_RESEARCH_HANDOFF_2026-09-02.md
docs/SOURCE_VALIDATION_POLICY.md
research_results/README.md
research_results/OFFICIAL_STUDY_DESIGN_V1.md
research_results/SECONDARY_B3_ANCHORS_DRAFT.md
docs/DISTRIBUTED_MAIN_PRETEST_2026-09-02.md
```

필요할 때만:

```text
docs/CHARACTER_AUDIT_2026-09-02.md
docs/DISTRIBUTED_DAMAGE_BUCKET_AUDIT_2026-09-02.md
docs/RAID14_CHECKPOINT_64POINT_REALISTIC_V3_2026-09-01.md
docs/RAID14_PATTERN_LOSS_FOLLOWUP_2026-09-01.md
```

`RAID14_CHECKPOINT_*` 값과 `DISTRIBUTED_MAIN_PRETEST_*` 값은 개발/진단 checkpoint이며 공식 publication result가 아니다.

---

# 1. 저장소 / 브랜치

```text
repo: asdadas1113/crown-mast-engine
working branch: research/14-burst-baseline
main: 수정/병합 금지 unless explicitly requested
```

새 채팅에서는 문서에 적힌 SHA를 최신으로 간주하지 말고 **항상 branch HEAD를 GitHub에서 다시 확인**한다.

---

# 2. 연구 목적

목표는 NIKKE 전체를 완벽히 재현하는 범용 시뮬레이터가 아니다.

핵심 질문:

> 외생변수를 최대한 제거한 동일 조건에서 Crown/Mast B2 운용만 바꿨을 때, 관습적인 `한 딜러가 강하면 Mast를 몰아준다`는 판단이 실제로 얼마나 넓은 범위에서 유효한가?

확인할 가설:

1. 몰아주기 유효구간이 제한적인가.
2. 유효하더라도 이득 폭이 작은가.
3. 몰아주기 우세 파티 구조가 일반적인 실전 구성에서 흔하지 않은가.

정확한 하나의 보편 Main-share 임계값을 찾는 것이 주목적은 아니다.

기본 연구에서 제거하는 외생변수:
- boss jump / movement
- invulnerability
- forced cover
- part exposure
- 기타 패턴 손실

이들은 필요하면 후속 pattern-loss 연구로 분리한다.

---

# 3. 현행 RAID14 baseline

```text
fight: 180 sec
burst cycles: 14
B1 interval: 12.70 sec
B1 -> B2: 0.06 sec
B2 -> B3: 0.06 sec
first B1: 2.20 sec
c14 B1: 167.30 sec
c14 FB end: 177.42 sec
c15 theoretical B1: 180.00 sec, excluded
```

Conventional with M1 opener:

```text
M1,C,M3 / C,C,M3 / C,C,M3 / C,C,M3 / C,M2
```

Sustained funnel:

```text
M1,C,M3 / C,M2,C / C,C,M3 / C,M2,C / C,M2
```

M1 opener는 첫 macro에서만 가능한 특수조건이다. M3 이후 Hangover 때문에 반복하지 않는다.

---

# 4. 현행 엔진 검증 상태

2026-09-02 audit에서 다음을 교정/확정했다.

- Rapi: Red Hood B1 Combat Assist 지원
- Raven DoT -> 하나의 refreshing stack-scaled DoT, max 10
- Quency: Escape Queen -> dual-SMG 2-hit trigger / sequential route / expiry 교정
- Cinderella: Crystal Wave MG Core Strike -> forced-core
- cast-instant B3 damage -> 동일 timestamp에서 FB +50%를 잘못 받지 않도록 교정
- Distributed Damage buff -> ordinary Damage Taken과 같은 additive Taken bucket으로 교정

분배 버킷은 Moris calculator + NIKKE.gg 교차검증으로 확정했다.

```text
Distributed hit Taken multiplier
= 1 + ordinary Damage Taken + applicable Distributed Damage
```

별도 distributed multiplier와 곱하지 않는다.

관련 문서:

```text
docs/DISTRIBUTED_DAMAGE_BUCKET_AUDIT_2026-09-02.md
```

현재 알려진 distributed-bucket blocker는 해소된 상태다.

---

# 5. 출처 정책

최상위 규칙:

```text
docs/SOURCE_VALIDATION_POLICY.md
```

우선순위:

1. 직접 인게임 검증 / 공식 정보
2. Moris calculator + NIKKE.gg 주요 독립 참조
3. 필요시 Prydwen / 다른 현행 독립 자료
4. nikke-sim은 datamine provenance / 구조화 데이터 / reference implementation용 보조 source

새 mechanic semantic을 nikke-sim 단독으로 확정하지 않는다. timing / trigger / damage bucket처럼 연구 결과를 바꾸는 항목은 교차검증한다.

---

# 6. 공식 v1 표본 — 동결

구현:

```text
crown_mast_engine/official_study.py
```

## B1 — 5

```text
Liter
Anis: Star
Moran (Favorite Item)
Little Mermaid
Rapi: Red Hood
```

`Neon: Vision Eye`는 구현되어 있지만 official-v1에는 포함하지 않고 확장/민감도 후보로 둔다.

## Main B3 — 9

```text
Rapi: Red Hood
Scarlet: Black Shadow
Bready
Cinderella: Crystal Wave
Liberalio
Milk: Blooming Bunny
Phantom (Favorite Item)
Quency: Escape Queen
Raven
```

이 목록은 티어표 주장이 아니라 연구 표본 설계다.

## Secondary B3 — 3

```text
Epinel
Helm
Snow White: Heavy Arms
```

## Rapi 중복 규칙

Rapi RH를 B1 Combat Assist로 배정하면 같은 Rapi를 Main/Secondary B3로 동시에 사용할 수 없다.

`TeamRoster` core validation이 모든 동일 캐릭터 중복을 거부하며, official generator도 duplicate roster를 생성 전에 제외한다.

```text
raw rosters: 5 x 9 x 3 = 135
invalid Rapi B1/Main duplicates: 3
valid rosters: 132
```

Secondary anchors에는 Rapi가 없으므로 추가 duplicate exclusion은 없다.

---

# 7. Secondary B3 역할 정의

상세:

```text
research_results/SECONDARY_B3_ANCHORS_DRAFT.md
```

내부 역할:

```text
Epinel
-> Low opportunity-cost / positive control

Helm
-> Practical middle anchor

Snow White: Heavy Arms
-> High opportunity-cost / upper-bound stress test
```

중요:
- SWHA를 `일반적인 강한 서브딜러 대표`로 해석하지 않는다.
- SWHA는 메인급 딜러를 Secondary 위치에 둔 상단 경계/스트레스 표본이다.
- 최종 분석은 Low/Mid/High 이름보다 **Conventional 기준 실제 Secondary damage share**를 주 분석변수로 사용한다.
- Helm을 현실적 중앙 기준으로 우선 해석하고 Epinel/SWHA를 양쪽 경계값으로 본다.

---

# 8. robustness grid / 공식 scenario 수

성장축:

```text
B1 growth        4
Main B3 growth   4
Secondary growth 4

4 x 4 x 4 = 64 growth points
```

환경축:

```text
Core off = 0% eligible core-hit rate
Core on  = 100% eligible core-hit rate

Main advantage off/on = 2
```

Core 0/100은 실전 코어 노출률 추정치가 아니라 **통제 민감도 극단값**이다.

Main advantage on은 Main이 우월인 실제 boss element를 사용한다. 같은 속성 teammate가 있으면 그 teammate도 자연스럽게 우월 효과를 받는다. Main만 인위적으로 element multiplier를 주는 축이 아니다.

따라서:

```text
64 growth x 2 core x 2 advantage = 256 scenarios / valid roster
132 valid rosters x 256 = 33,792 official-v1 scenarios
```

각 grid point는 확률표본이 아니다. 전체 funnel-win 비율을 실제 실전 발생확률로 해석하지 않는다.

---

# 9. 분배딜 Main 사전검증 — 완료

최종 연구 전에 Scarlet: Black Shadow가 유독 Funnel에 약해 보인다는 문제를 확인하기 위해 별도 진단을 수행했다.

상세:

```text
docs/DISTRIBUTED_MAIN_PRETEST_2026-09-02.md
```

진단 조건:

```text
B1 Liter
Secondary Helm
neutral boss
core 0%
range bonus 0%
64 growth points per Main
```

비교한 distributed Main:

```text
Scarlet: Black Shadow
Bready
Quency: Escape Queen
Phantom FI
Milk: Blooming Bunny
```

대조군:

```text
Rapi: Red Hood
```

64점 평균 Main `g`:

```text
Quency EQ       +3.707%
Rapi RH         +2.311%   <- non-distributed control
Milk BB         +2.151%
Phantom FI      +1.162%
SBS             +0.918%
Bready          -0.050%
```

동일 조건에서 rest-of-team loss `l`은 모두 약 3.871%로 사실상 동일했다.

핵심 결론:

> `distributed` 태그 자체가 Funnel 반응을 약하게 만드는 것은 아니다.

Quency는 distributed burst를 쓰면서 Rapi control보다 `g`가 높다. Milk도 Rapi에 근접한다.

SBS source-level 대표점에서는:

```text
normal_attack                    +0.641%
skill1_phase1 plain              +0.785%
skill1_phase2 distributed        +1.326%
skill1_phase3 distributed        +0.798%
```

즉 SBS 분배 packet이 Mast buff를 못 받는 징후가 없다.

SBS가 최종적으로 약한 이유는 cycle-level cancellation 쪽이다.

```text
cycle 5   +10.05%
cycle 6   -21.28%
cycle 11  +10.17%
cycle 12  -16.76%
```

Quency 대표점에서는 `burst_distributed`가 +8.642% 증가하고 Main 전체 `g`는 +3.561%였다. 약 97%의 Main 절대 gain이 이 burst packet에서 나온다.

따라서 현재 해석:

> **Main의 Funnel receptivity는 distributed 여부보다, 고가치 딜이 Main-targeted Mast-favored window에 얼마나 집중되는지와 인접 cycle의 손실이 얼마나 상쇄하는지에 크게 좌우된다.**

Bready는 Mast distributed buff 자체가 Recommended Taste 상태를 활성화하므로 mechanic-specific edge case로 본다.

이 진단으로 인해 official Main 후보를 제거하지 않는다.

최종 분석에서는 `distributed/non-distributed`를 주 분류축으로 사용하지 않고 다음을 유지한다.

```text
Main actor
Main g
Main conventional share
Main absolute gain
outlier 해석 시 source/timing structure
```

---

# 10. 공식 결과 저장 설계

상세:

```text
research_results/OFFICIAL_STUDY_DESIGN_V1.md
```

실행 shard 단위:

```text
1 valid roster = 256 scenarios
```

제안 구조:

```text
research_results/runs/<run_id>/
  manifest.json
  raw/<roster_id>.jsonl
  tables/scenarios.csv
  tables/rosters.csv
  analysis/
    secondary_anchor_summary.md
    effect_size_summary.md
    reversal_structure.md
```

원칙:
- manifest + compact raw JSONL을 canonical로 둔다.
- 33,792개 모든 scenario에 verbose full ComparisonReport를 저장하지 않는다.
- full report가 필요한 selected case는 manifest 조건으로 재현 가능하게 한다.
- CSV/analysis tables는 raw에서 파생한다.

compact raw에 최소 포함:

```text
case / roster / growth / environment identifiers
engine / hook / catalog revisions
Conventional/Funnel team totals and delta
outcome
Main damage/share and absolute gain
Secondary damage/share
rest-of-team opportunity loss
g / l / break-even
per-character damage/share
```

---

# 11. 분석 중심

Primary outputs:

1. Secondary anchor별 Funnel win/loss 구조
2. Funnel 승리점의 효과크기 분포
3. Conventional 승리점에서 Funnel 손실률 분포
4. 역전점의 Conventional Secondary damage share
5. Main gain vs rest-of-team opportunity loss

Secondary slicing:

- Main actor / Main `g`
- B1 actor
- growth state
- core on/off
- Main advantage on/off

특히 확인할 구조:

> Secondary 기여도가 높아질수록 몰아주기 승리영역이 얼마나 축소되는가?

예상 결론을 미리 고정하지 않는다.

---

# 12. 연구에서 주장하지 않을 것

- 모든 NIKKE / 모든 boss에서 Conventional이 항상 우월하다고 주장하지 않는다.
- grid Funnel 승리비율을 실전 승리확률로 해석하지 않는다.
- 하나의 보편 Main-share 임계값이 존재한다고 주장하지 않는다.
- pattern-loss가 없는 baseline을 모든 실전 패턴에 그대로 적용하지 않는다.
- Snow White: Heavy Arms를 일반적인 Secondary 대표라고 주장하지 않는다.
- distributed Main을 하나의 동질 집단으로 취급하지 않는다.

---

# 13. 현재 연구 상태 / 다음 작업

```text
Official candidate lists: frozen
Official valid rosters: 132
Official scenario count: 33,792
Secondary anchor roles: frozen
Distributed Main blocker check: completed / no generic distributed-bucket blocker found
Official research batch: NOT RUN
Official result count: 0
main branch: untouched
```

사용자 명시 승인 전에는 official 33,792 batch를 실행하지 않는다.

다음 pre-batch 작업:

```text
1. compact raw row schema/writer 구현
2. run manifest factory / shard writer 구현
3. 소규모 writer/smoke verification
4. 사용자 명시 승인 후 official batch 실행
5. raw + derived tables 저장
6. Secondary opportunity-cost 중심 분석
7. 필요 시 pattern-loss follow-up
```

기존 historical checkpoint와 이번 distributed pretest를 공식 결과로 승격하지 않는다.
