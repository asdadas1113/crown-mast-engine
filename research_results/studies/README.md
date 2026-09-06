# 연구별 결과 저장 구조

이 디렉터리는 Crown–Mast 연구를 **연구 단위로 분리**해 보관하는 최상위 영역이다.

## 기본 구조

```text
studies/
├─ 01_exploratory/
│  ├─ human/
│  │  └─ reports/<run_id>/
│  ├─ machine/
│  │  └─ runs/<run_id>/
│  └─ validation/
│     └─ runs/<run_id>/
├─ 02_followup_placeholder/
└─ README.md
```

### `human/`

연구 목적·설계와 사람이 읽는 한글 결과 보고서를 저장한다. 공식 실행 결과는 `human/reports/<run_id>/` 아래에 둔다.

### `machine/`

manifest, scenario 정의, raw 결과, aggregate, provenance를 저장한다. 공식 실행 데이터는 반드시 `machine/runs/<run_id>/` 아래에 분리하며 다른 연구나 다른 run과 섞지 않는다.

### `validation/`

설계 검증, 표본 수 검증, 회귀 검증, 실행 후 완전성·재현성·이상치 확인을 보관한다. 실행 후 검증은 `validation/runs/<run_id>/`에 둔다.

프로젝트 전체 테스트 코드는 루트 `tests/`에 유지한다.

## 저장 원칙

- 하나의 공식 실행은 하나의 고유 `run_id`를 가진다.
- 기계 데이터·사람용 보고서·validation은 같은 `run_id`로 연결한다.
- 재실행은 기존 run을 덮어쓰지 않는다.
- scenario/raw는 수만 개의 개별 Git 파일 대신 shard 단위 JSONL/CSV를 사용하며 필요하면 압축한다.
- 과거 archive 결과를 새 연구 결과에 혼합하지 않는다.

## 현재 1연구 상태

```text
study_id = crown-mast-study-01-exploratory-v1
87 rosters × 27 growth × 12 environments = 28,188 scenarios
execution model gates = 0
execution_ready = true
status = design-frozen-execution-unapproved
```

최종 실행 전 검증은 완료됐으나 공식 28,188 scenario 전투 batch는 아직 실행하지 않았다.

## 실행 정책

사용자의 명시 승인 전에는 공식 batch를 실행하지 않는다. 승인 후 실행 commit SHA와 `run_id`, manifest를 먼저 동결하고 그 다음 전투 계산을 시작한다. `main`은 수정하거나 병합하지 않는다.
