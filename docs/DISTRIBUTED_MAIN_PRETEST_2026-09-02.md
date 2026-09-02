# Distributed Main B3 Pretest — 2026-09-02

Status: **diagnostic pretest only; not an official research result**

This checkpoint was added before the full Crown–Mast official study because Scarlet: Black Shadow (SBS) had shown unusually weak sustained-funnel response in earlier validation runs. The purpose is to determine whether that behavior is a general consequence of `distributed` damage or a character/timing-specific interaction.

## 1. Scope and fixed conditions

Isolation grid:

```text
B1: Liter
Secondary B3: Helm
Boss DEF: 140
Boss element: neutral
Core hit rate: 0%
Range bonus: 0%
Growth grid: checkpoint-v3 4 x 4 x 4 = 64 per Main
```

The neutral/core-off condition is intentional. It removes elemental/core axes from this diagnostic so that Main-specific response to the Crown/Mast rotation change is easier to inspect.

Distributed Main B3 candidates in official-v1 that currently emit audited distributed packets:

```text
Scarlet: Black Shadow
Bready
Quency: Escape Queen
Phantom (Favorite Item)
Milk: Blooming Bunny
```

Non-distributed control:

```text
Rapi: Red Hood
```

`g` is the Main actor's own relative damage change under Funnel versus Conventional:

```text
g = Main_funnel / Main_conventional - 1
```

`l` is the relative loss of the other four actors. Under this fixed roster/environment structure it is effectively identical across Main choices, so differences between Main actors are primarily differences in `g`.

## 2. 64-point isolation results

| Main | Structure | Avg Main `g` | Avg team Funnel change | Avg Conventional Main share | Avg break-even Main share | Funnel wins |
|---|---|---:|---:|---:|---:|---:|
| Quency: Escape Queen | distributed burst + normal | **+3.707%** | -1.223% | 34.97% | 51.07% | 0 / 64 |
| Rapi: Red Hood | non-distributed control | +2.311% | -1.199% | 43.34% | 62.79% | 0 / 64 |
| Milk: Blooming Bunny | distributed skill route | +2.151% | -1.787% | 34.61% | 64.25% | 0 / 64 |
| Phantom (FI) | mixed distributed/plain | +1.162% | -1.901% | 39.12% | 76.87% | 0 / 64 |
| Scarlet: Black Shadow | cyclic distributed/plain | +0.918% | -1.545% | 48.59% | 80.88% | 0 / 64 |
| Bready | Mast-triggered distributed route | **-0.050%** | -2.495% | 35.93% | mostly unavailable; finite cases ~98.7% | 0 / 64 |

Across these fixed cases, average `l` is approximately **3.871%** for every Main. This confirms that the large difference between SBS, Quency, Milk, Phantom, Bready, and Rapi is located in the Main actor response rather than a change in the fixed rest-of-team opportunity cost.

Important interpretation:

- The distributed tag does **not** imply weak Funnel response.
- Quency's average `g` is about four times SBS's and exceeds the non-distributed Rapi control.
- Milk is close to the Rapi control.
- SBS is weak among the distributed set, but Bready is even weaker and can lose Main damage under Funnel.

Therefore the hypothesis `distributed damage itself causes SBS's weak funnel result` is rejected by this pretest.

## 3. Representative source-level diagnostic

A single representative point was then selected for each Main:

```text
B1 growth: g3-ol0-sr15-e3-a3
Main growth: g3-ol0-sr15-e3-a3
Secondary growth: g3-ol0-sr15-e3-a3
same neutral/core-off environment
```

### Scarlet: Black Shadow

Main total:

```text
+0.898%
```

By source:

| Source | Conventional share of SBS | Funnel change |
|---|---:|---:|
| normal_attack | 23.49% | +0.641% |
| skill1_phase1 (plain) | 9.89% | +0.785% |
| skill1_phase2 (distributed) | 26.16% | **+1.326%** |
| skill1_phase3 (distributed) | 40.46% | +0.798% |

There is no source-level sign that SBS distributed packets fail to receive the Mast-related benefit. In fact phase 2 responds more strongly than the plain phase and normal attack in this representative point.

The net weakness comes from cycle-level cancellation. The only large divergences are approximately:

```text
cycle 5   Main +10.05%
cycle 6   Main -21.28%
cycle 11  Main +10.17%
cycle 12  Main -16.76%
```

Most other cycles are unchanged. The large positive windows are therefore cancelled by adjacent negative windows.

### Bready

Main total:

```text
-0.002%
```

By source:

```text
normal_attack                    +0.211%
skill2_recommended_distributed   -0.124%
```

Cycle-level changes again show cancellation:

```text
cycle 5   +13.20%
cycle 6   -16.01%
cycle 11  +10.84%
cycle 12  -17.70%
```

Bready is a special case because Mast's distributed-damage buff itself activates the Recommended Taste route. The result should therefore be interpreted as a character-specific state/timing interaction, not as a generic distributed bucket penalty.

### Milk: Blooming Bunny

Main total:

```text
+2.036%
```

By source:

```text
normal_attack                        +1.147%
skill2_overconfident_distributed     +2.650%
```

The distributed source responds positively and accounts for most of Milk's Main gain.

### Phantom (Favorite Item)

Main total:

```text
+1.184%
```

By source:

```text
burst_distributed              +9.168%
normal_attack                  -0.880%
skill2_max_stack_additional    -0.872%
skill2_max_stack_distributed   -1.300%
```

Phantom is another cancellation example: a highly Funnel-sensitive burst packet is offset by losses in sustained sources.

### Quency: Escape Queen

Main total:

```text
+3.561%
```

By source:

```text
burst_distributed   +8.642%
normal_attack       +0.178%
```

About 97% of Quency's Main absolute gain at this representative point comes from `burst_distributed`. This high-value packet is strongly aligned with the Funnel-favored Main burst windows.

### Rapi: Red Hood control

Main total:

```text
+2.591%
```

Key source responses:

```text
burst_stage3_missile       +8.291%
skill2_rocket_attachment   +3.392%
skill2_rocket_explosion    +1.610%
normal_attack              -0.927%
```

Like Quency and Phantom, Rapi receives a large positive contribution from a burst-concentrated source while some sustained damage can decline.

## 4. Interpretation

The diagnostic supports the following mechanism:

> **Funnel receptivity is primarily determined by how much of a Main dealer's valuable damage is concentrated in the Main-targeted Mast-favored windows, and by how the altered Crown/Mast sequence changes adjacent windows. It is not determined by the distributed-damage flag itself.**

SBS has a large fraction of its damage in continuously cycling Skill 1 phases rather than a single highly concentrated B3 packet. The Funnel-favored cycles increase its damage, but the following altered cycles lose enough damage to cancel most of that gain.

Quency is the clearest counterexample to the generic distributed-damage hypothesis: its distributed burst packet gains strongly enough that its average 64-point `g` exceeds Rapi's non-distributed control.

Bready should be treated as a mechanic-specific edge case because the Mast distributed buff is also a trigger for her Recommended Taste state.

## 5. Consequence for the official study

No official Main candidate needs to be removed on the basis of this pretest.

For the final analysis, Main characters should **not** be collapsed into a simple `distributed vs non-distributed` category. Retain and report at least:

```text
Main actor
Main g
Main conventional share
Main absolute gain
source/timing structure when interpreting outliers
```

SBS's low `g` is a real modeled character/timing behavior under the current audited hooks, not evidence of an unresolved distributed-damage bucket bug.

The full official batch remains **not run** and official result count remains **0**.

## 6. Execution provenance

Pretest implementation:

```text
scripts/run_distributed_pretest.py
scripts/run_distributed_source_diagnostic.py
```

Relevant branch:

```text
research/14-burst-baseline
```

Source-level diagnostic commit:

```text
3a324da9977158a03e3000575d68e842f75e91a3
```

GitHub Actions source diagnostic run:

```text
33584299157
```

The regression suite is separate from the diagnostic jobs. The official batch and benchmark are not invoked by these pretest markers.
