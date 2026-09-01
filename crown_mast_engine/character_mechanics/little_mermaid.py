from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import AmmoChargeEffect, SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class LittleMermaidSkillHook(SkillHookBase):
    def __init__(self, context: SkillHookContext) -> None:
        self._team_ammo_consumed = 0

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
                    skill="skill2_bubble",
                    stat="damage_taken_pct",
                    value=context.definition.skill_value(
                        "skill2", "damage_taken_pct"
                    ),
                    target=target,
                    start=0.0,
                    end=inf,
                )
            )

        full_burst_duration = context.definition.skill_value(
            "skill1", "duration_sec"
        )
        burst_duration = context.definition.skill_value("burst", "duration_sec")
        for event in events:
            if event.event_type == EventType.FULL_BURST_ENTER:
                for target in context.roster.members:
                    buffs.append(
                        BuffWindow(
                            source=context.actor,
                            skill="skill1_full_burst",
                            stat="attack_damage_pct",
                            value=context.definition.skill_value(
                                "skill1", "attack_damage_pct"
                            ),
                            target=target,
                            start=event.time,
                            end=event.time + full_burst_duration,
                        )
                    )
            elif event.event_type == EventType.B1_CAST and event.actor == context.actor:
                for target in context.roster.members:
                    buffs.append(
                        BuffWindow(
                            source=context.actor,
                            skill="burst",
                            stat="attack_damage_pct",
                            value=context.definition.skill_value(
                                "burst", "attack_damage_pct"
                            ),
                            target=target,
                            start=event.time,
                            end=event.time + burst_duration,
                        )
                    )
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="burst_self",
                        stat="caster_atk_pct",
                        value=context.definition.skill_value(
                            "burst", "self_caster_atk_pct"
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time + burst_duration,
                        caster=context.actor,
                        snapshot=True,
                    )
                )
        return tuple(buffs)

    def ammo_charge_effects(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[AmmoChargeEffect, ...]:
        fraction = context.definition.skill_value("burst", "ammo_charge_pct")
        return tuple(
            AmmoChargeEffect(event.time, target, fraction)
            for event in events
            if event.event_type == EventType.B1_CAST and event.actor == context.actor
            for target in context.roster.members
        )

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if event.event_type != EventType.FULL_BURST_ENTER:
            return ()
        ticks = int(context.definition.skill_value("skill2", "bubble_wave_ticks"))
        interval = context.definition.skill_value(
            "skill2", "bubble_wave_interval_sec"
        )
        return tuple(
            DamageRequest(
                time=round(event.time + tick * interval, 6),
                actor=context.actor,
                source="skill2_bubble_wave",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill2", "bubble_wave_damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    sequential=True,
                    core_eligible=False,
                ),
                sequential_multiplier=context.definition.skill_value(
                    "skill2", "bubble_wave_hits"
                ),
            )
            for tick in range(ticks)
        )

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        self._team_ammo_consumed += shot.rounds_consumed
        threshold = int(
            context.definition.skill_value("skill2", "team_ammo_threshold")
        )
        if self._team_ammo_consumed < threshold:
            return ()

        effects: list[SkillEffect] = []
        while self._team_ammo_consumed >= threshold:
            self._team_ammo_consumed -= threshold
            effects.append(
                DamageRequest(
                    time=shot.time,
                    actor=context.actor,
                    source="skill2_bubble_barrage",
                    category=DamageCategory.SKILL,
                    coefficient_pct=context.definition.skill_value(
                        "skill2", "bubble_barrage_damage_pct"
                    ),
                    traits=DamageTraits(
                        category=DamageCategory.SKILL,
                        sequential=True,
                        core_eligible=False,
                    ),
                    sequential_multiplier=context.definition.skill_value(
                        "skill2", "bubble_barrage_hits"
                    ),
                )
            )
        return tuple(effects)
