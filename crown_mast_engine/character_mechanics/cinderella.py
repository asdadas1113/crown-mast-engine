from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class CinderellaSkillHook(SkillHookBase):
    """Controlled single-boss implementation of original Cinderella.

    The Crown-Mast baseline has no incoming enemy damage, so Cinderella's Decoy is
    treated as continuously alive.  Beautiful therefore accumulates deterministically
    every three seconds until 12 stacks.  Entering Burst Stage III grants her Max-HP
    to ATK conversion regardless of which B3 actor casts, matching the audited trigger.

    Her unusual RL cadence is declared in character data and handled by the shared
    triggered-charge cadence extension: one normal full charge starts +100% charge
    speed, the weapon is capped at three shots/s, and a real reload to max ammo resets
    that acceleration.
    """

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        interval = context.definition.skill_value("skill2", "beautiful_interval_sec")
        per_stack = context.definition.skill_value(
            "skill2", "beautiful_max_hp_pct_per_stack"
        )
        max_stacks = int(
            context.definition.skill_value("skill2", "beautiful_max_stacks")
        )
        buffs: list[BuffWindow] = []
        for stack in range(1, max_stacks + 1):
            start = interval * stack
            if start >= context.duration_sec:
                break
            buffs.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill2_beautiful",
                    stat="max_hp_pct",
                    value=per_stack * stack,
                    target=context.actor,
                    start=start,
                    end=inf,
                )
            )
        return tuple(buffs)

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if event.event_type != EventType.B3_STAGE_ENTER:
            return ()

        effects: list[SkillEffect] = [
            BuffWindow(
                source=context.actor,
                skill="skill1_flawless_glass",
                stat="max_hp_to_atk_pct",
                value=context.definition.skill_value("skill1", "max_hp_to_atk_pct"),
                target=context.actor,
                start=event.time,
                end=event.time
                + context.definition.skill_value("skill1", "duration_sec"),
            )
        ]

        if event.actor != context.actor:
            return tuple(effects)

        sequential_hits = context.definition.skill_value("burst", "sequential_hits")
        burst_traits = DamageTraits(
            category=DamageCategory.BURST,
            sequential=True,
            core_eligible=False,
            range_eligible=False,
            full_burst_eligible=False,
        )
        effects.append(
            DamageRequest(
                time=event.time,
                actor=context.actor,
                source="burst_glass_slippers_full_contact",
                category=DamageCategory.BURST,
                coefficient_pct=context.definition.skill_value("burst", "damage_pct"),
                traits=burst_traits,
                sequential_multiplier=sequential_hits,
            )
        )

        interval = context.definition.skill_value("skill2", "beautiful_interval_sec")
        max_stacks = int(
            context.definition.skill_value("skill2", "beautiful_max_stacks")
        )
        beautiful_stacks = min(max_stacks, int(event.time // interval))
        if beautiful_stacks > 0:
            effects.append(
                DamageRequest(
                    time=event.time,
                    actor=context.actor,
                    source="burst_beautiful_additional",
                    category=DamageCategory.BURST,
                    coefficient_pct=(
                        context.definition.skill_value(
                            "burst", "beautiful_additional_damage_pct_per_stack"
                        )
                        * beautiful_stacks
                    ),
                    traits=burst_traits,
                    sequential_multiplier=sequential_hits,
                )
            )
        return tuple(effects)

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor or not shot.charged:
            return ()
        return (
            DamageRequest(
                time=shot.time,
                actor=context.actor,
                source="skill1_full_charge_additional",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill1", "full_charge_additional_damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    core_eligible=False,
                    range_eligible=False,
                ),
                shot_index=shot.shot_index,
                magazine_index=shot.magazine_index,
            ),
        )
