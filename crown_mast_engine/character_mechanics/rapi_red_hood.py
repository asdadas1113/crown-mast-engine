from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class RapiRedHoodSkillHook(SkillHookBase):
    def __init__(self, context: SkillHookContext) -> None:
        if not context.roster.b1 or context.roster.b1 == context.actor:
            raise NotImplementedError(
                "Rapi: Red Hood Combat Assist mode without a separate B1 is not implemented"
            )
        self._pulls = 0
        self._rocket_meter = 0
        self._stored_rockets = 0
        self._own_stage3_until = 0.0

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        buffs = [
            BuffWindow(
                source=context.actor,
                skill="skill2_passive",
                stat="projectile_attachment_pct",
                value=context.definition.skill_value(
                    "skill2",
                    "projectile_attachment_pct",
                ),
                target=context.actor,
                start=0.0,
                end=inf,
            ),
            BuffWindow(
                source=context.actor,
                skill="skill2_passive",
                stat="projectile_explosion_pct",
                value=context.definition.skill_value(
                    "skill2",
                    "projectile_explosion_pct",
                ),
                target=context.actor,
                start=0.0,
                end=inf,
            ),
        ]
        for event in events:
            if event.event_type == EventType.FULL_BURST_ENTER:
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_full_burst",
                        stat="atk_pct",
                        value=context.definition.skill_value("skill1", "atk_pct"),
                        target=context.actor,
                        start=event.time,
                        end=event.time
                        + context.definition.skill_value("skill1", "duration_sec"),
                    )
                )
            elif (
                event.event_type == EventType.B3_STAGE_ENTER
                and event.actor == context.actor
            ):
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="burst_stage3",
                        stat="projectile_attachment_pct",
                        value=context.definition.skill_value(
                            "burst",
                            "projectile_attachment_pct",
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time
                        + context.definition.skill_value("burst", "duration_sec"),
                    )
                )
        return tuple(buffs)

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if (
            event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == context.actor
        ):
            self._own_stage3_until = event.time + context.definition.skill_value(
                "burst",
                "duration_sec",
            )
            if self._pulls < context.definition.skill_value(
                "burst",
                "required_pulls",
            ):
                return ()
            return (
                DamageRequest(
                    time=round(
                        event.time
                        + context.definition.skill_value("burst", "delay_sec"),
                        6,
                    ),
                    actor=context.actor,
                    source="burst_stage3_missile",
                    category=DamageCategory.BURST,
                    coefficient_pct=context.definition.skill_value(
                        "burst",
                        "damage_pct",
                    ),
                    traits=DamageTraits(
                        category=DamageCategory.BURST,
                        core_eligible=False,
                        range_eligible=False,
                    ),
                ),
            )

        if event.event_type != EventType.FULL_BURST_ENTER or self._stored_rockets == 0:
            return ()
        stored = self._stored_rockets
        self._stored_rockets = 0
        return (self._explosion_request(event.time, stored, context),)

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor:
            return ()
        self._pulls += 1
        self._rocket_meter += 1
        threshold = int(
            context.definition.skill_value(
                "skill2",
                (
                    "own_burst_attack_count"
                    if shot.time < self._own_stage3_until
                    else "normal_attack_count"
                ),
            )
        )
        effects: list[SkillEffect] = []
        while self._rocket_meter >= threshold:
            self._rocket_meter -= threshold
            effects.append(
                DamageRequest(
                    time=shot.time,
                    actor=context.actor,
                    source="skill2_rocket_attachment",
                    category=DamageCategory.SKILL,
                    coefficient_pct=context.definition.skill_value(
                        "skill2",
                        "attachment_damage_pct",
                    ),
                    traits=DamageTraits(
                        category=DamageCategory.SKILL,
                        projectile_attachment=True,
                        core_eligible=True,
                        range_eligible=False,
                    ),
                    shot_index=shot.shot_index,
                    magazine_index=shot.magazine_index,
                )
            )
            if self._is_full_burst(shot.time, context):
                effects.append(self._explosion_request(shot.time, 1, context))
            else:
                self._stored_rockets += 1
        return tuple(effects)

    @staticmethod
    def _is_full_burst(time: float, context: SkillHookContext) -> bool:
        return any(
            cycle.full_burst_start <= time < cycle.full_burst_end
            for cycle in context.timeline
        )

    @staticmethod
    def _explosion_request(
        time: float,
        rockets: int,
        context: SkillHookContext,
    ) -> DamageRequest:
        return DamageRequest(
            time=time,
            actor=context.actor,
            source="skill2_rocket_explosion",
            category=DamageCategory.SKILL,
            coefficient_pct=(
                context.definition.skill_value("skill2", "explosion_damage_pct")
                * rockets
            ),
            traits=DamageTraits(
                category=DamageCategory.SKILL,
                projectile_explosion=True,
                core_eligible=False,
                range_eligible=False,
            ),
        )
