# Crown–Mast 연구 결과 / 현재 상태

이 디렉터리는 **재검증된 새 연구의 active 상태와 결과만** 담는다.

과거 연구 설계·진단·결과는 `archive/` 아래에만 보존하며 새 연구의 결론·목표값·사전 기대값으로 사용하지 않는다.

## 현재 읽을 것

```text
../docs/CURRENT_RESEARCH_HANDOFF.md
../docs/CURRENT_RESEARCH_HANDOFF_2026-09-07.md
../docs/AI_HANDOFF_PROTOCOL.md
../docs/SOURCE_VALIDATION_POLICY.md
studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md
studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
studies/01_exploratory/validation/05_최종_실행전_검증_2026-09-06.md
```

## 1연구 상태

```text
study_id = crown-mast-study-01-exploratory-v1
valid rosters = 87
growth points = 27
environments = 12
expected scenarios = 28,188
execution model gates = 0
execution_ready = true
status = design-frozen-execution-unapproved
```

검증된 engine commit `801cab5fa3b0d64150ea0ebd9558acce6bce47ba`에서 focused 19/19, full regression 327/327, no-simulation case-generation 28,188/28,188이 통과했다. 공식 전투 batch는 아직 실행하지 않았다. `RESEARCH_STATUS_2026-09-06.md`와 GitHub Actions `34002759044`는 그 이전 검증 시점 기록이다.

## 결과 저장 위치

새 결과는 전역 `research_results/runs/`를 사용하지 않는다. **연구별·run별로 고정**한다.

```text
studies/01_exploratory/
├─ machine/
│  ├─ manifest/manifest_template.json
│  └─ runs/<run_id>/
│     ├─ manifest.json
│     ├─ scenarios/
│     ├─ raw/
│     ├─ aggregate/
│     └─ provenance/
├─ human/
│  └─ reports/<run_id>/
└─ validation/
   └─ runs/<run_id>/
```

- `machine/runs/<run_id>/raw/`: scenario별 원시 출력
- `machine/runs/<run_id>/aggregate/`: 집계표·요약 통계
- `human/reports/<run_id>/`: 사람이 읽는 한글 보고서
- `validation/runs/<run_id>/`: 실행 후 검증 기록

재실행은 기존 결과를 덮어쓰지 않고 새 `run_id`를 생성한다.

1차 연구 후 엔진을 수정할 때도 완료된 1차 연구 run은 불변으로 보존한다. 새 가설을 문서화한 뒤 별도 브랜치와 새 `run_id`에서 진행하며, 연구 설계가 바뀌면 새 study ID를 사용한다.

## 현재 실행 상태

- 공식 연구 실행: **미승인**
- 실제 공식 run ID: 없음
- 실제 manifest: 없음
- raw/aggregate 결과: 없음
- 한글 결과 보고서: 없음

사용자의 별도 명시 승인 전에는 공식 28,188 scenario 전투 batch를 실행하지 않는다.
