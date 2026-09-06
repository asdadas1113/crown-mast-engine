# RAID14 opener B3 spot-check (2026-09-01)

This is a follow-up to `RAID14_RECALC_2026-09-01.md`.
It tests whether the default-case M1 opener advantage survives changes to the main B3 character.

## Controlled conditions

- B1: Liter
- B2: Crown + Mast: Romantic Maid
- secondary B3: Helm (Favorite Item)
- timeline: `RAID14_TIMELINE`
- current standard builds/catalog/combat settings
- opening comparison window: first B1 until opening buff-state convergence
- boss-pattern losses: OFF

Only the main B3 is changed.

## Results

| Main B3 | M1 opener vs Crown opener | Conventional vs funnel | Break-even main share | Conventional main share |
|---|---:|---:|---:|---:|
| Rapi: Red Hood | +1.7108% | -1.7793% | 66.3750% | 40.0096% |
| Scarlet: Black Shadow | **-0.3610%** | -1.9973% | 81.9259% | 45.3958% |
| Snow White: Heavy Arms | +3.2340% | -1.9681% | 81.5417% | 45.7152% |
| Epinel | +0.4883% | -3.8467% | 98.8333% | 13.9583% |
| Neon: Vision Eye | +3.3927% | -2.3818% | 97.0982% | 45.4677% |

Positive opener values mean M1 opener is stronger; negative values mean Crown opener is stronger.

The key result is the Scarlet: Black Shadow counterexample. The previous B1 spot-check showed M1 winning for four B1 choices while Rapi/Helm stayed fixed, but changing the main B3 can reverse the opener result. Therefore the statement "M1 opener is stronger at equal Crown/Mast investment" cannot be treated as a universal rotation rule from the current engine results.

## Why Rapi and Scarlet move in opposite directions

Opening-window damage decomposition:

### Rapi: Red Hood main

```text
Liter                    +265,719.95
Crown                  -3,929,425.85
Mast                   +3,743,213.50
Rapi: Red Hood         +3,402,915.88
Helm                     +392,523.85
team                   +3,874,947.33  (+1.7108%)
```

### Scarlet: Black Shadow main

```text
Liter                    +265,719.95
Crown                  -3,929,425.85
Mast                   +3,743,213.50
Scarlet: Black Shadow  -1,577,129.42
Helm                     +392,523.85
team                   -1,105,098.00  (-0.3610%)
```

The non-main members move almost identically between the two cases. The sign flip comes from the main B3 response: Rapi gains about 3.40 million from the M1 opening configuration, while Scarlet loses about 1.58 million.

This means the opener question is not just a direct Crown-vs-Mast B2 buff-strength comparison. It depends on how the active B3 converts Crown's 15-second Attack Damage/reload/caster-ATK structure versus Mast's 10-second crit/Attack Damage/caster-ATK structure into actual damage.

## Current interpretation

- M1 opener is a strong candidate for many compositions and is clearly better in the current Rapi, Snow White, Epinel, and Neon spot-checks.
- Crown opener can still be optimal for at least some B3 mechanics; Scarlet: Black Shadow is a concrete current-engine counterexample.
- Opening choice should therefore remain an independent variable in the research engine instead of being hard-coded to Mast.
- The conventional `C,C,M` vs sustained-funnel winner stayed conventional in all five spot-checks at the tested builds/shares.

These are controlled engine results, not universal gameplay claims. Additional build and B3 combinations remain necessary before publishing a broad opener recommendation.
