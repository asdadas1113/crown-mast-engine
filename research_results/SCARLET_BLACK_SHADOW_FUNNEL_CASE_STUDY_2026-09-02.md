# Scarlet: Black Shadow Funnel Response Case Study — 2026-09-02

Status: **independent diagnostic research result / not part of the official 33,792-scenario v1 batch**

This document preserves an anomalous but informative result discovered while validating the Crown–Mast study before the official batch. Scarlet: Black Shadow (SBS, 흑련) showed a much weaker Main-dealer response to sustained Mast funneling than several other Main B3 candidates. The behavior was investigated separately because it could have indicated a distributed-damage implementation problem, a specific B1 interaction, or a character-specific timing structure.

The conclusion is that SBS is a **real character/timing outlier in this model**, not a broken distributed-damage case. Her own Burst III window becomes substantially stronger under Funnel, but she continues to deal a large amount of valuable Skill 1 damage outside her own B3 window. The Conventional route therefore gives up less Main damage than expected when it keeps a stronger Mast stack for the following Secondary-B3 cycle. In SBS's case, the gain in the Main-targeted cycle is heavily cancelled by the loss in the adjacent cycle.

This finding is useful information in its own right, but it must remain separate from the official v1 publication result because the tests below were purpose-built diagnostics rather than the frozen 33,792-scenario research design.

---

## 1. Why this case was investigated

During the distributed-Main pretest, SBS showed unusually low Main gain `g` under Funnel.

`g` is defined as:

```text
g = Main_funnel / Main_conventional - 1
```

It measures how much the **Main actor's own total damage** changes when moving from Conventional Crown/Mast usage to sustained Mast Funnel usage.

Under the first isolation test:

```text
B1: Liter
Secondary B3: Helm
Boss DEF: 140
Boss element: neutral
Core hit rate: 0%
Range bonus: 0%
Growth grid: checkpoint-v3 4 x 4 x 4 = 64 per Main
```

64-point average Main `g` was:

| Main | Structure | Avg Main `g` |
|---|---|---:|
| Quency: Escape Queen | distributed burst + normal | **+3.707%** |
| Rapi: Red Hood | non-distributed control | +2.311% |
| Milk: Blooming Bunny | distributed skill route | +2.151% |
| Phantom (Favorite Item) | mixed distributed/plain | +1.162% |
| **Scarlet: Black Shadow** | cyclic distributed/plain | **+0.918%** |
| Bready | Mast-triggered mechanic edge case | -0.050% |

Bready is numerically lower, but it is not the same kind of case: Mast's distributed-damage buff itself changes Bready's Recommended Taste state. Bready is therefore a mechanic-specific edge case. SBS was the more important anomaly for the general Crown/Mast question because her low `g` appeared without such a direct state trigger.

The first suspicion was that SBS's distributed Skill 1 packets might be interacting incorrectly with Mast's distributed-damage buff.

---

## 2. SBS mechanic structure relevant to the anomaly

The audited engine definition for SBS uses the following Skill 1 cadence:

```text
outside own B3 window:  3 full-charge shots per Skill 1 phase advance
inside own B3 window:   1 full-charge shot per Skill 1 phase advance

phase 1: 283.03% plain damage
phase 2: 565.00% distributed damage
phase 3: 848.03% distributed damage
```

Her own Burst III lasts 10 seconds and also grants strong self ATK and charge-damage bonuses. Thus her B3 window is unquestionably stronger than her normal state.

However, an important feature is that **Skill 1 does not stop outside her B3**. The phase cycle continues at the slower 3-full-charge cadence, and phases 2 and 3 remain high-coefficient distributed attacks. SBS therefore retains meaningful sustained damage in the cycle immediately after her own B3.

This distinction is central to the result: she is burst-enhanced, but not a character whose valuable damage is almost entirely confined to her own B3 window.

---

## 3. Rotation-level reason the Funnel trade is unfavorable for SBS

The meaningful difference between the two studied rotations occurs around the Main-B3 / Secondary-B3 pair.

Conceptually:

```text
Conventional
Main cycle:      Crown + Main B3
following cycle: Mast 3-stack + Secondary B3

Sustained Funnel
Main cycle:      Mast 2-stack + Main B3
following cycle: Crown + Secondary B3
```

For the Main actor, Funnel is therefore not a free Mast buff. It is a **timing trade**:

> move Mast value forward into the Main's own B3 cycle, while giving up the stronger Mast value the Main would also have received during the following cycle.

For a burst-concentrated Main, this can be favorable because the Main gains much more in its own B3 than it loses afterward.

For SBS, the following cycle still contains substantial normal attack + Skill 1 damage, so the lost M3 value is expensive.

---

## 4. Representative source-level diagnostic

A representative middle-growth point was selected:

```text
B1: Liter
Main: Scarlet: Black Shadow
Secondary: Helm
B1 growth: g3-ol0-sr15-e3-a3
Main growth: g3-ol0-sr15-e3-a3
Secondary growth: g3-ol0-sr15-e3-a3
Boss: neutral
Core: 0%
Range bonus: 0%
```

### 4.1 Total SBS result

```text
Conventional SBS damage: 1,761,817,101.47
Funnel SBS damage:       1,777,635,586.33
Absolute gain:             +15,818,484.86
Main g:                         +0.89785%
```

The result is positive, but far smaller than one would expect if the Main-targeted Mast window were simply being added on top of otherwise unchanged SBS damage.

### 4.2 Damage-source response

| SBS damage source | Share of Conventional SBS damage | Funnel change |
|---|---:|---:|
| normal_attack | 23.49% | +0.641% |
| skill1_phase1, plain | 9.89% | +0.785% |
| skill1_phase2, distributed | 26.16% | **+1.326%** |
| skill1_phase3, distributed | 40.46% | +0.798% |

This directly rejects the hypothesis that SBS is weak because her distributed packets fail to benefit from Mast.

The clearest counterexample is Skill 1 phase 2: the distributed packet gains **+1.326%**, which is more than the plain phase 1 and normal attack in the same representative test.

Therefore:

```text
SBS low g != distributed packet not receiving Mast value
```

---

## 5. Cycle-level cancellation: the actual cause

The representative diagnostic becomes clear when SBS damage is split by burst cycle.

Most cycles are effectively unchanged. The large differences occur at the two Main-targeted Funnel windows and the immediately following cycles:

| Cycle | Conventional SBS | Funnel SBS | Absolute delta | Relative change |
|---:|---:|---:|---:|---:|
| 5 | 195.369m | 215.004m | **+19.634m** | **+10.05%** |
| 6 | 61.712m | 48.579m | **-13.132m** | **-21.28%** |
| 11 | 185.590m | 204.466m | **+18.876m** | **+10.17%** |
| 12 | 57.816m | 48.123m | **-9.693m** | **-16.76%** |

Cycle 13 adds only a very small residual difference of roughly +0.133m; the other cycles are essentially unchanged.

The structure is therefore:

```text
cycle 5:  Main-targeted Mast window      -> large SBS gain
cycle 6:  following M3 removed           -> large SBS loss

cycle 11: Main-targeted Mast window      -> large SBS gain
cycle 12: following M3 removed           -> large SBS loss
```

The two Main-favored cycles add approximately:

```text
+19.634m + 18.876m = +38.510m
```

The two immediately following cycles remove approximately:

```text
-13.132m - 9.693m = -22.825m
```

A large fraction of the apparent Funnel benefit is therefore returned immediately in the next cycle. After all cycles are summed, SBS is left with only about **+0.90% Main gain** at the representative point.

This is the defining feature of the SBS case.

---

## 6. Why Quency behaves differently despite also using distributed damage

Quency: Escape Queen was used as the strongest counterexample to the distributed-damage hypothesis.

In the representative source diagnostic:

```text
Quency Main total g:          +3.561%
Quency burst_distributed:     +8.642%
Quency normal_attack:         +0.178%
```

Approximately 97% of Quency's absolute Main gain at that point came from the `burst_distributed` source.

This means Quency's valuable Funnel-sensitive damage is much more concentrated in the exact Main-targeted window. She still has sustained damage, but the high-value distributed burst packet aligns directly with the cycle where Mast is moved forward.

SBS is structurally different. Her damage is distributed across continuously cycling Skill 1 phases, so the following cycle remains valuable enough that removing M3 produces a large counter-loss.

This comparison shows that the useful explanatory axis is not:

```text
distributed vs non-distributed
```

but rather something closer to:

```text
how concentrated is valuable Main damage in the Main-targeted Mast-favored window?
vs
how much valuable Main damage remains in the adjacent cycle that loses M3?
```

---

## 7. B1 sensitivity test: Liter was not the cause

A second hypothesis was that SBS's low `g` might be specific to Liter's short, strong B1 buff structure. To test this, only B1 was changed from Liter to Little Mermaid while keeping the isolation environment and 64-point growth grid.

Results:

| B1 | Main | Avg Main `g` | Avg team Funnel change | Avg Conventional Main share | Avg break-even Main share | Funnel wins |
|---|---|---:|---:|---:|---:|---:|
| Liter | SBS | +0.918% | -1.545% | 48.59% | 80.88% | 0 / 64 |
| **Little Mermaid** | **SBS** | **+1.068%** | **-1.753%** | 42.15% | 78.11% | 0 / 64 |
| Liter | Quency | +3.707% | -1.223% | 34.97% | 51.07% | 0 / 64 |
| **Little Mermaid** | **Quency** | **+3.332%** | **-1.781%** | 27.78% | 52.93% | 0 / 64 |

Changing B1 changes exact magnitudes and damage shares, as expected, but the response ordering survives cleanly:

```text
Little Mermaid B1
Quency Main g: +3.332%
SBS Main g:    +1.068%
```

Quency still gains a little over three times as much proportional Main damage as SBS.

SBS is also clear-Conventional in all 64 Little Mermaid cases.

Therefore the narrower hypothesis:

```text
SBS low g is mainly a Liter-specific interaction
```

is rejected.

---

## 8. Hypotheses tested and disposition

### Hypothesis A — Distributed damage is incorrectly receiving Mast value

**Rejected.**

SBS distributed Skill 1 packets increase normally. Phase 2 gains +1.326% in the representative source diagnostic. Other distributed Mains such as Quency and Milk also show substantially stronger Funnel response.

### Hypothesis B — Distributed-damage characters are generally poor Funnel targets

**Rejected.**

Quency averages +3.707% Main `g` with Liter and +3.332% with Little Mermaid. Milk also approaches the non-distributed Rapi control in the first isolation test.

### Hypothesis C — Liter's B1 timing/buff profile causes the SBS anomaly

**Rejected.**

Little Mermaid preserves the same qualitative ordering and SBS remains low-response.

### Hypothesis D — SBS's own burst/non-burst damage distribution causes strong adjacent-cycle cancellation

**Supported by the current diagnostics.**

SBS gains about +10% in the Main-targeted cycles but loses roughly 17–21% in the following altered cycles. Her continuously cycling Skill 1 leaves substantial valuable damage outside her own B3 window, making the lost M3 unusually expensive.

This is the best current explanation.

---

## 9. Interpretation for the wider Crown–Mast study

SBS should remain in the official Main sample. Nothing in this investigation justifies removing or correcting her result.

Instead, SBS should be retained as an informative outlier demonstrating that **Main damage share alone does not fully describe Funnel receptivity**.

Two Mains can have similar overall contribution but react very differently depending on the temporal distribution of their damage.

The SBS case suggests that final interpretation should retain at least:

```text
Main actor
Main g
Main Conventional damage share
Main absolute gain
Secondary opportunity cost
source/timing structure for outliers
```

A useful conceptual variable for future analysis is **burst concentration / Funnel-window concentration**:

> the fraction of the Main's valuable damage that occurs in the cycle where Mast is moved forward, relative to the valuable damage that remains in the following cycle where M3 is removed.

This does not need to become a new official study axis before the frozen v1 batch. It is primarily an explanatory lens for interpreting character-level outliers after the official results exist.

---

## 10. Scope and limitations

This case study does **not** claim:

- that SBS is always a poor Mast target in every encounter;
- that real boss movement, invulnerability, parts, forced cover, or phase transitions cannot change the result;
- that one universal burst-concentration threshold exists;
- that the 64 diagnostic grid is a probability distribution of real player builds;
- that the Funnel/Conventional result here is an official v1 result.

The baseline deliberately removes encounter-pattern loss. A boss pattern that disproportionately removes SBS's non-B3 damage or changes which cycles connect could alter the practical trade.

The result should therefore be read as:

> under the controlled RAID14 baseline, SBS is unusually resistant to sustained Mast funneling because her valuable damage is not concentrated enough in her own B3 window to outweigh the adjacent-cycle Mast opportunity cost.

---

## 11. Reproducibility / provenance

Branch:

```text
research/14-burst-baseline
```

Primary diagnostic scripts:

```text
scripts/run_distributed_pretest.py
scripts/run_distributed_source_diagnostic.py
```

Source-level diagnostic commit/run:

```text
commit: 3a324da9977158a03e3000575d68e842f75e91a3
GitHub Actions run: 33584299157
```

Little Mermaid B1 sensitivity implementation/execution:

```text
620178e05f02e18359dbbfa5fc6875d9ca252491  add B1 sensitivity option
6b97d3cb4d7118ce35b00a0a79eb6b85f579997c  SBS/Quency Little Mermaid matrix
GitHub Actions run 33585317692                 SBS full 64-point result

d67dcda64d776657929a8f9f5413e4c58eac93b4  Quency 4-way profile sharding
GitHub Actions run 33585697924                 Quency 4 x 16-point result
```

Audited SBS mechanic implementation:

```text
crown_mast_engine/character_mechanics/scarlet_black_shadow.py
crown_mast_engine/data/characters.json
```

Related broader diagnostic document:

```text
docs/DISTRIBUTED_MAIN_PRETEST_2026-09-02.md
```

Official study status at time of this case study:

```text
official 33,792-scenario batch: NOT RUN
official result count: 0
```

---

## 12. Final case-study conclusion

The SBS anomaly is considered **resolved and non-blocking**.

The result is not caused by a generic distributed-damage bug and is not primarily caused by Liter. It is a character-specific timing effect produced by SBS's relatively broad damage distribution across both her own B3 cycle and the following cycle.

In short:

> **SBS receives Mast correctly. She simply has too much valuable non-B3 / adjacent-cycle damage for moving Mast forward to create the same net Main gain seen on burst-concentrated characters such as Quency.**

For future interpretation, SBS should be treated as a canonical example of why `Main is strong` and `Main has high total damage share` are insufficient by themselves to predict whether Mast funneling will be efficient.
