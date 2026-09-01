from __future__ import annotations

from dataclasses import replace
from math import inf

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import (
    SkillEffect,
    SkillHookBase,
    SkillHookContext,
    WeaponMode,
    WeaponShotModifier,
)
from ..models import BattleEvent, DamageCategory, EventType


class SnowWhiteHeavyArmsSkillHook(SkillHookBase):
    """Single-target implementation of Snow White: Heavy Arms."""

    def __init__(self, context: SkillHookContext) -> None:
        pass

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        buffs: list[BuffWindow] = []
        for target in context.roster.members:
            buffs.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill1_lock_on",
                    stat="damage_taken_pct",
                    value=context.definition.skill_value(
                        "skill1", "damage_taken_pct"
                    ),
                    target=target,
                    start=0.0,
                    end=inf,
                )
            )
        buffs.append(
            BuffWindow(
                source=context.actor,
                skill="skill2_fixed_charge",
                stat="charge_time_fixed_frames",
                value=context.definition.skill_value(
                    "skill2", "fixed_charge_frames"
                ),
                target=context.actor,
                start=0.0,
                end=inf,
            )
        )

        b3_duration = context.definition.skill_value(
            "skill2", "b3_atk_duration_sec"
        )
        burst_duration = context.definition.skill_value("burst", "duration_sec")
        for event in events:
            if event.event_type == EventType.B3_STAGE_ENTER:
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill2_b3_stage",
                        stat="atk_pct",
                        value=context.definition.skill_value(
                            "skill2", "b3_atk_pct"
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time + b3_duration,
                    )
                )
            if (
                event.event_type == EventType.B3_STAGE_ENTER
                and event.actor == context.actor
            ):
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="burst_fully_active",
                        stat="attack_damage_pct",
                        value=context.definition.skill_value(
                            "burst", "attack_damage_pct"
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time + burst_duration,
                    )
                )
        return tuple(buffs)

    def scheduled_weapon_modes(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[WeaponMode, ...]:
        duration = context.definition.skill_value("burst", "duration_sec")
        weapon = replace(
            context.definition.weapon,
            charge_frames=int(
                context.definition.skill_value(
                    "burst", "fully_active_charge_frames"
                )
            ),
        )
        return tuple(
            WeaponMode(
                actor=context.actor,
                name="seven-dwarves-fully-active",
                start=event.time,
                end=event.time + duration,
                weapon=weapon,
                pulls_per_second=1.0,
                max_shots=int(
                    context.definition.skill_value("burst", "fully_active_shots")
                ),
                refill_base_ammo_on_end=False,
                share_base_ammo=True,
            )
            for event in events
            if event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == context.actor
        )

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor or not shot.charged:
            return ()

        active = shot.weapon_mode == "seven-dwarves-fully-active"
        effects: list[SkillEffect] = [
            BuffWindow(
                source=context.actor,
                skill="skill2_full_charge",
                stat="atk_pct",
                value=context.definition.skill_value(
                    "skill2", "full_charge_atk_pct"
                ),
                target=context.actor,
                start=shot.time,
                end=shot.time
                + context.definition.skill_value(
                    "skill2", "full_charge_duration_sec"
                ),
            ),
            DamageRequest(
                time=shot.time,
                actor=context.actor,
                source="skill1_auto_fire_aoe",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill1", "auto_fire_aoe_damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    core_eligible=False,
                ),
                shot_index=shot.shot_index,
                magazine_index=shot.magazine_index,
            ),
            DamageRequest(
                time=shot.time,
                actor=context.actor,
                source="skill1_auto_fire_sequential",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill1", "auto_fire_sequential_damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    sequential=True,
                    core_eligible=False,
                ),
                shot_index=shot.shot_index,
                magazine_index=shot.magazine_index,
                sequential_damage_pct=(
                    context.definition.skill_value(
                        "skill2", "fully_active_sequential_damage_pct"
                    )
                    if active
                    else 0.0
                ),
            ),
        ]
        if active:
            effects.extend(
                (
                    WeaponShotModifier(
                        actor=context.actor,
                        shot_index=shot.shot_index,
                        charge_damage_pct=context.definition.skill_value(
                            "skill2", "fully_active_charge_damage_pct"
                        ),
                    ),
                    DamageRequest(
                        time=shot.time,
                        actor=context.actor,
                        source="skill1_fully_active_extra_sequential",
                        category=DamageCategory.SKILL,
                        coefficient_pct=context.definition.skill_value(
                            "skill1", "fully_active_extra_sequential_damage_pct"
                        ),
                        traits=DamageTraits(
                            category=DamageCategory.SKILL,
                            sequential=True,
                            core_eligible=False,
                        ),
                        shot_index=shot.shot_index,
                        magazine_index=shot.magazine_index,
                        sequential_damage_pct=context.definition.skill_value(
                            "skill2", "fully_active_sequential_damage_pct"
                        ),
                    ),
                )
            )
        return tuple(effects)
