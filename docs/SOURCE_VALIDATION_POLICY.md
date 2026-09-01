# Source validation policy — 2026-09-02

> **Source-policy note (2026-09-02):** any `nikke-sim` reference below is provenance/secondary-reference only, not the authority priority. Current mechanics work must prefer Moris calculator / NIKKE.gg (and direct evidence when available) and must be independently cross-validated. See `docs/SOURCE_VALIDATION_POLICY.md`.


This policy supersedes older wording in the repository that may describe a pinned
`nikke-sim` revision as the default or authoritative mechanics reference.

## Authority order

For current character/mechanics decisions, use this order:

1. **Direct in-game evidence / official skill text**, when available and relevant to the exact question.
2. **Moris calculator (`Moris-kr/nikke-calc`) and NIKKE.gg** as the preferred current external references for implementation behavior, trigger conditions, damage flavor, and practical interpretation.
3. **Another current independent source** such as Prydwen or a documented community measurement when it materially strengthens the check.
4. **`nikke-sim` only as a secondary structured source**: useful for pinned datamine values, frame/cadence clues, and reference implementation details, but not sufficient by itself to settle behavior.

A `source_revision` field containing `nikke-sim@...` records **provenance**, not authority priority.

## Mandatory cross-validation

Every newly added character or newly changed mechanic must be checked against at
least one current source/site independent of `nikke-sim`. The normal minimum is:

- Moris calculator **plus** NIKKE.gg, or
- one of those plus direct in-game/official evidence.

Do **not** confirm a trigger, timing rule, damage bucket, status interaction, or
special-case behavior from `nikke-sim` alone.

For timing / trigger order / damage-bucket questions that can change research
semantics, require either:

- two independent current references that agree, or
- direct in-game measurement/evidence.

If the evidence is still insufficient, leave the behavior explicitly unresolved or
out of scope rather than inventing a rule.

## Conflicts

When sources disagree:

- record the disagreement;
- state which behavior the engine uses and why;
- prefer direct measurement and current evidence over an older pinned implementation;
- do not silently choose `nikke-sim` because it is easier to encode.

A source conflict can justify a documented temporary scope lock, as with a visual
landing-time ambiguity, but the lock must remain visible in code/docs until resolved.

## Research-result rule

Any mechanics correction that can change damage totals invalidates affected aggregate
checkpoints until they are rerun. Old result documents may remain for history, but they
must not be presented as current verified results after such a correction.
