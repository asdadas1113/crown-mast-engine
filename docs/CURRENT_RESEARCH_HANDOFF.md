# 최신 연구 인수인계

새 AI가 가장 먼저 읽을 운영 프로토콜:

```text
docs/AI_HANDOFF_PROTOCOL.md
```

현재 canonical 인계문서:

```text
docs/CURRENT_RESEARCH_HANDOFF_2026-09-07.md
```

현재 canonical 1연구 설계:

```text
research_results/studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
```

현재 연구 상태:

- 작업 branch: `research/14-burst-baseline`
- 1연구 설계 동결
- actor model gate: **0개**
- `execution_ready=true`
- 상태: `design-frozen-execution-unapproved`
- 검증된 engine commit: `801cab5fa3b0d64150ea0ebd9558acce6bce47ba`
- focused **19/19** / full regression **327/327**
- case-generation preflight **28,188/28,188**
- 공식 28,188 scenario 전투 batch: **미실행**
- study ID: `crown-mast-study-01-exploratory-v1`

결과 저장 위치는 1연구 디렉터리 안으로 고정한다.

```text
research_results/studies/01_exploratory/
├─ machine/runs/<run_id>/     기계용 scenario/raw/aggregate/provenance/manifest
├─ human/reports/<run_id>/    사람이 읽는 한글 결과·해석 보고서
└─ validation/                실행 전후 검증 기록
```

`execution_ready=true`는 기술적 준비 완료를 뜻할 뿐 공식 실행 승인을 뜻하지 않는다. 사용자 명시 승인 전에는 28,188개 전투 시뮬레이션을 실행하지 않는다.

과거/폐기 문서와 브랜치 snapshot은 `archive/` 아래에만 보존한다. `main`은 사용자 명시 지시 없이 수정하거나 병합하지 않는다.

1차 연구 이후의 코드 변경은 기존 run을 덮어쓰지 않는다. 새 가설을 먼저 문서화하고 새 브랜치·새 run ID에서 진행하며, 연구 설계가 달라지면 새 study ID를 사용한다.
