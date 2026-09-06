from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class AnisStarSkillHook(SkillHookBase):
    def __init__(self, context: SkillHookContext) -> None:
        pass

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        buffs = [
            BuffWindow(
                source=context.actor,
                skill="skill1_sole_b1",
                stat="atk_pct",
                value=context.definition.skill_value("skill1", "self_atk_pct"),
                target=context.actor,
                start=0.0,
                end=inf,
            )
        ]
        team_duration = context.definition.skill_value("skill2", "duration_sec")
        burst_duration = context.definition.skill_value("burst", "duration_sec")
        for event in events:
            if event.event_type == EventType.FULL_BURST_ENTER:
                for target in context.roster.members:
                    buffs.extend(
                        (
                            BuffWindow(
                                source=context.actor,
                                skill="skill2_full_burst",
                                stat="caster_atk_pct",
                                value=context.definition.skill_value(
                                    "skill2", "caster_atk_pct"
                                ),
                                target=target,
                                start=event.time,
                                end=event.time + team_duration,
                                caster=context.actor,
                                snapshot=True,
                            ),
                            BuffWindow(
                                source=context.actor,
                                skill="skill2_full_burst",
                                stat="attack_damage_pct",
                                value=context.definition.skill_value(
                                    "skill2", "attack_damage_pct"
                                ),
                                target=target,
                                start=event.time,
                                end=event.time + team_duration,
                            ),
                            # The current research roster treats its offensive
                            # allies as below Anis' DEF. DEF targeting is recorded
                            # as an explicit scope limitation in the README.
                            BuffWindow(
                                source=context.actor,
                                skill="skill2_full_burst",
                                stat="projectile_explosion_pct",
                                value=context.definition.skill_value(
                                    "skill2", "projectile_explosion_pct"
                                ),
                                target=target,
                                start=event.time,
                                end=event.time + team_duration,
                            ),
                        )
                    )
            elif event.event_type == EventType.B1_CAST and event.actor == context.actor:
                buffs.extend(
                    (
                        BuffWindow(
                            source=context.actor,
                            skill="burst",
                            stat="attack_damage_pct",
                            value=context.definition.skill_value(
                                "burst", "self_attack_damage_pct"
                            ),
                            target=context.actor,
                            start=event.time,
                            end=event.time + burst_duration,
                        ),
                        BuffWindow(
                            source=context.actor,
                            skill="burst",
                            stat="charge_time_fixed_frames",
                            value=context.definition.skill_value(
                                "burst", "fixed_charge_frames"
                            ),
                            target=context.actor,
                            start=event.time,
                            end=event.time + burst_duration,
                        ),
                    )
                )
        return tuple(buffs)

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if event.event_type != EventType.B1_CAST or event.actor != context.actor:
            return ()

        duration = context.definition.skill_value("burst", "duration_sec")
        interval = context.definition.skill_value(
            "burst", "shooting_star_tick_interval_sec"
        )
        ticks = int(round(duration / interval))
        return tuple(
            DamageRequest(
                time=round(event.time + tick * interval, 6),
                actor=context.actor,
                source="burst_shooting_star",
                category=DamageCategory.NORMAL,
                coefficient_pct=context.definition.skill_value(
                    "burst", "shooting_star_damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.NORMAL,
                    projectile_explosion=True,
                    core_eligible=False,
                ),
            )
            for tick in range(ticks)
        )

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
                source="skill1_full_charge",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill1", "full_charge_damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    core_eligible=False,
                ),
                shot_index=shot.shot_index,
                magazine_index=shot.magazine_index,
            ),
        )
