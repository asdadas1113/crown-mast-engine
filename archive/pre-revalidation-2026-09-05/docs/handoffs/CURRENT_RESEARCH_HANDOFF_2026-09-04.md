# Crown–Mast Engine 연구 인수인계 — 2026-09-04

이 문서는 `research/14-burst-baseline` 브랜치에서 Crown–Mast 공식 연구를 이어가기 위한 최신 인계문서다.

## 0. 재개 시 먼저 확인할 것

1. GitHub에서 `research/14-burst-baseline`의 최신 HEAD를 다시 확인한다.
2. `main`은 사용자 명시 지시 없이는 수정하거나 병합하지 않는다.
3. 공식 연구 배치는 사용자 명시 승인 전에는 실행하지 않는다.
4. 아래 문서를 우선 읽는다.

```text
docs/CURRENT_RESEARCH_HANDOFF_2026-09-04.md
docs/SOURCE_VALIDATION_POLICY.md
research_results/README.md
research_results/OFFICIAL_STUDY_DESIGN_V1.md
research_results/runs/README.md
research_results/SECONDARY_B3_ANCHORS_DRAFT.md
research_results/SCARLET_BLACK_SHADOW_FUNNEL_CASE_STUDY_2026-09-02.md
```

필요할 때만:

```text
docs/CHARACTER_AUDIT_2026-09-02.md
docs/DISTRIBUTED_DAMAGE_BUCKET_AUDIT_2026-09-02.md
docs/DISTRIBUTED_MAIN_PRETEST_2026-09-02.md
docs/RAID14_PATTERN_LOSS_FOLLOWUP_2026-09-01.md
```

---

# 1. 연구 목적

이 엔진의 목적은 NIKKE 전투 전체를 완벽하게 재현하는 것이 아니다.

핵심 질문:

> 외생변수를 최대한 제거한 동일 조건에서 Crown/Mast B2 운용만 바꿨을 때, 관습적인 `강한 Main 딜러가 있으면 Mast를 몰아준다`는 판단이 실제로 얼마나 넓은 범위에서 유효한가?

주요 가설:

1. 몰아주기 유효구간은 제한적인가.
2. 몰아주기가 이겨도 효과크기가 작은가.
3. 실전적인 Secondary 기여도가 생기면 몰아주기 우세영역이 얼마나 줄어드는가.

보편적인 Main 딜 지분 임계값 하나를 찾는 것이 주목적은 아니다.

기본 연구에서는 boss jump / movement / invulnerability / forced cover / part exposure 등 패턴 손실을 제외한다. 패턴 손실은 별도 후속연구로 다룬다.

---

# 2. 현행 RAID14 기준선

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

Sustained Funnel:

```text
M1,C,M3 / C,M2,C / C,C,M3 / C,M2,C / C,M2
```

M1 opener는 첫 macro에서만 사용한다.

---

# 3. 공식 표본 후보 — 2026-09-04 재정리

구현:

```text
crown_mast_engine/official_study.py
```

## B1 — 5명

```text
Liter
Anis: Star
Moran (Favorite Item)
Little Mermaid
Rapi: Red Hood — B1 Combat Assist
```

주의: `Anis: Star`가 정확한 명칭이다. `Anis: Sparkling Summer`가 아니다.

## Main B3 — 8명

```text
Rapi: Red Hood
Scarlet: Black Shadow
Cinderella
Cinderella: Crystal Wave
Liberalio
Neon: Vision Eye
Phantom (Favorite Item)
Raven
```

2026-09-04 결정으로 공식 Main에서 제외:

```text
Bready
Milk: Blooming Bunny
Quency: Escape Queen
```

제외된 캐릭터의 구현과 기존 독립 진단 결과는 삭제하지 않는다.

네온: 비전 아이는 이미 구현돼 있었고 이번에 공식 Main 표본으로 편입했다.

원본 신데렐라는 2026-09-04 직전 신규 구현 및 공식 Main 표본 편입을 마쳤다.

## Secondary B3 — 3명

```text
Epinel                  -> 낮은 기회비용 대조군
Helm                    -> 실전적인 중앙 기준점
Snow White: Heavy Arms  -> 상단 기회비용 스트레스 테스트
```

SWHA는 일반적인 `강한 서브딜러 대표`가 아니다. 메인급 딜러를 Secondary 위치에 둬 기회비용 상단을 확인하기 위한 스트레스 표본이다.

최종 분석은 캐릭터 라벨보다 Conventional 기준 실제 Secondary 총딜/5인 딜 지분을 우선한다.

---

# 4. 공식 scenario 수

성장 격자:

```text
B1 growth        4
Main growth      4
Secondary growth 4
= 64 growth points
```

환경축:

```text
core off/on = 2
Main advantage off/on = 2
```

roster당:

```text
64 x 2 x 2 = 256 scenarios
```

현재 후보군:

```text
5 B1 x 8 Main x 3 Secondary = 120 raw rosters
Rapi B1 + Rapi Main duplicate = -3
117 valid rosters
117 x 256 = 29,952 official scenarios
```

각 scenario는 확률표본이 아니라 통제된 결정론적 checkpoint다. 29,952개 중 Funnel 승리 비율을 실전 발생확률로 해석하지 않는다.

---

# 5. 최근 구현 상태

원본 Cinderella 추가를 위해 다음을 구현했다.

```text
crown_mast_engine/data/character_cinderella.json
crown_mast_engine/character_mechanics/cinderella.py
tests/test_cinderella.py
```

주요 지원:
- Defender 기준 progression HP
- 장비/성장 상태를 반영한 최대체력 처리
- 최종 최대체력 -> 공격력 변환
- Beautiful 최대체력 누적
- 완충 추가타
- 첫 완충 후 가속, 실제 재장전 뒤 다시 예열되는 특수 RL cadence
- 자기 B3 10회 순차 공격 및 Beautiful 추가타

이 과정에서 공용 엔진에 HP/특수 charge cadence 지원이 추가되어 engine rule revision도 갱신됐다.

첫 CI에서 Cinderella hook 생성자 연결 오류 1건이 잡혔고 수정했다. 이후 후보군 변경은 공식 연구 generator/test/document에 반영됐다.

새 채팅에서는 CI 상태를 과거 인계 내용으로 추정하지 말고 최신 HEAD의 Actions 상태를 직접 확인한다.

---

# 6. 흑련 및 기존 독립 진단의 의미

흑련 케이스 스터디는 공식 배치 결과가 아니지만 보존 가치가 있다.

핵심:

> 흑련은 메스트 분배 대미지 버프를 정상적으로 받는다. 다만 자기 B3 외의 인접 cycle에도 가치 있는 딜이 많이 남아 있어, Main-targeted Mast 이득이 다음 cycle의 M3 손실로 크게 상쇄된다.

따라서 Main의 몰아주기 반응을 설명할 때 단순 `강한 딜러인가`, `분배딜인가`보다 **딜의 시간적 집중도와 인접 cycle 상쇄**를 봐야 할 가능성이 높다.

Bready / Quency / Milk는 공식 Main에서는 빠졌지만 기존 진단 자료는 이 가설을 검증한 독립 자료로 계속 보존한다.

---

# 7. 공식 결과 저장 구조 — 2026-09-04 확정

결과는 사람이 읽는 자료와 기계가 읽는 자료를 분리한다.

최상위 구조:

```text
research_results/runs/<run_id>/
  manifest.json
  machine/
    raw/
      <roster_id>.jsonl
    tables/
      scenarios.csv
      rosters.csv
  human/
    00_전체_요약.md
    01_세컨더리_기준점_분석.md
    02_메인_B3_분석.md
    03_B1_분석.md
    04_효과크기_분석.md
    05_역전_구조_분석.md
    06_성장_및_환경_민감도.md
    cases/
      몰아주기_승리_대표사례.md
      기존운용_승리_대표사례.md
      경계_사례.md
      이상치_사례.md
```

실제 디렉터리 골격은 다음에 생성돼 있다.

```text
research_results/runs/README.md
research_results/runs/_template/
```

## manifest.json

사람/기계 양쪽이 공유하는 provenance 원본이다.

최소 기록:
- study_id / run_id
- branch / commit SHA
- engine / skill hook / catalog revisions
- RAID14 timeline
- candidate lists
- growth grid
- core / Main advantage axes
- roster/scenario counts
- shard policy
- completed shard ids

## machine/

재분석·검증·재현용.

`raw/<roster_id>.jsonl`:
- roster 하나당 256 compact rows
- manifest와 함께 canonical raw

`tables/scenarios.csv`:
- 29,952 scenario의 평탄화 분석표

`tables/rosters.csv`:
- roster별 집계표

모든 scenario의 verbose cycle/source/damage-event report는 기본 저장하지 않는다. 상세 사례는 manifest + commit SHA로 재현한다.

## human/

사람이 읽는 결과 해석용.

우선순위:
1. 전체 요약
2. Secondary opportunity-cost 분석
3. Main별 분석
4. B1 보조 분석
5. 효과크기
6. 역전 구조
7. 성장/환경 민감도
8. 대표 사례

원자료를 Markdown에 전부 복사하지 않는다.

---

# 8. 공식 배치 직전 남은 체크포인트

공식 연구 결과는 아직 0건이다.

공식 배치 전 남은 작업:

1. 최신 HEAD 전체 회귀 CI 성공 확인
2. compact raw row schema/writer 확정
3. manifest writer/factory 확정
4. 작은 roster 1개 수준의 writer/smoke 검증
5. 사용자에게 공식 배치 실행 명시 승인 받기
6. 승인 후 117 roster x 256 = 29,952 scenario 공식 실행

공식 배치 승인 전에는 29,952 전체 실행을 시작하지 않는다.

---

# 9. 결과 분석 우선순위

Primary:

1. Secondary 실제 기여도가 올라갈수록 Funnel 승리영역이 얼마나 축소되는가
2. Funnel이 이길 때 실제 효과크기는 얼마나 큰가
3. Conventional이 이기는 점에서 Funnel을 선택했을 때 손실폭은 얼마인가
4. Main gain `g`와 rest-of-team opportunity loss `l` 중 무엇이 역전을 주도하는가
5. 같은 roster에서 성장/core/우월 한 축만 바꿨을 때 역전되는 paired case는 무엇인가

Main별 특이값은 `human/02_메인_B3_분석.md`와 `human/cases/이상치_사례.md`에서 별도로 다룬다.

---

# 10. 주의사항

- `main` 수정/병합 금지.
- 공식 배치 무단 실행 금지.
- 과거 checkpoint를 공식 결과로 승격하지 않기.
- 승패 빈도를 실전 확률로 해석하지 않기.
- SWHA를 일반적인 strong Secondary 대표로 서술하지 않기.
- Bready/Milk/Quency를 공식 Main에서 다시 넣지 않기 unless user reopens candidate discussion.
- `Anis: Star` 명칭 유지.
- 새 mechanic semantic은 `SOURCE_VALIDATION_POLICY.md` 우선순위를 따른다.

---

# 11. 현재 인계 시점

이 문서 작성 직전 확인한 branch HEAD는 결과 폴더 템플릿 추가 작업을 포함한 상태였다. 그러나 새 작업을 시작할 때는 반드시 GitHub에서 최신 HEAD를 다시 조회한다.

현재 단계는 **공식 배치 실행 전 결과 writer/smoke 준비 단계**다.
