from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class RavenSkillHook(SkillHookBase):
    """Single stage-target boss implementation of Raven.

    Shock Wave is one target DoT state: each Full Charge adds one stack up to 10
    and refreshes the whole state's 5s duration. Its 1s tick reads the live stack
    count. This matches Moris' max_stack + scaling=stack_count representation and
    NIKKE.gg's explicit add-stack-and-refresh description.
    """

    _STACK_STAT = "raven_sustained_stack_count"

    def __init__(self, context: SkillHookContext) -> None:
        self._sustained_stacks = 0
        self._sustained_until = 0.0
        self._next_dot_tick: float | None = None
        self._scheduled_ticks: set[float] = set()

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
                value=context.definition.skill_value("burst", "sustained_damage_pct"),
                target=context.actor,
                start=event.time,
                end=event.time + context.definition.skill_value("burst", "duration_sec"),
            ),
            DamageRequest(
                time=event.time,
                actor=context.actor,
                source="burst_nuke",
                category=DamageCategory.BURST,
                coefficient_pct=context.definition.skill_value("burst", "damage_pct"),
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
        if shot.actor != context.actor or not shot.charged:
            return ()

        interval = context.definition.skill_value("skill1", "sustained_interval_sec")
        duration = context.definition.skill_value("skill1", "sustained_duration_sec")
        max_stacks = int(context.definition.skill_value("skill1", "sustained_max_stacks"))

        if shot.time > self._sustained_until:
            self._sustained_stacks = 0
            self._next_dot_tick = round(shot.time + interval, 6)

        self._sustained_stacks = min(max_stacks, self._sustained_stacks + 1)
        self._sustained_until = round(shot.time + duration, 6)
        if self._next_dot_tick is None:
            self._next_dot_tick = round(shot.time + interval, 6)

        effects: list[SkillEffect] = [
            BuffWindow(
                source=context.actor,
                skill="skill1_sustained_stack_state",
                stat=self._STACK_STAT,
                value=float(self._sustained_stacks),
                target=context.actor,
                start=shot.time,
                # Include the terminal 5s tick on the half-open BuffWindow interval.
                end=self._sustained_until + 1e-6,
            )
        ]

        while self._next_dot_tick <= self._sustained_until + 1e-9:
            tick_time = round(self._next_dot_tick, 6)
            if tick_time not in self._scheduled_ticks:
                self._scheduled_ticks.add(tick_time)
                effects.append(
                    DamageRequest(
                        time=tick_time,
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
                        coefficient_multiplier_stat=self._STACK_STAT,
                    )
                )
            self._next_dot_tick = round(self._next_dot_tick + interval, 6)

        return tuple(effects)
