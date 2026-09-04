from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import FPS, DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class LiberalioSkillHook(SkillHookBase):
    """Single stage-target boss implementation of Liberalio.

    The Crown-Mast research has one boss and no non-stage-target Raptures, so every
    Liberalio Full Charge enters/maintains Raging Current. Gentle Current is outside
    this scope. Her core-hit-gated 20.83% Attack Damage line is retained in data but
    remains inert while the base research uses 0% core hit rate.

    Current Prydwen and NIKKE.gg references independently describe the 925%
    Burst packet as additional damage landing about 1.1 seconds after cast. The
    delayed packet therefore uses Full Burst and the buffs active at landing.
    """

    def __init__(self, context: SkillHookContext) -> None:
        pass

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        other_b3 = (
            context.roster.secondary_b3
            if context.roster.main_b3 == context.actor
            else context.roster.main_b3
        )
        buffs: list[BuffWindow] = []
        for event in events:
            if event.event_type != EventType.FULL_BURST_ENTER:
                continue
            buffs.extend(
                (
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_full_burst",
                        stat="atk_pct",
                        value=context.definition.skill_value(
                            "skill1", "full_burst_atk_pct"
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time
                        + context.definition.skill_value(
                            "skill1", "full_burst_atk_duration_sec"
                        ),
                    ),
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_other_b3_charge_speed",
                        stat="charge_speed_pct",
                        value=context.definition.skill_value(
                            "skill1", "other_b3_charge_speed_pct"
                        ),
                        target=other_b3,
                        start=event.time,
                        end=event.time
                        + context.definition.skill_value(
                            "skill1", "other_b3_charge_speed_duration_sec"
                        ),
                    ),
                )
            )
        return tuple(buffs)

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if (
            event.event_type != EventType.B3_STAGE_ENTER
            or event.actor != context.actor
        ):
            return ()

        duration = context.definition.skill_value("burst", "duration_sec")
        return (
            BuffWindow(
                source=context.actor,
                skill="burst",
                stat="attack_damage_pct",
                value=context.definition.skill_value(
                    "burst", "attack_damage_pct"
                ),
                target=context.actor,
                start=event.time,
                end=event.time + duration,
            ),
            DamageRequest(
                time=round(
                    event.time
                    + context.definition.skill_value("burst", "landing_delay_sec"),
                    6,
                ),
                actor=context.actor,
                source="burst_nuke",
                category=DamageCategory.BURST,
                coefficient_pct=context.definition.skill_value(
                    "burst", "damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.BURST,
                    core_eligible=False,
                    full_burst_eligible=True,
                    range_eligible=False,
                ),
            ),
        )

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor or not shot.charged:
            return ()

        # Raging Current is gained by landing this Full Charge, so the triggering
        # shot itself must not receive the 231% Attack Damage buff.
        after_hit = round(shot.time + 1 / FPS, 6)
        return (
            BuffWindow(
                source=context.actor,
                skill="skill2_raging_current",
                stat="attack_damage_pct",
                value=context.definition.skill_value(
                    "skill2", "raging_current_attack_damage_pct"
                ),
                target=context.actor,
                start=after_hit,
                end=inf,
            ),
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
