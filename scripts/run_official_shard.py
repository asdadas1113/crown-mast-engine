from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from crown_mast_engine.official_results import (
    OFFICIAL_RAW_ROW_SCHEMA_VERSION,
    write_official_roster_jsonl,
)
from crown_mast_engine.official_study import (
    OFFICIAL_SCENARIOS_PER_ROSTER,
    iter_official_rosters,
    build_official_roster_cases,
    official_roster_id,
)
from crown_mast_engine.samples import run_sample_batch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute exactly one canonical official-study roster shard."
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--roster-index", type=int, required=True)
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def _strict_json(line: str) -> dict[str, object]:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant in official raw row: {value}")

    parsed = json.loads(line, parse_constant=reject_constant)
    if not isinstance(parsed, dict):
        raise ValueError("official raw row must be a JSON object")
    return parsed


def main() -> None:
    args = parse_args()
    if args.workers < 1:
        raise ValueError("workers must be at least 1")

    rosters = tuple(iter_official_rosters())
    if not 0 <= args.roster_index < len(rosters):
        raise ValueError(
            f"roster-index must be in [0, {len(rosters) - 1}], got {args.roster_index}"
        )

    roster = rosters[args.roster_index]
    roster_id = official_roster_id(roster)
    cases = build_official_roster_cases(roster)
    if len(cases) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("official shard did not build exactly 256 scenarios")

    batch = run_sample_batch(cases, workers=args.workers)
    if len(batch.results) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("official shard did not return exactly 256 results")

    run_dir = Path(args.output_dir)
    raw_path = write_official_roster_jsonl(
        run_dir,
        batch,
        run_id=args.run_id,
    )

    rows = [
        _strict_json(line)
        for line in raw_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("official raw shard must contain exactly 256 rows")
    if len({row["case_id"] for row in rows}) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("official raw shard case ids must be unique")
    if {row["run_id"] for row in rows} != {args.run_id}:
        raise AssertionError("official raw shard run_id mismatch")
    if {row["roster_id"] for row in rows} != {roster_id}:
        raise AssertionError("official raw shard roster_id mismatch")
    if {row["schema_version"] for row in rows} != {OFFICIAL_RAW_ROW_SCHEMA_VERSION}:
        raise AssertionError("official raw shard schema version mismatch")

    environment_counts: dict[tuple[str, str], int] = {}
    growth_environment_keys = set()
    for row in rows:
        environment = row["environment"]
        growth = row["growth"]
        if not isinstance(environment, dict) or not isinstance(growth, dict):
            raise AssertionError("official raw shard growth/environment schema mismatch")
        env_key = (
            str(environment["core_condition"]),
            str(environment["main_advantage"]),
        )
        environment_counts[env_key] = environment_counts.get(env_key, 0) + 1
        growth_environment_keys.add(
            (
                str(growth["b1"]),
                str(growth["main_b3"]),
                str(growth["secondary_b3"]),
                *env_key,
            )
        )

    expected_environment_counts = {
        ("off", "off"): 64,
        ("off", "on"): 64,
        ("on", "off"): 64,
        ("on", "on"): 64,
    }
    if environment_counts != expected_environment_counts:
        raise AssertionError(
            f"official raw shard environment coverage mismatch: {environment_counts}"
        )
    if len(growth_environment_keys) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("official raw shard growth/environment grid is incomplete")

    print(
        "OFFICIAL_SHARD_OK "
        f"index={args.roster_index} roster_id={roster_id} "
        f"scenarios={len(rows)} raw={raw_path}"
    )


if __name__ == "__main__":
    main()
