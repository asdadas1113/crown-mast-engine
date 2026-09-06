from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import FPS, DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class EpinelSkillHook(SkillHookBase):
    """Single immortal boss implementation of Epinel's kit."""

    def __init__(self, context: SkillHookContext) -> None:
        pass

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
        return (
            DamageRequest(
                time=event.time,
                actor=context.actor,
                source="burst_safe_50_50",
                category=DamageCategory.BURST,
                coefficient_pct=context.definition.skill_value(
                    "burst", "damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.BURST,
                    core_eligible=False,
                    full_burst_eligible=False,
                    range_eligible=False,
                ),
            ),
        )

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor or not shot.last_bullet:
            return ()

        start = round(shot.time + 1 / FPS, 6)
        end = start + context.definition.skill_value(
            "skill2", "duration_sec"
        )
        return (
            BuffWindow(
                source=context.actor,
                skill="skill2_last_bullet",
                stat="crit_rate_pct",
                value=context.definition.skill_value(
                    "skill2", "crit_rate_pct"
                ),
                target=context.actor,
                start=start,
                end=end,
            ),
            BuffWindow(
                source=context.actor,
                skill="skill2_last_bullet",
                stat="crit_damage_pct",
                value=context.definition.skill_value(
                    "skill2", "crit_damage_pct"
                ),
                target=context.actor,
                start=start,
                end=end,
            ),
        )
