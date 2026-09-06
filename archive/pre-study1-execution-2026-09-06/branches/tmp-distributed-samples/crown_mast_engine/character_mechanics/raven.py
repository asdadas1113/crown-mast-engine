from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class RavenSkillHook(SkillHookBase):
    """Single stage-target boss implementation of Raven.

    Each Full Charge attack appends an independent 5-second sustained-damage
    instance. At the pinned RL cadence fewer than 10 instances can overlap, so the
    kit's 10-stack cap is non-binding and does not require an additional runtime
    state machine in this scope.

    Damage-to-parts buffs and the part-destroy Single Point Attack route are retained
    in character data for provenance but are inert/unreachable against the base
    partless boss model.
    """

    def __init__(self, context: SkillHookContext) -> None:
        pass

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        return tuple(
            BuffWindow(
                source=context.actor,
                skill="skill1_full_burst",
                stat="caster_atk_pct",
                value=context.definition.skill_value(
                    "skill1", "full_burst_caster_atk_pct"
                ),
                target=context.actor,
                start=event.time,
                end=event.time
                + context.definition.skill_value(
                    "skill1", "full_burst_duration_sec"
                ),
                caster=context.actor,
            )
            for event in events
            if event.event_type == EventType.FULL_BURST_ENTER
        )

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
            BuffWindow(
                source=context.actor,
                skill="burst_an_mode",
                stat="sustained_damage_pct",
                value=context.definition.skill_value(
                    "burst", "sustained_damage_pct"
                ),
                target=context.actor,
                start=event.time,
                end=event.time
                + context.definition.skill_value("burst", "duration_sec"),
            ),
            DamageRequest(
                time=event.time,
                actor=context.actor,
                source="burst_nuke",
                category=DamageCategory.BURST,
                coefficient_pct=context.definition.skill_value(
                    "burst", "damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.BURST,
                    core_eligible=False,
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

        interval = context.definition.skill_value(
            "skill1", "sustained_interval_sec"
        )
        duration = context.definition.skill_value(
            "skill1", "sustained_duration_sec"
        )
        ticks = int(round(duration / interval))
        return tuple(
            DamageRequest(
                time=round(shot.time + interval * tick, 6),
                actor=context.actor,
                source="skill1_sustained_dot",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill1", "sustained_damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    sustained=True,
                    core_eligible=False,
                    range_eligible=False,
                ),
                shot_index=shot.shot_index,
                magazine_index=shot.magazine_index,
            )
            for tick in range(1, ticks + 1)
        )
