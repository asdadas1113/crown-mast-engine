from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import FPS, DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class QuencyEscapeQueenSkillHook(SkillHookBase):
    """Single-boss implementation of Quency: Escape Queen's Explore Route.

    Quency fires two hits per SMG pull. Her `after 2 normal attacks` data trigger is
    therefore one engine pull. Stage 2 unlocks only after Stage 1 reaches 10, and
    Stage 3 only after Stage 2 reaches 10. The 2s/1s/0.5s stack durations are live:
    Stage 1 survives the normal reload while Stages 2/3 lapse and rebuild.
    """

    def __init__(self, context: SkillHookContext) -> None:
        self._hit_meter = 0
        self._stage1 = 0
        self._stage2 = 0
        self._stage3 = 0
        self._stage1_until = 0.0
        self._stage2_until = 0.0
        self._stage3_until = 0.0

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        buffs: list[BuffWindow] = []
        duration = context.definition.skill_value("burst", "duration_sec")
        for event in events:
            if event.event_type == EventType.B3_STAGE_ENTER and event.actor == context.actor:
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="burst_reload",
                        stat="reload_speed_pct",
                        value=context.definition.skill_value("burst", "reload_speed_pct"),
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
        if event.event_type != EventType.B3_STAGE_ENTER or event.actor != context.actor:
            return ()

        duration = context.definition.skill_value("burst", "duration_sec")
        return (
            BuffWindow(
                source=context.actor,
                skill="burst",
                stat="attack_damage_pct",
                value=context.definition.skill_value("burst", "attack_damage_pct"),
                target=context.actor,
                start=event.time,
                end=event.time + duration,
            ),
            DamageRequest(
                time=event.time,
                actor=context.actor,
                source="burst_distributed",
                category=DamageCategory.BURST,
                coefficient_pct=context.definition.skill_value("burst", "damage_pct"),
                traits=DamageTraits(
                    category=DamageCategory.BURST,
                    distributed=True,
                    core_eligible=False,
                    full_burst_eligible=False,
                    range_eligible=False,
                ),
            ),
        )

    def _expire_route(self, time: float) -> None:
        if self._stage1 and time >= self._stage1_until:
            self._stage1 = self._stage2 = self._stage3 = 0
            self._stage1_until = self._stage2_until = self._stage3_until = 0.0
            return
        if self._stage2 and time >= self._stage2_until:
            self._stage2 = self._stage3 = 0
            self._stage2_until = self._stage3_until = 0.0
            return
        if self._stage3 and time >= self._stage3_until:
            self._stage3 = 0
            self._stage3_until = 0.0

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor:
            return ()

        self._hit_meter += context.definition.weapon.hits_per_shot
        trigger_hits = int(
            context.definition.skill_value("skill2", "normal_attacks_per_trigger")
        )
        if self._hit_meter < trigger_hits:
            return ()
        self._hit_meter -= trigger_hits
        self._expire_route(shot.time)

        stage1_max = int(context.definition.skill_value("skill2", "stage1_max_stacks"))
        stage2_max = int(context.definition.skill_value("skill2", "stage2_max_stacks"))
        stage3_max = int(context.definition.skill_value("skill2", "stage3_max_stacks"))

        if self._stage1 < stage1_max:
            self._stage1 += 1
        elif self._stage2 < stage2_max:
            self._stage2 += 1
        elif self._stage3 < stage3_max:
            self._stage3 += 1

        after_hit = round(shot.time + 1 / FPS, 6)
        self._stage1_until = after_hit + context.definition.skill_value(
            "skill2", "stage1_duration_sec"
        )
        if self._stage2:
            self._stage2_until = after_hit + context.definition.skill_value(
                "skill2", "stage2_duration_sec"
            )
        if self._stage3:
            self._stage3_until = after_hit + context.definition.skill_value(
                "skill2", "stage3_duration_sec"
            )

        effects: list[SkillEffect] = [
            BuffWindow(
                source=context.actor,
                skill="skill2_stage1",
                stat="atk_pct",
                value=context.definition.skill_value(
                    "skill2", "stage1_atk_pct_per_stack"
                ) * self._stage1,
                target=context.actor,
                start=after_hit,
                end=self._stage1_until,
            )
        ]
        if self._stage1 >= stage1_max:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill1_stage1_max",
                    stat="distributed_damage_pct",
                    value=context.definition.skill_value("skill1", "distributed_damage_pct"),
                    target=context.actor,
                    start=after_hit,
                    end=self._stage1_until,
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
                    start=after_hit,
                    end=self._stage2_until,
                )
            )
            if self._stage2 >= stage2_max:
                effects.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_stage2_max",
                        stat="core_damage_pct",
                        value=context.definition.skill_value("skill1", "core_damage_pct"),
                        target=context.actor,
                        start=after_hit,
                        end=self._stage2_until,
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
                    start=after_hit,
                    end=self._stage3_until,
                )
            )
            if self._stage3 >= stage3_max:
                effects.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_stage3_max",
                        stat="crit_rate_pct",
                        value=context.definition.skill_value("skill1", "crit_rate_pct"),
                        target=context.actor,
                        start=after_hit,
                        end=self._stage3_until,
                    )
                )

        return tuple(effects)
