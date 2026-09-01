# Character audit — 2026-09-02

> **Source-policy note (2026-09-02):** any `nikke-sim` reference below is provenance/secondary-reference only, not the authority priority. Current mechanics work must prefer Moris calculator / NIKKE.gg (and direct evidence when available) and must be independently cross-validated. See `docs/SOURCE_VALIDATION_POLICY.md`.


Scope: Crown–Mast single stage-target, externally fixed RAID14 timeline. No research batch was run.

Cross-check sources (authority order):
- `Moris-kr/nikke-calc` current `data/parsed_skills.json` and damage/timeline implementation
- NIKKE.gg current character guides / mechanics explanations
- direct in-game or official evidence when available; Prydwen/other current sources as additional corroboration
- `Infernal-Crack-LED/nikke-sim@43308bd02276a476660e44af730785c2ae91eea3` only as secondary structured provenance/reference implementation

No new mechanic is accepted from nikke-sim alone. Cross-site/source validation is mandatory; unresolved conflicts remain documented and out of scope until evidence is sufficient.

Confirmed corrections:
1. Rapi: Red Hood now supports the no-separate-B1 Combat Assist branch: B1 team caster-ATK 18.01%/10s and Full-Burst team Attack Damage 8.02%/10s. Her 20s self B1 CDR and 7.48s team FB CDR are documented but do not alter the externally measured RAID14 timestamps.
2. Raven Shock Wave is one refreshing target state, stacking to 10 and ticking once per second at 68.46% × current stacks. The prior independent-five-tick-per-shot approximation was wrong.
3. Quency: Escape Queen's dual SMG supplies the two-hit trigger every pull. Explore Route now unlocks sequentially and honors 2s/1s/0.5s expiry, so Stage 2/3 lapse and rebuild across reloads.
4. Cinderella: Crystal Wave's MG 833.79% core-strike uses a forced-core path; it is not diluted by the externally configured normal-attack core-hit rate.
5. Burst-cast instant damage is explicitly Full-Burst-major-exempt even where RAID14 stores B3 cast and Full Burst start at the same timestamp. Applied to Liberalio, Raven, CCW, Phantom FI, Quency EQ, Epinel, and Helm. Delayed Rapi B3 and FB-enter CCW riders remain timing-eligible.

Checked with no correction required in this study scope:
- Bready: Recommended Taste route values/conditions agree. Lingering Taste's 349.8 semantics remain source-disputed but are not activated by the Crown–Mast Recommended route.
- Liberalio: single stage-target Raging Current route, 202.5 full-charge rider, 160% FB ATK, 231% Raging Current, 925 burst packet agree. Gentle Current is out of scope.
- Milk: Blooming Bunny: this engine intentionally uses AUTO basis. 447.7% distributed ×5, +220% ATK and +117.64% Pierce Damage are retained. Moris models the manual 0.5s hold/Embarrassment route; it is deliberately not claimed here.
- Phantom FI: Calling Card/Dagger, 250% distributed rider, distributed-amplification stacks, 1457.28% Burst, and Fire-target 18% vulnerability agree for the single-boss favorite-item scope.

Known scope notes:
- CCW remains MG-only by project decision; Snipe state machine is excluded.
- Fixed RAID14 means gauge-generation and CDR effects are not allowed to move burst timestamps.
- Parts/jumps/invulnerability remain outside the base research model.


## Validation

The finalized patch is gated by `python -m unittest discover -v tests` (279 tests) plus `compileall`. Research batches and benchmarks are intentionally not run as part of this audit.
