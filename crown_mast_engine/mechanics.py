from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Iterable, Mapping, Protocol, TypeAlias

from .buffs import BuffWindow
from .characters import CharacterDefinition, WeaponProfile
from .combat import (
    STANDARD_COMBAT_SETTINGS,
    CombatSettings,
    DamageRequest,
    WeaponShot,
)
from .models import BattleEvent, TeamRoster
from .timeline import BurstCycle


ENGINE_RULE_REVISION = "2026-09-02-r10-audited-damage-buckets"


@dataclass(frozen=True)
class MechanicsSignature:
    engine_rule_revision: str
    skill_hook_revision: str
    skill_hook_factories: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class WeaponShotModifier:
    actor: str
    shot_index: int
    charge_damage_pct: float = 0.0
    charge_damage_mult_pct: float = 0.0


@dataclass(frozen=True)
class RecoveryEffect:
    time: float
    receiver: str


@dataclass(frozen=True)
class AmmoChargeEffect:
    time: float
    receiver: str
    fraction_pct: float


@dataclass(frozen=True)
class WeaponMode:
    actor: str
    name: str
    start: float
    end: float
    weapon: WeaponProfile
    pulls_per_second: float
    source: str = "normal_attack"
    refill_base_ammo_on_end: bool = True
    max_shots: int | None = None
    share_base_ammo: bool = False

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("weapon mode end must be after start")
        if self.start < 0:
            raise ValueError("weapon mode start must be non-negative")
        if self.pulls_per_second <= 0:
            raise ValueError("weapon mode pulls per second must be positive")
        if self.max_shots is not None and self.max_shots <= 0:
            raise ValueError("weapon mode max shots must be positive")
        if self.share_base_ammo and self.max_shots is None:
            raise ValueError("shared-ammo weapon mode requires max shots")
        if self.share_base_ammo and self.weapon.charge_frames <= 0:
            raise ValueError("shared-ammo weapon mode requires a charge weapon")


SkillEffect: TypeAlias = DamageRequest | BuffWindow | WeaponShotModifier | RecoveryEffect


@dataclass(frozen=True)
class SkillHookContext:
    actor: str
    definition: CharacterDefinition
    roster: TeamRoster
    timeline: tuple[BurstCycle, ...]
    duration_sec: float
    combat_settings: CombatSettings = STANDARD_COMBAT_SETTINGS


class CharacterSkillHook(Protocol):
    """Stateful character logic fed by the shared chronological combat stream."""

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> Iterable[BuffWindow]: ...

    def instant_reload_times(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> Iterable[float]: ...

    def ammo_charge_effects(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> Iterable[AmmoChargeEffect]: ...

    def scheduled_weapon_modes(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> Iterable[WeaponMode]: ...

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> Iterable[SkillEffect]: ...

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> Iterable[SkillEffect]: ...


class SkillHookBase:
    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> Iterable[BuffWindow]:
        return ()

    def instant_reload_times(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> Iterable[float]:
        return ()

    def ammo_charge_effects(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> Iterable[AmmoChargeEffect]:
        return tuple(
            AmmoChargeEffect(time, context.actor, 100.0)
            for time in self.instant_reload_times(events, context)
        )

    def scheduled_weapon_modes(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> Iterable[WeaponMode]:
        return ()

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> Iterable[SkillEffect]:
        return ()

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> Iterable[SkillEffect]:
        return ()


SkillHookFactory: TypeAlias = Callable[[SkillHookContext], CharacterSkillHook]


class SkillHookRegistry:
    def __init__(
        self,
        factories: Mapping[str, SkillHookFactory] | None = None,
        *,
        revision: str = "custom-hooks",
    ) -> None:
        if not revision:
            raise ValueError("skill hook revision must not be empty")
        self._factories = MappingProxyType(dict(factories or {}))
        self._revision = revision

    @property
    def mechanics_signature(self) -> MechanicsSignature:
        return MechanicsSignature(
            engine_rule_revision=ENGINE_RULE_REVISION,
            skill_hook_revision=self._revision,
            skill_hook_factories=tuple(
                sorted(
                    (actor, _factory_signature(factory))
                    for actor, factory in self._factories.items()
                )
            ),
        )

    def create(self, context: SkillHookContext) -> CharacterSkillHook | None:
        factory = self._factories.get(context.actor)
        return None if factory is None else factory(context)


def _factory_signature(factory: SkillHookFactory) -> str:
    module = getattr(factory, "__module__", type(factory).__module__)
    qualname = getattr(factory, "__qualname__", type(factory).__qualname__)
    code = getattr(factory, "__code__", None)
    if code is None:
        return f"{module}.{qualname}"
    return f"{module}.{qualname}@{code.co_filename}:{code.co_firstlineno}"