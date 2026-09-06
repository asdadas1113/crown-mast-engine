# Crown–Mast Research Engine

NIKKE의 Crown + Mast: Romantic Maid 운용을 통제 조건에서 비교하기 위한 개인 연구용 엔진이다.

## 현재 상태 — 2026-09-06

기존 29,952 scenario 연구와 이전 설계는 폐기/superseded 상태이며 `archive/pre-revalidation-2026-09-05/`에 보존한다. 현재 1연구는 새 설계로 다시 동결됐다.

```text
study_id = crown-mast-study-01-exploratory-v1
87 valid rosters
27 growth points
12 environments
28,188 scenarios
execution model gates = 0
execution_ready = true
status = design-frozen-execution-unapproved
```

최종 실행 전 검증:

```text
GitHub Actions run 34002759044
focused 68/68
full regression 322/322
case-generation preflight 28,188/28,188
simulation executed: no
```

즉 모델·회귀·case generator의 기술적 gate는 닫혔지만 공식 28,188 scenario 전투 batch는 아직 실행하지 않았다.

## 활성 시간축

- 엔진과 연구 API의 기본 시간축은 `RAID14_TIMELINE`이며 180초·14버스트를 사용한다.
- `STANDARD_TIMELINE`도 `RAID14_TIMELINE`의 호환 별칭이다.
- 폐기된 12버스트 시간축은 과거 결과 재현 전용 `LEGACY_12_BURST_TIMELINE`으로만 남긴다.
- 사용자가 현재 요청에서 12버스트 재현을 명시적으로 지시하지 않는 한 어떤 분석·연구·테스트·신규 코드에서도 `LEGACY_12_BURST_TIMELINE`을 절대 사용하지 않는다.
- 12버스트 재현이 명시적으로 요청된 경우에만 `timeline=LEGACY_12_BURST_TIMELINE`을 직접 지정한다.
- `archive/` 아래의 코드와 문서는 활성 엔진 기준으로 사용하지 않는다.

## 1연구 목적

1연구는 하나의 보편적 최적 운용 규칙을 확정하는 연구가 아니다.

> 대표적인 Crown/Mast 통제 조건에서 운용의 상대 손익을 움직이는 변수와 상호작용, 반복되는 예외를 탐색하고 후속 연구 후보를 선별한다.

승패 점유율을 실전 승률이나 모든 계정·보스에 적용되는 보편 규칙으로 해석하지 않는다.

## 현재 읽을 문서

```text
docs/CURRENT_RESEARCH_HANDOFF.md
docs/CURRENT_RESEARCH_HANDOFF_2026-09-06.md
docs/SOURCE_VALIDATION_POLICY.md
research_results/README.md
research_results/RESEARCH_STATUS_2026-09-06.md
research_results/studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md
research_results/studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
research_results/studies/01_exploratory/validation/05_최종_실행전_검증_2026-09-06.md
```

공식 실행 직전 정리에서 active 영역에서 제거한 역사 문서와 옛 실험 브랜치 snapshot은 다음에 보존한다.

```text
archive/pre-study1-execution-2026-09-06/
```

## 결과 저장 구조

공식 실행 승인 후 고유 `run_id`를 만들고 다음 위치에 저장한다.

```text
research_results/studies/01_exploratory/
├─ machine/runs/<run_id>/
│  ├─ manifest.json
│  ├─ scenarios/
│  ├─ raw/
│  ├─ aggregate/
│  └─ provenance/
├─ human/reports/<run_id>/
└─ validation/runs/<run_id>/
```

scenario/raw는 수만 개의 개별 Git 파일 대신 shard 단위 JSONL/CSV로 저장하며 필요하면 압축한다. 재실행은 기존 run을 덮어쓰지 않는다.

## 운영 원칙

- active 개발 기준 branch는 `research/14-burst-baseline`이다.
- `main`은 사용자 명시 지시 없이 수정하거나 병합하지 않는다.
- 공식 batch는 사용자 명시 승인 후에만 실행한다.
- 실행 전 commit SHA, `run_id`, manifest를 먼저 동결한다.
- 과거 폐기 결과가 재현되도록 엔진이나 파라미터를 조정하지 않는다.
- deterministic grid point를 실전 발생확률로 해석하지 않는다.
