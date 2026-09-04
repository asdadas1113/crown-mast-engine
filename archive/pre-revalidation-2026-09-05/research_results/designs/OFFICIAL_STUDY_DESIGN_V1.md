# Crown–Mast 공식 연구 설계 v1

상태: **공식 배치 실행 전 후보군 재검토 완료 / 공식 연구 결과 없음**

Study id:

```text
crown-mast-secondary-opportunity-v1
```

이 문서는 사용자가 공식 연구 배치를 명시적으로 승인했을 때 사용할 표본 공간과 실행·저장 구조를 정의한다. 연구 결과를 담는 문서가 아니다.

2026-09-02 첫 공식 배치 실행 전에 Main 표본을 다시 검토했다. 원본 신데렐라(Cinderella)를 추가하고, 브래디 / 밀크: 블루밍 버니 / 퀀시: 이스케이프 퀸을 공식 Main 축에서 제외했으며, 네온: 비전 아이를 공식 Main 후보로 편입했다. 세 제외 캐릭터의 엔진 구현과 독립 진단 가치는 유지한다.

---

## 1. 연구 질문

외생변수를 통제한 RAID14 기준선에서 Crown/Mast B2 운용만 바꾸었을 때 다음 관습적 판단이 실제로 얼마나 넓은 범위에서 유효한지 확인한다.

> `강한 Main 딜러가 있으면 Mast를 반복적으로 Main에게 몰아주는 편이 유리하다.`

주요 질문은 다음과 같다.

1. 지속 몰아주기가 이기는 조건은 제한적인가?
2. 몰아주기가 이기더라도 이득 폭은 작은가?
3. 몰아주기 우세 파티 구조는 현실적인 편성에서 쉽게 만들어지는가?

분석의 중심은 보편적인 Main 딜 지분 임계값 하나가 아니라 **Secondary B3를 포기하면서 발생하는 기회비용**이다.

---

## 2. B1 표본 — 5명

엔진 slug:

```text
liter
anis-star
moran-favorite-item
little-mermaid
rapi-red-hood
```

표시명:

```text
리타
아니스: 스타
목단(애장품)
리틀 머메이드
라피: 레드 후드 — B1 Combat Assist
```

B1 축은 서로 다른 버프·자체딜 환경을 확보하기 위한 표본이다.

라피: 레드 후드를 B1으로 사용하는 경우 같은 라피를 Main B3에 동시에 편성할 수 없다. 공식 generator가 `TeamRoster` 생성 전에 해당 중복 조합을 제외하고, `TeamRoster`의 중복 검증이 두 번째 안전장치로 작동한다.

```text
B1 라피 + Main 라피 -> 제외
```

---

## 3. Main B3 표본 — 8명

엔진 slug:

```text
rapi-red-hood
scarlet-black-shadow
cinderella
cinderella-crystal-wave
liberalio
neon-vision-eye
phantom
raven
```

표시명:

```text
라피: 레드 후드
홍련: 흑영
신데렐라
신데렐라: 크리스탈 웨이브
리버렐리오
네온: 비전 아이
팬텀(애장품)
레이븐
```

이 목록은 보편적인 티어표가 아니라 연구 표본이다. 현재 상위권 Main과 서로 다른 딜 시간분포·메커니즘을 확보하는 것이 목적이다.

원본 신데렐라는 다음 구조를 추가한다.

- 최종 최대체력 기반 공격력 변환
- B3 Stage 진입마다 갱신되는 10초 공격력 변환 구간
- 첫 완충 후 가속되고 재장전 시 다시 예열되는 특수 RL 사격 주기
- 자기 B3에서 10회 순차 공격으로 집중되는 큰 버스트 대미지
- 전투 시간이 지날수록 누적되는 Beautiful 최대체력 스택

네온: 비전 아이는 이미 구현·검증된 B3 딜러이며, 이번 재검토에서 공식 Main 표본으로 편입했다.

다음 캐릭터는 공식 Main 표본에서는 제외하지만 엔진 구현과 진단 자료는 유지한다.

```text
bready
milk-blooming-bunny
quency-escape-queen
```

브래디는 메스트 분배 대미지 버프가 Recommended Taste 상태를 직접 건드리는 특수 상호작용이 있고, 밀크와 퀀시는 독립 진단용 정보 가치는 충분하지만 현재 공식 Main 대표 표본에서는 우선순위를 낮췄다.

Secondary anchor 세 명은 Main 축과 의도적으로 분리한다. 따라서 에피넬 / 헬름 / 스노우 화이트: 헤비암즈는 현재 Main 후보로 사용하지 않는다.

---

## 4. Secondary B3 기준점 — 3명

```text
epinel                 -> 낮은 기회비용 대조군
helm                    -> 실전적인 중앙 기준점
snow-white-heavy-arms   -> 높은 기회비용 상단 스트레스 테스트
```

스노우 화이트: 헤비암즈는 일반적인 `강한 서브딜러`의 대표가 아니다. 메인 캐리급 자체딜을 가진 캐릭터를 Secondary에 두어 **포기 비용의 상단 경계**를 확인하기 위한 스트레스 테스트다.

최종 분석에서는 Low/Mid/High 라벨보다 기존 운용 기준으로 실제 계산된 **Secondary 총딜 및 5인 딜 지분**을 우선한다.

---

## 5. 성장 격자

B1 / Main B3 / Secondary B3 각각 기존 realistic-v3 성장 checkpoint 4개를 사용한다.

```text
B1 성장        4
Main B3 성장   4
Secondary 성장 4

4 x 4 x 4 = 64 성장점
```

성장 프로필:

```text
g1-base5-none
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

Crown과 Mast는 기존 v3의 고정 B2 빌드를 유지한다.

64점은 발생확률 표본이 아니라 불균형 성장 상태까지 포함해 결론의 강건성을 확인하기 위한 결정론적 통제점이다.

---

## 6. 환경축

### 6.1 코어 off / on

```text
core off -> core_hit_rate_pct = 0
core on  -> core_hit_rate_pct = 100
```

`core on`은 코어가 완전히 노출된 민감도 극단값이다. 실제 전투에서 항상 100% 코어를 때린다는 뜻이 아니다.

### 6.2 Main 우월코드 off / on

우월코드는 Main에게만 인위적으로 배율을 주지 않는다.

```text
advantage off -> 중립 보스 속성
advantage on  -> Main B3가 실제로 우월을 가지는 보스 속성
```

같은 속성의 다른 아군도 실제 규칙에 따라 우월코드를 함께 받는다.

---

## 7. roster 및 시나리오 수

Raw roster:

```text
5 B1 x 8 Main x 3 Secondary = 120 rosters
```

중복 제외:

```text
Rapi B1 + Rapi Main x 3 Secondary = 3
```

유효 roster:

```text
120 - 3 = 117
```

한 roster당:

```text
64 growth x 2 core x 2 Main advantage = 256 scenarios
```

총 표본 공간:

```text
117 x 256 = 29,952 scenarios
```

Secondary별로는:

```text
39 valid B1/Main pairs x 256 = 9,984 scenarios
3 anchors                        = 29,952 scenarios
```

`29,952`는 현재 공식 v1 후보군 기준 canonical count다. 각 시나리오는 발생확률 표본이 아니라 결정론적 통제점이다.

---

## 8. 실행 단위

실행 shard는 **유효 roster 하나**다.

```text
1 roster shard
= 64 growth
x 2 core
x 2 Main advantage
= 256 scenarios
```

현재 공식 후보군에서는 117개의 독립 shard가 된다.

장점:

- 실패한 roster만 다시 실행할 수 있음
- 전체 결과를 한 번에 메모리에 올릴 필요가 없음
- roster와 raw 파일의 provenance가 명확함
- Secondary 기준점별 분석을 쉽게 합칠 수 있음

공식 배치는 사용자의 명시적 승인 전에는 실행하지 않는다.

---

## 9. 저장 구조

공식 배치 승인 후 다음 구조를 사용한다.

```text
research_results/runs/<run_id>/
  manifest.json
  raw/
    <roster_id>.jsonl
  tables/
    scenarios.csv
    rosters.csv
  analysis/
    secondary_anchor_summary.md
    effect_size_summary.md
    reversal_structure.md
```

`manifest.json`에는 최소 다음을 기록한다.

```text
study_id
run_id
branch
commit_sha
engine_rule_revision
skill_hook_revision
catalog_source_revision
timeline revision / exact parameters
baseline rotation
candidate lists
growth grid
core axis
Main advantage axis
valid roster count
scenario count
shard policy
completed shard ids
```

`raw/<roster_id>.jsonl`에는 시나리오당 compact record 하나를 저장한다. 모든 29,952점의 verbose cycle/source report를 저장하지 않고, 필요한 상세 사례는 manifest를 기준으로 재현한다.

compact row에는 최소 다음을 포함한다.

```text
case / study / run / roster id
B1 / Main / Secondary
각 역할 성장 프로필
core / Main advantage 조건
engine / hook / catalog revision
기존 운용 / 몰아주기 팀 총딜
절대·상대 변화량
outcome band
Main 기존/몰아주기 딜 및 지분
Main 절대 이득
Secondary 기존/몰아주기 딜 및 지분
나머지 파티 opportunity loss
g / l / local break-even
캐릭터별 기존/몰아주기 딜 및 지분
```

---

## 10. 우선 분석 항목

Primary:

1. Secondary 기준점별 몰아주기 승/패/동률 구간
2. 몰아주기 승리점의 효과크기 분포
3. 기존 운용 승리점에서 몰아주기를 택했을 때의 손실 분포
4. 역전 부근의 실제 Secondary 딜 지분
5. Main 절대 이득과 나머지 파티 opportunity loss의 비교

Secondary slicing:

```text
Main B3
B1
성장 조합
core off/on
Main advantage off/on
```

핵심 해석 질문은 다음과 같다.

> 기존 운용에서 Secondary의 기여도가 커질수록 지속 몰아주기의 승리영역은 얼마나 빠르게 줄어드는가?

---

## 11. 이 연구가 주장하지 않는 것

현재 v1 grid는 다음을 직접 증명하지 않는다.

- 보편적인 Main 딜 지분 임계값
- 실전에서 몰아주기가 이길 확률
- 모든 NIKKE 전투에서 Crown-Crown-Mast가 항상 최선이라는 주장
- 100% 코어 노출이 일반적이라는 주장
- 현재 Main 후보들이 보편적인 티어표 상위 8명이라는 주장
- 점프·무적·강제 엄폐·부위 노출 등의 패턴 손실이 있는 전투에서도 결과가 그대로 유지된다는 주장

패턴 손실은 별도 후속연구로 다룬다.

---

## 12. 구현 상태

현재 구현:

```text
crown_mast_engine/official_study.py
tests/test_official_study.py
crown_mast_engine/data/character_cinderella.json
crown_mast_engine/character_mechanics/cinderella.py
tests/test_cinderella.py
```

현재 상태:

- 원본 신데렐라 엔진 구현: 완료
- 네온: 비전 아이 공식 Main 편입: 완료
- 브래디 / 밀크: 블루밍 버니 / 퀀시: 이스케이프 퀸 공식 Main 제외: 완료
- 공식 Main 후보: 8명
- 유효 roster: 117
- 공식 표본 공간: 29,952
- 공식 research batch: **실행하지 않음**
- 공식 연구 결과 수: **0**
