# Crown–Mast 1연구 상태 — 2026-09-06

## 현재 판정

```text
study_id = crown-mast-study-01-exploratory-v1
status = design-frozen-execution-unapproved
execution_ready = true
execution model gates = 0
official combat batch = not executed
```

현재 1연구 설계는 동결됐고 모델·회귀·case generator의 실행 전 gate는 모두 닫혔다. 사용자 명시 승인 전에는 공식 28,188 scenario 전투 batch를 실행하지 않는다.

## 동결 표본

- 87 valid rosters
- B1/Main/Secondary 성장 3×3×3 = 27 growth points
- DEF 3 × core 2 × Main advantage 2 = 12 environments
- roster당 324 scenarios
- 전체 28,188 scenarios
- RAID14 timeline
- Crown/Mast OL5 + SR15 대표 build 고정

## 최종 preflight

```text
GitHub Actions run: 34002759044
job: 101404457366
head: f60f4cefbc3d48275f5bc33147e7d2d5c3b19674
Python: 3.12.14
result: success
```

- focused: 68/68
- full regression: 322/322
- no-simulation case generation: 28,188/28,188
- model gates: 0
- simulation executed: no

상세 검증은 다음을 따른다.

```text
studies/01_exploratory/validation/05_최종_실행전_검증_2026-09-06.md
```

## 공식 결과 저장 위치

공식 실행 승인 후 하나의 `run_id`를 생성하고 해당 run의 기계 자료와 사람용 보고서를 같은 ID로 연결한다.

```text
studies/01_exploratory/
├─ machine/runs/<run_id>/
│  ├─ manifest.json
│  ├─ scenarios/
│  ├─ raw/
│  ├─ aggregate/
│  └─ provenance/
├─ human/reports/<run_id>/
└─ validation/runs/<run_id>/
```

재실행은 기존 run을 덮어쓰지 않고 새 `run_id`를 사용한다.

## 실행 승인 후 순서

1. 실행 commit SHA 동결
2. `run_id` 생성
3. manifest 완성
4. run별 저장 디렉터리 생성
5. 공식 28,188 scenario 전투 실행
6. raw 완전성 및 checksum 검증
7. aggregate 생성
8. 한글 결과 보고서 작성
9. 실행 후 validation 기록 고정

현재는 4단계 이전 상태이며 공식 run ID와 실제 결과 파일은 없다.
