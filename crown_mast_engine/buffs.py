from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable


@dataclass(frozen=True)
class BuffWindow:
    source: str
    skill: str
    stat: str
    value: float
    target: str
    start: float
    end: float
    caster: str | None = None
    snapshot: bool = False

    @property
    def key(self) -> tuple[str, str, str, str]:
        return (self.source, self.skill, self.stat, self.target)

    def active_at(self, time: float) -> bool:
        return self.start <= time < self.end


@dataclass(frozen=True)
class ResolvedOffensiveBuffs:
    atk_pct: float
    caster_atk_flat: float
    max_hp_pct: float
    max_hp_to_atk_pct: float
    attack_damage_pct: float
    crit_rate_pct: float
    crit_rate_normal_pct: float
    crit_damage_pct: float
    core_damage_pct: float
    normal_attack_pct: float
    reload_speed_pct: float
    charge_speed_pct: float
    charge_damage_pct: float
    charge_damage_mult_pct: float
    distributed_damage_pct: float
    projectile_attachment_pct: float
    projectile_explosion_pct: float
    sustained_damage_pct: float
    damage_taken_pct: float
    charge_time_fixed_frames: float


class BuffBook:
    def __init__(self) -> None:
        self._windows: list[BuffWindow] = []
        self._indices_by_target: dict[str, list[int]] = {}
        self._indices_by_target_stat: dict[tuple[str, str], list[int]] = {}
        self._indices_by_key: dict[tuple[str, str, str, str], list[int]] = {}
        self._indices_by_source_skill: dict[tuple[str, str], list[int]] = {}

    @property
    def windows(self) -> tuple[BuffWindow, ...]:
        return tuple(self._windows)

    def apply(self, buff: BuffWindow) -> None:
        if buff.end < buff.start:
            raise ValueError(f"buff window has end before start: {buff}")
        if buff.end == buff.start:
            return
        for index in self._indices_by_key.get(buff.key, ()):
            existing = self._windows[index]
            if existing.start == buff.start:
                self._windows[index] = buff
                return
            if existing.active_at(buff.start):
                self._windows[index] = replace(existing, end=buff.start)
        index = len(self._windows)
        self._windows.append(buff)
        self._indices_by_target.setdefault(buff.target, []).append(index)
        self._indices_by_target_stat.setdefault((buff.target, buff.stat), []).append(index)
        self._indices_by_key.setdefault(buff.key, []).append(index)
        self._indices_by_source_skill.setdefault((buff.source, buff.skill), []).append(index)

    def close(self, source: str, skill: str, time: float) -> None:
        for index in self._indices_by_source_skill.get((source, skill), ()):
            existing = self._windows[index]
            if existing.active_at(time):
                self._windows[index] = replace(existing, end=time)

    def active(
        self,
        time: float,
        target: str,
        stat: str | None = None,
    ) -> tuple[BuffWindow, ...]:
        indices = (
            self._indices_by_target.get(target, ())
            if stat is None
            else self._indices_by_target_stat.get((target, stat), ())
        )
        return tuple(
            self._windows[index]
            for index in indices
            if self._windows[index].active_at(time)
        )

    def total(self, time: float, target: str, stat: str) -> float:
        return sum(buff.value for buff in self.active(time, target, stat))

    def grouped_totals(
        self,
        time: float,
        target: str,
        stat: str,
    ) -> tuple[float, ...]:
        grouped: dict[tuple[str, str], float] = {}
        for buff in self.active(time, target, stat):
            key = (buff.source, buff.skill)
            grouped[key] = grouped.get(key, 0.0) + buff.value
        return tuple(grouped.values())

    def caster_atk_flat(
        self,
        time: float,
        target: str,
        static_atk_resolver: Callable[[str], float],
    ) -> float:
        total = 0.0
        for buff in self.active(time, target, "caster_atk_pct"):
            if buff.caster is None:
                raise ValueError(f"caster ATK buff has no caster: {buff}")
            total += static_atk_resolver(buff.caster) * buff.value / 100
        return total

    def _max_hp_to_atk_flat(
        self,
        *,
        target: str,
        max_hp_pct: float,
        max_hp_to_atk_pct: float,
        static_atk_resolver: Callable[[str], float],
    ) -> float:
        if max_hp_to_atk_pct == 0:
            return 0.0

        # SimulationResult.resolved_offensive_buffs passes its bound static_atk
        # resolver here.  That gives this generic buff layer access to the same
        # catalog/build snapshot without adding a Cinderella-only branch to the
        # damage formula or changing every existing resolver call site.
        result = getattr(static_atk_resolver, "__self__", None)
        if result is None or not hasattr(result, "catalog") or not hasattr(result, "build_profile"):
            raise ValueError("Max HP to ATK conversion requires a simulation-bound resolver")

        definition = result.catalog.require(target)
        if definition.progression_hp <= 0:
            raise ValueError(f"Max HP to ATK conversion has no HP baseline: {target}")
        build = result.build_profile(target)
        static_max_hp = (
            definition.progression_hp
            + build.equipment.gear_hp(definition.unit_class)
            + build.collection.flat_hp
        )
        final_max_hp = static_max_hp * (1 + max_hp_pct / 100)
        return final_max_hp * max_hp_to_atk_pct / 100

    def resolve_offensive(
        self,
        time: float,
        target: str,
        static_atk_resolver: Callable[[str], float],
    ) -> ResolvedOffensiveBuffs:
        totals: dict[str, float] = {}
        caster_atk_flat = 0.0
        for index in self._indices_by_target.get(target, ()):
            buff = self._windows[index]
            if not buff.active_at(time):
                continue
            if buff.stat == "caster_atk_pct":
                if buff.caster is None:
                    raise ValueError(f"caster ATK buff has no caster: {buff}")
                caster_atk_flat += static_atk_resolver(buff.caster) * buff.value / 100
            else:
                totals[buff.stat] = totals.get(buff.stat, 0.0) + buff.value

        max_hp_pct = totals.get("max_hp_pct", 0.0)
        max_hp_to_atk_pct = totals.get("max_hp_to_atk_pct", 0.0)
        caster_atk_flat += self._max_hp_to_atk_flat(
            target=target,
            max_hp_pct=max_hp_pct,
            max_hp_to_atk_pct=max_hp_to_atk_pct,
            static_atk_resolver=static_atk_resolver,
        )

        return ResolvedOffensiveBuffs(
            atk_pct=totals.get("atk_pct", 0.0),
            caster_atk_flat=caster_atk_flat,
            max_hp_pct=max_hp_pct,
            max_hp_to_atk_pct=max_hp_to_atk_pct,
            attack_damage_pct=totals.get("attack_damage_pct", 0.0),
            crit_rate_pct=totals.get("crit_rate_pct", 0.0),
            crit_rate_normal_pct=totals.get("crit_rate_normal_pct", 0.0),
            crit_damage_pct=totals.get("crit_damage_pct", 0.0),
            core_damage_pct=totals.get("core_damage_pct", 0.0),
            normal_attack_pct=totals.get("normal_attack_pct", 0.0),
            reload_speed_pct=totals.get("reload_speed_pct", 0.0),
            charge_speed_pct=totals.get("charge_speed_pct", 0.0),
            charge_damage_pct=totals.get("charge_damage_pct", 0.0),
            charge_damage_mult_pct=totals.get("charge_damage_mult_pct", 0.0),
            distributed_damage_pct=totals.get("distributed_damage_pct", 0.0),
            projectile_attachment_pct=totals.get("projectile_attachment_pct", 0.0),
            projectile_explosion_pct=totals.get("projectile_explosion_pct", 0.0),
            sustained_damage_pct=totals.get("sustained_damage_pct", 0.0),
            damage_taken_pct=totals.get("damage_taken_pct", 0.0),
            charge_time_fixed_frames=totals.get("charge_time_fixed_frames", 0.0),
        )
