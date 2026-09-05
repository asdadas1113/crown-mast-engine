from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from heapq import heappop, heappush
from itertools import count
from math import inf
from types import MappingProxyType
from typing import Iterable, Mapping

from .buffs import BuffBook, BuffWindow, ResolvedOffensiveBuffs
from .characters import CharacterCatalog, STANDARD_CHARACTER_CATALOG
from .character_mechanics import STANDARD_SKILL_HOOKS
from .combat import (
    FPS,
    STANDARD_COMBAT_SETTINGS,
    CombatSettings,
    DamageEvent,
    DamageRequest,
    SharedChargeWeaponMode,
    WeaponShot,
    generate_weapon_shots,
)
from .damage import DamageContext, DamageTraits, calculate_damage
from .equipment import (
    BuildProfile,
    CollectionProfile,
    OverloadProfile,
    standard_build_for_actor,
)
from .mechanics import (
    CharacterSkillHook,
    MechanicsSignature,
    RecoveryEffect,
    SkillEffect,
    SkillHookContext,
    SkillHookRegistry,
    WeaponMode,
    WeaponShotModifier,
)
from .models import BattleEvent, CycleSnapshot, DamageCategory, EventType, TeamRoster
from .rotations import RotationPolicy
from .timeline import STANDARD_TIMELINE, BurstCycle


@dataclass
class MastState:
    max_stacks: int
    hangover_duration: float
    drunken_stacks: int = 0
    hangover_until: float = 0.0

    def add_drunken_stack(self) -> bool:
        previous = self.drunken_stacks
        self.drunken_stacks = min(self.max_stacks, self.drunken_stacks + 1)
        return previous == 0 and self.drunken_stacks == 1

    def is_hungover(self, time: float) -> bool:
        return time < self.hangover_until

    def reset_at_full_burst_end(self, time: float) -> bool:
        if self.drunken_stacks < self.max_stacks:
            return False
        self.drunken_stacks = 0
        self.hangover_until = time + self.hangover_duration
        return True


@dataclass(frozen=True)
class SimulationResult:
    policy_name: str
    roster: TeamRoster
    timeline: tuple[BurstCycle, ...]
    events: tuple[BattleEvent, ...]
    snapshots: tuple[CycleSnapshot, ...]
    buffs: BuffBook
    catalog: CharacterCatalog
    builds: Mapping[str, BuildProfile]
    combat_settings: CombatSettings
    mechanics_signature: MechanicsSignature
    damage_events: tuple[DamageEvent, ...] = ()

    def active_buffs(self, time: float, target: str, stat: str | None = None) -> tuple[BuffWindow, ...]:
        return self.buffs.active(time, target, stat)

    def buff_total(self, time: float, target: str, stat: str) -> float:
        return self.buffs.total(time, target, stat)

    def resolved_offensive_buffs(self, time: float, target: str) -> ResolvedOffensiveBuffs:
        return self.buffs.resolve_offensive(time, target, self.static_atk)

    @cached_property
    def _static_atk_by_slug(self) -> Mapping[str, float]:
        return MappingProxyType(
            {
                definition.slug: (
                    definition.progression_atk
                    + self.build_profile(definition.slug).equipment.gear_atk(
                        definition.unit_class
                    )
                    + self.build_profile(definition.slug).collection.flat_atk
                )
                for definition in self.catalog.definitions
            }
        )

    def static_atk(self, slug: str) -> float:
        try:
            return self._static_atk_by_slug[slug]
        except KeyError:
            self.catalog.require(slug)
            raise AssertionError("unreachable")

    def overload_profile(self, slug: str) -> OverloadProfile:
        return self.build_profile(slug).overload

    def build_profile(self, slug: str) -> BuildProfile:
        return self.builds.get(slug, standard_build_for_actor(slug))

    def collection_profile(self, slug: str) -> CollectionProfile:
        return self.build_profile(slug).collection

    def collection_weapon_effect(self, slug: str, stat: str) -> float:
        definition = self.catalog.require(slug)
        effect = self.collection_profile(slug).weapon_effect(
            definition.weapon.weapon_type
        )
        return 0.0 if effect is None or effect[0] != stat else effect[1]

    def max_ammo_pct_groups(self, time: float, slug: str) -> tuple[float, ...]:
        overload_pct = self.overload_profile(slug).ammo_pct
        collection_pct = self.collection_weapon_effect(slug, "max_ammo_pct")
        groups = self.buffs.grouped_totals(time, slug, "max_ammo_pct")
        return (
            ((overload_pct,) if overload_pct else ())
            + ((collection_pct,) if collection_pct else ())
            + groups
        )

    def damage_events_for(
        self,
        actor: str | None = None,
        category: DamageCategory | None = None,
        burst_cycle: int | None = None,
        macro_cycle: int | None = None,
    ) -> tuple[DamageEvent, ...]:
        return tuple(
            event
            for event in self.damage_events
            if (actor is None or event.actor == actor)
            and (category is None or event.category == category)
            and (burst_cycle is None or event.burst_cycle == burst_cycle)
            and (macro_cycle is None or event.macro_cycle == macro_cycle)
        )

    def damage_total(self, actor: str | None = None) -> float:
        return sum(event.damage for event in self.damage_events_for(actor=actor))

    @property
    def damage_by_character(self) -> Mapping[str, float]:
        totals = {member: self.damage_total(member) for member in self.roster.members}
        return MappingProxyType(totals)

    def is_full_burst(self, time: float) -> bool:
        return any(
            cycle.full_burst_start <= time < cycle.full_burst_end
            for cycle in self.timeline
        )

    def burst_cycle_at(self, time: float) -> int | None:
        if not self.timeline:
            return None
        for cycle in reversed(self.timeline):
            if time >= cycle.b1_time:
                return cycle.cycle
        return self.timeline[0].cycle

    def macro_cycle_at(self, time: float) -> int | None:
        cycle = self.burst_cycle_at(time)
        return None if cycle is None else (cycle - 1) // 3 + 1


class CrownMastEngine:
    def __init__(
        self,
        policy: RotationPolicy,
        roster: TeamRoster | None = None,
        timeline: tuple[BurstCycle, ...] = STANDARD_TIMELINE,
        catalog: CharacterCatalog = STANDARD_CHARACTER_CATALOG,
        builds: Mapping[str, BuildProfile] | None = None,
        combat_settings: CombatSettings = STANDARD_COMBAT_SETTINGS,
        skill_hooks: SkillHookRegistry = STANDARD_SKILL_HOOKS,
    ) -> None:
        self.policy = policy
        self.roster = roster or TeamRoster()
        self.timeline = timeline
        for previous, current in zip(self.timeline, self.timeline[1:]):
            if current.b1_time < previous.full_burst_end:
                raise ValueError(
                    f"burst cycles overlap: {previous.cycle} and {current.cycle}"
                )
        self.catalog = catalog
        self.builds = MappingProxyType(dict(builds or {}))
        self.combat_settings = combat_settings
        self.skill_hooks = skill_hooks
        self.crown_definition = catalog.require(self.roster.crown)
        self.mast_definition = catalog.require(self.roster.mast)
        self.mast = MastState(
            max_stacks=int(self._mast_skill("skill1", "max_drunken_stacks")),
            hangover_duration=self._mast_skill("skill2", "hangover_duration_sec"),
        )
        self.buffs = BuffBook()
        self.events: list[BattleEvent] = []
        self.snapshots: list[CycleSnapshot] = []

    def run(self) -> SimulationResult:
        for cycle in self.timeline:
            self._run_cycle(cycle)
        result = SimulationResult(
            policy_name=self.policy.name,
            roster=self.roster,
            timeline=self.timeline,
            events=tuple(self.events),
            snapshots=tuple(self.snapshots),
            buffs=self.buffs,
            catalog=self.catalog,
            builds=self.builds,
            combat_settings=self.combat_settings,
            mechanics_signature=self.skill_hooks.mechanics_signature,
        )
        damage_events = self._damage_events(result)
        events = tuple(
            sorted(
                self.events,
                key=lambda event: (
                    event.time,
                    event.event_type.value,
                    event.actor or "",
                ),
            )
        )
        return replace(result, events=events, damage_events=damage_events)

    def _damage_events(self, result: SimulationResult) -> tuple[DamageEvent, ...]:
        duration = self.combat_settings.duration_sec
        hook_contexts = self._skill_hook_contexts(duration)
        battle_events = tuple(sorted(self.events, key=lambda event: event.time))
        hooks = tuple(
            (context, hook)
            for context in hook_contexts
            if (hook := self.skill_hooks.create(context)) is not None
        )
        for context, hook in hooks:
            for buff in hook.scheduled_buffs(battle_events, context):
                self.buffs.apply(buff)

        weapon_modes = tuple(
            mode
            for context, hook in hooks
            for mode in hook.scheduled_weapon_modes(battle_events, context)
        )

        shots = self._weapon_shots(
            result,
            duration,
            hooks,
            battle_events,
            weapon_modes,
        )
        requests: list[DamageRequest] = []
        sequence = count()
        stream: list[
            tuple[float, int, int, BattleEvent | WeaponShot | RecoveryEffect]
        ] = []
        for event in battle_events:
            heappush(stream, (event.time, 0, next(sequence), event))
        for shot in shots:
            heappush(stream, (shot.time, 1, next(sequence), shot))

        while stream:
            _, _, _, item = heappop(stream)
            if isinstance(item, RecoveryEffect):
                self.apply_recovery(
                    item.time,
                    item.receiver,
                    result.burst_cycle_at(item.time) or 0,
                )
                continue
            if isinstance(item, BattleEvent):
                recoveries: list[RecoveryEffect] = []
                for context, hook in hooks:
                    self._collect_skill_effects(
                        hook.on_battle_event(item, context),
                        requests,
                        result,
                        recoveries=recoveries,
                    )
                for recovery in recoveries:
                    if recovery.time < duration:
                        heappush(
                            stream,
                            (recovery.time, 2, next(sequence), recovery),
                        )
                continue

            modifiers: list[WeaponShotModifier] = []
            recoveries = []
            for context, hook in hooks:
                self._collect_skill_effects(
                    hook.on_weapon_shot(item, context),
                    requests,
                    result,
                    modifiers,
                    recoveries,
                )
            for recovery in recoveries:
                if recovery.time < duration:
                    heappush(
                        stream,
                        (recovery.time, 2, next(sequence), recovery),
                    )
            for modifier in modifiers:
                if modifier.actor != item.actor or modifier.shot_index != item.shot_index:
                    raise ValueError(
                        "weapon shot modifier does not match the current shot: "
                        f"{modifier.actor}#{modifier.shot_index} != "
                        f"{item.actor}#{item.shot_index}"
                    )
            definition = result.catalog.require(item.actor)
            requests.append(
                DamageRequest(
                    time=item.time,
                    actor=item.actor,
                    source=item.source,
                    category=DamageCategory.NORMAL,
                    coefficient_pct=(
                        item.coefficient_pct
                        if item.coefficient_pct is not None
                        else definition.weapon.normal_attack_pct
                    ),
                    traits=DamageTraits(
                        category=DamageCategory.NORMAL,
                        charged=item.charged,
                        core_eligible=item.core_eligible,
                    ),
                    shot_index=item.shot_index,
                    magazine_index=item.magazine_index,
                    charge_multiplier=(
                        definition.weapon.charge_multiplier_pct / 100
                        if item.charged
                        else 1.0
                    ),
                    charge_damage_pct=sum(
                        modifier.charge_damage_pct for modifier in modifiers
                    ),
                    charge_damage_mult_pct=sum(
                        modifier.charge_damage_mult_pct for modifier in modifiers
                    ),
                )
            )

        events = [
            self._resolve_damage_request(result, request)
            for request in requests
            if request.time < duration
        ]
        events.sort(
            key=lambda event: (
                event.time,
                event.actor,
                event.shot_index if event.shot_index is not None else -1,
                event.source,
            )
        )
        return tuple(events)

    def _skill_hook_contexts(self, duration: float) -> tuple[SkillHookContext, ...]:
        contexts: list[SkillHookContext] = []
        seen: set[str] = set()
        for actor in self.roster.members:
            if actor in seen:
                continue
            seen.add(actor)
            definition = self.catalog.get(actor)
            if definition is None:
                continue
            contexts.append(
                SkillHookContext(
                    actor=actor,
                    definition=definition,
                    roster=self.roster,
                    timeline=self.timeline,
                    duration_sec=duration,
                    combat_settings=self.combat_settings,
                )
            )
        return tuple(contexts)

    def _weapon_shots(
        self,
        result: SimulationResult,
        duration: float,
        hooks: tuple[tuple[SkillHookContext, CharacterSkillHook], ...],
        battle_events: tuple[BattleEvent, ...],
        weapon_modes: tuple[WeaponMode, ...],
    ) -> tuple[WeaponShot, ...]:
        shots: list[WeaponShot] = []
        mast_hangovers = tuple(
            (event.time, float(event.payload["until"]))
            for event in self.events
            if event.event_type == EventType.HANGOVER_START
            and event.actor == self.roster.mast
        )
        ammo_charge_by_actor_frame: dict[tuple[str, int], float] = {}
        for context, hook in hooks:
            for effect in hook.ammo_charge_effects(battle_events, context):
                if effect.receiver not in self.roster.members:
                    raise ValueError(f"ammo charge receiver is not in roster: {effect.receiver}")
                if not 0 < effect.fraction_pct <= 100:
                    raise ValueError("ammo charge fraction must be in (0, 100]")
                if 0 <= effect.time < duration:
                    key = (effect.receiver, round(effect.time * FPS))
                    ammo_charge_by_actor_frame[key] = min(
                        100.0,
                        ammo_charge_by_actor_frame.get(key, 0.0) + effect.fraction_pct,
                    )
        seen: set[str] = set()
        for actor in self.roster.members:
            if actor in seen:
                continue
            seen.add(actor)
            definition = self.catalog.get(actor)
            if definition is None:
                continue
            declared_modes = tuple(sorted(
                (mode for mode in weapon_modes if mode.actor == actor),
                key=lambda mode: (mode.start, mode.end, mode.name),
            ))
            for first, second in zip(declared_modes, declared_modes[1:]):
                if first.end > second.start:
                    raise ValueError(
                        f"overlapping weapon modes for {actor}: "
                        f"{first.name}, {second.name}"
                    )
            shared_charge_modes = tuple(
                SharedChargeWeaponMode(
                    name=mode.name,
                    start=mode.start,
                    end=mode.end,
                    charge_frames=mode.weapon.charge_frames,
                    max_shots=(
                        mode.max_shots if mode.max_shots is not None else 0
                    ),
                    source=mode.source,
                    coefficient_pct=mode.weapon.normal_attack_pct,
                    session=session,
                )
                for session, mode in enumerate(declared_modes)
                if mode.share_base_ammo
            )
            actor_modes: list[WeaponMode] = []
            actor_mode_shots: list[tuple[int, WeaponMode, tuple[WeaponShot, ...]]] = []
            for session, mode in enumerate(declared_modes):
                if mode.share_base_ammo:
                    continue
                mode_duration = min(duration, mode.end) - max(0.0, mode.start)
                if mode_duration <= 0:
                    continue
                generated = generate_weapon_shots(
                    actor=actor,
                    weapon=mode.weapon,
                    duration_sec=mode_duration,
                    startup_delay_frames=0,
                    pulls_per_second_override=(
                        mode.pulls_per_second if mode.pulls_per_second is not None else (
                            20.0 if mode.weapon.weapon_type == "SMG"
                            and not self.combat_settings.min_firing_rounds_adjustment else None
                        )
                    ),
                )
                if mode.max_shots is not None:
                    generated = generated[: mode.max_shots]
                    if len(generated) == mode.max_shots:
                        mode = replace(
                            mode,
                            end=min(
                                mode.end,
                                mode.start + generated[-1].time + 1 / FPS,
                            ),
                        )
                actor_modes.append(mode)
                actor_mode_shots.append((session, mode, generated))
            actor_modes_tuple = tuple(actor_modes)
            for first, second in zip(actor_modes_tuple, actor_modes_tuple[1:]):
                if first.end > second.start:
                    raise ValueError(
                        f"overlapping weapon modes for {actor}: "
                        f"{first.name}, {second.name}"
                    )
            for mode in actor_modes_tuple:
                if mode.refill_base_ammo_on_end and mode.end < duration:
                    ammo_charge_by_actor_frame[(actor, round(mode.end * FPS))] = 100.0
            actor_shots = generate_weapon_shots(
                actor=actor,
                weapon=definition.weapon,
                duration_sec=duration,
                reload_speed_at=lambda time, target=actor: result.buff_total(
                    time,
                    target,
                    "reload_speed_pct",
                ),
                charge_speed_at=lambda time, target=actor: result.buff_total(
                    time,
                    target,
                    "charge_speed_pct",
                ),
                fixed_charge_frames_at=lambda time, target=actor: result.buff_total(
                    time,
                    target,
                    "charge_time_fixed_frames",
                ),
                max_ammo_pct_at=lambda time, target=actor: result.buff_total(
                    time,
                    target,
                    "max_ammo_pct",
                ),
                max_ammo_pct_groups_at=lambda time, target=actor: (
                    result.max_ammo_pct_groups(time, target)
                ),
                initial_max_ammo_pct_groups=(
                    (
                        (result.overload_profile(actor).ammo_pct,)
                        if result.overload_profile(actor).ammo_pct
                        else ()
                    )
                    + (
                        (
                            result.collection_weapon_effect(
                                actor,
                                "max_ammo_pct",
                            ),
                        )
                        if result.collection_weapon_effect(actor, "max_ammo_pct")
                        else ()
                    )
                ),
                disabled_at=lambda time, target=actor: (
                    (
                        target == self.roster.mast
                        and any(start <= time < end for start, end in mast_hangovers)
                    )
                    or any(mode.start <= time < mode.end for mode in actor_modes_tuple)
                ),
                instant_reload_at=lambda time, target=actor: (
                    ammo_charge_by_actor_frame.get((target, round(time * FPS)), 0.0)
                ),
                startup_delay_frames=self.combat_settings.startup_delay_frames,
                pulls_per_second_override=(
                    20.0 if definition.weapon.weapon_type == "SMG"
                    and not self.combat_settings.min_firing_rounds_adjustment else None
                ),
                shared_charge_modes=shared_charge_modes,
            )
            shots.extend(actor_shots)
            for session, mode, mode_shots in actor_mode_shots:
                shots.extend(
                    replace(
                        shot,
                        time=round(mode.start + shot.time, 6),
                        frame=round(mode.start * FPS) + shot.frame,
                        source=mode.source,
                        coefficient_pct=mode.weapon.normal_attack_pct,
                        weapon_mode=mode.name,
                        weapon_mode_session=session,
                    )
                    for shot in mode_shots
                    if mode.start + shot.time < min(duration, mode.end)
                )
        shots.sort(key=lambda shot: (shot.time, shot.actor, shot.shot_index))
        actor_indices: dict[str, int] = {}
        reindexed: list[WeaponShot] = []
        for shot in shots:
            shot_index = actor_indices.get(shot.actor, 0)
            actor_indices[shot.actor] = shot_index + 1
            reindexed.append(replace(shot, shot_index=shot_index))
        return tuple(reindexed)

    def _collect_skill_effects(
        self,
        effects: Iterable[SkillEffect],
        requests: list[DamageRequest],
        result: SimulationResult,
        modifiers: list[WeaponShotModifier] | None = None,
        recoveries: list[RecoveryEffect] | None = None,
    ) -> None:
        for effect in effects:
            if isinstance(effect, DamageRequest):
                if effect.time < 0:
                    raise ValueError(f"damage request time must be non-negative: {effect.time}")
                requests.append(effect)
            elif isinstance(effect, BuffWindow):
                if effect.stat in {
                    "reload_speed_pct",
                    "charge_speed_pct",
                    "charge_time_fixed_frames",
                    "max_ammo_pct",
                }:
                    raise ValueError(
                        f"timing-sensitive buff must be emitted from scheduled_buffs: {effect.stat}"
                    )
                self.buffs.apply(effect)
            elif isinstance(effect, WeaponShotModifier):
                if modifiers is None:
                    raise ValueError("weapon shot modifier was emitted outside a weapon shot")
                modifiers.append(effect)
            elif isinstance(effect, RecoveryEffect):
                if effect.time < 0:
                    raise ValueError(f"recovery time must be non-negative: {effect.time}")
                if recoveries is None:
                    raise ValueError("recovery effect cannot be scheduled in this context")
                recoveries.append(effect)
            else:
                raise TypeError(f"unsupported skill effect: {effect!r}")

    def _resolve_damage_request(
        self,
        result: SimulationResult,
        request: DamageRequest,
    ) -> DamageEvent:
        if request.category != request.traits.category:
            raise ValueError(
                f"damage category mismatch: {request.category} != {request.traits.category}"
            )
        definition = result.catalog.require(request.actor)
        buffs = result.resolved_offensive_buffs(request.time, request.actor)
        scoped_normal_crit = (
            buffs.crit_rate_normal_pct
            if request.category == DamageCategory.NORMAL
            else 0.0
        )
        crit_rate_pct = max(
            0.0,
            min(
                100.0,
                definition.base_crit_rate_pct
                + buffs.crit_rate_pct
                + scoped_normal_crit,
            ),
        )
        crit_bonus_pct = crit_rate_pct * (
            definition.base_crit_damage_pct + buffs.crit_damage_pct - 100
        ) / 100
        core_rate_pct = (
            100.0 if request.traits.forced_core
            else self.combat_settings.core_hit_rate_pct
        )
        core_bonus_pct = core_rate_pct * (
            definition.weapon.core_attack_pct
            - 100
            + result.collection_weapon_effect(
                request.actor,
                "core_damage_pct",
            )
            + buffs.core_damage_pct
        ) / 100
        coefficient_pct = request.coefficient_pct
        if request.coefficient_multiplier_stat is not None:
            coefficient_pct *= result.buff_total(
                request.time,
                request.actor,
                request.coefficient_multiplier_stat,
            )
        if request.category == DamageCategory.NORMAL:
            coefficient_pct *= max(
                0.0,
                1
                + (
                    buffs.normal_attack_pct
                    + result.collection_weapon_effect(
                        request.actor,
                        "normal_attack_pct",
                    )
                )
                / 100,
            )
        in_full_burst = result.is_full_burst(request.time)
        breakdown = calculate_damage(
            DamageContext(
                static_atk=result.static_atk(request.actor),
                coefficient_pct=coefficient_pct,
                boss_def=self.combat_settings.boss_def,
                atk_pct=buffs.atk_pct + result.overload_profile(request.actor).atk_pct,
                caster_atk_flat=buffs.caster_atk_flat,
                full_burst_bonus_pct=(
                    self.combat_settings.full_burst_bonus_pct
                    if in_full_burst
                    else 0.0
                ),
                range_bonus_pct=self.combat_settings.range_bonus_pct,
                expected_crit_bonus_pct=crit_bonus_pct,
                core_bonus_pct=core_bonus_pct,
                element_multiplier=self.combat_settings.element_multiplier_for(
                    request.actor,
                    definition.element,
                    result.overload_profile(request.actor).element_pct,
                    definition.extra_advantage_against,
                ),
                charge_multiplier=(
                    request.charge_multiplier
                    + request.charge_multiplier
                    * (
                        buffs.charge_damage_mult_pct
                        + request.charge_damage_mult_pct
                        + result.collection_weapon_effect(
                            request.actor,
                            "charge_damage_mult_pct",
                        )
                    )
                    / 100
                    + (
                        buffs.charge_damage_pct
                        + request.charge_damage_pct
                    )
                    / 100
                ),
                attack_damage_pct=buffs.attack_damage_pct,
                projectile_attachment_pct=(
                    buffs.projectile_attachment_pct
                    + request.projectile_attachment_pct
                ),
                projectile_explosion_pct=(
                    buffs.projectile_explosion_pct
                    + request.projectile_explosion_pct
                ),
                sequential_damage_pct=request.sequential_damage_pct,
                sustained_damage_pct=buffs.sustained_damage_pct,
                sequential_multiplier=request.sequential_multiplier,
                boss_damage_taken_pct=(
                    self.combat_settings.boss_damage_taken_pct
                    + buffs.damage_taken_pct
                ),
                ally_distributed_damage_pct=buffs.distributed_damage_pct,
            ),
            request.traits,
        )
        return DamageEvent(
            time=request.time,
            actor=request.actor,
            source=request.source,
            category=request.category,
            coefficient_pct=coefficient_pct,
            traits=request.traits,
            breakdown=breakdown,
            shot_index=request.shot_index,
            magazine_index=request.magazine_index,
            full_burst=in_full_burst,
            burst_cycle=result.burst_cycle_at(request.time),
            macro_cycle=result.macro_cycle_at(request.time),
        )

    def apply_recovery(self, time: float, receiver: str, cycle: int = 0) -> None:
        self.events.append(BattleEvent(time, cycle, EventType.RECOVERY, receiver))
        if receiver != self.roster.crown:
            return
        self._apply_to_all(
            source=self.roster.crown,
            skill="skill2_recovery",
            stat="attack_damage_pct",
            value=self._crown_skill("skill2", "attack_damage_pct"),
            start=time,
            duration=self._crown_skill("skill2", "duration_sec"),
        )

    def _run_cycle(self, cycle: BurstCycle) -> None:
        self._on_b1(cycle)
        b2_actor = self._b2_actor(cycle.cycle)
        b3_actor = self._b3_actor(cycle)
        stack_at_b2 = self.mast.drunken_stacks
        hungover_at_b2 = self.mast.is_hungover(cycle.b2_time)
        self._on_b2(cycle, b2_actor)
        stack_at_b3 = self.mast.drunken_stacks
        self._on_b3(cycle, b3_actor)
        self._on_full_burst_enter(cycle, b2_actor, b3_actor)
        reset = self._on_full_burst_end(cycle)
        self.snapshots.append(
            CycleSnapshot(
                cycle=cycle.cycle,
                b2_actor=b2_actor,
                b3_actor=b3_actor,
                mast_stack_at_b2=stack_at_b2,
                mast_stack_at_b3=stack_at_b3,
                mast_reset_at_end=reset,
                mast_hangover_at_b2=hungover_at_b2,
            )
        )

    def _on_b1(self, cycle: BurstCycle) -> None:
        activated = self.mast.add_drunken_stack()
        self.events.append(
            BattleEvent(
                cycle.b1_time,
                cycle.cycle,
                EventType.B1_CAST,
                self.roster.b1,
                {"mast_stacks": self.mast.drunken_stacks},
            )
        )
        self.buffs.apply(
            BuffWindow(
                source=self.roster.mast,
                skill="skill1_drunken_self",
                stat="normal_attack_pct",
                value=(
                    -self._mast_skill(
                        "skill1",
                        "expected_normal_damage_loss_per_stack_pct",
                    )
                    * self.mast.drunken_stacks
                ),
                target=self.roster.mast,
                start=cycle.b1_time,
                end=inf,
            )
        )
        if activated:
            self._apply_to_all(
                source=self.roster.mast,
                skill="skill1_drunken",
                stat="crit_rate_pct",
                value=self._mast_skill("skill1", "crit_rate_pct"),
                start=cycle.b1_time,
                duration=inf,
            )
            self._apply_to_all(
                source=self.roster.mast,
                skill="skill1_drunken",
                stat="caster_atk_pct",
                value=self._mast_skill("skill1", "caster_atk_pct"),
                start=cycle.b1_time,
                duration=inf,
                caster=self.roster.mast,
                snapshot=True,
            )

    def _on_b2(self, cycle: BurstCycle, actor: str) -> None:
        self.events.append(
            BattleEvent(
                cycle.b2_time,
                cycle.cycle,
                EventType.B2_CAST,
                actor,
                {"mast_stacks": self.mast.drunken_stacks},
            )
        )
        if actor == self.roster.crown:
            self._apply_to_all(
                source=self.roster.crown,
                skill="burst",
                stat="attack_damage_pct",
                value=self._crown_skill("burst", "attack_damage_pct"),
                start=cycle.b2_time,
                duration=self._crown_skill("burst", "duration_sec"),
            )
            return
        if actor != self.roster.mast:
            raise ValueError(f"unsupported B2 actor: {actor}")
        if self.mast.is_hungover(cycle.b2_time):
            raise ValueError(
                f"Mast cannot cast during Hangover at cycle {cycle.cycle} ({cycle.b2_time}s)"
            )
        stack = self.mast.drunken_stacks
        self._apply_to_all(
            source=self.roster.mast,
            skill="burst",
            stat="crit_damage_pct",
            value=self._mast_skill("burst", "crit_damage_pct"),
            start=cycle.b2_time,
            duration=self._mast_skill("burst", "duration_sec"),
        )
        self._apply_to_all(
            source=self.roster.mast,
            skill="burst",
            stat="attack_damage_pct",
            value=self._mast_skill("burst", "attack_damage_pct"),
            start=cycle.b2_time,
            duration=self._mast_skill("burst", "duration_sec"),
        )
        self._apply_to_all(
            source=self.roster.mast,
            skill="burst",
            stat="caster_atk_pct",
            value=self._mast_skill("burst", "caster_atk_per_stack_pct") * stack,
            start=cycle.b2_time,
            duration=self._mast_skill("burst", "duration_sec"),
            caster=self.roster.mast,
            snapshot=True,
        )

    def _on_b3(self, cycle: BurstCycle, b3_actor: str) -> None:
        stack = self.mast.drunken_stacks
        self.events.append(
            BattleEvent(
                cycle.b3_time,
                cycle.cycle,
                EventType.B3_STAGE_ENTER,
                b3_actor,
                {"mast_stacks": stack},
            )
        )
        if stack <= 0:
            return
        self._apply_to_all(
            source=self.roster.mast,
            skill="skill2_b3_stage",
            stat="distributed_damage_pct",
            value=self._mast_skill("skill2", "distributed_per_stack_pct") * stack,
            start=cycle.b3_time,
            duration=self._mast_skill("skill2", "duration_sec"),
        )
        self._apply_to_all(
            source=self.roster.mast,
            skill="skill2_b3_stage",
            stat="reload_speed_pct",
            value=self._mast_skill("skill2", "reload_per_stack_pct") * stack,
            start=cycle.b3_time,
            duration=self._mast_skill("skill2", "duration_sec"),
        )

    def _on_full_burst_enter(
        self,
        cycle: BurstCycle,
        b2_actor: str,
        b3_actor: str,
    ) -> None:
        burst_casters = (self.roster.b1, b2_actor, b3_actor)
        self.events.append(
            BattleEvent(
                cycle.full_burst_start,
                cycle.cycle,
                EventType.FULL_BURST_ENTER,
                payload={"burst_casters": burst_casters},
            )
        )
        self._apply_to_all(
            source=self.roster.crown,
            skill="skill1_full_burst",
            stat="reload_speed_pct",
            value=self._crown_skill("skill1", "reload_speed_pct"),
            start=cycle.full_burst_start,
            duration=self._crown_skill("skill1", "duration_sec"),
        )
        for target in burst_casters:
            self.buffs.apply(
                BuffWindow(
                    source=self.roster.crown,
                    skill="skill1_full_burst",
                    stat="caster_atk_pct",
                    value=self._crown_skill("skill1", "caster_atk_pct"),
                    target=target,
                    start=cycle.full_burst_start,
                    end=cycle.full_burst_start
                    + self._crown_skill("skill1", "duration_sec"),
                    caster=self.roster.crown,
                    snapshot=True,
                )
            )

    def _on_full_burst_end(self, cycle: BurstCycle) -> bool:
        self.events.append(
            BattleEvent(cycle.full_burst_end, cycle.cycle, EventType.FULL_BURST_END)
        )
        reset = self.mast.reset_at_full_burst_end(cycle.full_burst_end)
        if not reset:
            return False
        self.buffs.close(self.roster.mast, "skill1_drunken", cycle.full_burst_end)
        self.buffs.close(
            self.roster.mast,
            "skill1_drunken_self",
            cycle.full_burst_end,
        )
        self.events.append(
            BattleEvent(cycle.full_burst_end, cycle.cycle, EventType.MAST_RESET, self.roster.mast)
        )
        self.events.append(
            BattleEvent(
                cycle.full_burst_end,
                cycle.cycle,
                EventType.HANGOVER_START,
                self.roster.mast,
                {"until": self.mast.hangover_until},
            )
        )
        return True

    def _b3_actor(self, cycle: BurstCycle) -> str:
        try:
            return getattr(self.roster, cycle.b3_slot)
        except AttributeError as exc:
            raise ValueError(f"unsupported B3 slot: {cycle.b3_slot}") from exc

    def _b2_actor(self, cycle: int) -> str:
        slot = self.policy.b2_slot(cycle)
        try:
            return getattr(self.roster, slot)
        except AttributeError as exc:
            raise ValueError(f"unsupported B2 slot: {slot}") from exc

    def _crown_skill(self, skill: str, key: str) -> float:
        return self.crown_definition.skill_value(skill, key)

    def _mast_skill(self, skill: str, key: str) -> float:
        return self.mast_definition.skill_value(skill, key)

    def _apply_to_all(
        self,
        *,
        source: str,
        skill: str,
        stat: str,
        value: float,
        start: float,
        duration: float,
        caster: str | None = None,
        snapshot: bool = False,
    ) -> None:
        for target in self.roster.members:
            self.buffs.apply(
                BuffWindow(
                    source=source,
                    skill=skill,
                    stat=stat,
                    value=value,
                    target=target,
                    start=start,
                    end=start + duration,
                    caster=caster,
                    snapshot=snapshot,
                )
            )


def simulate_rotation(
    policy: RotationPolicy,
    roster: TeamRoster | None = None,
    timeline: tuple[BurstCycle, ...] = STANDARD_TIMELINE,
    catalog: CharacterCatalog = STANDARD_CHARACTER_CATALOG,
    builds: Mapping[str, BuildProfile] | None = None,
    combat_settings: CombatSettings = STANDARD_COMBAT_SETTINGS,
    skill_hooks: SkillHookRegistry = STANDARD_SKILL_HOOKS,
) -> SimulationResult:
    return CrownMastEngine(
        policy=policy,
        roster=roster,
        timeline=timeline,
        catalog=catalog,
        builds=builds,
        combat_settings=combat_settings,
        skill_hooks=skill_hooks,
    ).run()
