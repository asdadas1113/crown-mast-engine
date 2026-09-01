# RAID14 sample-batch multiprocessing verification — 2026-09-01

## Scope

The goal is not to parallelize combat internals. Independent `SampleCase` executions are parallelized so larger controlled checkpoint grids can be evaluated without changing research semantics.

## Implementation

`run_sample_batch(cases, *, workers=None)` now supports process-based case parallelism.

- `workers=1`: serial fallback using the previous execution path.
- `workers=None`: uses `min(os.cpu_count(), case_count)` workers.
- Parallel execution uses `ProcessPoolExecutor` with an explicit `spawn` multiprocessing context.
- `SampleCase` objects are not sent across the process boundary.
- Each parent-side scenario is converted with `ResearchScenario.to_dict()` to plain pickle-safe data.
- Workers reconstruct `ResearchScenario`, run `run_research_scenario()`, and return a plain report payload.
- Parent process reconstructs the existing report/result objects.
- `executor.map()` preserves input case order.
- Existing mechanics-signature and baseline-rotation compatibility validation is still applied after results are assembled.

## Targeted regression verification

GitHub Actions runner:

- Ubuntu 24.04
- CPython 3.11.16
- 4 logical CPUs reported by `os.cpu_count()`

`tests/test_samples.py`:

- 9 tests
- 9/9 PASS
- runtime: about 3.0 seconds

Covered explicitly:

1. serial and parallel batch payloads are exactly equal
2. serialized JSON is exactly equal
3. `workers=1` does not construct a process pool
4. default workers use a `spawn` process pool
5. output order matches input order
6. worker exceptions propagate to the caller
7. invalid worker counts are rejected
8. duplicate case ids still fail before execution
9. mixed baseline rotations are still rejected

`compileall` also passed.

## RAID14 12-point benchmark

Checkpoint set:

- B1: Liter
- Main B3: Rapi: Red Hood
- Secondary B3: Helm
- current RAID14 checkpoint definitions
- 12 cases total

Measured on the same 4-CPU GitHub runner:

- serial (`workers=1`): `55.495113 s`
- parallel (`workers=None`, effective workers=4): `24.742627 s`
- speedup: `2.2429x`
- serial/parallel result payloads: exactly identical

This is enough improvement to justify keeping case-level multiprocessing before expanding the checkpoint grid to 24/32/48+ cases.

## Full-suite diagnostic note

A one-off full `unittest discover` run executed 214 tests and reported 6 failures. These were not failures of the multiprocessing path:

- `test_samples.py` passed completely in the same job.
- Four failures were hard-coded billion-scale damage expectations differing only by approximately `1e-4` to `1e-8` absolute on the Linux runner, i.e. platform-level floating-point tolerance issues in old assertions.
- One first-entry conservation assertion differed by about `2.4e-6` absolute for the same reason.
- One interface assertion still expected the old first-entry convergence value `20.1`; the current RAID14 interface correctly returns `17.32`.

Those stale/tolerance-sensitive assertions are separate regression-test maintenance work and were not changed as part of the batch-parallelization task.

## Checkpoint-v2 follow-up

The next controlled grid is implemented separately from the legacy 12-point web checkpoint route as `raid14-36point-v2`. It uses a fully crossed design:

- B1 development: 4 levels
- Main build: 3 levels (`O5 bare`, `O5 ATK3`, `O5 Ammo2`)
- Secondary gear: 3 levels (`O5`, `O0`, `B5`)
- total: 36 points

The legacy 12-point interface remains available as a regression/reference path until the v2 grid is measured and accepted.

## Conclusion

Case-level multiprocessing is validated for the intended research batch path. The next research step is validating the 36-point checkpoint-v2 grid and then using it for broader Crown/Mast studies rather than deeper engine-internal optimization.
