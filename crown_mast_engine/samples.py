from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .mechanics import MechanicsSignature
from .research import (
    CharacterReport,
    ComparisonReport,
    DamagePairReport,
    OutcomeBand,
    ResearchScenario,
    SliceReport,
    run_research_scenario,
)


SAMPLE_BATCH_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class SampleCase:
    case_id: str
    scenario: ResearchScenario
    labels: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ValueError("sample case id must be a non-empty string")
        labels = dict(self.labels)
        if any(
            not isinstance(key, str)
            or not key
            or not isinstance(value, str)
            or not value
            for key, value in labels.items()
        ):
            raise TypeError("sample labels must contain non-empty string keys and values")
        object.__setattr__(self, "labels", MappingProxyType(labels))


@dataclass(frozen=True)
class SampleResult:
    case_id: str
    labels: Mapping[str, str]
    report: ComparisonReport

    def __post_init__(self) -> None:
        object.__setattr__(self, "labels", MappingProxyType(dict(self.labels)))

    def summary_row(self) -> dict[str, Any]:
        scenario = self.report.scenario
        overall = self.report.overall
        break_even = overall.break_even_main_share_c
        main_share = overall.conventional_main_share
        return {
            "case_id": self.case_id,
            "labels": dict(self.labels),
            "b1": scenario.roster.b1,
            "crown": scenario.roster.crown,
            "mast": scenario.roster.mast,
            "main_actor": scenario.main_actor,
            "baseline_rotation": scenario.baseline_rotation,
            "secondary_b3": scenario.roster.secondary_b3,
            "boss_element": scenario.combat_settings.boss_element,
            "boss_def": scenario.combat_settings.boss_def,
            "duration_sec": scenario.combat_settings.duration_sec,
            "conventional_damage": overall.team.conventional,
            "funnel_damage": overall.team.funnel,
            "relative_change": overall.team.relative_change,
            "conventional_main_share": main_share,
            "funnel_main_share": overall.funnel_main_share,
            "g": overall.g,
            "l": overall.l,
            "lambda_star": overall.lambda_star,
            "break_even_main_share_c": break_even,
            "margin": (
                None
                if main_share is None or break_even is None
                else main_share - break_even
            ),
            "local_slope": overall.local_slope,
            "comparison_case": overall.comparison_case,
            "observed_winner": overall.observed_winner,
            "outcome_band": overall.outcome_band.value,
            "character_shares": {
                actor: {
                    "conventional": character.conventional_share,
                    "funnel": character.funnel_share,
                }
                for actor, character in self.report.by_character.items()
            },
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "labels": dict(self.labels),
            "summary": self.summary_row(),
            "report": self.report.to_dict(),
        }


@dataclass(frozen=True)
class SampleBatchResult:
    results: tuple[SampleResult, ...]

    def __post_init__(self) -> None:
        if not self.results:
            raise ValueError("sample batch must contain at least one result")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SAMPLE_BATCH_SCHEMA_VERSION,
            "results": [result.to_dict() for result in self.results],
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )


def run_sample_batch(
    cases: Iterable[SampleCase],
    *,
    workers: int | None = None,
) -> SampleBatchResult:
    prepared = tuple(cases)
    if not prepared:
        raise ValueError("sample batch must contain at least one case")
    case_ids = tuple(case.case_id for case in prepared)
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("sample case ids must be unique")
    if workers is not None:
        if isinstance(workers, bool) or not isinstance(workers, int):
            raise TypeError("sample batch workers must be an integer or None")
        if workers < 1:
            raise ValueError("sample batch workers must be at least 1")

    requested_workers = workers if workers is not None else (os.cpu_count() or 1)
    effective_workers = min(requested_workers, len(prepared))

    if effective_workers == 1:
        reports = tuple(
            run_research_scenario(case.scenario)
            for case in prepared
        )
    else:
        scenario_payloads = tuple(
            case.scenario.to_dict()
            for case in prepared
        )
        with ProcessPoolExecutor(
            max_workers=effective_workers,
            mp_context=get_context("spawn"),
        ) as executor:
            report_payloads = tuple(
                executor.map(
                    _run_research_scenario_payload,
                    scenario_payloads,
                )
            )
        reports = tuple(
            _comparison_report_from_payload(payload)
            for payload in report_payloads
        )

    results = tuple(
        SampleResult(
            case_id=case.case_id,
            labels=case.labels,
            report=report,
        )
        for case, report in zip(prepared, reports, strict=True)
    )
    _validate_batch_compatibility(results)
    return SampleBatchResult(results)


def _run_research_scenario_payload(
    scenario_payload: Mapping[str, Any],
) -> dict[str, Any]:
    scenario = ResearchScenario.from_dict(scenario_payload)
    return run_research_scenario(scenario).to_dict()


def _validate_batch_compatibility(results: tuple[SampleResult, ...]) -> None:
    reference = results[0].report
    for result in results[1:]:
        reference.assert_compatible_with(result.report)
        if reference.scenario.baseline_rotation != result.report.scenario.baseline_rotation:
            raise ValueError("sample batch cannot mix baseline rotations")


def _comparison_report_from_payload(payload: Mapping[str, Any]) -> ComparisonReport:
    signature_payload = payload["mechanics_signature"]
    return ComparisonReport(
        scenario=ResearchScenario.from_dict(payload["scenario"]),
        mechanics_signature=MechanicsSignature(
            engine_rule_revision=signature_payload["engine_rule_revision"],
            skill_hook_revision=signature_payload["skill_hook_revision"],
            skill_hook_factories=tuple(
                (item["actor"], item["factory"])
                for item in signature_payload["skill_hook_factories"]
            ),
        ),
        overall=_slice_report_from_payload(payload["overall"]),
        by_character={
            actor: _character_report_from_payload(report)
            for actor, report in payload["by_character"].items()
        },
        macro_cycles={
            int(cycle): _slice_report_from_payload(report)
            for cycle, report in payload["macro_cycles"].items()
        },
        burst_cycles={
            int(cycle): _slice_report_from_payload(report)
            for cycle, report in payload["burst_cycles"].items()
        },
        by_category={
            category: _damage_pair_from_payload(report)
            for category, report in payload["by_category"].items()
        },
        by_source=tuple(
            (
                item["actor"],
                item["source"],
                _damage_pair_from_payload(item["damage"]),
            )
            for item in payload["by_source"]
        ),
        secondary_b3_mast3_burst_omission_cycles=tuple(
            payload["secondary_b3_mast3_burst_omission_cycles"]
        ),
    )


def _character_report_from_payload(payload: Mapping[str, Any]) -> CharacterReport:
    return CharacterReport(
        actor=payload["actor"],
        damage=_damage_pair_from_payload(payload["damage"]),
        conventional_share=payload["conventional_share"],
        funnel_share=payload["funnel_share"],
    )


def _slice_report_from_payload(payload: Mapping[str, Any]) -> SliceReport:
    return SliceReport(
        team=_damage_pair_from_payload(payload["team"]),
        main_conventional=payload["main_conventional"],
        main_funnel=payload["main_funnel"],
        others_conventional=payload["others_conventional"],
        others_funnel=payload["others_funnel"],
        conventional_main_share=payload["conventional_main_share"],
        funnel_main_share=payload["funnel_main_share"],
        g=payload["g"],
        l=payload["l"],
        lambda_star=payload["lambda_star"],
        break_even_main_share_c=payload["break_even_main_share_c"],
        local_slope=payload["local_slope"],
        comparison_case=payload["comparison_case"],
        observed_winner=payload["observed_winner"],
        outcome_band=OutcomeBand(payload["outcome_band"]),
    )


def _damage_pair_from_payload(payload: Mapping[str, Any]) -> DamagePairReport:
    return DamagePairReport(
        conventional=payload["conventional"],
        funnel=payload["funnel"],
        delta=payload["delta"],
        relative_change=payload["relative_change"],
    )
