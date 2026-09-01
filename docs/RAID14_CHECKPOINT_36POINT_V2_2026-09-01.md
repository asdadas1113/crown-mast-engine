# RAID14 36-point checkpoint v2 — 2026-09-01

## Purpose

The legacy 12-point checkpoint was useful as a first controlled sweep, but its dealer axis was not fully orthogonal. For example, `Main O5 ATK3` appeared only with `Secondary B5`, while `Main O5 Ammo2` appeared only with `Secondary O5`. That means a main-build change and a secondary-build change could be bundled into the same checkpoint.

`raid14-36point-v2` keeps those dimensions independent and fully crosses them. The legacy 12-point route is preserved as a regression/reference path.

## Grid definition

### B1 development — 4 levels

| ID | Gear | OL options | Collection |
|---|---|---|---|
| `b1-low` | Base5 | none | none* |
| `b1-developing` | OL0 | none | SR15 |
| `b1-standard` | OL5 | none | SR15 |
| `b1-high` | OL5 | ATK4 / Element4 / Ammo3 | SR15 |

\* Favorite-item B1 actors keep SR15 because the favorite-item mechanics require it.

On the current neutral-boss study, the B1 High element lines do not contribute damage; they remain part of the general build definition for later elemental studies.

### Main B3 — 3 independent profiles

All use OL5 gear + SR15.

- `main-o5-bare`: no OL options
- `main-o5-atk3`: ATK3 only
- `main-o5-ammo2`: Ammo2 only

ATK3 and Ammo2 are never combined.

### Secondary B3 — 3 independent profiles

All use SR15 and no OL options.

- `secondary-o5`: OL5
- `secondary-o0`: OL0
- `secondary-b5`: Base5

### Fixed B2 builds

Crown and Mast are fixed at OL5 bare + SR15.

### Total

`4 B1 × 3 Main × 3 Secondary = 36 points`

Every case explicitly uses `RAID14_TIMELINE`.

## Validation

`tests/test_checkpoints_v2.py` passes on GitHub Actions and verifies:

- exactly 36 unique combinations
- full 4 × 3 × 3 crossing
- RAID14 timeline on every case
- fixed Crown/Mast builds
- ATK3 and Ammo2 remain independent
- Secondary O5/O0/B5 axis has no OL-option contamination
- B1 progression is distinct
- opening baseline selection is preserved
- favorite-item B1 keeps SR15

The existing sample-batch multiprocessing regression tests also remain 9/9 PASS.

## Crown-entry 36-point study

Conditions:

- DEF 140
- neutral boss
- Core 0%
- Range bonus 0%
- Secondary B3: Helm FI
- Crown entry
- four Main B3 candidates
- B1: Liter and Anis: Star

All percentages below are relative values × 100.

### Liter

| Main B3 | Funnel change | Main share | Break-even | g | l | Outcome |
|---|---:|---:|---:|---:|---:|---|
| Rapi: Red Hood | -1.5754 ~ -1.2388% | 39.45 ~ 44.48% | 60.34 ~ 63.92% | +2.57 ~ +2.79% | 4.25 ~ 4.56% | 36/36 conventional |
| Scarlet: Black Shadow | -1.9567 ~ -1.7732% | 45.34 ~ 50.13% | 81.45 ~ 85.01% | +0.80 ~ +0.97% | 4.25 ~ 4.56% | 36/36 conventional |
| Snow White: Heavy Arms | -1.9208 ~ -1.7383% | 45.64 ~ 50.19% | 79.26 ~ 82.89% | +0.94 ~ +1.11% | 4.25 ~ 4.56% | 36/36 conventional |
| Epinel | -3.8441 ~ -3.5288% | 14.77 ~ 17.99% | ~99.61 ~ 99.64% where finite | -0.089 ~ +0.016% | 4.25 ~ 4.56% | 36/36 conventional; 24 dominate |

Epinel breakdown:

- `conventional_dominates`: 24/36
- formal `standard_break_even`: 12/36
- all 36 are clear conventional by observed damage

### Anis: Star

| Main B3 | Funnel change | Main share | Break-even | g | l | Outcome |
|---|---:|---:|---:|---:|---:|---|
| Rapi: Red Hood | -1.6482 ~ -1.2843% | 31.65 ~ 37.84% | 56.31 ~ 67.57% | +1.79 ~ +2.49% | 3.20 ~ 3.74% | 36/36 conventional |
| Scarlet: Black Shadow | -1.6980 ~ -1.4553% | 37.82 ~ 44.32% | 72.93 ~ 77.56% | +1.07 ~ +1.20% | 3.20 ~ 3.74% | 36/36 conventional |
| Snow White: Heavy Arms | -1.8533 ~ -1.5710% | 37.19 ~ 43.71% | 77.83 ~ 81.16% | +0.86 ~ +0.92% | 3.20 ~ 3.74% | 36/36 conventional |
| Epinel | -3.3268 ~ -2.8294% | 10.90 ~ 14.35% | none | -0.405 ~ -0.274% | 3.20 ~ 3.74% | 36/36 conventional_dominates |

## Crown-entry interpretation

Across `2 B1 × 4 Main × 36 points = 288` controlled Crown-entry comparisons, sustained funnel wins **0/288**.

The important result of v2 is not a dramatic widening of the numerical ranges. Most extrema closely reproduce the legacy 12-point study. Instead, v2 removes dealer-axis confounding and shows that the same conclusion survives a fully crossed Main/Secondary design.

There are small extensions that demonstrate the added combinations are not perfectly redundant:

- Liter + SBS break-even upper edge moves from about 84.87% to about 85.01%.
- Anis + SBS upper edge moves from about 77.45% to about 77.56%.
- Anis + Rapi upper edge moves from about 67.43% to about 67.57%.
- Rapi also finds a slightly less-negative Liter funnel extreme (`-1.2388%`) than the old 12-point grid (`-1.2550%`).

So the 36-point grid gives more defensible coverage while preserving the original direction of the result.

## Pending in this checkpoint

- Mast-entry 36-point study is run separately because first-B2 entry choice is an independent variable.
- 36-point serial vs multiprocessing benchmark is recorded after the verification runner finishes.
- The legacy web checkpoint route is not replaced until the v2 study is accepted.
