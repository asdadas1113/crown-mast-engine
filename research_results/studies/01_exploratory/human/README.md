# 1연구 사람용 문서

이 디렉터리는 1연구를 사람이 읽고 검토하기 위한 문서와 실행 후 보고서를 저장한다.

## 현재 canonical 문서

```text
02_연구_실행_재현성_및_기록_규격.md
03_1연구_실행_설계_확정본.md
```

`01_연구_설계_초안.md`은 설계 확정 이전 문서이므로 active 영역에서 제외하고 pre-execution archive에 보존한다.

현재 설계:

```text
87 valid rosters
27 growth points
12 environments
28,188 scenarios
execution model gates = 0
execution_ready = true
status = design-frozen-execution-unapproved
```

## 실행 후 보고서 저장 구조

공식 실행마다 `run_id`를 하나 만들고 사람용 보고서는 다음에 저장한다.

```text
reports/<run_id>/
├─ 00_전체_요약.md
├─ 01_세컨더리_기준점_분석.md
├─ 02_메인_B3_분석.md
├─ 03_B1_분석.md
├─ 04_효과크기_분석.md
├─ 05_역전_구조_분석.md
├─ 06_성장_및_환경_민감도.md
├─ 07_해석과_한계.md
├─ 08_후속_연구_후보.md
└─ cases/
```

각 보고서는 같은 `run_id`의 `machine/runs/<run_id>/manifest.json`, aggregate, validation 기록을 근거로 작성한다.

## 작성 원칙

- 제목과 본문은 한글을 기본으로 한다.
- 관측 결과와 해석을 분리한다.
- 1연구의 통제 범위를 넘어선 일반화를 피한다.
- 과거 archive 결과를 새 결과처럼 사용하지 않는다.
- 특이 결과는 후속 연구 후보로 남기되 별도 검증 전 기전을 확정하지 않는다.
- 재실행 결과는 기존 보고서를 덮어쓰지 않고 새 `run_id` 아래에 작성한다.

사용자 명시 승인 전에는 결과 보고서를 만들지 않으며 공식 28,188 scenario 전투 batch도 실행하지 않는다.
