from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class ScarletBlackShadowSkillHook(SkillHookBase):
    def __init__(self, context: SkillHookContext) -> None:
        self._phase = 0
        self._charge_count = 0
        self._own_burst_until = 0.0

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
                        skill="skill2_full_burst",
                        stat="max_ammo_pct",
                        value=context.definition.skill_value(
                            "skill2",
                            "max_ammo_pct",
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time
                        + context.definition.skill_value(
                            "skill2",
                            "duration_sec",
                        ),
                    )
                )
            elif (
                event.event_type == EventType.B3_STAGE_ENTER
                and event.actor == context.actor
            ):
                end = event.time + context.definition.skill_value(
                    "burst",
                    "duration_sec",
                )
                buffs.extend(
                    (
                        BuffWindow(
                            source=context.actor,
                            skill="burst",
                            stat="atk_pct",
                            value=context.definition.skill_value(
                                "burst",
                                "atk_pct",
                            ),
                            target=context.actor,
                            start=event.time,
                            end=end,
                        ),
                        BuffWindow(
                            source=context.actor,
                            skill="burst",
                            stat="charge_damage_pct",
                            value=context.definition.skill_value(
                                "burst",
                                "charge_damage_pct",
                            ),
                            target=context.actor,
                            start=event.time,
                            end=end,
                        ),
                    )
                )
        return tuple(buffs)

    def instant_reload_times(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[float, ...]:
        fraction_pct = context.definition.skill_value(
            "skill2",
            "instant_reload_fraction_pct",
        )
        if fraction_pct != 100:
            raise NotImplementedError(
                "partial instant reload is not implemented: "
                f"{fraction_pct}%"
            )
        return tuple(
            event.time
            for event in events
            if event.event_type == EventType.FULL_BURST_ENTER
        )

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if (
            event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == context.actor
        ):
            self._own_burst_until = event.time + context.definition.skill_value(
                "burst",
                "duration_sec",
            )
        return ()

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor or not shot.charged:
            return ()

        count_key = (
            "own_burst_phase_charge_count"
            if shot.time < self._own_burst_until
            else "outside_phase_charge_count"
        )
        required = int(context.definition.skill_value("skill1", count_key))
        self._charge_count += 1
        if self._charge_count < required:
            return ()

        self._charge_count = 0
        self._phase = self._phase % 3 + 1
        distributed = self._phase in {2, 3}
        coefficient_key = (
            f"phase{self._phase}_distributed_damage_pct"
            if distributed
            else "phase1_damage_pct"
        )
        return (
            DamageRequest(
                time=shot.time,
                actor=context.actor,
                source=f"skill1_phase{self._phase}",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill1",
                    coefficient_key,
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    distributed=distributed,
                    core_eligible=False,
                    range_eligible=False,
                ),
                shot_index=shot.shot_index,
                magazine_index=shot.magazine_index,
            ),
        )
