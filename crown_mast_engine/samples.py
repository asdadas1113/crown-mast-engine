from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .research import ComparisonReport, ResearchScenario, run_research_scenario


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


def run_sample_batch(cases: Iterable[SampleCase]) -> SampleBatchResult:
    prepared = tuple(cases)
    if not prepared:
        raise ValueError("sample batch must contain at least one case")
    case_ids = tuple(case.case_id for case in prepared)
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("sample case ids must be unique")

    results: list[SampleResult] = []
    for case in prepared:
        report = run_research_scenario(case.scenario)
        if results:
            results[0].report.assert_compatible_with(report)
            if (
                results[0].report.scenario.baseline_rotation
                != report.scenario.baseline_rotation
            ):
                raise ValueError(
                    "sample batch cannot mix baseline rotations"
                )
        results.append(
            SampleResult(
                case_id=case.case_id,
                labels=case.labels,
                report=report,
            )
        )
    return SampleBatchResult(tuple(results))
