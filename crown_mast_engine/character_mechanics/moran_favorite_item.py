from __future__ import annotations

from dataclasses import replace

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext, WeaponMode
from ..models import BattleEvent, DamageCategory, EventType


class MoranFavoriteItemSkillHook(SkillHookBase):
    """Favorite Item Burst weapon mode and caster-ATK team buff."""

    def __init__(self, context: SkillHookContext) -> None:
        self._weapon_mode_session: int | None = None
        self._weapon_mode_hits = 0

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        duration = context.definition.skill_value("burst", "duration_sec")
        return tuple(
            BuffWindow(
                source=context.actor,
                skill="burst_favorite_item",
                stat="caster_atk_pct",
                value=context.definition.skill_value("burst", "caster_atk_pct"),
                target=target,
                start=event.time,
                end=event.time + duration,
                caster=context.actor,
                snapshot=True,
            )
            for event in events
            if event.event_type == EventType.B1_CAST and event.actor == context.actor
            for target in context.roster.members
        )

    def scheduled_weapon_modes(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[WeaponMode, ...]:
        duration = context.definition.skill_value("burst", "duration_sec")
        rate = context.definition.skill_value("burst", "weapon_swap_fire_rate")
        weapon = replace(
            context.definition.weapon,
            weapon_type="SMG",
            normal_attack_pct=context.definition.skill_value(
                "burst", "weapon_swap_damage_pct"
            ),
            ammo=1_000_000,
            reload_frames=0,
        )
        return tuple(
            WeaponMode(
                actor=context.actor,
                name="fair-and-square",
                start=event.time,
                end=event.time + duration,
                weapon=weapon,
                pulls_per_second=rate,
                source="burst_weapon_attack",
            )
            for event in events
            if event.event_type == EventType.B1_CAST and event.actor == context.actor
        )

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor or shot.weapon_mode != "fair-and-square":
            return ()
        if shot.weapon_mode_session != self._weapon_mode_session:
            self._weapon_mode_session = shot.weapon_mode_session
            self._weapon_mode_hits = 0
        self._weapon_mode_hits += shot.rounds_consumed
        if self._weapon_mode_hits % 5:
            return ()
        return (
            DamageRequest(
                time=shot.time,
                actor=context.actor,
                source="skill1_weapon_swap_fifth_hit",
                category=DamageCategory.SKILL,
                coefficient_pct=context.definition.skill_value(
                    "skill1", "weapon_swap_fifth_hit_damage_pct"
                ),
                traits=DamageTraits(
                    category=DamageCategory.SKILL,
                    core_eligible=False,
                    range_eligible=False,
                ),
                shot_index=shot.shot_index,
                magazine_index=shot.magazine_index,
            ),
        )
