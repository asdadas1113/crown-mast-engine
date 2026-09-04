# Distributed Damage bucket audit — 2026-09-02

## Conclusion

For Distributed Damage packets, an ally-side `Distributed Damage ▲` modifier shares the same Damage Taken multiplier with ordinary enemy `Damage Taken ▲`; it is additive inside that bucket rather than a separate multiplicative layer.

Current implementation rule:

```text
Taken factor for ordinary packet
= 1 + ordinary Damage Taken

Taken factor for distributed packet
= 1 + ordinary Damage Taken + applicable Distributed Damage modifiers
```

Example:

```text
Damage Taken +40%
Distributed Damage +40%

correct distributed factor = 1 + 0.40 + 0.40 = 1.80
not                        = 1.40 × 1.40 = 1.96
```

## Cross-validation

This rule was adopted only after independent current-source agreement, following `docs/SOURCE_VALIDATION_POLICY.md`.

1. Moris calculator source (`Jgaram/nikke-calc`, `calculator/damage.py`, master observed 2026-09-02): `_factor6` explicitly computes `1 + received_dmg + split_dmg_pct` for split/distributed packets.
2. NIKKE.gg Damage Formula, updated 2026-08-07: `Damage Taken = 1 + Damage Taken + Distributed Damage` and describes those terms as sharing the same category/multiplier.

The pinned `nikke-sim` snapshot is not used as the authority for this rule.

## Engine change

`crown_mast_engine/damage.py` now adds `ally_distributed_damage_pct` into `DamageBreakdown.taken` only for `DamageTraits.distributed=True` packets. `DamageBreakdown.distributed` is retained as `1.0` for report-schema compatibility and is no longer a second multiplier.

A regression test fixes the 40% + 40% example at a total factor of `1.80`, preventing accidental return to `1.96`.

Because this changes damage semantics for affected distributed-damage compositions, the engine rule revision was bumped to:

```text
2026-09-02-r10-audited-damage-buckets
```

Pre-existing development/checkpoint outputs are not canonical research results and are not regenerated here.
