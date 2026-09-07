# Repository Agent Instructions

- 새 AI는 작업을 시작하기 전에 `docs/CURRENT_RESEARCH_HANDOFF.md`와 `docs/AI_HANDOFF_PROTOCOL.md`를 읽고 현재 branch·HEAD·연구 상태를 확인한다.
- 활성 연구 시간축은 `RAID14_TIMELINE` 하나이며 모든 신규 분석·연구·테스트·코드는 180초·14버스트를 사용한다.
- 요청이 모호하거나 시간축이 지정되지 않았으면 반드시 `RAID14_TIMELINE`을 사용한다.
- `LEGACY_12_BURST_TIMELINE`은 폐기된 결과의 역사적 재현 전용이다.
- 사용자가 현재 요청에서 12버스트 재현을 명시적으로 지시하지 않는 한 `LEGACY_12_BURST_TIMELINE`을 절대 사용하지 않는다.
- `archive/` 아래의 코드·문서·브랜치 snapshot은 활성 구현이나 신규 작업의 기준으로 사용하지 않는다.
- 현재 공식 1연구 정의는 `crown_mast_engine/wave_a_study.py`의 `crown-mast-study-01-exploratory-v1`(87 roster × 324 = 28,188 scenario) 하나뿐이다.
- 과거 `crown-mast-secondary-opportunity-v1` 29,952 scenario 설계는 폐기된 역사 자료이며 신규 연구·manifest·결과 writer에 사용하지 않는다.
- 공식 전투 batch는 사용자의 명시적 승인 없이 실행하지 않는다.
- 공식 run이 시작되면 manifest의 commit SHA·catalog·schema와 다른 코드로 기존 run을 실행하거나 재개하지 않는다.
- 1차 연구 후 코드 변경은 기존 run과 결과를 덮어쓰지 않고 새 브랜치·새 run ID에서 진행한다. 연구 설계가 바뀌면 새 study ID를 사용한다.
