from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class NeonVisionEyeSkillHook(SkillHookBase):
    """Single stage-target boss implementation of Neon: Vision Eye."""

    def __init__(self, context: SkillHookContext) -> None:
        self._firepower_gauge = 100
        self._charge_until = 0.0
        self._super_firepower_until = 0.0

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if (
            event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == context.actor
        ):
            return self._on_own_burst(event.time, context)

        if event.event_type == EventType.FULL_BURST_ENTER:
            duration = context.definition.skill_value(
                "skill2", "maximum_firepower_duration_sec"
            )
            effects: list[SkillEffect] = [
                BuffWindow(
                    source=context.actor,
                    skill="skill2_maximum_firepower",
                    stat="atk_pct",
                    value=context.definition.skill_value(
                        "skill2", "maximum_firepower_atk_pct"
                    ),
                    target=context.actor,
                    start=event.time,
                    end=event.time + duration,
                )
            ]
            if event.time < self._super_firepower_until:
                effects.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill2_super_firepower",
                        stat="atk_pct",
                        value=context.definition.skill_value(
                            "skill2", "super_firepower_atk_pct"
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time + duration,
                    )
                )
            return tuple(effects)

        if (
            event.event_type == EventType.FULL_BURST_END
            and self._charge_until
            and event.time >= self._charge_until
        ):
            self._firepower_gauge = min(
                100,
                self._firepower_gauge
                + int(
                    context.definition.skill_value(
                        "skill2", "charge_end_gauge_gain"
                    )
                ),
            )
            self._charge_until = 0.0
        return ()

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor or not shot.charged:
            return ()

        if 0 < self._charge_until and shot.time < self._charge_until:
            self._firepower_gauge = min(
                100,
                self._firepower_gauge
                + int(
                    context.definition.skill_value(
                        "skill2", "normal_attack_gauge_gain"
                    )
                ),
            )

        effects: list[SkillEffect] = [
            self._bonus_damage_request(
                shot,
                context,
                source="skill1_firepower_explosion",
                coefficient_key="firepower_explosion_damage_pct",
            )
        ]
        if shot.time < self._super_firepower_until:
            effects.append(
                self._bonus_damage_request(
                    shot,
                    context,
                    source="skill1_super_firepower_extra",
                    coefficient_key="super_firepower_extra_damage_pct",
                )
            )
        return tuple(effects)

    def _on_own_burst(
        self,
        time: float,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        duration = context.definition.skill_value("burst", "duration_sec")
        effects: list[SkillEffect] = [
            BuffWindow(
                source=context.actor,
                skill="burst_firepower_enhancement",
                stat="attack_damage_pct",
                value=context.definition.skill_value(
                    "burst", "attack_damage_pct"
                ),
                target=context.actor,
                start=time,
                end=time + duration,
            )
        ]
        if self._firepower_gauge >= 100:
            self._firepower_gauge = 0
            self._super_firepower_until = time + duration
            self._charge_until = 0.0
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="burst_super_firepower",
                    stat="attack_damage_pct",
                    value=context.definition.skill_value(
                        "burst", "super_firepower_attack_damage_pct"
                    ),
                    target=context.actor,
                    start=time,
                    end=time + duration,
                )
            )
        else:
            self._super_firepower_until = 0.0
            self._charge_until = time + duration
            self._firepower_gauge = min(
                100,
                self._firepower_gauge
                + int(
                    context.definition.skill_value(
                        "burst", "charge_start_gauge_gain"
                    )
                ),
            )
        return tuple(effects)

    @staticmethod
    def _bonus_damage_request(
        shot: WeaponShot,
        context: SkillHookContext,
        *,
        source: str,
        coefficient_key: str,
    ) -> DamageRequest:
        return DamageRequest(
            time=shot.time,
            actor=context.actor,
            source=source,
            category=DamageCategory.SKILL,
            coefficient_pct=context.definition.skill_value(
                "skill1", coefficient_key
            ),
            traits=DamageTraits(
                category=DamageCategory.SKILL,
                core_eligible=False,
                range_eligible=False,
            ),
            shot_index=shot.shot_index,
            magazine_index=shot.magazine_index,
        )
