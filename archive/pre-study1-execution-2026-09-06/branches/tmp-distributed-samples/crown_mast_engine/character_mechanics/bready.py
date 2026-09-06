from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class BreadySkillHook(SkillHookBase):
    """Crown-Mast research implementation of Bready's Recommended Taste route.

    In the current research roster Mast: Romantic Maid supplies a distributed-damage
    buff at B3 stage entry whenever Drunken stacks are present. That buff gain is the
    actual trigger for Recommended Taste, so this hook derives the state from the
    existing B3 event payload instead of exposing a manual mode switch.

    Lingering Taste values are retained in character data for provenance, but that
    route is intentionally not activated without a sustained-damage-buff source.
    """

    def __init__(self, context: SkillHookContext) -> None:
        self._recommended_until = 0.0

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        buffs: list[BuffWindow] = []
        for event in events:
            if event.event_type == EventType.FULL_BURST_ENTER:
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_full_burst",
                        stat="atk_pct",
                        value=context.definition.skill_value(
                            "skill1", "full_burst_atk_pct"
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time
                        + context.definition.skill_value(
                            "skill1", "full_burst_duration_sec"
                        ),
                    )
                )
                continue

            if (
                event.event_type == EventType.B3_STAGE_ENTER
                and int(event.payload.get("mast_stacks", 0)) > 0
            ):
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_recommended_taste",
                        stat="charge_speed_pct",
                        value=-context.definition.skill_value(
                            "skill1", "taste_charge_speed_down_pct"
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time
                        + context.definition.skill_value(
                            "skill1", "taste_duration_sec"
                        ),
                    )
                )
        return tuple(buffs)

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if event.event_type != EventType.B3_STAGE_ENTER:
            return ()

        if int(event.payload.get("mast_stacks", 0)) > 0:
            self._recommended_until = max(
                self._recommended_until,
                event.time
                + context.definition.skill_value(
                    "skill1", "taste_duration_sec"
                ),
            )

        if event.actor != context.actor:
            return ()

        duration = context.definition.skill_value("burst", "duration_sec")
        effects: list[SkillEffect] = [
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
            )
        ]
        if event.time < self._recommended_until:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="burst_recommended_taste",
                    stat="atk_pct",
                    value=context.definition.skill_value(
                        "burst", "recommended_atk_pct"
                    ),
                    target=context.actor,
                    start=event.time,
                    end=event.time + duration,
                )
            )
        return tuple(effects)

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if (
            shot.actor != context.actor
            or not shot.charged
            or shot.time >= self._recommended_until
        ):
            return ()

        return (
            BuffWindow(
                source=context.actor,
                skill="skill2_recommended_taste",
                stat="attack_damage_pct",
                value=context.definition.skill_value(
                    "skill2", "recommended_attack_damage_pct"
                ),
                target=context.actor,
                start=shot.time,
                end=shot.time
                + context.definition.skill_value(
                    "skill2", "recommended_attack_damage_duration_sec"
                ),
            ),
            DamageRequest(
                time=shot.time,
                actor=context.actor,
                source="skill2_recommended_distributed",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill2", "recommended_distributed_damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    distributed=True,
                    core_eligible=False,
                    range_eligible=False,
                ),
                shot_index=shot.shot_index,
                magazine_index=shot.magazine_index,
            ),
        )
