from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping

from .analysis import (
    DamageComparison,
    DamageSliceComparison,
    RotationComparison,
    analyze_rotations,
    compare_rotation_results,
)
from .characters import CharacterCatalog, STANDARD_CHARACTER_CATALOG
from .character_mechanics import STANDARD_SKILL_HOOKS
from .combat import CombatSettings
from .equipment import (
    GEAR_SLOTS,
    BuildProfile,
    EquipmentLoadout,
    GearState,
    OverloadProfile,
    STANDARD_BUILD,
    CollectionProfile,
    standard_build_for_actor,
)
from .engine import SimulationResult, simulate_rotation
from .mechanics import ENGINE_RULE_REVISION, MechanicsSignature, SkillHookRegistry
from .models import DamageCategory, TeamRoster
from .rotations import (
    CROWN_CROWN_MAST,
    OPENING_MAST_CROWN_MAST,
    OPENING_MAST_SUSTAINED_FUNNEL,
    SUSTAINED_FUNNEL,
    baseline_rotation as resolve_baseline_rotation,
)
from .timeline import STANDARD_TIMELINE, BurstCycle


RESEARCH_SCENARIO_SCHEMA_VERSION = 2
COMPARISON_REPORT_SCHEMA_VERSION = 3

BREAK_EVEN_METHODOLOGY = MappingProxyType(
    {
        "method": "local_main_damage_scaling",
        "scaled_components": ("main_conventional", "main_funnel"),
        "fixed_components": (
            "non_main_damage",
            "event_timing",
            "buff_windows",
            "skill_procs",
        ),
        "reported_share_basis": "conventional_total_at_break_even",
    }
)


class OutcomeBand(str, Enum):
    TIE_BAND = "tie_band"
    MARGINAL_CONVENTIONAL = "marginal_conventional"
    MARGINAL_FUNNEL = "marginal_funnel"
    CLEAR_CONVENTIONAL = "clear_conventional"
    CLEAR_FUNNEL = "clear_funnel"


@dataclass(frozen=True)
class OutcomeThresholds:
    tie_band_pct: float = 0.1
    clear_advantage_pct: float = 0.5

    def __post_init__(self) -> None:
        values = (self.tie_band_pct, self.clear_advantage_pct)
        if any(isinstance(value, bool) for value in values):
            raise TypeError("outcome thresholds must be numeric")
        if any(not isfinite(value) or value < 0 for value in values):
            raise ValueError("outcome thresholds must be finite and non-negative")
        if self.clear_advantage_pct < self.tie_band_pct:
            raise ValueError("clear_advantage_pct must be at least tie_band_pct")

    def classify(self, relative_change: float | None) -> OutcomeBand:
        if relative_change is None:
            return OutcomeBand.TIE_BAND
        change_pct = relative_change * 100
        magnitude = abs(change_pct)
        if magnitude <= self.tie_band_pct:
            return OutcomeBand.TIE_BAND
        if change_pct > 0:
            if magnitude >= self.clear_advantage_pct:
                return OutcomeBand.CLEAR_FUNNEL
            return OutcomeBand.MARGINAL_FUNNEL
        if magnitude >= self.clear_advantage_pct:
            return OutcomeBand.CLEAR_CONVENTIONAL
        return OutcomeBand.MARGINAL_CONVENTIONAL

    def to_dict(self) -> dict[str, float]:
        return {
            "tie_band_pct": self.tie_band_pct,
            "clear_advantage_pct": self.clear_advantage_pct,
        }


@dataclass(frozen=True)
class ResearchScenario:
    roster: TeamRoster
    builds: Mapping[str, BuildProfile]
    combat_settings: CombatSettings
    main_actor: str
    baseline_rotation: str = CROWN_CROWN_MAST.name
    timeline: tuple[BurstCycle, ...] = STANDARD_TIMELINE
    thresholds: OutcomeThresholds = OutcomeThresholds()
    expected_engine_rule_revision: str = ENGINE_RULE_REVISION
    expected_skill_hook_revision: str = (
        STANDARD_SKILL_HOOKS.mechanics_signature.skill_hook_revision
    )
    expected_catalog_source_revision: str = (
        STANDARD_CHARACTER_CATALOG.scope.source_revision
    )

    def __post_init__(self) -> None:
        if any(
            not isinstance(actor, str) or not actor
            for actor in self.roster.members
        ):
            raise TypeError("research roster members must be non-empty strings")
        if len(set(self.roster.members)) != len(self.roster.members):
            raise ValueError("research roster members must be unique")
        if self.main_actor not in self.roster.members:
            raise ValueError(f"main actor is not in the roster: {self.main_actor}")
        resolve_baseline_rotation(self.baseline_rotation)
        builds = dict(self.builds)
        if any(not isinstance(build, BuildProfile) for build in builds.values()):
            raise TypeError("scenario builds must contain BuildProfile values")
        missing = set(self.roster.members) - builds.keys()
        extra = builds.keys() - set(self.roster.members)
        if missing or extra:
            details = []
            if missing:
                details.append(f"missing={sorted(missing)}")
            if extra:
                details.append(f"extra={sorted(extra)}")
            raise ValueError("scenario builds must match roster: " + ", ".join(details))
        object.__setattr__(self, "builds", MappingProxyType(builds))

        override_actors = set(self.combat_settings.element_multiplier_by_actor)
        unknown_overrides = override_actors - set(self.roster.members)
        if unknown_overrides:
            raise ValueError(
                "element overrides contain actors outside roster: "
                f"{sorted(unknown_overrides)}"
            )
        revisions = (
            self.expected_engine_rule_revision,
            self.expected_skill_hook_revision,
            self.expected_catalog_source_revision,
        )
        if any(not isinstance(revision, str) or not revision for revision in revisions):
            raise ValueError("expected revisions must be non-empty strings")
        timeline = tuple(self.timeline)
        object.__setattr__(self, "timeline", timeline)
        _validate_timeline(timeline, self.combat_settings.duration_sec)

    @classmethod
    def standard(cls) -> ResearchScenario:
        roster = TeamRoster()
        return cls(
            roster=roster,
            builds={actor: standard_build_for_actor(actor) for actor in roster.members},
            combat_settings=CombatSettings(),
            main_actor=roster.main_b3,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": RESEARCH_SCENARIO_SCHEMA_VERSION,
            "expected_revisions": {
                "engine_rule": self.expected_engine_rule_revision,
                "skill_hooks": self.expected_skill_hook_revision,
                "catalog_source": self.expected_catalog_source_revision,
            },
            "roster": {
                "b1": self.roster.b1,
                "crown": self.roster.crown,
                "mast": self.roster.mast,
                "main_b3": self.roster.main_b3,
                "secondary_b3": self.roster.secondary_b3,
            },
            "main_actor": self.main_actor,
            "baseline_rotation": self.baseline_rotation,
            "builds": {
                actor: _build_to_dict(self.builds[actor])
                for actor in self.roster.members
            },
            "combat_settings": _combat_settings_to_dict(self.combat_settings),
            "timeline": [_cycle_to_dict(cycle) for cycle in self.timeline],
            "thresholds": self.thresholds.to_dict(),
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ResearchScenario:
        schema_version = payload.get("schema_version")
        fields = {
            "schema_version",
            "expected_revisions",
            "roster",
            "main_actor",
            "builds",
            "combat_settings",
            "timeline",
            "thresholds",
        }
        if schema_version == RESEARCH_SCENARIO_SCHEMA_VERSION:
            fields.add("baseline_rotation")
        elif schema_version != 1:
            raise ValueError(
                f"unsupported research scenario schema: {schema_version}"
            )
        _require_exact_keys(payload, fields, "scenario")
        roster_payload = _require_mapping(payload["roster"], "roster")
        _require_exact_keys(
            roster_payload,
            {"b1", "crown", "mast", "main_b3", "secondary_b3"},
            "roster",
        )
        roster = TeamRoster(
            **{
                key: _require_string(value, f"roster.{key}")
                for key, value in roster_payload.items()
            }
        )

        builds_payload = _require_mapping(payload["builds"], "builds")
        builds = {
            actor: _build_from_dict(
                _require_mapping(build_payload, f"builds.{actor}"),
                f"builds.{actor}",
            )
            for actor, build_payload in builds_payload.items()
        }
        combat_payload = _require_mapping(
            payload["combat_settings"],
            "combat_settings",
        )
        thresholds_payload = _require_mapping(payload["thresholds"], "thresholds")
        _require_exact_keys(
            thresholds_payload,
            {"tie_band_pct", "clear_advantage_pct"},
            "thresholds",
        )
        revisions = _require_mapping(payload["expected_revisions"], "expected_revisions")
        _require_exact_keys(
            revisions,
            {"engine_rule", "skill_hooks", "catalog_source"},
            "expected_revisions",
        )
        timeline_payload = payload["timeline"]
        if not isinstance(timeline_payload, list):
            raise TypeError("timeline must be a list")

        return cls(
            roster=roster,
            builds=builds,
            combat_settings=_combat_settings_from_dict(combat_payload),
            main_actor=_require_string(payload["main_actor"], "main_actor"),
            baseline_rotation=(
                CROWN_CROWN_MAST.name
                if schema_version == 1
                else _require_string(
                    payload["baseline_rotation"],
                    "baseline_rotation",
                )
            ),
            timeline=tuple(
                _cycle_from_dict(
                    _require_mapping(cycle, f"timeline[{index}]"),
                    f"timeline[{index}]",
                )
                for index, cycle in enumerate(timeline_payload)
            ),
            thresholds=OutcomeThresholds(**thresholds_payload),
            expected_engine_rule_revision=_require_string(
                revisions["engine_rule"],
                "expected_revisions.engine_rule",
            ),
            expected_skill_hook_revision=_require_string(
                revisions["skill_hooks"],
                "expected_revisions.skill_hooks",
            ),
            expected_catalog_source_revision=_require_string(
                revisions["catalog_source"],
                "expected_revisions.catalog_source",
            ),
        )

    @classmethod
    def from_json(cls, payload: str) -> ResearchScenario:
        parsed = json.loads(payload)
        return cls.from_dict(_require_mapping(parsed, "scenario"))


@dataclass(frozen=True)
class DamagePairReport:
    conventional: float
    funnel: float
    delta: float
    relative_change: float | None

    @classmethod
    def from_comparison(cls, comparison: DamageComparison) -> DamagePairReport:
        return cls(
            conventional=comparison.conventional,
            funnel=comparison.funnel,
            delta=comparison.delta,
            relative_change=comparison.relative_change,
        )

    def to_dict(self) -> dict[str, float | None]:
        return {
            "conventional": self.conventional,
            "funnel": self.funnel,
            "delta": self.delta,
            "relative_change": self.relative_change,
        }


@dataclass(frozen=True)
class FirstBurstEntryDamageReport:
    crown_entry: float
    mast_entry: float
    delta_mast_minus_crown: float
    relative_change: float | None

    @classmethod
    def from_totals(
        cls,
        crown_entry: float,
        mast_entry: float,
    ) -> FirstBurstEntryDamageReport:
        return cls(
            crown_entry=crown_entry,
            mast_entry=mast_entry,
            delta_mast_minus_crown=mast_entry - crown_entry,
            relative_change=(
                None
                if crown_entry == 0
                else mast_entry / crown_entry - 1
            ),
        )

    def to_dict(self) -> dict[str, float | None]:
        return {
            "crown_entry": self.crown_entry,
            "mast_entry": self.mast_entry,
            "delta_mast_minus_crown": self.delta_mast_minus_crown,
            "relative_change": self.relative_change,
        }


@dataclass(frozen=True)
class FirstBurstEntryReport:
    cycle: int
    window_start: float
    window_end: float
    team: FirstBurstEntryDamageReport
    by_character: Mapping[str, FirstBurstEntryDamageReport]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "by_character",
            MappingProxyType(dict(self.by_character)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle": self.cycle,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "window_semantics": (
                "b1_activation_inclusive_to_entry_buff_state_convergence_exclusive"
            ),
            "team": self.team.to_dict(),
            "by_character": {
                actor: damage.to_dict()
                for actor, damage in self.by_character.items()
            },
        }


@dataclass(frozen=True)
class EntryVariantAnalysis:
    crown_entry: RotationComparison
    mast_entry: RotationComparison
    first_burst: FirstBurstEntryReport


@dataclass(frozen=True)
class SliceReport:
    team: DamagePairReport
    main_conventional: float
    main_funnel: float
    others_conventional: float
    others_funnel: float
    conventional_main_share: float | None
    funnel_main_share: float | None
    g: float | None
    l: float | None
    lambda_star: float | None
    break_even_main_share_c: float | None
    local_slope: float | None
    comparison_case: str
    observed_winner: str
    outcome_band: OutcomeBand

    @classmethod
    def from_comparison(
        cls,
        comparison: DamageSliceComparison,
        thresholds: OutcomeThresholds,
    ) -> SliceReport:
        team = DamagePairReport(
            conventional=comparison.team_c,
            funnel=comparison.team_f,
            delta=comparison.delta_total,
            relative_change=comparison.team_relative_change,
        )
        return cls(
            team=team,
            main_conventional=comparison.r_c,
            main_funnel=comparison.r_f,
            others_conventional=comparison.o_c,
            others_funnel=comparison.o_f,
            conventional_main_share=comparison.conventional_main_share,
            funnel_main_share=comparison.funnel_main_share,
            g=comparison.g,
            l=comparison.l,
            lambda_star=comparison.lambda_star,
            break_even_main_share_c=comparison.break_even_main_share_c,
            local_slope=comparison.local_slope,
            comparison_case=comparison.comparison_case.value,
            observed_winner=comparison.observed_winner.value,
            outcome_band=thresholds.classify(comparison.team_relative_change),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "team": self.team.to_dict(),
            "main_conventional": self.main_conventional,
            "main_funnel": self.main_funnel,
            "others_conventional": self.others_conventional,
            "others_funnel": self.others_funnel,
            "conventional_main_share": self.conventional_main_share,
            "funnel_main_share": self.funnel_main_share,
            "g": self.g,
            "l": self.l,
            "lambda_star": self.lambda_star,
            "break_even_main_share_c": self.break_even_main_share_c,
            "local_slope": self.local_slope,
            "comparison_case": self.comparison_case,
            "observed_winner": self.observed_winner,
            "outcome_band": self.outcome_band.value,
        }


@dataclass(frozen=True)
class CharacterReport:
    actor: str
    damage: DamagePairReport
    conventional_share: float | None
    funnel_share: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor": self.actor,
            "damage": self.damage.to_dict(),
            "conventional_share": self.conventional_share,
            "funnel_share": self.funnel_share,
        }


@dataclass(frozen=True)
class ComparisonReport:
    scenario: ResearchScenario
    mechanics_signature: MechanicsSignature
    overall: SliceReport
    by_character: Mapping[str, CharacterReport]
    macro_cycles: Mapping[int, SliceReport]
    burst_cycles: Mapping[int, SliceReport]
    by_category: Mapping[str, DamagePairReport]
    by_source: tuple[tuple[str, str, DamagePairReport], ...]
    secondary_b3_mast3_burst_omission_cycles: tuple[int, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "by_character",
            MappingProxyType(dict(self.by_character)),
        )
        object.__setattr__(self, "macro_cycles", MappingProxyType(dict(self.macro_cycles)))
        object.__setattr__(self, "burst_cycles", MappingProxyType(dict(self.burst_cycles)))
        object.__setattr__(self, "by_category", MappingProxyType(dict(self.by_category)))

    @classmethod
    def from_comparison(
        cls,
        scenario: ResearchScenario,
        comparison: RotationComparison,
    ) -> ComparisonReport:
        _validate_runtime_revisions(
            scenario,
            comparison.conventional_result.mechanics_signature,
            comparison.conventional_result.catalog.scope.source_revision,
        )
        if comparison.main_actor != scenario.main_actor:
            raise ValueError("comparison main actor does not match scenario")
        if comparison.conventional_result.policy_name != scenario.baseline_rotation:
            raise ValueError("comparison baseline rotation does not match scenario")
        if comparison.conventional_result.roster != scenario.roster:
            raise ValueError("comparison roster does not match scenario")
        comparison_builds = {
            actor: comparison.conventional_result.builds.get(
                actor,
                standard_build_for_actor(actor),
            )
            for actor in scenario.roster.members
        }
        if comparison_builds != dict(scenario.builds):
            raise ValueError("comparison builds do not match scenario")
        if comparison.conventional_result.combat_settings != scenario.combat_settings:
            raise ValueError("comparison combat settings do not match scenario")
        if comparison.conventional_result.timeline != scenario.timeline:
            raise ValueError("comparison timeline does not match scenario")

        overall = SliceReport.from_comparison(
            comparison.overall,
            scenario.thresholds,
        )
        team_c = comparison.overall.team_c
        team_f = comparison.overall.team_f
        by_character = {
            actor: CharacterReport(
                actor=actor,
                damage=DamagePairReport.from_comparison(damage),
                conventional_share=(
                    None if team_c == 0 else damage.conventional / team_c
                ),
                funnel_share=None if team_f == 0 else damage.funnel / team_f,
            )
            for actor, damage in comparison.by_character.items()
        }
        return cls(
            scenario=scenario,
            mechanics_signature=comparison.conventional_result.mechanics_signature,
            overall=overall,
            by_character=by_character,
            macro_cycles={
                cycle: SliceReport.from_comparison(value, scenario.thresholds)
                for cycle, value in comparison.macro_cycles.items()
            },
            burst_cycles={
                cycle: SliceReport.from_comparison(value, scenario.thresholds)
                for cycle, value in comparison.burst_cycles.items()
            },
            by_category={
                category.value: DamagePairReport.from_comparison(value)
                for category, value in comparison.by_category.items()
            },
            by_source=tuple(
                (
                    actor,
                    source,
                    DamagePairReport.from_comparison(value),
                )
                for (actor, source), value in sorted(comparison.by_source.items())
            ),
            secondary_b3_mast3_burst_omission_cycles=(
                comparison.secondary_b3_mast3_burst_omission_cycles
            ),
        )

    def assert_compatible_with(self, other: ComparisonReport) -> None:
        if self.mechanics_signature != other.mechanics_signature:
            raise ValueError("comparison reports use different mechanics signatures")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": COMPARISON_REPORT_SCHEMA_VERSION,
            "break_even_methodology": {
                key: list(value) if isinstance(value, tuple) else value
                for key, value in BREAK_EVEN_METHODOLOGY.items()
            },
            "scenario": self.scenario.to_dict(),
            "mechanics_signature": _mechanics_signature_to_dict(
                self.mechanics_signature
            ),
            "overall": self.overall.to_dict(),
            "by_character": {
                actor: report.to_dict()
                for actor, report in self.by_character.items()
            },
            "macro_cycles": {
                str(cycle): report.to_dict()
                for cycle, report in self.macro_cycles.items()
            },
            "burst_cycles": {
                str(cycle): report.to_dict()
                for cycle, report in self.burst_cycles.items()
            },
            "by_category": {
                category: report.to_dict()
                for category, report in self.by_category.items()
            },
            "by_source": [
                {
                    "actor": actor,
                    "source": source,
                    "damage": damage.to_dict(),
                }
                for actor, source, damage in self.by_source
            ],
            "secondary_b3_mast3_burst_omission_cycles": list(
                self.secondary_b3_mast3_burst_omission_cycles
            ),
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )


def run_research_scenario(
    scenario: ResearchScenario,
    *,
    catalog: CharacterCatalog = STANDARD_CHARACTER_CATALOG,
    skill_hooks: SkillHookRegistry = STANDARD_SKILL_HOOKS,
) -> ComparisonReport:
    comparison = analyze_research_scenario(
        scenario,
        catalog=catalog,
        skill_hooks=skill_hooks,
    )
    return ComparisonReport.from_comparison(scenario, comparison)


def analyze_research_scenario(
    scenario: ResearchScenario,
    *,
    catalog: CharacterCatalog = STANDARD_CHARACTER_CATALOG,
    skill_hooks: SkillHookRegistry = STANDARD_SKILL_HOOKS,
) -> RotationComparison:
    signature = skill_hooks.mechanics_signature
    _validate_runtime_revisions(
        scenario,
        signature,
        catalog.scope.source_revision,
    )
    for actor in scenario.roster.members:
        catalog.require(actor)

    return analyze_rotations(
        roster=scenario.roster,
        timeline=scenario.timeline,
        catalog=catalog,
        builds=scenario.builds,
        combat_settings=scenario.combat_settings,
        skill_hooks=skill_hooks,
        main_actor=scenario.main_actor,
        conventional_policy=resolve_baseline_rotation(
            scenario.baseline_rotation
        ),
    )


def analyze_first_burst_entry_choice(
    scenario: ResearchScenario,
    *,
    selected_comparison: RotationComparison | None = None,
    catalog: CharacterCatalog = STANDARD_CHARACTER_CATALOG,
    skill_hooks: SkillHookRegistry = STANDARD_SKILL_HOOKS,
) -> FirstBurstEntryReport:
    comparison = selected_comparison or analyze_research_scenario(
        scenario,
        catalog=catalog,
        skill_hooks=skill_hooks,
    )
    ComparisonReport.from_comparison(scenario, comparison)
    selected = comparison.conventional_result
    common = {
        "roster": scenario.roster,
        "timeline": scenario.timeline,
        "catalog": catalog,
        "builds": scenario.builds,
        "combat_settings": scenario.combat_settings,
        "skill_hooks": skill_hooks,
    }
    if selected.policy_name == CROWN_CROWN_MAST.name:
        crown_result = selected
        mast_result = simulate_rotation(OPENING_MAST_CROWN_MAST, **common)
    elif selected.policy_name == OPENING_MAST_CROWN_MAST.name:
        crown_result = simulate_rotation(CROWN_CROWN_MAST, **common)
        mast_result = selected
    else:
        raise ValueError(
            "first burst entry choice requires a registered baseline rotation"
        )
    return _first_burst_entry_report(
        scenario,
        crown_result=crown_result,
        mast_result=mast_result,
    )


def analyze_entry_variants(
    scenario: ResearchScenario,
    *,
    catalog: CharacterCatalog = STANDARD_CHARACTER_CATALOG,
    skill_hooks: SkillHookRegistry = STANDARD_SKILL_HOOKS,
) -> EntryVariantAnalysis:
    """Run the four single-calculator rotations without changing batch analysis."""
    signature = skill_hooks.mechanics_signature
    _validate_runtime_revisions(
        scenario,
        signature,
        catalog.scope.source_revision,
    )
    for actor in scenario.roster.members:
        catalog.require(actor)

    common = {
        "roster": scenario.roster,
        "timeline": scenario.timeline,
        "catalog": catalog,
        "builds": scenario.builds,
        "combat_settings": scenario.combat_settings,
        "skill_hooks": skill_hooks,
    }
    crown_conventional = simulate_rotation(CROWN_CROWN_MAST, **common)
    mast_conventional = simulate_rotation(OPENING_MAST_CROWN_MAST, **common)
    crown_funnel = simulate_rotation(SUSTAINED_FUNNEL, **common)
    mast_funnel = simulate_rotation(OPENING_MAST_SUSTAINED_FUNNEL, **common)

    return EntryVariantAnalysis(
        crown_entry=compare_rotation_results(
            crown_conventional,
            crown_funnel,
            main_actor=scenario.main_actor,
        ),
        mast_entry=compare_rotation_results(
            mast_conventional,
            mast_funnel,
            main_actor=scenario.main_actor,
        ),
        first_burst=_first_burst_entry_report(
            scenario,
            crown_result=crown_conventional,
            mast_result=mast_conventional,
        ),
    )


def _first_burst_entry_report(
    scenario: ResearchScenario,
    *,
    crown_result: SimulationResult,
    mast_result: SimulationResult,
) -> FirstBurstEntryReport:
    first = scenario.timeline[0]
    start = first.b1_time
    end = _entry_buff_state_convergence_time(
        scenario,
        crown_result=crown_result,
        mast_result=mast_result,
    )

    def window_total(result: SimulationResult, actor: str | None = None) -> float:
        return sum(
            event.damage
            for event in result.damage_events
            if start <= event.time < end
            and (actor is None or event.actor == actor)
        )

    return FirstBurstEntryReport(
        cycle=first.cycle,
        window_start=start,
        window_end=end,
        team=FirstBurstEntryDamageReport.from_totals(
            window_total(crown_result),
            window_total(mast_result),
        ),
        by_character={
            actor: FirstBurstEntryDamageReport.from_totals(
                window_total(crown_result, actor),
                window_total(mast_result, actor),
            )
            for actor in scenario.roster.members
        },
    )


def _entry_buff_state_convergence_time(
    scenario: ResearchScenario,
    *,
    crown_result: SimulationResult,
    mast_result: SimulationResult,
) -> float:
    first = scenario.timeline[0]
    duration = scenario.combat_settings.duration_sec
    boundaries = {first.full_burst_end, duration}
    for result in (crown_result, mast_result):
        for window in result.buffs.windows:
            if first.full_burst_end <= window.start <= duration:
                boundaries.add(window.start)
            if isfinite(window.end) and first.full_burst_end <= window.end <= duration:
                boundaries.add(window.end)

    def active_signature(result: SimulationResult, time: float) -> tuple[Any, ...]:
        return tuple(
            sorted(
                (
                    window.source,
                    window.skill,
                    window.stat,
                    window.value,
                    window.target,
                    window.caster or "",
                    window.snapshot,
                )
                for window in result.buffs.windows
                if window.active_at(time)
            )
        )

    for boundary in sorted(boundaries):
        if active_signature(crown_result, boundary) == active_signature(
            mast_result,
            boundary,
        ):
            return boundary
    return duration


def _validate_runtime_revisions(
    scenario: ResearchScenario,
    signature: MechanicsSignature,
    catalog_source_revision: str,
) -> None:
    if signature.engine_rule_revision != scenario.expected_engine_rule_revision:
        raise ValueError(
            "scenario engine revision does not match runtime: "
            f"{scenario.expected_engine_rule_revision} != "
            f"{signature.engine_rule_revision}"
        )
    if signature.skill_hook_revision != scenario.expected_skill_hook_revision:
        raise ValueError(
            "scenario skill hook revision does not match runtime: "
            f"{scenario.expected_skill_hook_revision} != "
            f"{signature.skill_hook_revision}"
        )
    if catalog_source_revision != scenario.expected_catalog_source_revision:
        raise ValueError(
            "scenario catalog revision does not match runtime: "
            f"{scenario.expected_catalog_source_revision} != "
            f"{catalog_source_revision}"
        )


def _validate_timeline(timeline: tuple[BurstCycle, ...], duration_sec: float) -> None:
    if not timeline:
        raise ValueError("research timeline must not be empty")
    cycles = [cycle.cycle for cycle in timeline]
    if any(
        isinstance(cycle, bool) or not isinstance(cycle, int) or cycle <= 0
        for cycle in cycles
    ):
        raise ValueError("research timeline cycle ids must be positive integers")
    if cycles != sorted(cycles) or len(set(cycles)) != len(cycles):
        raise ValueError("research timeline cycles must be unique and increasing")
    for cycle in timeline:
        times = (
            cycle.b1_time,
            cycle.b2_time,
            cycle.b3_time,
            cycle.full_burst_start,
            cycle.full_burst_end,
        )
        if any(not isfinite(value) or value < 0 for value in times):
            raise ValueError(f"cycle {cycle.cycle} contains invalid time")
        if not (
            cycle.b1_time
            <= cycle.b2_time
            <= cycle.b3_time
            <= cycle.full_burst_start
            < cycle.full_burst_end
        ):
            raise ValueError(f"cycle {cycle.cycle} times are not ordered")
        if cycle.full_burst_end > duration_sec:
            raise ValueError(f"cycle {cycle.cycle} exceeds combat duration")
        if cycle.b3_slot not in {"main_b3", "secondary_b3"}:
            raise ValueError(f"cycle {cycle.cycle} has unsupported b3_slot")


def _build_to_dict(build: BuildProfile) -> dict[str, Any]:
    states = {piece.slot.value: piece.state.value for piece in build.equipment.pieces}
    return {
        "equipment": states,
        "collection": build.collection.stage,
        "overload": {
            "atk_lines": build.overload.atk_lines,
            "element_lines": build.overload.element_lines,
            "ammo_lines": build.overload.ammo_lines,
        },
    }


def _build_from_dict(payload: Mapping[str, Any], path: str) -> BuildProfile:
    _require_exact_keys(payload, {"equipment", "collection", "overload"}, path)
    equipment = _require_mapping(payload["equipment"], f"{path}.equipment")
    expected_slots = {slot.value for slot in GEAR_SLOTS}
    _require_exact_keys(equipment, expected_slots, f"{path}.equipment")
    overload = _require_mapping(payload["overload"], f"{path}.overload")
    _require_exact_keys(
        overload,
        {"atk_lines", "element_lines", "ammo_lines"},
        f"{path}.overload",
    )
    try:
        states = [GearState(equipment[slot.value]) for slot in GEAR_SLOTS]
    except ValueError as exc:
        raise ValueError(f"{path}.equipment contains unsupported gear state") from exc
    return BuildProfile(
        equipment=EquipmentLoadout.from_states(*states),
        overload=OverloadProfile(**overload),
        collection=CollectionProfile(
            _require_string(payload["collection"], f"{path}.collection")
        ),
    )


def _combat_settings_to_dict(settings: CombatSettings) -> dict[str, Any]:
    return {
        "boss_def": settings.boss_def,
        "core_hit_rate_pct": settings.core_hit_rate_pct,
        "range_bonus_pct": settings.range_bonus_pct,
        "element_multiplier": settings.element_multiplier,
        "element_multiplier_by_actor": dict(settings.element_multiplier_by_actor),
        "boss_element": settings.boss_element,
        "full_burst_bonus_pct": settings.full_burst_bonus_pct,
        "boss_damage_taken_pct": settings.boss_damage_taken_pct,
        "startup_delay_frames": settings.startup_delay_frames,
        "duration_sec": settings.duration_sec,
    }


def _combat_settings_from_dict(payload: Mapping[str, Any]) -> CombatSettings:
    keys = {
        "boss_def",
        "core_hit_rate_pct",
        "range_bonus_pct",
        "element_multiplier",
        "element_multiplier_by_actor",
        "boss_element",
        "full_burst_bonus_pct",
        "boss_damage_taken_pct",
        "startup_delay_frames",
        "duration_sec",
    }
    _require_exact_keys(payload, keys, "combat_settings")
    values = dict(payload)
    values["element_multiplier_by_actor"] = _require_mapping(
        values["element_multiplier_by_actor"],
        "combat_settings.element_multiplier_by_actor",
    )
    return CombatSettings(**values)


def _cycle_to_dict(cycle: BurstCycle) -> dict[str, Any]:
    return {
        "cycle": cycle.cycle,
        "b1_time": cycle.b1_time,
        "b2_time": cycle.b2_time,
        "b3_time": cycle.b3_time,
        "full_burst_start": cycle.full_burst_start,
        "full_burst_end": cycle.full_burst_end,
        "b3_slot": cycle.b3_slot,
    }


def _cycle_from_dict(payload: Mapping[str, Any], path: str) -> BurstCycle:
    keys = {
        "cycle",
        "b1_time",
        "b2_time",
        "b3_time",
        "full_burst_start",
        "full_burst_end",
        "b3_slot",
    }
    _require_exact_keys(payload, keys, path)
    return BurstCycle(**payload)


def _mechanics_signature_to_dict(signature: MechanicsSignature) -> dict[str, Any]:
    return {
        "engine_rule_revision": signature.engine_rule_revision,
        "skill_hook_revision": signature.skill_hook_revision,
        "skill_hook_factories": [
            {"actor": actor, "factory": factory}
            for actor, factory in signature.skill_hook_factories
        ],
    }


def _require_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{path} must be a non-empty string")
    return value


def _require_exact_keys(
    payload: Mapping[str, Any],
    expected: set[str],
    path: str,
) -> None:
    missing = expected - payload.keys()
    extra = payload.keys() - expected
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing={sorted(missing)}")
        if extra:
            details.append(f"extra={sorted(extra)}")
        raise ValueError(f"{path} has invalid fields: " + ", ".join(details))
