# Crown–Mast official study design v1

Status: **sample space / execution-storage design finalized; official research batch not started**

Study id:

```text
crown-mast-secondary-opportunity-v1
```

This document freezes the canonical sample space that will be used when the user explicitly authorizes the official research batch. It does **not** contain research results.

---

## 1. Research question

Under the externally controlled RAID14 baseline, change only Crown/Mast B2 operation and test how broadly the conventional claim

> `if one Main dealer is strong, repeatedly funnel Mast into that dealer`

is actually useful.

The primary questions are:

1. Is the sustained-funnel winning region limited?
2. When funnel wins, is the gain usually small?
3. Are funnel-favorable party structures uncommon among practical compositions?

The analysis centers on the **opportunity cost of the Secondary B3** rather than on a universal Main-share threshold.

---

## 2. Final B1 sample — 5

Canonical engine slugs:

```text
liter
anis-star
moran-favorite-item
little-mermaid
rapi-red-hood
```

Display names:

```text
Liter
Anis: Star
Moran (Favorite Item)
Little Mermaid
Rapi: Red Hood — B1 Combat Assist role
```

The set intentionally spans materially different B1 environments: a conventional team buffer, a high-self-contribution B1, a favorite-item/self-damage route, a team damage/taken environment, and the audited Rapi RH Combat Assist branch.

`neon-vision-eye` remains implemented and available for later sensitivity work but is not part of the frozen v1 official B1 sample. The v1 B1 scope is the previously established four-B1 set plus the newly audited Rapi RH B1 branch.

### Rapi duplicate rule

If Rapi RH is assigned to B1, the same Rapi RH cannot also occupy Main B3.

The canonical generator excludes that pair **before** constructing `TeamRoster`.

```text
B1 Rapi + Main Rapi -> excluded
```

The `TeamRoster` unique-character validation remains the second safety layer.

---

## 3. Final Main B3 sample — 9

Canonical engine slugs:

```text
rapi-red-hood
scarlet-black-shadow
bready
cinderella-crystal-wave
liberalio
milk-blooming-bunny
phantom
quency-escape-queen
raven
```

Display names:

```text
Rapi: Red Hood
Scarlet: Black Shadow
Bready
Cinderella: Crystal Wave
Liberalio
Milk: Blooming Bunny
Phantom (Favorite Item)
Quency: Escape Queen
Raven
```

The purpose is not to claim that these are the nine universally strongest B3 units. They are the **audited research sample** used to cover meaningfully different damage structures and Mast/Crown interactions in the current engine.

The three Secondary anchors are deliberately not reused as Main candidates. This keeps the Main and Secondary experimental axes independent and prevents Epinel / Helm / Snow White: Heavy Arms self-duplicate exclusions from distorting the grid.

The current Main sample covers, among other structures:

- conventional high-output Main behavior;
- distributed-damage-heavy behavior;
- full-burst/charge-dependent behavior;
- forced-core skill damage;
- stack/route state machines;
- favorite-item behavior;
- DoT behavior.

Mechanic semantics for these actors remain governed by `docs/SOURCE_VALIDATION_POLICY.md` and the current character audit. The candidate list itself is a sampling decision, not a tier-list claim.

---

## 4. Secondary B3 anchors — 3

Frozen v1 anchors:

```text
epinel                 -> low-end positive control
helm                    -> practical middle anchor
snow-white-heavy-arms   -> high-contribution anchor
```

Final analysis must use **actual conventional Secondary damage/share** as the main explanatory variable. Low/Mid/High labels are only experimental shorthand.

---

## 5. Growth grid

Use the existing realistic-v3 checkpoints for each variable role:

```text
B1 growth        4
Main B3 growth   4
Secondary growth 4

4 x 4 x 4 = 64 growth points
```

The four profiles remain:

```text
g1-base5-none
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

Crown and Mast stay fixed at the existing v3 B2 build.

These 64 points are deterministic robustness checkpoints, not probability samples and not a dense estimator of a universal threshold.

---

## 6. Environment axes

### 6.1 Core: off / on

Operational v1 definition:

```text
core off -> core_hit_rate_pct = 0
core on  -> core_hit_rate_pct = 100
```

`core on` means a fully available core for otherwise core-eligible attacks. This is a controlled sensitivity extreme, **not** a claim that real encounters provide 100% core exposure.

If realistic partial core exposure is studied later, it is a separate sensitivity/follow-up axis and must not be silently mixed into this v1 grid.

### 6.2 Main elemental advantage: off / on

This remains a **real boss-element condition**, not an artificial Main-only multiplier.

```text
advantage off -> neutral boss element condition
advantage on  -> choose the boss element naturally beaten by the Main B3 element
```

Therefore, if another teammate has the same advantageous element, that teammate receives normal elemental advantage too. This is intentional and preserves a plausible battle environment.

---

## 7. Official roster and scenario count

Raw Cartesian roster count:

```text
5 B1 x 9 Main x 3 Secondary = 135 rosters
```

Invalid duplicate rosters:

```text
Rapi B1 + Rapi Main x 3 Secondary = 3
```

No Main candidate is one of the three Secondary anchors, and no B1 candidate is one of the three Secondary anchors. Therefore there are no additional role-duplicate exclusions in v1.

Valid rosters:

```text
135 - 3 = 132
```

Per valid roster:

```text
64 growth x 2 core x 2 Main advantage = 256 scenarios
```

Total official sample space:

```text
132 x 256 = 33,792 scenarios
```

Useful partitions:

```text
per Secondary anchor: 44 valid B1/Main pairs x 256 = 11,264 scenarios
all 3 anchors:                                  33,792 scenarios
```

`33,792` is now the canonical v1 arithmetic because the candidate lists above are frozen. It is still a count of controlled deterministic scenarios, not an estimate of real-world occurrence frequency.

---

## 8. Execution unit

The canonical execution shard is **one valid roster**.

```text
1 roster shard
= 64 growth points
x 2 core conditions
x 2 Main-advantage conditions
= 256 scenarios
```

Benefits:

- 132 independent, resumable shards;
- no need to hold all 33,792 full reports in memory;
- simple failure/retry boundary;
- easy provenance mapping from roster to raw result file;
- Secondary-anchor analysis can be assembled without rerunning simulations.

The batch must not start until the user explicitly authorizes official result collection.

---

## 9. Canonical storage layout

When the official batch is authorized, use a run-specific directory:

```text
research_results/runs/<run_id>/
  manifest.json
  raw/
    <roster_id>.jsonl
  tables/
    scenarios.csv
    rosters.csv
  analysis/
    secondary_anchor_summary.md
    effect_size_summary.md
    reversal_structure.md
```

### `manifest.json`

Must record at minimum:

```text
study_id
run_id
branch
commit_sha
engine_rule_revision
skill_hook_revision
catalog_source_revision
timeline_id / exact timeline parameters
baseline rotation
candidate lists
growth-grid definition
core-axis definition
Main-advantage definition
valid roster count
scenario count
shard policy
completed shard ids
```

The manifest is the authoritative provenance record for a run.

### `raw/<roster_id>.jsonl`

Store one compact record per scenario, 256 lines per completed roster shard.

Do **not** store the entire verbose `ComparisonReport` for all 33,792 cases by default. The study is deterministic and the manifest is sufficient to reproduce a selected full report later. Keeping full cycle/source breakdowns for every point would greatly inflate repository size without improving the primary analysis.

Each compact raw row should include at minimum:

```text
case_id
study_id / run_id / roster_id
B1 / Main / Secondary
B1 growth / Main growth / Secondary growth
core condition / core_hit_rate_pct
Main advantage condition / boss element
engine / hook / catalog revisions
conventional team damage
funnel team damage
team absolute delta
team relative delta
outcome band
Main conventional/funnel damage and share
Main absolute gain
Secondary conventional/funnel damage and share
rest-of-team conventional/funnel damage
rest-of-team opportunity loss
g / l / local break-even fields
per-character conventional/funnel damage and shares
```

This is enough for the planned Secondary-opportunity-cost analysis while remaining reproducible.

### Derived tables

`tables/scenarios.csv` is a flattened derivative of raw JSONL for plotting/statistics.

`tables/rosters.csv` contains one-row-per-roster aggregates and completion/provenance information.

Derived tables are rebuildable; raw JSONL + manifest are canonical.

---

## 10. Primary analysis outputs

Primary:

1. funnel win/loss/tie-band frequency by Secondary anchor;
2. funnel-win effect-size distribution;
3. funnel loss distribution where conventional wins;
4. conventional Secondary damage-share distribution around reversals;
5. absolute Main gain versus rest-of-team opportunity loss.

Secondary slicing:

```text
Main B3
B1
growth combination
core off/on
Main advantage off/on
```

The main interpretive question remains:

> As conventional Secondary contribution rises, how quickly does the sustained-funnel winning region contract?

---

## 11. Non-claims

The v1 grid does not establish:

- a universal Main-share threshold;
- the real-world probability that funnel wins;
- that Crown-Crown-Mast always wins every NIKKE encounter;
- that full core exposure is a normal boss condition;
- that the nine Main candidates are a universal tier list;
- that pattern-loss-free results transfer unchanged to bosses with jumps, invulnerability, forced cover, or part-exposure windows.

Pattern-loss work remains a separate follow-up.

---

## 12. Implementation status

Implemented without running research results:

```text
crown_mast_engine/official_study.py
tests/test_official_study.py
```

The generator freezes candidate lists, pre-excludes duplicate actors, exposes the canonical count, and builds one 256-scenario roster shard without executing it.

Official research results remain **0** until explicit user authorization.
