# Study 1 pre-execution archive — 2026-09-06

이 디렉터리는 공식 1연구 실행 직전 active 영역에서 제거한 역사 문서와 옛 실험 브랜치의 정확한 tree snapshot을 보존한다.

## 보존 문서

- `docs/CURRENT_RESEARCH_HANDOFF_2026-09-05.md`
- `docs/OPEN_MODEL_RISKS_2026-09-05.md`
- `docs/RELOAD_TIMING_AUDIT_2026-09-05.md`
- `research_results/RESEARCH_STATUS_2026-09-05.md`
- `research_results/WAVE_A_VERIFIED_CORE_DESIGN_DRAFT.md`
- `research_results/runs/README.md`
- `studies/01_exploratory/human/01_연구_설계_초안.md`

이 문서들은 현재 실행 설계의 canonical 문서가 아니다.

## 옛 브랜치 snapshot

### research/64point-secondary-epinel

```text
tip  = a6d67c2135f966f357bbd0f0ca9ce549fbfab90c
tree = 8bbe27f969b5fcaeaaf2ecc12693be67f4af0dec
```

현재 실행 branch와 갈라진 임시 Epinel secondary 64-point 연구 matrix다.

### tmp/distributed-samples

```text
tip  = 5b395e396d4f8d92d6f203d96ec179c194ff63f8
tree = 32d720653d24b9f8d27f72fe54f4a3dcb9f9c4a5
```

과거 distributed/추가 캐릭터 구현 실험 snapshot이다.

### tmp/rapi-b1-added-character-audit

```text
tip  = a23da41ce13d1ebcdae02416bd5bff8ed6f6c3e3
tree = 3e576e51a1a7180a65e2b459b1460750f16b949a
```

과거 Rapi B1 및 추가 캐릭터 audit iteration snapshot이다.

이 snapshot들은 역사·감사 목적으로만 보존하며 현재 `research/14-burst-baseline`에 병합하지 않는다.

## 실행 기준

- active 개발 branch: `research/14-burst-baseline`
- `main`: 수정/병합하지 않음
- 공식 28,188 scenario 전투 batch: 이 archive 생성 시점까지 미실행
- 현재 canonical 상태는 `docs/CURRENT_RESEARCH_HANDOFF_2026-09-06.md`와 `research_results/RESEARCH_STATUS_2026-09-06.md`를 따른다.
