from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from crown_mast_engine.character_mechanics import STANDARD_SKILL_HOOKS
from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from crown_mast_engine.mechanics import ENGINE_RULE_REVISION
from crown_mast_engine.official_results import OFFICIAL_RAW_ROW_SCHEMA_VERSION
from crown_mast_engine.official_study import (
    OFFICIAL_SCENARIOS_PER_ROSTER,
    OFFICIAL_STUDY_ID,
    build_official_roster_cases,
    iter_official_rosters,
    official_roster_id,
)


EXPECTED_TOP_KEYS = {
    "case_id",
    "characters",
    "environment",
    "growth",
    "main",
    "opportunity",
    "outcome_band",
    "revisions",
    "roster",
    "roster_id",
    "run_id",
    "schema_version",
    "secondary",
    "study_id",
    "team",
}

EXPECTED_SECTION_KEYS = {
    "roster": {"b1", "main_b3", "secondary_b3"},
    "growth": {"b1", "main_b3", "secondary_b3"},
    "environment": {
        "boss_element",
        "core_condition",
        "core_hit_rate_pct",
        "main_advantage",
    },
    "revisions": {"catalog_source", "engine_rule", "skill_hooks"},
    "team": {
        "conventional_damage",
        "delta",
        "funnel_damage",
        "relative_change",
    },
    "main": {
        "absolute_gain",
        "actor",
        "conventional_damage",
        "conventional_share",
        "funnel_damage",
        "funnel_share",
        "relative_change",
    },
    "secondary": {
        "absolute_loss",
        "actor",
        "conventional_damage",
        "conventional_share",
        "delta",
        "funnel_damage",
        "funnel_share",
        "relative_change",
    },
    "opportunity": {
        "break_even_main_share_c",
        "comparison_case",
        "g",
        "l",
        "lambda_star",
        "local_slope",
        "observed_winner",
        "rest_of_team_absolute_loss",
        "rest_of_team_conventional_damage",
        "rest_of_team_funnel_damage",
    },
}

EXPECTED_CHARACTER_KEYS = {
    "conventional_damage",
    "conventional_share",
    "delta",
    "funnel_damage",
    "funnel_share",
    "relative_change",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Strictly audit official-study raw shard files without executing combat."
    )
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--start-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    return parser.parse_args()


def _strict_json(line: str) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant in official raw row: {value}")

    parsed = json.loads(line, parse_constant=reject_constant)
    if not isinstance(parsed, dict):
        raise ValueError("official raw row must be a JSON object")
    return parsed


def _assert_finite(value: Any, path: str) -> None:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise AssertionError(f"non-finite numeric value at {path}: {value}")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            _assert_finite(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_finite(child, f"{path}[{index}]")


def _require_dict(row: dict[str, Any], key: str) -> dict[str, Any]:
    value = row.get(key)
    if not isinstance(value, dict):
        raise AssertionError(f"{key} must be an object")
    return value


def main() -> None:
    args = parse_args()
    if args.shard_count < 1:
        raise ValueError("shard-count must be at least 1")

    rosters = tuple(iter_official_rosters())
    stop_index = args.start_index + args.shard_count
    if args.start_index < 0 or stop_index > len(rosters):
        raise ValueError(
            f"requested shard range [{args.start_index}, {stop_index}) "
            f"is outside 0..{len(rosters)}"
        )

    expected_rosters = rosters[args.start_index:stop_index]
    expected_ids = tuple(official_roster_id(roster) for roster in expected_rosters)
    expected_id_set = set(expected_ids)

    raw_dir = Path(args.raw_dir)
    paths = sorted(raw_dir.glob("*.jsonl"))
    actual_ids = {path.stem for path in paths}
    if len(paths) != args.shard_count:
        raise AssertionError(
            f"expected {args.shard_count} raw shard files, found {len(paths)}"
        )
    if actual_ids != expected_id_set:
        missing = sorted(expected_id_set - actual_ids)
        unexpected = sorted(actual_ids - expected_id_set)
        raise AssertionError(
            f"official audit shard set mismatch; missing={missing}, unexpected={unexpected}"
        )

    signature = STANDARD_SKILL_HOOKS.mechanics_signature
    expected_revisions = {
        "engine_rule": ENGINE_RULE_REVISION,
        "skill_hooks": signature.skill_hook_revision,
        "catalog_source": STANDARD_CHARACTER_CATALOG.scope.source_revision,
    }

    all_case_ids: set[str] = set()
    total_rows = 0

    for roster in expected_rosters:
        roster_id = official_roster_id(roster)
        path = raw_dir / f"{roster_id}.jsonl"
        rows = [
            _strict_json(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(rows) != OFFICIAL_SCENARIOS_PER_ROSTER:
            raise AssertionError(f"{roster_id} does not contain exactly 256 rows")

        expected_cases = {
            case.case_id: case
            for case in build_official_roster_cases(roster)
        }
        if len(expected_cases) != OFFICIAL_SCENARIOS_PER_ROSTER:
            raise AssertionError(f"{roster_id} canonical case map is not exactly 256")

        shard_case_ids = {str(row.get("case_id")) for row in rows}
        if shard_case_ids != set(expected_cases):
            missing = sorted(set(expected_cases) - shard_case_ids)
            unexpected = sorted(shard_case_ids - set(expected_cases))
            raise AssertionError(
                f"{roster_id} case set mismatch; "
                f"missing={missing[:5]}, unexpected={unexpected[:5]}"
            )

        overlap = all_case_ids & shard_case_ids
        if overlap:
            raise AssertionError(
                f"cross-shard duplicate case ids: {sorted(overlap)[:5]}"
            )

        for row in rows:
            case_id = str(row["case_id"])
            case = expected_cases[case_id]
            labels = case.labels
            scenario = case.scenario

            if set(row) != EXPECTED_TOP_KEYS:
                raise AssertionError(f"{case_id} top-level raw schema mismatch")
            for section, expected_keys in EXPECTED_SECTION_KEYS.items():
                payload = _require_dict(row, section)
                if set(payload) != expected_keys:
                    raise AssertionError(f"{case_id} {section} schema mismatch")

            if row["schema_version"] != OFFICIAL_RAW_ROW_SCHEMA_VERSION:
                raise AssertionError(f"{case_id} raw schema version mismatch")
            if row["study_id"] != OFFICIAL_STUDY_ID:
                raise AssertionError(f"{case_id} study id mismatch")
            if row["run_id"] != args.run_id:
                raise AssertionError(f"{case_id} run id mismatch")
            if row["roster_id"] != roster_id:
                raise AssertionError(f"{case_id} roster id mismatch")

            expected_roster_payload = {
                "b1": roster.b1,
                "main_b3": roster.main_b3,
                "secondary_b3": roster.secondary_b3,
            }
            if row["roster"] != expected_roster_payload:
                raise AssertionError(f"{case_id} roster payload mismatch")

            expected_growth = {
                "b1": labels["b1_profile"],
                "main_b3": labels["main_profile"],
                "secondary_b3": labels["secondary_profile"],
            }
            if row["growth"] != expected_growth:
                raise AssertionError(f"{case_id} growth labels mismatch")

            expected_environment = {
                "core_condition": labels["core_condition"],
                "core_hit_rate_pct": scenario.combat_settings.core_hit_rate_pct,
                "main_advantage": labels["main_advantage"],
                "boss_element": scenario.combat_settings.boss_element or "neutral",
            }
            if row["environment"] != expected_environment:
                raise AssertionError(f"{case_id} environment payload mismatch")

            if row["revisions"] != expected_revisions:
                raise AssertionError(f"{case_id} engine/catalog revision mismatch")

            main_payload = _require_dict(row, "main")
            secondary_payload = _require_dict(row, "secondary")
            if main_payload["actor"] != roster.main_b3:
                raise AssertionError(f"{case_id} Main actor mismatch")
            if secondary_payload["actor"] != roster.secondary_b3:
                raise AssertionError(f"{case_id} Secondary actor mismatch")

            characters = _require_dict(row, "characters")
            expected_characters = {
                roster.b1,
                "crown",
                "mast-romantic-maid",
                roster.main_b3,
                roster.secondary_b3,
            }
            if set(characters) != expected_characters:
                raise AssertionError(f"{case_id} character set mismatch")
            for actor, payload in characters.items():
                if not isinstance(payload, dict) or set(payload) != EXPECTED_CHARACTER_KEYS:
                    raise AssertionError(
                        f"{case_id} character schema mismatch for {actor}"
                    )

            _assert_finite(row, case_id)

        all_case_ids.update(shard_case_ids)
        total_rows += len(rows)

    expected_rows = args.shard_count * OFFICIAL_SCENARIOS_PER_ROSTER
    if total_rows != expected_rows or len(all_case_ids) != expected_rows:
        raise AssertionError("official audit scenario total/uniqueness mismatch")

    print(
        "OFFICIAL_AUDIT_OK "
        f"range=[{args.start_index},{stop_index}) shards={args.shard_count} "
        f"scenarios={total_rows} unique_cases={len(all_case_ids)}"
    )
    print(
        "OFFICIAL_AUDIT_OK revisions="
        f"{expected_revisions['engine_rule']} / {expected_revisions['skill_hooks']}"
    )


if __name__ == "__main__":
    main()
