from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Mapping

from .characters import CharacterCatalog, STANDARD_CHARACTER_CATALOG
from .combat import STANDARD_COMBAT_SETTINGS, CombatSettings
from .engine import SimulationResult, simulate_rotation
from .equipment import BuildProfile
from .mechanics import SkillHookRegistry
from .character_mechanics import STANDARD_SKILL_HOOKS
from .models import DamageCategory, TeamRoster
from .rotations import (
    CROWN_CROWN_MAST,
    OPENING_MAST_CROWN_MAST,
    OPENING_MAST_SUSTAINED_FUNNEL,
    SUSTAINED_FUNNEL,
    RotationPolicy,
)
from .timeline import RAID14_TIMELINE, BurstCycle


class ComparisonCase(str, Enum):
    STANDARD_BREAK_EVEN = "standard_break_even"
    FUNNEL_DOMINATES = "funnel_dominates"
    CONVENTIONAL_DOMINATES = "conventional_dominates"
    REVERSE_BREAK_EVEN = "reverse_break_even"
    EQUAL = "equal"


class RotationWinner(str, Enum):
    CONVENTIONAL = "conventional"
    FUNNEL = "funnel"
    TIE = "tie"


class BreakEvenDirection(str, Enum):
    FUNNEL_ABOVE = "funnel_above"
    FUNNEL_BELOW = "funnel_below"


@dataclass(frozen=True)
class DamageComparison:
    conventional: float
    funnel: float

    @property
    def delta(self) -> float:
        return self.funnel - self.conventional

    @property
    def relative_change(self) -> float | None:
        if self.conventional == 0:
            return None
        return self.funnel / self.conventional - 1

    @property
    def loss_from_funnel(self) -> float:
        return self.conventional - self.funnel

    @property
    def relative_loss_from_funnel(self) -> float | None:
        if self.conventional == 0:
            return None
        return 1 - self.funnel / self.conventional


@dataclass(frozen=True)
class DamageSliceComparison:
    r_c: float
    r_f: float
    o_c: float
    o_f: float
    g: float | None
    l: float | None
    comparison_case: ComparisonCase
    lambda_star: float | None
    break_even_main_share_c: float | None
    funnel_wins_above_break_even: bool | None

    @property
    def team_c(self) -> float:
        return self.r_c + self.o_c

    @property
    def team_f(self) -> float:
        return self.r_f + self.o_f

    @property
    def delta_r(self) -> float:
        return self.r_f - self.r_c

    @property
    def delta_o(self) -> float:
        return self.o_f - self.o_c

    @property
    def delta_total(self) -> float:
        return self.team_f - self.team_c

    @property
    def team_relative_change(self) -> float | None:
        if self.team_c == 0:
            return None
        return self.team_f / self.team_c - 1

    @property
    def conventional_main_share(self) -> float | None:
        return None if self.team_c == 0 else self.r_c / self.team_c

    @property
    def funnel_main_share(self) -> float | None:
        return None if self.team_f == 0 else self.r_f / self.team_f

    @property
    def local_slope(self) -> float | None:
        if self.g is None or self.l is None:
            return None
        return self.g + self.l

    @property
    def local_extreme_upside(self) -> float | None:
        return self.g

    @property
    def has_scaling_break_even(self) -> bool:
        return self.lambda_star is not None

    @property
    def has_share_break_even(self) -> bool:
        return self.break_even_main_share_c is not None

    @property
    def break_even_direction(self) -> BreakEvenDirection | None:
        if self.funnel_wins_above_break_even is None:
            return None
        if self.funnel_wins_above_break_even:
            return BreakEvenDirection.FUNNEL_ABOVE
        return BreakEvenDirection.FUNNEL_BELOW

    def require_break_even_main_share_c(self) -> float:
        if self.break_even_main_share_c is None:
            raise ValueError(
                "break-even main share is unavailable for comparison case: "
                f"{self.comparison_case.value}"
            )
        return self.break_even_main_share_c

    @property
    def observed_winner(self) -> RotationWinner:
        tolerance = _zero_tolerance(self.team_c, self.team_f)
        if abs(self.delta_total) <= tolerance:
            return RotationWinner.TIE
        if self.delta_total > 0:
            return RotationWinner.FUNNEL
        return RotationWinner.CONVENTIONAL


@dataclass(frozen=True)
class RotationComparison:
    main_actor: str
    conventional_result: SimulationResult
    funnel_result: SimulationResult
    overall: DamageSliceComparison
    macro_cycles: Mapping[int, DamageSliceComparison]
    burst_cycles: Mapping[int, DamageSliceComparison]
    by_character: Mapping[str, DamageComparison]
    by_character_burst_cycle: Mapping[str, Mapping[int, DamageComparison]]
    by_category: Mapping[DamageCategory, DamageComparison]
    by_character_category: Mapping[
        str,
        Mapping[DamageCategory, DamageComparison],
    ]
    by_source: Mapping[tuple[str, str], DamageComparison]
    secondary_b3_mast3_burst_omission_cycles: tuple[int, ...]

    @property
    def secondary_b3(self) -> DamageComparison:
        return self.by_character[self.conventional_result.roster.secondary_b3]

    @property
    def secondary_b3_mast3_burst_omission_cycle_damage(self) -> DamageComparison:
        actor = self.conventional_result.roster.secondary_b3
        cycle_damage = self.by_character_burst_cycle[actor]
        return DamageComparison(
            conventional=sum(
                cycle_damage[cycle].conventional
                for cycle in self.secondary_b3_mast3_burst_omission_cycles
            ),
            funnel=sum(
                cycle_damage[cycle].funnel
                for cycle in self.secondary_b3_mast3_burst_omission_cycles
            ),
        )

    @property
    def secondary_b3_mast3_deprivation_cycles(self) -> tuple[int, ...]:
        return self.secondary_b3_mast3_burst_omission_cycles

    @property
    def secondary_b3_mast3_deprivation(self) -> DamageComparison:
        return self.secondary_b3_mast3_burst_omission_cycle_damage

    @property
    def secondary_b3_mast3_unavailable_cycles(self) -> tuple[int, ...]:
        return self.secondary_b3_mast3_burst_omission_cycles

    @property
    def secondary_b3_mast3_unavailable_cycle_damage(self) -> DamageComparison:
        return self.secondary_b3_mast3_burst_omission_cycle_damage


@dataclass
class _DamageIndex:
    total: float
    by_actor: dict[str, float]
    by_macro_cycle: dict[int, float]
    by_actor_macro_cycle: dict[tuple[str, int], float]
    by_burst_cycle: dict[int, float]
    by_actor_burst_cycle: dict[tuple[str, int], float]
    by_category: dict[DamageCategory, float]
    by_actor_category: dict[tuple[str, DamageCategory], float]
    by_actor_source: dict[tuple[str, str], float]

    @classmethod
    def from_result(cls, result: SimulationResult) -> _DamageIndex:
        all_damage: list[float] = []
        by_actor: dict[str, list[float]] = {}
        by_macro_cycle: dict[int, list[float]] = {}
        by_actor_macro_cycle: dict[tuple[str, int], list[float]] = {}
        by_burst_cycle: dict[int, list[float]] = {}
        by_actor_burst_cycle: dict[tuple[str, int], list[float]] = {}
        by_category: dict[DamageCategory, list[float]] = {}
        by_actor_category: dict[tuple[str, DamageCategory], list[float]] = {}
        by_actor_source: dict[tuple[str, str], list[float]] = {}

        for event in result.damage_events:
            damage = event.damage
            all_damage.append(damage)
            _append_damage(by_actor, event.actor, damage)
            _append_damage(by_category, event.category, damage)
            _append_damage(by_actor_category, (event.actor, event.category), damage)
            _append_damage(by_actor_source, (event.actor, event.source), damage)
            if event.macro_cycle is not None:
                _append_damage(by_macro_cycle, event.macro_cycle, damage)
                _append_damage(
                    by_actor_macro_cycle,
                    (event.actor, event.macro_cycle),
                    damage,
                )
            if event.burst_cycle is not None:
                _append_damage(by_burst_cycle, event.burst_cycle, damage)
                _append_damage(
                    by_actor_burst_cycle,
                    (event.actor, event.burst_cycle),
                    damage,
                )

        return cls(
            total=sum(all_damage),
            by_actor=_sum_damage_groups(by_actor),
            by_macro_cycle=_sum_damage_groups(by_macro_cycle),
            by_actor_macro_cycle=_sum_damage_groups(by_actor_macro_cycle),
            by_burst_cycle=_sum_damage_groups(by_burst_cycle),
            by_actor_burst_cycle=_sum_damage_groups(by_actor_burst_cycle),
            by_category=_sum_damage_groups(by_category),
            by_actor_category=_sum_damage_groups(by_actor_category),
            by_actor_source=_sum_damage_groups(by_actor_source),
        )


def _append_damage(mapping: dict, key: object, damage: float) -> None:
    mapping.setdefault(key, []).append(damage)


def _sum_damage_groups(mapping: dict) -> dict:
    return {key: sum(values) for key, values in mapping.items()}


def compare_damage_totals(
    *,
    r_c: float,
    r_f: float,
    o_c: float,
    o_f: float,
) -> DamageSliceComparison:
    values = (r_c, r_f, o_c, o_f)
    if any(not isfinite(value) or value < 0 for value in values):
        raise ValueError("damage totals must be finite and non-negative")

    delta_r = r_f - r_c
    delta_o = o_f - o_c
    tolerance = _zero_tolerance(*values)
    sign_r = _sign(delta_r, tolerance)
    sign_o = _sign(delta_o, tolerance)

    if sign_r == 0 and sign_o == 0:
        comparison_case = ComparisonCase.EQUAL
    elif sign_r > 0 and sign_o < 0:
        comparison_case = ComparisonCase.STANDARD_BREAK_EVEN
    elif sign_r < 0 and sign_o > 0:
        comparison_case = ComparisonCase.REVERSE_BREAK_EVEN
    elif sign_r >= 0 and sign_o >= 0 and (sign_r > 0 or sign_o > 0):
        comparison_case = ComparisonCase.FUNNEL_DOMINATES
    elif sign_r <= 0 and sign_o <= 0 and (sign_r < 0 or sign_o < 0):
        comparison_case = ComparisonCase.CONVENTIONAL_DOMINATES
    else:
        raise AssertionError(
            f"unhandled comparison signs: delta_r={sign_r}, delta_o={sign_o}"
        )

    lambda_star: float | None = None
    break_even_share: float | None = None
    funnel_wins_above: bool | None = None
    if comparison_case in {
        ComparisonCase.STANDARD_BREAK_EVEN,
        ComparisonCase.REVERSE_BREAK_EVEN,
    }:
        lambda_star = -delta_o / delta_r
        break_even_total = lambda_star * r_c + o_c
        if r_c > tolerance and o_c > tolerance and isfinite(break_even_total):
            break_even_share = lambda_star * r_c / break_even_total
        funnel_wins_above = comparison_case == ComparisonCase.STANDARD_BREAK_EVEN

    return DamageSliceComparison(
        r_c=r_c,
        r_f=r_f,
        o_c=o_c,
        o_f=o_f,
        g=None if r_c == 0 else r_f / r_c - 1,
        l=None if o_c == 0 else 1 - o_f / o_c,
        comparison_case=comparison_case,
        lambda_star=lambda_star,
        break_even_main_share_c=break_even_share,
        funnel_wins_above_break_even=funnel_wins_above,
    )


def compare_rotation_results(
    conventional: SimulationResult,
    funnel: SimulationResult,
    *,
    main_actor: str | None = None,
) -> RotationComparison:
    _validate_compatible_results(conventional, funnel)
    main_actor = main_actor or conventional.roster.main_b3
    if main_actor not in conventional.roster.members:
        raise ValueError(f"main actor is not in the roster: {main_actor}")

    conventional_index = _DamageIndex.from_result(conventional)
    funnel_index = _DamageIndex.from_result(funnel)
    overall = _slice_comparison(conventional_index, funnel_index, main_actor)
    macro_ids = sorted(
        conventional_index.by_macro_cycle.keys()
        | funnel_index.by_macro_cycle.keys()
    )
    macro_cycles = MappingProxyType(
        {
            macro_cycle: _slice_comparison(
                conventional_index,
                funnel_index,
                main_actor,
                macro_cycle=macro_cycle,
            )
            for macro_cycle in macro_ids
        }
    )

    burst_ids = sorted(
        conventional_index.by_burst_cycle.keys()
        | funnel_index.by_burst_cycle.keys()
    )
    burst_cycles = MappingProxyType(
        {
            burst_cycle: _slice_comparison(
                conventional_index,
                funnel_index,
                main_actor,
                burst_cycle=burst_cycle,
            )
            for burst_cycle in burst_ids
        }
    )

    actors = conventional.roster.members
    by_character = MappingProxyType(
        {
            actor: DamageComparison(
                conventional_index.by_actor.get(actor, 0.0),
                funnel_index.by_actor.get(actor, 0.0),
            )
            for actor in actors
        }
    )
    by_character_burst_cycle = MappingProxyType(
        {
            actor: MappingProxyType(
                {
                    burst_cycle: DamageComparison(
                        conventional_index.by_actor_burst_cycle.get(
                            (actor, burst_cycle),
                            0.0,
                        ),
                        funnel_index.by_actor_burst_cycle.get(
                            (actor, burst_cycle),
                            0.0,
                        ),
                    )
                    for burst_cycle in burst_ids
                }
            )
            for actor in actors
        }
    )
    by_category = MappingProxyType(
        {
            category: DamageComparison(
                conventional_index.by_category.get(category, 0.0),
                funnel_index.by_category.get(category, 0.0),
            )
            for category in DamageCategory
        }
    )
    by_character_category = MappingProxyType(
        {
            actor: MappingProxyType(
                {
                    category: DamageComparison(
                        conventional_index.by_actor_category.get(
                            (actor, category),
                            0.0,
                        ),
                        funnel_index.by_actor_category.get(
                            (actor, category),
                            0.0,
                        ),
                    )
                    for category in DamageCategory
                }
            )
            for actor in actors
        }
    )
    source_keys = sorted(
        conventional_index.by_actor_source.keys()
        | funnel_index.by_actor_source.keys()
    )
    by_source = MappingProxyType(
        {
            key: DamageComparison(
                conventional_index.by_actor_source.get(key, 0.0),
                funnel_index.by_actor_source.get(key, 0.0),
            )
            for key in source_keys
        }
    )
    conventional_snapshots = {
        snapshot.cycle: snapshot for snapshot in conventional.snapshots
    }
    funnel_snapshots = {
        snapshot.cycle: snapshot for snapshot in funnel.snapshots
    }
    max_mast_stacks = int(
        conventional.catalog.require(conventional.roster.mast).skill_value(
            "skill1",
            "max_drunken_stacks",
        )
    )
    mast3_burst_omission_cycles = tuple(
        cycle
        for cycle in sorted(conventional_snapshots.keys() & funnel_snapshots.keys())
        if conventional_snapshots[cycle].b2_actor == conventional.roster.mast
        and conventional_snapshots[cycle].mast_stack_at_b2 == max_mast_stacks
        and funnel_snapshots[cycle].b2_actor != funnel.roster.mast
        and conventional_snapshots[cycle].b3_actor
        == conventional.roster.secondary_b3
        and funnel_snapshots[cycle].b3_actor == funnel.roster.secondary_b3
    )
    return RotationComparison(
        main_actor=main_actor,
        conventional_result=conventional,
        funnel_result=funnel,
        overall=overall,
        macro_cycles=macro_cycles,
        burst_cycles=burst_cycles,
        by_character=by_character,
        by_character_burst_cycle=by_character_burst_cycle,
        by_category=by_category,
        by_character_category=by_character_category,
        by_source=by_source,
        secondary_b3_mast3_burst_omission_cycles=mast3_burst_omission_cycles,
    )


def analyze_rotations(
    *,
    roster: TeamRoster | None = None,
    timeline: tuple[BurstCycle, ...] = RAID14_TIMELINE,
    catalog: CharacterCatalog = STANDARD_CHARACTER_CATALOG,
    builds: Mapping[str, BuildProfile] | None = None,
    combat_settings: CombatSettings = STANDARD_COMBAT_SETTINGS,
    skill_hooks: SkillHookRegistry = STANDARD_SKILL_HOOKS,
    main_actor: str | None = None,
    conventional_policy: RotationPolicy = CROWN_CROWN_MAST,
    funnel_policy: RotationPolicy | None = None,
) -> RotationComparison:
    common = {
        "roster": roster,
        "timeline": timeline,
        "catalog": catalog,
        "builds": builds,
        "combat_settings": combat_settings,
        "skill_hooks": skill_hooks,
    }
    conventional = simulate_rotation(conventional_policy, **common)
    if funnel_policy is None:
        funnel_policy = (
            OPENING_MAST_SUSTAINED_FUNNEL
            if conventional_policy.name == OPENING_MAST_CROWN_MAST.name
            else SUSTAINED_FUNNEL
        )
    funnel = simulate_rotation(funnel_policy, **common)
    return compare_rotation_results(
        conventional,
        funnel,
        main_actor=main_actor,
    )


def analyze_mast_expected_hit_loss_sensitivity(
    loss_per_stack_values: tuple[float, ...] = (0.0, 18.0, 20.0, 22.0),
    *,
    roster: TeamRoster | None = None,
    timeline: tuple[BurstCycle, ...] = RAID14_TIMELINE,
    catalog: CharacterCatalog = STANDARD_CHARACTER_CATALOG,
    builds: Mapping[str, BuildProfile] | None = None,
    combat_settings: CombatSettings = STANDARD_COMBAT_SETTINGS,
    skill_hooks: SkillHookRegistry = STANDARD_SKILL_HOOKS,
    main_actor: str | None = None,
    conventional_policy: RotationPolicy = CROWN_CROWN_MAST,
) -> Mapping[float, RotationComparison]:
    roster = roster or TeamRoster()
    max_stacks = int(
        catalog.require(roster.mast).skill_value(
            "skill1",
            "max_drunken_stacks",
        )
    )
    if max_stacks <= 0:
        raise ValueError("Mast max Drunken stacks must be positive")
    maximum_loss = 100 / max_stacks
    normalized_values: list[float] = []
    for value in loss_per_stack_values:
        value = float(value)
        if not isfinite(value) or not 0 <= value <= maximum_loss:
            raise ValueError(
                "expected normal damage loss per stack must be finite and "
                f"between 0 and {maximum_loss}"
            )
        if value in normalized_values:
            raise ValueError(f"duplicate sensitivity value: {value}")
        normalized_values.append(value)

    return MappingProxyType(
        {
            value: analyze_rotations(
                roster=roster,
                timeline=timeline,
                catalog=catalog.with_skill_value(
                    roster.mast,
                    "skill1",
                    "expected_normal_damage_loss_per_stack_pct",
                    value,
                ),
                builds=builds,
                combat_settings=combat_settings,
                skill_hooks=skill_hooks,
                main_actor=main_actor,
                conventional_policy=conventional_policy,
            )
            for value in normalized_values
        }
    )


def _slice_comparison(
    conventional: _DamageIndex,
    funnel: _DamageIndex,
    main_actor: str,
    *,
    macro_cycle: int | None = None,
    burst_cycle: int | None = None,
) -> DamageSliceComparison:
    if macro_cycle is not None and burst_cycle is not None:
        raise ValueError("damage slice cannot select macro and burst cycles together")
    if macro_cycle is not None:
        team_c = conventional.by_macro_cycle.get(macro_cycle, 0.0)
        team_f = funnel.by_macro_cycle.get(macro_cycle, 0.0)
        r_c = conventional.by_actor_macro_cycle.get((main_actor, macro_cycle), 0.0)
        r_f = funnel.by_actor_macro_cycle.get((main_actor, macro_cycle), 0.0)
    elif burst_cycle is not None:
        team_c = conventional.by_burst_cycle.get(burst_cycle, 0.0)
        team_f = funnel.by_burst_cycle.get(burst_cycle, 0.0)
        r_c = conventional.by_actor_burst_cycle.get((main_actor, burst_cycle), 0.0)
        r_f = funnel.by_actor_burst_cycle.get((main_actor, burst_cycle), 0.0)
    else:
        team_c = conventional.total
        team_f = funnel.total
        r_c = conventional.by_actor.get(main_actor, 0.0)
        r_f = funnel.by_actor.get(main_actor, 0.0)
    return compare_damage_totals(
        r_c=r_c,
        r_f=r_f,
        o_c=team_c - r_c,
        o_f=team_f - r_f,
    )


def _validate_compatible_results(
    conventional: SimulationResult,
    funnel: SimulationResult,
) -> None:
    mismatches: list[str] = []
    if conventional.roster != funnel.roster:
        mismatches.append("roster")
    if conventional.timeline != funnel.timeline:
        mismatches.append("timeline")
    if conventional.combat_settings != funnel.combat_settings:
        mismatches.append("combat_settings")
    if conventional.mechanics_signature != funnel.mechanics_signature:
        mismatches.append("mechanics_signature")
    if dict(conventional.builds) != dict(funnel.builds):
        mismatches.append("builds")
    if conventional.catalog.scope != funnel.catalog.scope:
        mismatches.append("catalog.scope")
    if conventional.catalog.definitions != funnel.catalog.definitions:
        mismatches.append("catalog.definitions")
    if mismatches:
        raise ValueError(
            "rotation results are not a controlled pair; mismatched: "
            + ", ".join(mismatches)
        )


def _zero_tolerance(*values: float) -> float:
    return max(1e-6, max((abs(value) for value in values), default=0.0) * 1e-12)


def _sign(value: float, tolerance: float) -> int:
    if abs(value) <= tolerance:
        return 0
    return 1 if value > 0 else -1
