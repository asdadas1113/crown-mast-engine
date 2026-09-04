from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil, floor
from types import MappingProxyType
from typing import Callable, Mapping

from .characters import WeaponProfile
from .damage import DamageBreakdown, DamageTraits
from .models import DamageCategory


FPS = 60
STANDARD_BATTLE_DURATION_SEC = 180.0
RELOAD_TAIL_FRAMES = 13
MG_WINDDOWN_GRACE_FRAMES = 16
MG_WINDDOWN_DECAY = 2.78
MG_NO_CORE_RAMP_ROUNDS = 18
CHARGE_RELEASE_RECOVERY_FRAMES = 22

# Current PvE baseline assumes Min Firing Rounds Adjustment is enabled.
PULLS_PER_SECOND: dict[str, float] = {
    "AR": 12.0,
    "SMG": 24.0,
    "SG": 1.5,
    "MG": 60.0,
    "Pistol": 4.0,
}

ELEMENTS = frozenset({"Fire", "Water", "Wind", "Electric", "Iron"})
ELEMENT_BEATS: dict[str, str] = {
    "Fire": "Wind",
    "Wind": "Iron",
    "Iron": "Electric",
    "Electric": "Water",
    "Water": "Fire",
}

MG_RAMP_INTERVALS: tuple[int, ...] = (
    23,
    14,
    10,
    8,
    7,
    6,
    5,
    5,
    4,
    4,
    4,
    3,
    3,
    3,
    3,
    3,
    3,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
)


def _cumulative(values: tuple[int, ...]) -> tuple[int, ...]:
    result = [0]
    for value in values:
        result.append(result[-1] + value)
    return tuple(result)


MG_LADDER_CUM = _cumulative(MG_RAMP_INTERVALS)


@dataclass(frozen=True)
class CombatSettings:
    boss_def: float = 12_000.0
    core_hit_rate_pct: float = 0.0
    range_bonus_pct: float = 0.0
    element_multiplier: float = 1.0
    element_multiplier_by_actor: Mapping[str, float] = field(default_factory=dict)
    boss_element: str | None = None
    full_burst_bonus_pct: float = 50.0
    boss_damage_taken_pct: float = 0.0
    # PvE baseline uses Settings > Battle > Convenience > Min Firing Rounds Adjustment ON.
    # At 60 FPS, ON preserves programmed 24/s SMGs; OFF quantizes them to 20/s.
    min_firing_rounds_adjustment: bool = True
    startup_delay_frames: int = 8
    duration_sec: float = STANDARD_BATTLE_DURATION_SEC

    def __post_init__(self) -> None:
        if self.boss_def < 0:
            raise ValueError("boss_def must be non-negative")
        if not 0 <= self.core_hit_rate_pct <= 100:
            raise ValueError("core_hit_rate_pct must be between 0 and 100")
        if self.element_multiplier <= 0:
            raise ValueError("element_multiplier must be positive")
        if any(value <= 0 for value in self.element_multiplier_by_actor.values()):
            raise ValueError("actor element multipliers must be positive")
        if self.boss_element is not None and self.boss_element not in ELEMENTS:
            raise ValueError(f"unsupported boss element: {self.boss_element}")
        object.__setattr__(
            self,
            "element_multiplier_by_actor",
            MappingProxyType(dict(self.element_multiplier_by_actor)),
        )
        if self.startup_delay_frames < 0:
            raise ValueError("startup_delay_frames must be non-negative")
        if self.duration_sec <= 0:
            raise ValueError("duration_sec must be positive")

    def element_multiplier_for(
        self,
        actor: str,
        actor_element: str | None = None,
        element_damage_pct: float = 0.0,
        extra_advantage_against: tuple[str, ...] = (),
    ) -> float:
        override = self.element_multiplier_by_actor.get(actor)
        if override is not None:
            return override
        if (
            self.boss_element is not None
            and actor_element is not None
            and (
                ELEMENT_BEATS.get(actor_element) == self.boss_element
                or self.boss_element in extra_advantage_against
            )
        ):
            return 1.1 + element_damage_pct / 100
        return self.element_multiplier


STANDARD_COMBAT_SETTINGS = CombatSettings()


@dataclass(frozen=True)
class WeaponShot:
    time: float
    frame: int
    actor: str
    shot_index: int
    magazine_index: int
    rounds_consumed: int
    core_eligible: bool
    charged: bool = False
    last_bullet: bool = False
    source: str = "normal_attack"
    coefficient_pct: float | None = None
    weapon_mode: str | None = None
    weapon_mode_session: int | None = None


@dataclass(frozen=True)
class SharedChargeWeaponMode:
    name: str
    start: float
    end: float
    charge_frames: int
    max_shots: int
    source: str
    coefficient_pct: float
    session: int

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("shared charge weapon mode end must be after start")
        if self.charge_frames <= 0:
            raise ValueError("shared charge weapon mode charge frames must be positive")
        if self.max_shots <= 0:
            raise ValueError("shared charge weapon mode max shots must be positive")


@dataclass(frozen=True)
class DamageEvent:
    time: float
    actor: str
    source: str
    category: DamageCategory
    coefficient_pct: float
    traits: DamageTraits
    breakdown: DamageBreakdown
    shot_index: int | None = None
    magazine_index: int | None = None
    full_burst: bool = False
    burst_cycle: int | None = None
    macro_cycle: int | None = None

    @property
    def damage(self) -> float:
        return self.breakdown.total


@dataclass(frozen=True)
class DamageRequest:
    """Damage specification emitted before live buffs are resolved."""

    time: float
    actor: str
    source: str
    category: DamageCategory
    coefficient_pct: float
    traits: DamageTraits
    shot_index: int | None = None
    magazine_index: int | None = None
    charge_multiplier: float = 1.0
    charge_damage_pct: float = 0.0
    charge_damage_mult_pct: float = 0.0
    projectile_attachment_pct: float = 0.0
    projectile_explosion_pct: float = 0.0
    sequential_damage_pct: float = 0.0
    sequential_multiplier: float = 1.0
    coefficient_multiplier_stat: str | None = None


def js_round(value: float) -> int:
    """Match JavaScript Math.round for the non-negative timing values used here."""
    if value < 0:
        raise ValueError("js_round only supports non-negative values")
    return floor(value + 0.5)


def effective_reload_frames(base_frames: int, reload_speed_pct: float) -> int:
    """Resolve a displayed/raw reload body expressed in 60-FPS frames."""
    scaled = base_frames * 0.975 * max(0.0, 1 - reload_speed_pct / 100)
    return js_round(scaled) + RELOAD_TAIL_FRAMES


def effective_charge_frames(base_frames: int, charge_speed_pct: float) -> int:
    charge_speed_pct = min(100.0, charge_speed_pct)
    return max(1, js_round(base_frames * (1 - charge_speed_pct / 100)))


def effective_max_ammo(
    base_ammo: int,
    max_ammo_pct: float = 0.0,
    *,
    max_ammo_pct_groups: tuple[float, ...] | None = None,
) -> int:
    groups = (
        max_ammo_pct_groups
        if max_ammo_pct_groups is not None
        else ((max_ammo_pct,) if max_ammo_pct else ())
    )
    ammo_gain = sum(js_round(base_ammo * group / 100) for group in groups)
    return max(1, base_ammo + ammo_gain)


def generate_weapon_shots(
    *,
    actor: str,
    weapon: WeaponProfile,
    duration_sec: float,
    reload_speed_at: Callable[[float], float] = lambda _time: 0.0,
    charge_speed_at: Callable[[float], float] = lambda _time: 0.0,
    fixed_charge_frames_at: Callable[[float], float] = lambda _time: 0.0,
    max_ammo_pct_at: Callable[[float], float] = lambda _time: 0.0,
    max_ammo_pct_groups_at: Callable[[float], tuple[float, ...]] | None = None,
    initial_max_ammo_pct_groups: tuple[float, ...] = (),
    disabled_at: Callable[[float], bool] = lambda _time: False,
    instant_reload_at: Callable[[float], bool | float] = lambda _time: False,
    startup_delay_frames: int = 8,
    pulls_per_second_override: float | None = None,
    shared_charge_modes: tuple[SharedChargeWeaponMode, ...] = (),
) -> tuple[WeaponShot, ...]:
    if weapon.ammo <= 0:
        return ()

    def max_ammo_at(time: float) -> int:
        groups = (
            max_ammo_pct_groups_at(time)
            if max_ammo_pct_groups_at is not None
            else None
        )
        return effective_max_ammo(
            weapon.ammo,
            max_ammo_pct_at(time),
            max_ammo_pct_groups=groups,
        )

    if weapon.charge_frames > 0:
        if weapon.weapon_type not in {"SR", "RL"}:
            raise NotImplementedError(
                f"charge weapon cadence is not implemented: {weapon.weapon_type}"
            )
        total_frames = ceil(duration_sec * FPS)
        ammo = effective_max_ammo(
            weapon.ammo,
            max_ammo_pct_groups=initial_max_ammo_pct_groups,
        )
        magazine_index = 0
        shot_index = 0
        reloading = False
        reload_progress = 0
        charge_progress = 0
        recovery_frames = 0
        shots: list[WeaponShot] = []
        mode_shot_counts = [0] * len(shared_charge_modes)

        for first, second in zip(shared_charge_modes, shared_charge_modes[1:]):
            if first.end > second.start:
                raise ValueError(
                    "overlapping shared charge weapon modes: "
                    f"{first.name}, {second.name}"
                )

        for frame in range(total_frames):
            if frame < startup_delay_frames:
                continue
            time = frame / FPS
            ammo_charge = instant_reload_at(time)
            if ammo_charge:
                fraction_pct = 100.0 if isinstance(ammo_charge, bool) else float(ammo_charge)
                if not 0 < fraction_pct <= 100:
                    raise ValueError("ammo charge fraction must be in (0, 100]")
                reloading = False
                reload_progress = 0
                max_ammo = max_ammo_at(time)
                ammo = min(
                    max_ammo,
                    ammo + js_round(max_ammo * fraction_pct / 100),
                )
                if fraction_pct == 100:
                    magazine_index += 1
            if disabled_at(time):
                continue

            if reloading:
                reload_progress += 1
                needed = effective_reload_frames(
                    weapon.reload_frames,
                    reload_speed_at(time),
                )
                if reload_progress >= needed:
                    reloading = False
                    reload_progress = 0
                    ammo = max_ammo_at(time)
                    magazine_index += 1
                continue

            if recovery_frames > 0:
                recovery_frames -= 1
                continue

            charge_progress += 1
            active_mode_index = next(
                (
                    index
                    for index, mode in enumerate(shared_charge_modes)
                    if mode.start <= time < mode.end
                    and mode_shot_counts[index] < mode.max_shots
                ),
                None,
            )
            if active_mode_index is not None:
                active_mode = shared_charge_modes[active_mode_index]
                needed = active_mode.charge_frames
            else:
                active_mode = None
                fixed_charge_frames = fixed_charge_frames_at(time)
                needed = (
                    max(1, js_round(fixed_charge_frames))
                    if fixed_charge_frames > 0
                    else effective_charge_frames(
                        weapon.charge_frames,
                        charge_speed_at(time),
                    )
                )
            if charge_progress < needed:
                continue

            charge_progress = 0
            ammo -= 1
            last_bullet = ammo <= 0
            shots.append(
                WeaponShot(
                    time=time,
                    frame=frame,
                    actor=actor,
                    shot_index=shot_index,
                    magazine_index=magazine_index,
                    rounds_consumed=1,
                    core_eligible=True,
                    charged=True,
                    last_bullet=last_bullet,
                    source=(
                        active_mode.source
                        if active_mode is not None
                        else "normal_attack"
                    ),
                    coefficient_pct=(
                        active_mode.coefficient_pct
                        if active_mode is not None
                        else None
                    ),
                    weapon_mode=(
                        active_mode.name
                        if active_mode is not None
                        else None
                    ),
                    weapon_mode_session=(
                        active_mode.session
                        if active_mode is not None
                        else None
                    ),
                )
            )
            if active_mode_index is not None:
                mode_shot_counts[active_mode_index] += 1
            shot_index += 1
            recovery_frames = weapon.charge_release_recovery_frames
            if last_bullet:
                reloading = True
                reload_progress = 0

        return tuple(shots)

    total_frames = ceil(duration_sec * FPS)
    ammo = effective_max_ammo(
        weapon.ammo,
        max_ammo_pct_groups=initial_max_ammo_pct_groups,
    )
    magazine_index = 0
    shot_index = 0
    reloading = False
    reload_progress = 0
    fire_acc = 0.0
    mg_ramp_round = 0
    mg_cooldown = 0.0
    mg_idle_frames = 0
    shots: list[WeaponShot] = []

    pulls_per_sec = (
        pulls_per_second_override
        if pulls_per_second_override is not None
        else PULLS_PER_SECOND.get(weapon.weapon_type)
    )
    if pulls_per_sec is not None and not 0 < pulls_per_sec <= FPS:
        raise ValueError(f"pulls per second must be in (0, {FPS}]")
    if weapon.weapon_type != "MG" and pulls_per_sec is None:
        raise NotImplementedError(
            f"non-charge weapon cadence is not implemented: {weapon.weapon_type}"
        )

    for frame in range(total_frames):
        if frame < startup_delay_frames:
            continue
        time = frame / FPS
        ammo_charge = instant_reload_at(time)
        if ammo_charge:
            fraction_pct = 100.0 if isinstance(ammo_charge, bool) else float(ammo_charge)
            if not 0 < fraction_pct <= 100:
                raise ValueError("ammo charge fraction must be in (0, 100]")
            reloading = False
            reload_progress = 0
            max_ammo = max_ammo_at(time)
            ammo = min(
                max_ammo,
                ammo + js_round(max_ammo * fraction_pct / 100),
            )
            if fraction_pct == 100:
                magazine_index += 1
        if disabled_at(time):
            if weapon.weapon_type == "MG":
                mg_idle_frames += 1
            continue

        if reloading:
            if weapon.weapon_type == "MG":
                mg_idle_frames += 1
            reload_progress += 1
            needed = effective_reload_frames(
                weapon.reload_frames,
                reload_speed_at(time),
            )
            if reload_progress >= needed:
                reloading = False
                reload_progress = 0
                ammo = max_ammo_at(time)
                magazine_index += 1
            continue

        if weapon.weapon_type == "MG":
            if mg_idle_frames > 0:
                lost = MG_WINDDOWN_DECAY * max(
                    0,
                    mg_idle_frames - MG_WINDDOWN_GRACE_FRAMES,
                )
                if lost > 0:
                    position = max(
                        0.0,
                        MG_LADDER_CUM[min(mg_ramp_round, len(MG_RAMP_INTERVALS))]
                        - lost,
                    )
                    mg_ramp_round = 0
                    while (
                        mg_ramp_round < len(MG_RAMP_INTERVALS)
                        and MG_LADDER_CUM[mg_ramp_round + 1] <= position
                    ):
                        mg_ramp_round += 1
                    mg_cooldown = 0.0
                mg_idle_frames = 0

            mg_cooldown -= 1.0
            while mg_cooldown <= 0 and not reloading:
                fire_acc += 1
                if fire_acc >= weapon.hits_per_shot:
                    fire_acc -= weapon.hits_per_shot
                    rounds_consumed = weapon.hits_per_shot
                    shots.append(
                        WeaponShot(
                            time=time,
                            frame=frame,
                            actor=actor,
                            shot_index=shot_index,
                            magazine_index=magazine_index,
                            rounds_consumed=rounds_consumed,
                            core_eligible=mg_ramp_round >= MG_NO_CORE_RAMP_ROUNDS,
                            last_bullet=ammo - rounds_consumed <= 0,
                        )
                    )
                    shot_index += 1
                    ammo -= rounds_consumed
                    if ammo <= 0:
                        reloading = True
                        reload_progress = 0

                interval = (
                    MG_RAMP_INTERVALS[mg_ramp_round]
                    if mg_ramp_round < len(MG_RAMP_INTERVALS)
                    else 1
                )
                mg_ramp_round += 1
                mg_cooldown += interval
            continue

        fire_acc += pulls_per_sec / FPS
        while fire_acc >= 1 and not reloading:
            fire_acc -= 1
            shots.append(
                WeaponShot(
                    time=time,
                    frame=frame,
                    actor=actor,
                    shot_index=shot_index,
                    magazine_index=magazine_index,
                    rounds_consumed=1,
                    core_eligible=True,
                    last_bullet=ammo - 1 <= 0,
                )
            )
            shot_index += 1
            ammo -= 1
            if ammo <= 0:
                reloading = True
                reload_progress = 0

    return tuple(shots)
