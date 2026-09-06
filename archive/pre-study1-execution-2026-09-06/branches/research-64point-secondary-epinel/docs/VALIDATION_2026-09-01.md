# RAID14 regression validation (2026-09-01)

This note records the final verification pass after the practical 14-burst conversion.

## Result

```text
test modules  22
tests         209
passed        209 / 209
compileall    PASS
```

The full suite was executed module-by-module. Running all 209 tests in one process exceeds the execution limit of the chat runtime because several simulation-heavy modules are slow; split execution completed successfully.

## What was covered

- practical `RAID14_TIMELINE`: 14 cycles, 12.70 s B1-to-B1 interval
- c14 terminal Mast at Drunken 2 stacks
- c15 rejection in normal Crown/Mast policies
- Crown Burst refresh without double stacking
- Crown S1 Burst-caster-only caster-ATK targeting
- Mast Drunken stack growth, reset and Hangover
- Crown-vs-M1 opening comparison
- RAID14 opening influence convergence at 17.32 s
- independence of opening choice from later conventional/funnel comparison
- legacy 12-burst regression totals and break-even reference
- RAID14 conventional/funnel recalculation and local break-even
- character hooks, weapon state, ammo, reload, charge and delayed damage
- equipment, collection item, OL ATK/element/ammo and elemental advantage
- damage aggregation by character, source, category and burst cycle
- research scenario/report serialization and compatibility checks
- interface and sample/batch calculation paths

## Stale-test correction

One failure appeared during the first split run:

`tests/test_engine.py::test_opening_mast_crown_mast_only_changes_first_macro_cycle`

The engine policy had already been intentionally extended to the validated 14-cycle sequence, but the test still expected the old 12-cycle tuple. The expected policy was updated from:

```text
M,C,M / C,C,M / C,C,M / C,C,M
```

to:

```text
M,C,M / C,C,M / C,C,M / C,C,M / C,M2
```

After the expectation was corrected, the engine test module passed. No production engine logic change was needed for this failure.

## Interpretation

No unresolved functional regression was found in the RAID14 conversion. The remaining limitation is execution speed of the entire suite in one process, which is not a priority for this personal research engine.
