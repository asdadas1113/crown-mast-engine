from __future__ import annotations

from dataclasses import dataclass

from .models import DamageCategory


@dataclass(frozen=True)
class DamageTraits:
    category: DamageCategory
    distributed: bool = False
    projectile_attachment: bool = False
    projectile_explosion: bool = False
    charged: bool = False
    sequential: bool = False
    sustained: bool = False
    crit_eligible: bool = True
    full_burst_eligible: bool = True
    range_eligible: bool = True
    core_eligible: bool = True
    forced_core: bool = False
    element_eligible: bool = True


@dataclass(frozen=True)
class DamageContext:
    static_atk: float
    coefficient_pct: float
    boss_def: float = 12_000.0
    boss_def_pct: float = 0.0
    atk_pct: float = 0.0
    caster_atk_flat: float = 0.0
    special_atk_flat: float = 0.0
    full_burst_bonus_pct: float = 0.0
    range_bonus_pct: float = 0.0
    expected_crit_bonus_pct: float = 0.0
    core_bonus_pct: float = 0.0
    element_multiplier: float = 1.0
    charge_multiplier: float = 1.0
    attack_damage_pct: float = 0.0
    projectile_attachment_pct: float = 0.0
    projectile_explosion_pct: float = 0.0
    sequential_damage_pct: float = 0.0
    sustained_damage_pct: float = 0.0
    sequential_multiplier: float = 1.0
    boss_damage_taken_pct: float = 0.0
    boss_distributed_taken_pct: float = 0.0
    ally_distributed_damage_pct: float = 0.0


@dataclass(frozen=True)
class DamageBreakdown:
    effective_atk: float
    boss_def_now: float
    base_atk: float
    coefficient: float
    major: float
    element: float
    charge: float
    damage_up: float
    sequential: float
    taken: float
    distributed: float
    total: float


def calculate_damage(context: DamageContext, traits: DamageTraits) -> DamageBreakdown:
    effective_atk = (
        context.static_atk * (1 + context.atk_pct / 100)
        + context.caster_atk_flat
        + context.special_atk_flat
    )
    boss_def_now = max(0.0, context.boss_def * (1 + context.boss_def_pct / 100))
    base_atk = max(0.0, effective_atk - boss_def_now)

    major_pct = context.range_bonus_pct if traits.range_eligible else 0.0
    if traits.full_burst_eligible:
        major_pct += context.full_burst_bonus_pct
    if traits.crit_eligible:
        major_pct += context.expected_crit_bonus_pct
    if traits.core_eligible:
        major_pct += context.core_bonus_pct
    major = 1 + major_pct / 100

    element = context.element_multiplier if traits.element_eligible else 1.0
    charge = context.charge_multiplier if traits.charged else 1.0

    damage_up_pct = context.attack_damage_pct
    if traits.projectile_attachment:
        damage_up_pct += context.projectile_attachment_pct
    if traits.projectile_explosion:
        damage_up_pct += context.projectile_explosion_pct
    if traits.sequential:
        damage_up_pct += context.sequential_damage_pct
    if traits.sustained:
        damage_up_pct += context.sustained_damage_pct
    damage_up = 1 + damage_up_pct / 100

    sequential = context.sequential_multiplier if traits.sequential else 1.0

    # Moris calculator and NIKKE.gg both place Distributed Damage in the same
    # Damage Taken multiplier as ordinary enemy Damage Taken.  Therefore an
    # ally-side Distributed Damage buff must add into this bucket rather than
    # multiply as an independent layer.  Enemy-side distributed-taken remains
    # conditionally enabled by the runtime profile represented here.
    distributed_taken_pct = 0.0
    if traits.distributed and context.boss_damage_taken_pct > 0:
        distributed_taken_pct = context.boss_distributed_taken_pct
    ally_distributed_pct = (
        context.ally_distributed_damage_pct if traits.distributed else 0.0
    )
    taken = 1 + (
        context.boss_damage_taken_pct
        + distributed_taken_pct
        + ally_distributed_pct
    ) / 100

    # Retained for report-schema compatibility.  The distributed contribution
    # now lives inside `taken`, so there is no second multiplicative layer.
    distributed = 1.0
    coefficient = context.coefficient_pct / 100

    total = (
        base_atk
        * coefficient
        * major
        * element
        * charge
        * damage_up
        * sequential
        * taken
        * distributed
    )
    return DamageBreakdown(
        effective_atk=effective_atk,
        boss_def_now=boss_def_now,
        base_atk=base_atk,
        coefficient=coefficient,
        major=major,
        element=element,
        charge=charge,
        damage_up=damage_up,
        sequential=sequential,
        taken=taken,
        distributed=distributed,
        total=total,
    )