from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class RapiRedHoodSkillHook(SkillHookBase):
    """Formation-branched Rapi: Red Hood implementation.

    Moris parsed skills and NIKKE.gg are the primary cross-checks here; the
    pinned nikke-sim snapshot is secondary structured provenance only.
    When Rapi occupies the B1 slot herself, Combat Assist is active: she supplies
    the B1 cast and the team Full-Burst Attack-Damage buff instead of the 95.04%
    self-ATK Full-Burst buff. Her 7.48s team CDR and 20s self B1 CDR are real kit
    lines, but this Crown-Mast study intentionally keeps its externally measured
    RAID14 timestamps fixed, so those two timing effects do not move the timeline.
    """

    COMBAT_ASSIST_TEAM_CDR_SEC = 7.48
    COMBAT_ASSIST_ATTACK_DAMAGE_PCT = 8.02
    B1_SELF_CDR_SEC = 20.0
    B1_CASTER_ATK_PCT = 18.01
    COMBAT_ASSIST_DURATION_SEC = 10.0

    def __init__(self, context: SkillHookContext) -> None:
        self._combat_assist = context.roster.b1 == context.actor
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
                    "skill2", "projectile_attachment_pct"
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
                    "skill2", "projectile_explosion_pct"
                ),
                target=context.actor,
                start=0.0,
                end=inf,
            ),
        ]
        targets = tuple(dict.fromkeys(context.roster.members))
        for event in events:
            if (
                event.event_type == EventType.B1_CAST
                and event.actor == context.actor
                and self._combat_assist
            ):
                for target in targets:
                    buffs.append(
                        BuffWindow(
                            source=context.actor,
                            skill="burst_stage1",
                            stat="caster_atk_pct",
                            value=self.B1_CASTER_ATK_PCT,
                            target=target,
                            start=event.time,
                            end=event.time + self.COMBAT_ASSIST_DURATION_SEC,
                            caster=context.actor,
                            snapshot=True,
                        )
                    )
                continue

            if event.event_type == EventType.FULL_BURST_ENTER:
                if self._combat_assist:
                    for target in targets:
                        buffs.append(
                            BuffWindow(
                                source=context.actor,
                                skill="skill1_combat_assist",
                                stat="attack_damage_pct",
                                value=self.COMBAT_ASSIST_ATTACK_DAMAGE_PCT,
                                target=target,
                                start=event.time,
                                end=event.time + self.COMBAT_ASSIST_DURATION_SEC,
                            )
                        )
                else:
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
                            "burst", "projectile_attachment_pct"
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
                "burst", "duration_sec"
            )
            if self._pulls < context.definition.skill_value("burst", "required_pulls"):
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
                    coefficient_pct=context.definition.skill_value("burst", "damage_pct"),
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
                        "skill2", "attachment_damage_pct"
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
