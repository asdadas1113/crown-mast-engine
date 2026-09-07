# Crown–Mast 연구 인수인계 — 2026-09-07

## 1. 인계 시작점

새 AI는 루트 `AGENTS.md`와 `docs/AI_HANDOFF_PROTOCOL.md`를 먼저 읽고 이 문서를 현재 canonical 상태로 사용한다.

## 2. 현재 기준

```text
branch = research/14-burst-baseline
verified engine commit = 801cab5fa3b0d64150ea0ebd9558acce6bce47ba
study_id = crown-mast-study-01-exploratory-v1
timeline = RAID14_TIMELINE
status = design-frozen-execution-unapproved
official combat batch = not executed
```

`801cab5`는 14버스트 단일 기본값과 현행 Study 1 writer/manifest 정렬을 포함해 전체 회귀를 통과한 엔진 기준점이다. 이 문서 이후 문서 전용 커밋이 추가될 수 있으므로 실제 실행 시에는 실행 직전 clean HEAD SHA를 별도로 manifest에 고정한다.

`main`은 사용자 명시 지시 없이 수정하거나 병합하지 않는다.

## 3. 현행 Study 1

canonical 설계:

```text
research_results/studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
```

표본:

- B1 5명
- Main B3 6명
- Secondary B3 3명
- raw 90 rosters 중 중복 3개 제외
- 87 valid rosters
- B1/Main/Secondary 성장 3×3×3 = 27 growth points
- DEF 3 × core 2 × Main advantage 2 = 12 environments
- roster당 324 scenarios
- 총 28,188 scenarios

과거 `crown-mast-secondary-opportunity-v1` 29,952 scenario 설계는 폐기됐다. 활성 코드의 `official_study.py`도 현행 `wave_a_study.py`로 연결되며 과거 설계를 신규 실행에 사용하지 않는다.

## 4. 시간축과 실행 금지선

- 활성 시간축은 180초·14버스트 `RAID14_TIMELINE` 하나다.
- `LEGACY_12_BURST_TIMELINE`은 사용자가 현재 요청에서 12버스트 역사 재현을 명시한 경우에만 사용한다.
- 사용자 명시 승인 전에는 공식 28,188 scenario 전투 batch를 실행하지 않는다.
- `execution_ready=true`는 기술적 준비 상태이며 실행 승인이 아니다.

## 5. 최신 검증

검증된 engine commit `801cab5` 기준:

```text
full regression = 327/327 passed
focused current Study 1/writer tests = 19/19 passed
case generation = 28,188/28,188
unique case IDs = 28,188
all timelines = RAID14
all baseline rotations = opening_mast_crown_mast
all study IDs = crown-mast-study-01-exploratory-v1
simulation executed by case preflight = no
```

공식 run ID, 실제 run manifest, 공식 raw/aggregate/report는 아직 없다.

## 6. 결과 저장 위치

승인된 공식 run은 다음 구조를 사용한다.

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

기존 run을 덮어쓰지 않는다. 실행과 재개는 manifest의 commit SHA·catalog digest·schema가 현재 checkout과 일치할 때만 허용한다.

## 7. 1차 연구 이후

현재는 1차 연구 결과가 없으므로 후속 가설이나 코드 변경안을 확정하지 않는다. 결과를 확인한 뒤 가설을 문서화하고 `research/post-study1-<topic>` 형태의 새 브랜치에서 변경한다.

1차 연구의 run·manifest·raw·validation·보고서는 불변으로 보존한다. 변경된 코드로 재계산할 때는 새 `run_id`를 사용하며, 연구 질문이나 표본 설계가 달라지면 새 study ID와 별도 연구 디렉터리를 사용한다.

오류를 발견해 재실행하는 경우에도 기존 run과 원본 manifest를 삭제하거나 덮어쓰지 않는다. 기존 run의 validation 상태를 `invalid` 또는 `superseded`로 표시한 뒤 새 run으로 연결한다.

## 8. 다음 AI가 할 일

사용자 요청이 단순 검수나 준비라면 읽기 전용 확인과 테스트까지만 수행한다. 사용자가 현재 대화에서 공식 실행을 명시적으로 승인한 경우에만 다음을 진행한다.

1. clean branch와 HEAD SHA 확인
2. 전체 회귀 및 28,188 case-generation 재검증
3. 고유 `run_id` 확정
4. 실제 manifest에 SHA·catalog·schema 고정
5. run 디렉터리 생성
6. 공식 batch 실행
7. raw 완전성·checksum 검증
8. aggregate와 한글 보고서 생성

세부 인계 규칙은 `docs/AI_HANDOFF_PROTOCOL.md`, 연구 기록 규격은 `research_results/studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md`를 따른다.
