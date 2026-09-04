# RAID14 12-point checkpoint study (2026-09-01)

This note records a controlled first pass using the existing 3 x 4 checkpoint design after routing the checkpoint calculation through the practical RAID14 timeline.

## Controlled setup

- timeline: `RAID14_TIMELINE`
- battle duration: 180 s
- B1: Liter
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

The main B3 set is intentionally small rather than exhaustive:

- Rapi: Red Hood
- Scarlet: Black Shadow
- Snow White: Heavy Arms
- Epinel

Epinel is included as an intentionally low-DPS extreme comparison case. Its result should not be interpreted as a practical main-carry recommendation.

## Crown-opener 12-point results

| Main B3 | Outcome | Funnel change range | Main share range | Local break-even range |
|---|---|---:|---:|---:|
| Rapi: Red Hood | Conventional 12/12 | -1.5754% to -1.2550% | 39.45% to 44.01% | 60.34% to 63.92% |
| Scarlet: Black Shadow | Conventional 12/12 | -1.9567% to -1.7732% | 45.34% to 50.13% | 81.45% to 84.87% |
| Snow White: Heavy Arms | Conventional 12/12 | -1.9208% to -1.7384% | 45.64% to 50.19% | 79.26% to 82.89% |
| Epinel | Conventional 12/12 | -3.8361% to -3.5495% | 14.77% to 17.99% | mostly unavailable; 99.62% where finite |

### Rapi

- average funnel change: -1.4453%
- average conventional Main share: 41.8429%
- average local break-even Main share: 62.2198%
- `g` (Main gain under funnel): about +2.57% to +2.79%
- `l` (other-four loss under funnel): about 4.25% to 4.56%

The 12 observed shares remain roughly 18-22 percentage points below their local break-even shares, so this checkpoint region is not close to a rotation flip.

### Scarlet: Black Shadow

- average funnel change: -1.8954%
- average conventional Main share: 47.3652%
- average local break-even Main share: 83.0168%
- `g`: about +0.80% to +0.97%
- `l`: about 4.25% to 4.56%

### Snow White: Heavy Arms

- average funnel change: -1.8477%
- average conventional Main share: 47.3265%
- average local break-even Main share: 81.3999%
- `g`: about +0.94% to +1.11%
- `l`: about 4.25% to 4.56%

### Epinel: extreme interpretation

Epinel is deliberately not treated like the three normal main-DPS cases.

- average funnel change: -3.7177%
- Main share: only about 14.77% to 17.99%
- Main `g` is approximately zero or slightly negative (-0.089% to +0.016%)
- in 9 of 12 cases the comparison is `conventional_dominates`, so there is no finite scaling break-even
- only the three ATK3-vs-Base5 cases have a tiny positive `g`, producing a formal break-even around 99.62%

The ~99.62% number is not a realistic practical threshold. It is the expected extreme behavior of the local scaling diagnostic when funneling gives the nominated Main almost no benefit while the other four still lose damage. This makes Epinel useful as a sanity check for the analysis machinery.

## Structural observation

The other-four loss `l` is essentially unchanged across the four main-B3 identities because those four members and their controlled conditions are unchanged: roughly 4.25% to 4.56%.

The large threshold movement therefore comes mainly from the main B3's own funnel response `g`:

```text
Rapi             ~ +2.6 to +2.8%   -> break-even ~60-64%
Scarlet BS       ~ +0.8 to +1.0%   -> break-even ~81-85%
Snow White HA    ~ +0.94 to +1.11% -> break-even ~79-83%
Epinel           ~ 0 or negative   -> no finite BE / ~99.6% extreme
```

Thus Main damage share is a useful coordinate for displaying a break-even, but it is not a universal causal constant. The local threshold depends on both the Main gain `g` and the rest-of-team loss `l`.

## M1-opener robustness check

After pairing M1 conventional with the matching M1 sustained-funnel policy, the 12-point result remains Conventional 12/12 for every tested main B3.

| Main B3 | M1 funnel change range | M1 Main share range | M1 break-even range |
|---|---:|---:|---:|
| Rapi: Red Hood | -1.5730% to -1.2524% | 39.51% to 44.06% | 60.43% to 63.97% |
| Scarlet: Black Shadow | -1.9556% to -1.7742% | 45.31% to 50.07% | 81.43% to 84.87% |
| Snow White: Heavy Arms | -1.9145% to -1.7329% | 45.79% to 50.33% | 79.35% to 82.96% |
| Epinel | -3.8335% to -3.5480% | 14.78% to 17.99% | mostly unavailable; ~99.62% where finite |

The opener can materially change first-cycle damage and can even reverse by B3, but it barely changes the long-horizon Conventional-vs-Funnel checkpoint conclusion in these tested regions.

## Tooling audit discovered during this run

Two legacy routing issues were found while exercising the checkpoint tool:

1. the interface/checkpoint constructor still inherited the legacy 12-burst `ResearchScenario` timeline instead of explicitly selecting `RAID14_TIMELINE`;
2. an M1 checkpoint baseline was paired against Crown-open sustained funnel by the generic analysis path, making that batch comparison asymmetric.

The corrected local research path explicitly uses RAID14 and pairs:

- Crown conventional -> Crown sustained funnel
- M1 conventional -> M1 sustained funnel

Targeted interface/analysis regression tests and `compileall` passed after these corrections. These newly added targeted checks are separate from the earlier 209/209 pre-audit split-suite validation record.
