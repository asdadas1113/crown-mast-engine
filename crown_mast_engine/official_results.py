from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from string import hexdigits
from typing import Any, Iterable, Literal, Mapping

from .character_mechanics import STANDARD_SKILL_HOOKS
from .characters import STANDARD_CHARACTER_CATALOG
from .checkpoints_v3 import CHECKPOINT_V3_ID
from .mechanics import ENGINE_RULE_REVISION
from .official_study import (
    OFFICIAL_SCENARIOS_PER_ROSTER,
    OFFICIAL_STUDY_ID,
    iter_official_rosters,
    official_roster_id,
    official_study_definition,
)
from .research import (
    COMPARISON_REPORT_SCHEMA_VERSION,
    RESEARCH_SCENARIO_SCHEMA_VERSION,
)
from .rotations import OPENING_MAST_CROWN_MAST
from .samples import SampleBatchResult, SampleCase, SampleResult
from .timeline import (
    RAID14_CYCLE_COUNT,
    RAID14_FIRST_B1_TIME,
    RAID14_FULL_BURST_DURATION_SEC,
    RAID14_INTERVAL_SEC,
    RAID14_STAGE_INPUT_GAP_SEC,
    RAID14_TIMELINE,
)
from .wave_a_study import (
    WAVE_A_CORE_HIT_RATE_PCT,
    WAVE_A_DEFENSE_ANCHORS,
    WAVE_A_GROWTH_PROFILES,
    WAVE_A_MAIN_ADVANTAGE_LEVELS,
)


OFFICIAL_RAW_ROW_SCHEMA_VERSION = 1
OFFICIAL_SCENARIO_ROW_SCHEMA_VERSION = 1
OFFICIAL_MANIFEST_SCHEMA_VERSION = 1
RunKind = Literal["preflight", "official"]


def _required_label(result: SampleResult, key: str) -> str:
    try:
        value = result.labels[key]
    except KeyError as exc:
        raise ValueError(f"official result is missing label: {key}") from exc
    if not value:
        raise ValueError(f"official result label is empty: {key}")
    return value


def _validate_result_identity(result: SampleResult) -> str:
    study_id = _required_label(result, "study_id")
    if study_id != OFFICIAL_STUDY_ID:
        raise ValueError(f"result is outside the official study: {study_id}")

    scenario = result.report.scenario
    expected_roster_id = official_roster_id(scenario.roster)
    roster_id = _required_label(result, "roster_id")
    if roster_id != expected_roster_id:
        raise ValueError("result roster_id does not match the scenario roster")

    expected_labels = {
        "b1_candidate": scenario.roster.b1,
        "main_b3_candidate": scenario.roster.main_b3,
        "secondary_anchor": scenario.roster.secondary_b3,
    }
    for key, expected in expected_labels.items():
        if _required_label(result, key) != expected:
            raise ValueError(f"result label does not match scenario: {key}")
    return roster_id


def compact_official_row(
    result: SampleResult,
    *,
    run_id: str,
) -> dict[str, Any]:
    """Return the canonical compact scenario row for official-study storage."""
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("run_id must be a non-empty string")

    roster_id = _validate_result_identity(result)
    scenario = result.report.scenario
    overall = result.report.overall
    main_actor = scenario.main_actor
    secondary_actor = scenario.roster.secondary_b3

    try:
        main = result.report.by_character[main_actor]
        secondary = result.report.by_character[secondary_actor]
    except KeyError as exc:
        raise ValueError("official result is missing Main/Secondary character report") from exc

    characters = {
        actor: {
            "conventional_damage": report.damage.conventional,
            "funnel_damage": report.damage.funnel,
            "delta": report.damage.delta,
            "relative_change": report.damage.relative_change,
            "conventional_share": report.conventional_share,
            "funnel_share": report.funnel_share,
        }
        for actor, report in sorted(result.report.by_character.items())
    }

    return {
        "schema_version": OFFICIAL_RAW_ROW_SCHEMA_VERSION,
        "case_id": result.case_id,
        "study_id": OFFICIAL_STUDY_ID,
        "run_id": run_id,
        "roster_id": roster_id,
        "roster": {
            "b1": scenario.roster.b1,
            "main_b3": scenario.roster.main_b3,
            "secondary_b3": scenario.roster.secondary_b3,
        },
        "growth": {
            "b1": _required_label(result, "b1_profile"),
            "main_b3": _required_label(result, "main_profile"),
            "secondary_b3": _required_label(result, "secondary_profile"),
        },
        "environment": {
            "defense_condition": _required_label(result, "def_condition"),
            "boss_def": scenario.combat_settings.boss_def,
            "core_condition": _required_label(result, "core_condition"),
            "core_hit_rate_pct": scenario.combat_settings.core_hit_rate_pct,
            "main_advantage": _required_label(result, "main_advantage"),
            "boss_element": scenario.combat_settings.boss_element or "neutral",
            "hit_model": _required_label(result, "hit_model"),
        },
        "revisions": {
            "engine_rule": result.report.mechanics_signature.engine_rule_revision,
            "skill_hooks": result.report.mechanics_signature.skill_hook_revision,
            "catalog_source": scenario.expected_catalog_source_revision,
        },
        "team": {
            "conventional_damage": overall.team.conventional,
            "funnel_damage": overall.team.funnel,
            "delta": overall.team.delta,
            "relative_change": overall.team.relative_change,
        },
        "outcome_band": overall.outcome_band.value,
        "main": {
            "actor": main_actor,
            "conventional_damage": main.damage.conventional,
            "funnel_damage": main.damage.funnel,
            "absolute_gain": main.damage.delta,
            "relative_change": main.damage.relative_change,
            "conventional_share": main.conventional_share,
            "funnel_share": main.funnel_share,
        },
        "secondary": {
            "actor": secondary_actor,
            "conventional_damage": secondary.damage.conventional,
            "funnel_damage": secondary.damage.funnel,
            "delta": secondary.damage.delta,
            "absolute_loss": secondary.damage.conventional - secondary.damage.funnel,
            "relative_change": secondary.damage.relative_change,
            "conventional_share": secondary.conventional_share,
            "funnel_share": secondary.funnel_share,
        },
        "opportunity": {
            "rest_of_team_conventional_damage": overall.others_conventional,
            "rest_of_team_funnel_damage": overall.others_funnel,
            "rest_of_team_absolute_loss": (
                overall.others_conventional - overall.others_funnel
            ),
            "g": overall.g,
            "l": overall.l,
            "lambda_star": overall.lambda_star,
            "break_even_main_share_c": overall.break_even_main_share_c,
            "local_slope": overall.local_slope,
            "comparison_case": overall.comparison_case,
            "observed_winner": overall.observed_winner,
        },
        "characters": characters,
    }


def _validate_official_batch(batch: SampleBatchResult) -> str:
    if len(batch.results) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise ValueError(
            "official roster raw writer requires exactly "
            f"{OFFICIAL_SCENARIOS_PER_ROSTER} results"
        )

    roster_ids = {_validate_result_identity(result) for result in batch.results}
    if len(roster_ids) != 1:
        raise ValueError("official roster raw writer requires exactly one roster")
    roster_id = next(iter(roster_ids))

    case_ids = tuple(result.case_id for result in batch.results)
    if len(set(case_ids)) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise ValueError(
            "official roster raw writer requires "
            f"{OFFICIAL_SCENARIOS_PER_ROSTER} unique case ids"
        )

    profile_ids = {profile.profile_id for profile in WAVE_A_GROWTH_PROFILES}
    coverage_keys = set()
    environment_counts: Counter[tuple[str, str, str]] = Counter()
    for result in batch.results:
        growth = (
            _required_label(result, "b1_profile"),
            _required_label(result, "main_profile"),
            _required_label(result, "secondary_profile"),
        )
        if any(profile not in profile_ids for profile in growth):
            raise ValueError("official roster raw writer received an unknown growth profile")
        environment = (
            _required_label(result, "def_condition"),
            _required_label(result, "core_condition"),
            _required_label(result, "main_advantage"),
        )
        if _required_label(result, "hit_model") != "ideal-hit":
            raise ValueError("official roster raw writer requires the ideal-hit model")
        environment_counts[environment] += 1
        coverage_keys.add((*growth, *environment))

    expected_environment_counts = Counter(
        {
            (defense, core, advantage): len(WAVE_A_GROWTH_PROFILES) ** 3
            for defense in WAVE_A_DEFENSE_ANCHORS
            for core in WAVE_A_CORE_HIT_RATE_PCT
            for advantage in WAVE_A_MAIN_ADVANTAGE_LEVELS
        }
    )
    if environment_counts != expected_environment_counts:
        raise ValueError("official roster raw writer requires the full 12-environment grid")
    if len(coverage_keys) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise ValueError("official roster raw writer requires the full growth/environment grid")
    return roster_id


def write_official_roster_jsonl(
    run_dir: str | Path,
    batch: SampleBatchResult,
    *,
    run_id: str,
) -> Path:
    """Write exactly one 324-scenario result shard to ``run_dir/raw``."""
    roster_id = _validate_official_batch(batch)
    rows = tuple(compact_official_row(result, run_id=run_id) for result in batch.results)

    raw_dir = Path(run_dir) / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{roster_id}.jsonl"
    payload = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
        for row in rows
    )
    _write_text_atomic(path, payload)
    return path


def _growth_grid_manifest() -> dict[str, Any]:
    return {
        "design": "full27-three-level",
        "source_profile_set": CHECKPOINT_V3_ID,
        "axes": {"b1": 3, "main_b3": 3, "secondary_b3": 3},
        "profiles": [
            {
                "id": profile.profile_id,
                "label": profile.label,
                "gear": profile.gear.value,
                "requested_collection": profile.collection_stage,
                "overload": {
                    "atk_lines": profile.overload.atk_lines,
                    "element_lines": profile.overload.element_lines,
                    "ammo_lines": profile.overload.ammo_lines,
                },
            }
            for profile in WAVE_A_GROWTH_PROFILES
        ],
        "favorite_item_policy": (
            "favorite-item actors force SR15 collection while preserving "
            "the requested gear and overload growth state"
        ),
    }


def _timeline_manifest() -> dict[str, Any]:
    return {
        "revision": "raid14-practical-baseline-2026-09-01",
        "fight_duration_sec": 180.0,
        "cycle_count": RAID14_CYCLE_COUNT,
        "interval_sec": RAID14_INTERVAL_SEC,
        "first_b1_time": RAID14_FIRST_B1_TIME,
        "stage_input_gap_sec": RAID14_STAGE_INPUT_GAP_SEC,
        "full_burst_duration_sec": RAID14_FULL_BURST_DURATION_SEC,
        "cycles": [
            {
                "cycle": cycle.cycle,
                "b1_time": cycle.b1_time,
                "b2_time": cycle.b2_time,
                "b3_time": cycle.b3_time,
                "full_burst_start": cycle.full_burst_start,
                "full_burst_end": cycle.full_burst_end,
                "b3_slot": cycle.b3_slot,
            }
            for cycle in RAID14_TIMELINE
        ],
    }


def build_official_manifest(
    *,
    run_id: str,
    branch: str,
    commit_sha: str,
    completed_shard_ids: Iterable[str] = (),
    run_kind: RunKind = "preflight",
    execution_approved: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("run_id must be a non-empty string")
    if not isinstance(branch, str) or not branch:
        raise ValueError("branch must be a non-empty string")
    if not isinstance(commit_sha, str) or not commit_sha:
        raise ValueError("commit_sha must be a non-empty string")
    if len(commit_sha) != 40 or any(
        character not in hexdigits for character in commit_sha
    ):
        raise ValueError("commit_sha must be a 40-character hexadecimal Git SHA")
    if run_kind not in ("preflight", "official"):
        raise ValueError(f"unsupported run kind: {run_kind}")
    if not isinstance(execution_approved, bool):
        raise TypeError("execution_approved must be a bool")
    if run_kind == "official" and not execution_approved:
        raise ValueError("official run preparation requires explicit execution approval")
    if branch != "research/14-burst-baseline":
        raise ValueError("official Study 1 must be prepared from research/14-burst-baseline")
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()
    if not isinstance(generated_at, str) or not generated_at:
        raise ValueError("generated_at must be a non-empty ISO-8601 string")

    definition = official_study_definition()
    valid_shards = {
        official_roster_id(roster)
        for roster in iter_official_rosters()
    }
    completed = tuple(dict.fromkeys(completed_shard_ids))
    if any(not isinstance(item, str) or not item for item in completed):
        raise ValueError("completed shard ids must be non-empty strings")
    unknown_shards = set(completed) - valid_shards
    if unknown_shards:
        raise ValueError(f"manifest contains unknown shard ids: {sorted(unknown_shards)}")

    signature = STANDARD_SKILL_HOOKS.mechanics_signature
    if signature.engine_rule_revision != ENGINE_RULE_REVISION:
        raise AssertionError("standard skill-hook signature does not match engine revision")

    return {
        "schema_version": OFFICIAL_MANIFEST_SCHEMA_VERSION,
        "study_id": OFFICIAL_STUDY_ID,
        "run_id": run_id,
        "run_kind": run_kind,
        "generated_at": generated_at,
        "status": (
            "prepared-execution-approved"
            if run_kind == "official"
            else "design-frozen-execution-unapproved"
        ),
        # A pre-run manifest is provenance, not a completed official result.
        "official_result": False,
        "branch": branch,
        "commit_sha": commit_sha,
        "git": {"branch": branch, "commit": commit_sha},
        "revisions": {
            "engine_rule": ENGINE_RULE_REVISION,
            "skill_hooks": signature.skill_hook_revision,
            "skill_hook_factories": [
                {"actor": actor, "factory": factory}
                for actor, factory in signature.skill_hook_factories
            ],
            "catalog_source": STANDARD_CHARACTER_CATALOG.scope.source_revision,
        },
        "mechanics": {
            "engine_rule_revision": ENGINE_RULE_REVISION,
            "skill_hook_revision": signature.skill_hook_revision,
            "skill_hook_factories": [
                {"actor": actor, "factory": factory}
                for actor, factory in signature.skill_hook_factories
            ],
        },
        "catalog": {
            "catalog_source_revision": STANDARD_CHARACTER_CATALOG.scope.source_revision,
            "catalog_sha256": _catalog_sha256(),
            "skill_overrides": [],
        },
        "study_definition": definition,
        "timeline": _timeline_manifest(),
        "baseline_rotation": OPENING_MAST_CROWN_MAST.name,
        "candidates": {
            "b1": definition["b1_candidates"],
            "main_b3": definition["main_b3_candidates"],
            "secondary_b3": definition["secondary_b3_anchors"],
        },
        "growth_grid": _growth_grid_manifest(),
        "environment_axes": definition["environment_axes"],
        "counts": {
            "raw_rosters": definition["raw_roster_count"],
            "invalid_duplicate_rosters": definition["invalid_duplicate_rosters"],
            "valid_rosters": definition["valid_roster_count"],
            "scenarios_per_roster": definition["scenarios_per_roster"],
            "official_scenarios": definition["scenario_count"],
            "completed_shards": len(completed),
            "completed_scenarios": len(completed) * definition["scenarios_per_roster"],
        },
        "sharding": {
            "policy": "one valid roster per shard, 324 scenarios per shard",
            "completed_shard_ids": list(completed),
        },
        "output_layout": {
            "scenarios": "scenarios/<roster_id>.jsonl",
            "raw": "raw/<roster_id>.jsonl",
            "aggregate": "aggregate/",
            "provenance": "provenance/",
        },
        "schemas": {
            "scenario": RESEARCH_SCENARIO_SCHEMA_VERSION,
            "raw_result": OFFICIAL_RAW_ROW_SCHEMA_VERSION,
            "comparison_report": COMPARISON_REPORT_SCHEMA_VERSION,
        },
        "output_shards": [],
    }


def _catalog_sha256() -> str:
    marker = "catalog-sha256:"
    source_revision = STANDARD_CHARACTER_CATALOG.scope.source_revision
    if marker not in source_revision:
        raise AssertionError("standard catalog revision is missing its SHA-256 digest")
    digest = source_revision.rsplit(marker, 1)[1]
    if len(digest) != 64 or any(character not in hexdigits for character in digest):
        raise AssertionError("standard catalog revision has an invalid SHA-256 digest")
    return digest.lower()


def compact_official_scenario_row(case: SampleCase) -> dict[str, Any]:
    """Return a self-contained, replayable Study 1 scenario input row."""
    study_id = case.labels.get("study_id")
    if study_id != OFFICIAL_STUDY_ID:
        raise ValueError(f"scenario is outside the official study: {study_id}")
    expected_roster_id = official_roster_id(case.scenario.roster)
    if case.labels.get("roster_id") != expected_roster_id:
        raise ValueError("scenario roster_id does not match the scenario roster")
    if case.scenario.timeline != RAID14_TIMELINE:
        raise ValueError("official Study 1 scenarios must use RAID14_TIMELINE")
    return {
        "schema_version": OFFICIAL_SCENARIO_ROW_SCHEMA_VERSION,
        "case_id": case.case_id,
        "study_id": OFFICIAL_STUDY_ID,
        "roster_id": expected_roster_id,
        "labels": dict(case.labels),
        "scenario": case.scenario.to_dict(),
    }


def write_official_scenario_jsonl(
    run_dir: str | Path,
    cases: Iterable[SampleCase],
) -> Path:
    """Write one complete 324-case input shard without running simulations."""
    prepared = tuple(cases)
    if len(prepared) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise ValueError(
            "official scenario writer requires exactly "
            f"{OFFICIAL_SCENARIOS_PER_ROSTER} cases"
        )
    rows = tuple(compact_official_scenario_row(case) for case in prepared)
    roster_ids = {row["roster_id"] for row in rows}
    if len(roster_ids) != 1:
        raise ValueError("official scenario writer requires exactly one roster")
    if len({row["case_id"] for row in rows}) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise ValueError("official scenario writer requires unique case ids")

    profile_ids = {profile.profile_id for profile in WAVE_A_GROWTH_PROFILES}
    coverage = set()
    for case in prepared:
        growth = (
            case.labels.get("b1_profile"),
            case.labels.get("main_profile"),
            case.labels.get("secondary_profile"),
        )
        if any(profile not in profile_ids for profile in growth):
            raise ValueError("official scenario writer received an unknown growth profile")
        environment = (
            case.labels.get("def_condition"),
            case.labels.get("core_condition"),
            case.labels.get("main_advantage"),
        )
        if environment[0] not in WAVE_A_DEFENSE_ANCHORS:
            raise ValueError("official scenario writer received an unknown defense anchor")
        if environment[1] not in WAVE_A_CORE_HIT_RATE_PCT:
            raise ValueError("official scenario writer received an unknown core condition")
        if environment[2] not in WAVE_A_MAIN_ADVANTAGE_LEVELS:
            raise ValueError("official scenario writer received an unknown advantage condition")
        if case.labels.get("hit_model") != "ideal-hit":
            raise ValueError("official scenario writer requires the ideal-hit model")
        coverage.add((*growth, *environment))
    if len(coverage) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise ValueError("official scenario writer requires the full Study 1 grid")

    roster_id = next(iter(roster_ids))
    scenarios_dir = Path(run_dir) / "scenarios"
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    path = scenarios_dir / f"{roster_id}.jsonl"
    payload = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
        for row in rows
    )
    _write_text_atomic(path, payload)
    return path


def write_official_manifest(
    run_dir: str | Path,
    manifest: Mapping[str, Any],
) -> Path:
    if manifest.get("study_id") != OFFICIAL_STUDY_ID:
        raise ValueError("manifest study_id does not match the official study")
    if manifest.get("schema_version") != OFFICIAL_MANIFEST_SCHEMA_VERSION:
        raise ValueError("unsupported official manifest schema version")

    path = Path(run_dir) / "manifest.json"
    payload = json.dumps(
        dict(manifest),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    _write_text_atomic(path, payload)
    return path


def _write_text_atomic(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(payload, encoding="utf-8")
    temp.replace(path)
