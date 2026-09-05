from __future__ import annotations

from math import ceil
from typing import Callable

from .characters import WeaponProfile
from .combat import (
    FPS,
    SharedChargeWeaponMode,
    WeaponShot,
    effective_charge_frames,
    effective_max_ammo,
    effective_weapon_reload_frames,
    generate_weapon_shots as _base_generate_weapon_shots,
    js_round,
)


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
    """Generate weapon shots, with optional full-charge-triggered charge cadence.

    Most characters delegate unchanged to the baseline combat generator. Original
    Cinderella needs one extra state: the first full-charge attack grants +100%
    charge speed until a real reload reaches max ammunition. Her weapon is also
    capped at three shots per second, represented by ``charge_cycle_floor_frames``.

    Ammo-charge effects are intentionally not treated as a reload reset because the
    skill condition is specifically reloading to max ammunition.
    """

    if weapon.full_charge_trigger_charge_speed_pct <= 0:
        return _base_generate_weapon_shots(
            actor=actor,
            weapon=weapon,
            duration_sec=duration_sec,
            reload_speed_at=reload_speed_at,
            charge_speed_at=charge_speed_at,
            fixed_charge_frames_at=fixed_charge_frames_at,
            max_ammo_pct_at=max_ammo_pct_at,
            max_ammo_pct_groups_at=max_ammo_pct_groups_at,
            initial_max_ammo_pct_groups=initial_max_ammo_pct_groups,
            disabled_at=disabled_at,
            instant_reload_at=instant_reload_at,
            startup_delay_frames=startup_delay_frames,
            pulls_per_second_override=pulls_per_second_override,
            shared_charge_modes=shared_charge_modes,
        )

    if weapon.charge_frames <= 0 or weapon.weapon_type not in {"SR", "RL"}:
        raise ValueError("triggered charge cadence requires a charge SR/RL weapon")
    if shared_charge_modes:
        raise NotImplementedError(
            "triggered charge cadence is not combined with shared charge weapon modes"
        )

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
    triggered_charge_speed = False
    shots: list[WeaponShot] = []

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
            needed_reload = effective_weapon_reload_frames(
                weapon,
                reload_speed_at(time),
            )
            if reload_progress >= needed_reload:
                reloading = False
                reload_progress = 0
                ammo = max_ammo_at(time)
                magazine_index += 1
                if weapon.full_charge_trigger_resets_on_reload:
                    triggered_charge_speed = False
            continue

        if recovery_frames > 0:
            recovery_frames -= 1
            continue

        charge_progress += 1
        fixed_charge_frames = fixed_charge_frames_at(time)
        if fixed_charge_frames > 0:
            needed_charge = max(1, js_round(fixed_charge_frames))
        else:
            triggered_pct = (
                weapon.full_charge_trigger_charge_speed_pct
                if triggered_charge_speed
                else 0.0
            )
            needed_charge = effective_charge_frames(
                weapon.charge_frames,
                charge_speed_at(time) + triggered_pct,
            )
        needed_charge = max(needed_charge, weapon.charge_cycle_floor_frames)
        if charge_progress < needed_charge:
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
            )
        )
        shot_index += 1
        triggered_charge_speed = True
        recovery_frames = weapon.charge_release_recovery_frames
        if last_bullet:
            reloading = True
            reload_progress = 0

    return tuple(shots)
