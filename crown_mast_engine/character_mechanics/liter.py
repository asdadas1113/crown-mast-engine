from __future__ import annotations

from ..buffs import BuffWindow
from ..mechanics import SkillHookBase, SkillHookContext
from ..models import BattleEvent, EventType


class LiterSkillHook(SkillHookBase):
    def __init__(self, context: SkillHookContext) -> None:
        pass

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        casts = [
            event
            for event in events
            if event.event_type == EventType.B1_CAST
            and event.actor == context.actor
        ]
        buffs: list[BuffWindow] = []
        duration = context.definition.skill_value("skill1", "duration_sec")
        for cast_count, event in enumerate(casts, start=1):
            buffs.extend(
                self._team_buff(
                    context,
                    skill="skill1_burst_cast",
                    stat="max_ammo_pct",
                    value=context.definition.skill_value(
                        "skill1",
                        "max_ammo_pct",
                    ),
                    start=event.time,
                    duration=duration,
                )
            )
            if cast_count >= 2:
                buffs.extend(
                    self._team_buff(
                        context,
                        skill="skill1_burst_cast",
                        stat="crit_damage_pct",
                        value=context.definition.skill_value(
                            "skill1",
                            "crit_damage_pct",
                        ),
                        start=event.time,
                        duration=duration,
                    )
                )
            if cast_count >= 3:
                buffs.extend(
                    self._team_buff(
                        context,
                        skill="skill1_burst_cast",
                        stat="atk_pct",
                        value=context.definition.skill_value(
                            "skill1",
                            "atk_pct",
                        ),
                        start=event.time,
                        duration=duration,
                    )
                )
            buffs.extend(
                self._team_buff(
                    context,
                    skill="burst",
                    stat="atk_pct",
                    value=context.definition.skill_value("burst", "atk_pct"),
                    start=event.time,
                    duration=context.definition.skill_value(
                        "burst",
                        "duration_sec",
                    ),
                )
            )
        return tuple(buffs)

    @staticmethod
    def _team_buff(
        context: SkillHookContext,
        *,
        skill: str,
        stat: str,
        value: float,
        start: float,
        duration: float,
    ) -> tuple[BuffWindow, ...]:
        return tuple(
            BuffWindow(
                source=context.actor,
                skill=skill,
                stat=stat,
                value=value,
                target=target,
                start=start,
                end=start + duration,
            )
            for target in context.roster.members
        )
