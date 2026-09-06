from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import DamageRequest
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class CinderellaCrystalWaveSkillHook(SkillHookBase):
    """MG-only single-boss implementation of Cinderella: Crystal Wave.

    The research scope intentionally keeps her in the default MG state for the whole
    battle. Snipe Mode, the double-reload state machine, its 40-round ammo spend, and
    the Preparation-for-Change reload clamp are therefore outside this implementation.

    Her 200-team-ammo Burst Gauge fill is retained in character data but is not fed
    back into the engine: Crown-Mast research uses an externally fixed measured burst
    timeline, so character gauge generation is not allowed to move cycle timestamps.
    """

    def __init__(self, context: SkillHookContext) -> None:
        self._interval_scheduled = False

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        return (
            BuffWindow(
                source=context.actor,
                skill="skill1_beauty_full",
                stat="attack_damage_pct",
                value=context.definition.skill_value(
                    "skill1", "beauty_full_attack_damage_pct"
                ),
                target=context.actor,
                start=0.0,
                end=inf,
            ),
            BuffWindow(
                source=context.actor,
                skill="skill2_passive_atk",
                stat="atk_pct",
                value=context.definition.skill_value("skill2", "passive_atk_pct"),
                target=context.actor,
                start=0.0,
                end=inf,
            ),
            BuffWindow(
                source=context.actor,
                skill="skill2_pinpoint",
                stat="core_damage_pct",
                value=context.definition.skill_value("skill2", "mg_core_damage_pct"),
                target=context.actor,
                start=0.0,
                end=inf,
            ),
        )

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        effects: list[SkillEffect] = []

        if not self._interval_scheduled:
            interval = context.definition.skill_value("skill1", "interval_sec")
            tick = interval
            while tick < context.duration_sec:
                effects.append(
                    DamageRequest(
                        time=round(tick, 6),
                        actor=context.actor,
                        source="skill1_interval_damage",
                        category=DamageCategory.SKILL,
                        coefficient_pct=context.definition.skill_value(
                            "skill1", "interval_damage_pct"
                        ),
                        traits=DamageTraits(
                            category=DamageCategory.SKILL,
                            core_eligible=False,
                            range_eligible=False,
                        ),
                    )
                )
                tick += interval
            self._interval_scheduled = True

        if event.event_type == EventType.FULL_BURST_ENTER:
            burst_casters = tuple(event.payload.get("burst_casters", ()))
            if context.actor in burst_casters:
                effects.append(
                    DamageRequest(
                        time=event.time,
                        actor=context.actor,
                        source="skill2_mg_full_burst_core_strike",
                        category=DamageCategory.SKILL,
                        coefficient_pct=context.definition.skill_value(
                            "skill2", "mg_full_burst_core_strike_pct"
                        ),
                        traits=DamageTraits(
                            category=DamageCategory.SKILL,
                            core_eligible=True,
                            forced_core=True,
                            range_eligible=False,
                        ),
                    )
                )

        if event.event_type == EventType.B3_STAGE_ENTER and event.actor == context.actor:
            duration = context.definition.skill_value("burst", "duration_sec")
            effects.extend(
                (
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
                    BuffWindow(
                        source=context.actor,
                        skill="burst",
                        stat="atk_pct",
                        value=context.definition.skill_value("burst", "atk_pct"),
                        target=context.actor,
                        start=event.time,
                        end=event.time + duration,
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
                    full_burst_eligible=False,
                            range_eligible=False,
                        ),
                    ),
                )
            )

        return tuple(effects)
