from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import FPS, DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class PhantomFavoriteItemSkillHook(SkillHookBase):
    """Single-target favorite-item Phantom implementation.

    Calling Card is tracked as a real 5s target state. The favorite item adds
    one Thief's Dagger every 30 normal attacks. At three stacks the consume
    deals the 84.33% additional hit plus 250% distributed rider, grants one
    permanent 12.86% distributed-amplification stack, and removes Calling
    Card. Hit Rate is omitted because this study fixes core-hit rate externally.

    The favorite-item Fire-only 18% enemy vulnerability is applied to the
    whole roster when the configured boss element is Fire.
    """

    def __init__(self, context: SkillHookContext) -> None:
        self._calling_card_until = 0.0
        self._dagger_stacks = 0
        self._dist_amp_stacks = 0
        self._next_round_attack_damage = False

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
                        skill="burst_max_ammo",
                        stat="max_ammo_pct",
                        value=context.definition.skill_value(
                            "burst", "max_ammo_pct"
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

        # The nuke is evaluated at the cast timestamp with the pre-reset stack
        # window. A zero-value replacement starts an epsilon later so the stack
        # removal still occurs before any subsequent weapon shot.
        reset_time = event.time + 1e-6
        self._dist_amp_stacks = 0
        effects: list[SkillEffect] = [
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
                    full_burst_eligible=False,
                    range_eligible=False,
                ),
            ),
            BuffWindow(
                source=context.actor,
                skill="skill2_dist_amp",
                stat="distributed_damage_pct",
                value=0.0,
                target=context.actor,
                start=reset_time,
                end=inf,
            ),
        ]
        if context.combat_settings.boss_element == "Fire":
            duration = context.definition.skill_value(
                "burst", "fire_damage_taken_duration_sec"
            )
            for target in dict.fromkeys(context.roster.members):
                effects.append(
                    BuffWindow(
                        source=context.actor,
                        skill="burst_fire_vulnerability",
                        stat="damage_taken_pct",
                        value=context.definition.skill_value(
                            "burst", "fire_damage_taken_pct"
                        ),
                        target=target,
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
        if shot.actor != context.actor:
            return ()

        after_hit = round(shot.time + 1 / FPS, 6)
        effects: list[SkillEffect] = []

        if self._next_round_attack_damage:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill1_calling_card_round",
                    stat="attack_damage_pct",
                    value=context.definition.skill_value(
                        "skill1", "calling_card_attack_damage_pct"
                    ),
                    target=context.actor,
                    start=shot.time,
                    end=after_hit,
                )
            )
        self._next_round_attack_damage = False

        was_in_calling_card = shot.time < self._calling_card_until
        if was_in_calling_card:
            self._next_round_attack_damage = True
        else:
            self._calling_card_until = (
                shot.time
                + context.definition.skill_value(
                    "skill1", "calling_card_duration_sec"
                )
            )
            self._dagger_stacks = min(
                int(context.definition.skill_value("skill1", "dagger_max_stacks")),
                self._dagger_stacks + 1,
            )

        treasure_every = int(
            context.definition.skill_value("skill1", "treasure_dagger_every_hits")
        )
        if (shot.shot_index + 1) % treasure_every == 0:
            self._dagger_stacks = min(
                int(context.definition.skill_value("skill1", "dagger_max_stacks")),
                self._dagger_stacks + 1,
            )

        if (shot.shot_index + 1) % int(
            context.definition.skill_value("skill2", "normal_hits_trigger")
        ) == 0:
            effects.extend(
                (
                    BuffWindow(
                        source=context.actor,
                        skill="skill2_10_hit_atk",
                        stat="atk_pct",
                        value=context.definition.skill_value(
                            "skill2", "atk_pct"
                        ),
                        target=context.actor,
                        start=after_hit,
                        end=after_hit
                        + context.definition.skill_value(
                            "skill2", "atk_duration_sec"
                        ),
                    ),
                    BuffWindow(
                        source=context.actor,
                        skill="skill2_10_hit_distributed",
                        stat="distributed_damage_pct",
                        value=context.definition.skill_value(
                            "skill2", "distributed_damage_pct"
                        ),
                        target=context.actor,
                        start=after_hit,
                        end=after_hit
                        + context.definition.skill_value(
                            "skill2", "distributed_duration_sec"
                        ),
                    ),
                )
            )

        if self._dagger_stacks < int(
            context.definition.skill_value("skill1", "dagger_max_stacks")
        ):
            return tuple(effects)

        effects.extend(
            (
                DamageRequest(
                    time=shot.time,
                    actor=context.actor,
                    source="skill2_max_stack_additional",
                    category=DamageCategory.SKILL,
                    coefficient_pct=context.definition.skill_value(
                        "skill2", "max_stack_additional_damage_pct"
                    ),
                    traits=DamageTraits(
                        category=DamageCategory.SKILL,
                        core_eligible=False,
                        range_eligible=False,
                    ),
                    shot_index=shot.shot_index,
                    magazine_index=shot.magazine_index,
                ),
                DamageRequest(
                    time=shot.time,
                    actor=context.actor,
                    source="skill2_max_stack_distributed",
                    category=DamageCategory.SKILL,
                    coefficient_pct=context.definition.skill_value(
                        "skill2", "max_stack_distributed_damage_pct"
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
        )

        self._dagger_stacks = 0
        self._calling_card_until = shot.time
        self._dist_amp_stacks = min(
            int(context.definition.skill_value("skill2", "distributed_stack_max")),
            self._dist_amp_stacks + 1,
        )
        effects.append(
            BuffWindow(
                source=context.actor,
                skill="skill2_dist_amp",
                stat="distributed_damage_pct",
                value=context.definition.skill_value(
                    "skill2", "distributed_stack_pct"
                ) * self._dist_amp_stacks,
                target=context.actor,
                start=after_hit,
                end=inf,
            )
        )
        return tuple(effects)
