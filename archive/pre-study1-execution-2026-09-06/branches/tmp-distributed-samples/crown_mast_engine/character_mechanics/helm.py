from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import FPS, DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import (
    RecoveryEffect,
    SkillEffect,
    SkillHookBase,
    SkillHookContext,
    WeaponShotModifier,
)
from ..models import BattleEvent, DamageCategory, EventType


class HelmSkillHook(SkillHookBase):
    def __init__(self, context: SkillHookContext) -> None:
        self._enhanced_rounds = 0

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
                    skill="skill2_passive",
                    stat="parts_damage_pct",
                    value=context.definition.skill_value(
                        "skill2",
                        "parts_damage_pct",
                    ),
                    target=target,
                    start=0.0,
                    end=inf,
                )
            )
        for event in events:
            if event.event_type != EventType.FULL_BURST_ENTER:
                continue
            for target in context.roster.members:
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill2_full_burst",
                        stat="attack_damage_pct",
                        value=context.definition.skill_value(
                            "skill2",
                            "attack_damage_pct",
                        ),
                        target=target,
                        start=event.time,
                        end=event.time
                        + context.definition.skill_value(
                            "skill2",
                            "attack_damage_duration_sec",
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

        self._enhanced_rounds = int(
            context.definition.skill_value("burst", "charge_damage_rounds")
        )
        effects: list[SkillEffect] = [
            DamageRequest(
                time=event.time,
                actor=context.actor,
                source="burst_nuke",
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
            )
        ]

        ticks = int(context.definition.skill_value("burst", "recovery_ticks"))
        interval = context.definition.skill_value(
            "burst",
            "recovery_interval_sec",
        )
        for tick in range(ticks):
            recovery_time = round(event.time + tick * interval + 1 / FPS, 6)
            for target in context.roster.members:
                effects.append(RecoveryEffect(recovery_time, target))
        return tuple(effects)

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor or not shot.charged:
            return ()

        effects: list[SkillEffect] = []
        if self._enhanced_rounds > 0:
            effects.append(
                WeaponShotModifier(
                    actor=context.actor,
                    shot_index=shot.shot_index,
                    charge_damage_mult_pct=context.definition.skill_value(
                        "burst",
                        "charge_damage_mult_pct",
                    ),
                )
            )
            self._enhanced_rounds = max(
                0,
                self._enhanced_rounds - shot.rounds_consumed,
            )

        effects.append(
            DamageRequest(
                time=shot.time,
                actor=context.actor,
                source="skill2_full_charge",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill2",
                    "full_charge_damage_pct",
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    core_eligible=False,
                    range_eligible=False,
                ),
                shot_index=shot.shot_index,
                magazine_index=shot.magazine_index,
            )
        )

        after_hit = round(shot.time + 1 / FPS, 6)
        for target in context.roster.members:
            effects.append(RecoveryEffect(after_hit, target))
        if shot.last_bullet:
            for target in context.roster.members:
                effects.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_last_bullet",
                        stat="crit_rate_normal_pct",
                        value=context.definition.skill_value(
                            "skill1",
                            "crit_rate_normal_pct",
                        ),
                        target=target,
                        start=after_hit,
                        end=after_hit
                        + context.definition.skill_value(
                            "skill1",
                            "crit_duration_sec",
                        ),
                    )
                )
        return tuple(effects)
