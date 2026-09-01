# RAID14 realistic 64-point checkpoint v3 — 2026-09-01

## Purpose

This checkpoint is designed for the original Crown/Mast research question: across growth states that can plausibly occur on a real account, is sustained funnel operation meaningfully worth using, or is conventional Crown-Crown-Mast the lower-expected-loss default?

It is intentionally not an OL-option attribution study. ATK, elemental damage, ammo, collection, and gear growth are bundled into realistic progression states rather than isolated as separate causal axes. The existing 36-point v2 grid remains available if a specific boundary later needs decomposition.

## Fixed research conditions

- Timeline: RAID14, 180 s / 14 bursts.
- Baseline opener: `opening_mast_crown_mast` (M1 opener), fixed for this study.
- Compared sustained policies: conventional Crown-Crown-Mast versus sustained funnel.
- Crown and Mast: OL5 / SR15 / no OL options, fixed.
- Secondary B3: Helm.
- Boss DEF: 140.
- Core hit rate: 0%.
- Range bonus: 0%.
- Boss mechanics such as invulnerability, jumps, forced cover, and part-exposure losses remain outside the base model.

Each B1, Main B3, and Secondary B3 axis uses the same four growth states:

1. `g1-base5-none`: Base5 / no collection / no OL options.
2. `g2-ol0-sr5`: OL0 / SR5 / no OL options.
3. `g3-ol0-sr15-e3-a3`: OL0 / SR15 / Element3 / ATK3.
4. `g4-ol5-sr15-e4-a4-ammo3`: OL5 / SR15 / Element4 / ATK4 / Ammo3.

This gives `4 × 4 × 4 = 64` growth points per roster and boss condition.

### Favorite-item actor handling

Helm is modeled by the engine with her favorite-item kit. Therefore pre-favorite collection states are not physically consistent with that character definition. For actors in `FAVORITE_ITEM_ACTORS`, the checkpoint keeps the requested gear and OL-option progression but forces collection to SR15. For the current study this means Helm is SR15 in all four Secondary growth states while Base5/OL0/OL5 and OL-option differences still vary.

## Boss conditions

Every 64-point grid is run twice:

- `neutral`: no boss element.
- `main-advantage`: boss element is selected so the Main B3 naturally has elemental advantage.

Elemental advantage is not artificially restricted to the Main B3. If another roster member naturally shares the advantageous element, that unit also receives the normal benefit. This is deliberate: v3 is intended to cover plausible roster states rather than isolate a Main-only elemental coefficient.

Main-advantage boss elements in this roster set:

- Rapi: Red Hood → Wind boss.
- Scarlet: Black Shadow → Iron boss.
- Snow White: Heavy Arms → Fire boss.
- Epinel → Iron boss.

## Study size

- B1: Liter, Anis: Star = 2.
- Main B3: Rapi: Red Hood, Scarlet: Black Shadow, Snow White: Heavy Arms, Epinel = 4.
- Boss condition: neutral, Main advantage = 2.
- Growth points per condition = 64.

Total controlled comparisons:

`2 × 4 × 2 × 64 = 1,024`.

## Result

**Sustained funnel wins: 0 / 1,024.**

Outcome bands:

- clear conventional: 978 / 1,024.
- marginal conventional: 46 / 1,024.
- tie: 0 / 1,024.
- marginal or clear funnel: 0 / 1,024.

All 46 marginal-conventional cases occur in the Rapi: Red Hood Main-advantage condition. Every neutral case and every SBS/SWHA/Epinel case is clear-conventional.

The equal-weight mean relative change across all 1,024 grid points is approximately **-1.9619%** for sustained funnel versus conventional. This average is a grid summary, not an estimate of real-world roster frequency.

### Per-roster summary

Negative relative change means sustained funnel dealt less total damage than conventional Crown-Crown-Mast.

| B1 | Main B3 | Neutral avg | Neutral range | Main-adv avg | Main-adv range | Funnel wins |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Liter | Rapi: Red Hood | -1.5968% | -1.8654% to -1.3088% | -1.0087% | -1.7157% to -0.3624% | 0 / 128 |
| Anis: Star | Rapi: Red Hood | -1.5112% | -1.8397% to -1.2111% | -1.0178% | -1.7237% to -0.3757% | 0 / 128 |
| Liter | Scarlet: Black Shadow | -1.8884% | -2.0517% to -1.6732% | -1.4278% | -1.9255% to -0.8906% | 0 / 128 |
| Anis: Star | Scarlet: Black Shadow | -1.6000% | -1.7811% to -1.3768% | -1.1914% | -1.6709% to -0.6870% | 0 / 128 |
| Liter | Snow White: Heavy Arms | -1.8457% | -2.0255% to -1.6006% | -1.9129% | -2.8710% to -0.9012% | 0 / 128 |
| Anis: Star | Snow White: Heavy Arms | -1.7108% | -1.9077% to -1.4548% | -1.8113% | -2.7560% to -0.8688% | 0 / 128 |
| Liter | Epinel | -3.6105% | -3.9301% to -3.1818% | -3.3481% | -3.8770% to -2.7221% | 0 / 128 |
| Anis: Star | Epinel | -3.0378% | -3.3632% to -2.6122% | -2.8720% | -3.3309% to -2.3231% | 0 / 128 |

## Closest observed approach to break-even

The most funnel-favorable point in the entire 1,024-comparison study is:

- B1: Liter.
- Main B3: Rapi: Red Hood.
- Boss: Main advantage (Wind).
- B1 growth: `g4-ol5-sr15-e4-a4-ammo3`.
- Main growth: `g3-ol0-sr15-e3-a3`.
- Secondary growth: `g4-ol5-sr15-e4-a4-ammo3`.
- Conventional Main share: 52.8210%.
- Calculated break-even Main share: 58.3966%.
- Main gain term `g`: +2.7039%.
- Other-four loss term `l`: 3.7953%.
- Sustained-funnel relative change: **-0.3624%**.

Thus even the closest tested point remains on the conventional side of break-even. It is classified as marginal conventional, not a tie or funnel win.

For Anis: Star + Rapi: Red Hood under Main advantage, the closest point is -0.3757%, also marginal conventional.

## Interpretation

Within this deliberately broad but still plausible growth envelope, changing B1/Main/Secondary relative investment and giving the Main dealer a natural elemental-advantage environment did not produce a single sustained-funnel win.

This supports the operational claim more directly than an OL-option attribution study would: for the tested roster family, conventional Crown-Crown-Mast is a robust default with low expected regret, while sustained funnel requires conditions more extreme than those reached by this 64-point realistic-growth grid.

The result does **not** prove that no NIKKE composition or boss pattern can ever favor funnel operation. Character-specific mechanics, different roster members, or external boss timing can still create exceptions. Those should be treated as exception studies rather than reasons to use funnel as the general default.

## Role of the other checkpoint grids

- v3 64-point realistic grid: primary broad robustness study for plausible account growth states.
- v2 36-point orthogonal grid: retain for diagnosis if an unexpected boundary or character-specific anomaly needs causal decomposition.
- legacy 12-point grid: retain for regression and existing compatibility.
