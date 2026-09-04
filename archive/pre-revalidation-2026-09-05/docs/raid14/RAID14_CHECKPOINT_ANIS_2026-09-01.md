# RAID14 12-point checkpoint study — Anis: Star B1 (2026-09-01)

This note repeats the corrected RAID14 checkpoint study with B1 changed from Liter to Anis: Star.

## Controlled setup

- timeline: `RAID14_TIMELINE`
- battle duration: 180 s
- B1: Anis: Star
- B2: Crown + Mast: Romantic Maid
- secondary B3: Helm (Favorite Item)
- boss DEF: 140
- boss element: none
- core hit rate: 0%
- range bonus: 0%
- Crown/Mast: OL5 bare + SR15
- B1 checkpoints: Low / Standard / High
- dealer checkpoints: 4 profiles
- total per main B3: 12 points
- openers checked separately: Crown opener and M1 Mast opener

Main B3 set:

- Rapi: Red Hood
- Scarlet: Black Shadow
- Snow White: Heavy Arms
- Epinel — intentionally low-DPS extreme comparison case

## Crown-opener results

| Main B3 | Outcome | Funnel change range | Main share range | Local break-even range |
|---|---|---:|---:|---:|
| Rapi: Red Hood | Conventional 12/12 | -1.6482% to -1.2843% | 31.65% to 37.64% | 56.31% to 67.43% |
| Scarlet: Black Shadow | Conventional 12/12 | -1.6980% to -1.4553% | 37.82% to 44.32% | 72.93% to 77.45% |
| Snow White: Heavy Arms | Conventional 12/12 | -1.8533% to -1.5710% | 37.19% to 43.71% | 77.83% to 81.16% |
| Epinel | Conventional 12/12 | -3.3227% to -2.8373% | 10.90% to 14.35% | unavailable in all 12 |

### Main gain `g` and other-four loss `l`

| Main B3 | Main `g` range | Other-four `l` range |
|---|---:|---:|
| Rapi: Red Hood | +1.789% to +2.493% | 3.199% to 3.740% |
| Scarlet: Black Shadow | +1.069% to +1.199% | 3.199% to 3.740% |
| Snow White: Heavy Arms | +0.862% to +0.918% | 3.199% to 3.740% |
| Epinel | -0.405% to -0.274% | 3.199% to 3.740% |

Epinel is `conventional_dominates` in all 12 points: the nominated Main itself loses damage under funneling, while the other four also lose damage. Therefore no finite scaling break-even exists. This is an extreme/sanity-check result, not a practical main-carry threshold.

## M1-opener results

| Main B3 | Outcome | Funnel change range | Main share range | Local break-even range |
|---|---|---:|---:|---:|
| Rapi: Red Hood | Conventional 12/12 | -1.6416% to -1.2802% | 31.68% to 37.66% | 56.34% to 67.50% |
| Scarlet: Black Shadow | Conventional 12/12 | -1.6942% to -1.4524% | 37.78% to 44.26% | 72.90% to 77.46% |
| Snow White: Heavy Arms | Conventional 12/12 | -1.8450% to -1.5641% | 37.28% to 43.80% | 77.91% to 81.22% |
| Epinel | Conventional 12/12 | -3.3124% to -2.8289% | 10.91% to 14.35% | unavailable in all 12 |

As in the Liter sweep, opener choice has little effect on the long-horizon Conventional-vs-Funnel conclusion in these tested regions.

## Comparison with the Liter sweep

The Liter reference sweep used the same B2/B3/boss/checkpoint structure.

Representative Crown-opener ranges:

| Main B3 | Liter Main share | Anis Main share | Liter break-even | Anis break-even |
|---|---:|---:|---:|---:|
| Rapi: Red Hood | 39.45–44.01% | 31.65–37.64% | 60.34–63.92% | 56.31–67.43% |
| Scarlet: Black Shadow | 45.34–50.13% | 37.82–44.32% | 81.45–84.87% | 72.93–77.45% |
| Snow White: Heavy Arms | 45.64–50.19% | 37.19–43.71% | 79.26–82.89% | 77.83–81.16% |
| Epinel | 14.77–17.99% | 10.90–14.35% | mostly none / ~99.62% extreme | none in all 12 |

Anis: Star contributes substantial controlled damage of her own through her RL, full-charge skill damage and Shooting Star while also supplying Full Burst buffs. Consequently the nominated Main occupies a smaller fraction of team damage than in the Liter cases. The local break-even is not determined by share alone: changing B1 also changes the Main response `g` and the other-four loss `l`.

The clearest example is Rapi. With Liter, `g` was about +2.57% to +2.79% and `l` about 4.25% to 4.56%. With Anis, `g` becomes about +1.79% to +2.49% and `l` about 3.20% to 3.74%. The resulting break-even range becomes wider rather than moving by a single constant amount.

## Interpretation

Across all four main B3s and both opener choices, this 96-comparison sweep contains no sustained-funnel win. This does not prove Conventional is universal; it shows that the tested 12-point regions remain below their local break-even or, for Epinel, have no finite break-even at all.

The B1 comparison reinforces the intended research interpretation:

- Main damage share is a useful display coordinate, not a universal causal threshold.
- The local threshold is jointly determined by the Main gain `g` and the other-four loss `l`.
- Changing B1 can move all three: actual Main share, `g`, and `l`.
- Epinel remains an extreme low-benefit control and should not be read as a practical carry recommendation.
