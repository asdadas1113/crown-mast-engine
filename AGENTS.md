# Repository Agent Instructions

- 활성 연구 시간축은 `RAID14_TIMELINE` 하나이며 모든 신규 분석·연구·테스트·코드는 180초·14버스트를 사용한다.
- 요청이 모호하거나 시간축이 지정되지 않았으면 반드시 `RAID14_TIMELINE`을 사용한다.
- `LEGACY_12_BURST_TIMELINE`은 폐기된 결과의 역사적 재현 전용이다.
- 사용자가 현재 요청에서 12버스트 재현을 명시적으로 지시하지 않는 한 `LEGACY_12_BURST_TIMELINE`을 절대 사용하지 않는다.
- `archive/` 아래의 코드·문서·브랜치 snapshot은 활성 구현이나 신규 작업의 기준으로 사용하지 않는다.
- 공식 전투 batch는 사용자의 명시적 승인 없이 실행하지 않는다.
