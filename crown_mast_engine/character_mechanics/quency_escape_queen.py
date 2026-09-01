from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class QuencyEscapeQueenSkillHook(SkillHookBase):
    """Single-boss implementation of Quency: Escape Queen's route stages."""

    def __init__(self, context: SkillHookContext) -> None:
        self._stage1 = 0
        self._stage2 = 0
        self._stage3 = 0

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        buffs: list[BuffWindow] = []
        duration = context.definition.skill_value("burst", "duration_sec")
        for event in events:
            if (
                event.event_type == EventType.B3_STAGE_ENTER
                and event.actor == context.actor
            ):
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="burst_reload",
                        stat="reload_speed_pct",
                        value=context.definition.skill_value(
                            "burst", "reload_speed_pct"
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time + duration,
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

        duration = context.definition.skill_value("burst", "duration_sec")
        return (
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
            DamageRequest(
                time=event.time,
                actor=context.actor,
                source="burst_distributed",
                category=DamageCategory.BURST,
                coefficient_pct=context.definition.skill_value(
                    "burst", "damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.BURST,
                    distributed=True,
                    core_eligible=False,
                    range_eligible=False,
                ),
            ),
        )

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor:
            return ()

        trigger_every = int(
            context.definition.skill_value("skill2", "normal_attacks_per_trigger")
        )
        if (shot.shot_index + 1) % trigger_every:
            return ()

        effects: list[SkillEffect] = []
        if self._stage1 < int(
            context.definition.skill_value("skill2", "stage1_max_stacks")
        ):
            self._stage1 += 1
        elif self._stage2 < int(
            context.definition.skill_value("skill2", "stage2_max_stacks")
        ):
            self._stage2 += 1
        elif self._stage3 < int(
            context.definition.skill_value("skill2", "stage3_max_stacks")
        ):
            self._stage3 += 1

        effects.append(
            BuffWindow(
                source=context.actor,
                skill="skill2_stage1",
                stat="atk_pct",
                value=context.definition.skill_value(
                    "skill2", "stage1_atk_pct_per_stack"
                ) * self._stage1,
                target=context.actor,
                start=shot.time,
                end=shot.time
                + context.definition.skill_value(
                    "skill2", "stage1_duration_sec"
                ),
            )
        )

        stage1_max = self._stage1 >= int(
            context.definition.skill_value("skill2", "stage1_max_stacks")
        )
        if stage1_max:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill1_stage1_max",
                    stat="distributed_damage_pct",
                    value=context.definition.skill_value(
                        "skill1", "distributed_damage_pct"
                    ),
                    target=context.actor,
                    start=shot.time,
                    end=inf,
                )
            )

        if self._stage2:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill2_stage2",
                    stat="atk_pct",
                    value=context.definition.skill_value(
                        "skill2", "stage2_atk_pct_per_stack"
                    ) * self._stage2,
                    target=context.actor,
                    start=shot.time,
                    end=shot.time
                    + context.definition.skill_value(
                        "skill2", "stage2_duration_sec"
                    ),
                )
            )

        stage2_max = self._stage2 >= int(
            context.definition.skill_value("skill2", "stage2_max_stacks")
        )
        if stage2_max:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill1_stage2_max",
                    stat="core_damage_pct",
                    value=context.definition.skill_value(
                        "skill1", "core_damage_pct"
                    ),
                    target=context.actor,
                    start=shot.time,
                    end=inf,
                )
            )

        if self._stage3:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill2_stage3",
                    stat="atk_pct",
                    value=context.definition.skill_value(
                        "skill2", "stage3_atk_pct_per_stack"
                    ) * self._stage3,
                    target=context.actor,
                    start=shot.time,
                    end=shot.time
                    + context.definition.skill_value(
                        "skill2", "stage3_duration_sec"
                    ),
                )
            )

        stage3_max = self._stage3 >= int(
            context.definition.skill_value("skill2", "stage3_max_stacks")
        )
        if stage3_max:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill1_stage3_max",
                    stat="crit_rate_pct",
                    value=context.definition.skill_value(
                        "skill1", "crit_rate_pct"
                    ),
                    target=context.actor,
                    start=shot.time,
                    end=inf,
                )
            )
        return tuple(effects)
