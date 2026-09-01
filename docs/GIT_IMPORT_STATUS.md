# Repository status

> 이 파일은 과거 `nikke-calc` 이관 시도 기록에서 시작했으며, 아래 내용은 2026-09-01 현재 상태로 갱신했다.

## Current canonical repository

- Repository: `asdadas1113/crown-mast-engine`
- Default branch: `main`
- Active validated research branch: `research/14-burst-baseline`
- Old `asdadas1113/nikke-calc` import target is no longer authoritative.
- The standalone `crown-mast-engine` repository is the canonical source.

## Current RAID14 state

- practical raid baseline: 180 s / 14 bursts / 12.70 s B1-to-B1 interval
- c14 terminal B2: Mast at Drunken 2 stacks
- c15: excluded from normal policy; exceptional runs require an explicit custom rotation
- first B2 Crown-vs-Mast influence is evaluated until active buff states converge, not only until the first Full Burst ends
- RAID14 opening convergence in the current timing model: 17.32 s elapsed
- legacy `STANDARD_TIMELINE` remains 12 bursts strictly for regression/reproduction of the v6 research record

## Verification

On 2026-09-01, the test suite was executed module-by-module because a single all-suite run exceeds the chat runtime limit.

- 22 test modules
- 209 tests
- 209 / 209 passed in split execution
- Python `compileall` passed
- one stale 12-cycle expectation in `tests/test_engine.py` was updated to the validated 14-cycle opening-Mast policy

The single combined run is computationally slow for this environment; this is treated as a performance characteristic, not an unresolved functional failure. The engine is intended for personal research, so no performance optimization is currently required.

## Relevant current notes

- `RAID14_BASELINE_2026-09-01.md`: timing measurement and terminal Mast rule
- `RAID14_RECALC_2026-09-01.md`: first 14-burst recalculation and legacy comparison
- `RAID14_OPENER_B3_SPOTCHECK_2026-09-01.md`: opener counterexamples by B3
- `VALIDATION_2026-09-01.md`: regression verification record
- `RESEARCH_HANDOFF_V6.md`: current pointer for the archived v6 master note
- `RESEARCH_HANDOFF_V6_LEGACY_FULL.md`: preserved full legacy 12-burst master note
