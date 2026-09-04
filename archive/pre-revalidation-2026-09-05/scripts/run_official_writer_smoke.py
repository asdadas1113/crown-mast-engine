from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from crown_mast_engine.models import TeamRoster
from crown_mast_engine.official_results import (
    OFFICIAL_MANIFEST_SCHEMA_VERSION,
    OFFICIAL_RAW_ROW_SCHEMA_VERSION,
    build_official_manifest,
    write_official_manifest,
    write_official_roster_jsonl,
)
from crown_mast_engine.official_study import (
    OFFICIAL_SCENARIOS_PER_ROSTER,
    build_official_roster_cases,
    official_roster_id,
)
from crown_mast_engine.samples import run_sample_batch


SMOKE_ROSTER = TeamRoster(
    b1="liter",
    main_b3="cinderella",
    secondary_b3="helm",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run exactly one official-study roster shard as a writer smoke test."
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.workers < 1:
        raise ValueError("workers must be at least 1")

    cases = build_official_roster_cases(SMOKE_ROSTER)
    if len(cases) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("smoke roster did not build exactly 256 scenarios")

    batch = run_sample_batch(cases, workers=args.workers)
    if len(batch.results) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("smoke execution did not return exactly 256 results")

    run_dir = Path(args.output_dir)
    roster_id = official_roster_id(SMOKE_ROSTER)
    raw_path = write_official_roster_jsonl(
        run_dir,
        batch,
        run_id=args.run_id,
    )
    manifest = build_official_manifest(
        run_id=args.run_id,
        branch=args.branch,
        commit_sha=args.commit_sha,
        completed_shard_ids=(roster_id,),
        run_kind="smoke",
    )
    manifest_path = write_official_manifest(run_dir, manifest)

    rows = [
        json.loads(line)
        for line in raw_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    parsed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if len(rows) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("raw JSONL must contain exactly 256 rows")
    if len({row["case_id"] for row in rows}) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("raw JSONL case ids must be unique")
    if {row["roster_id"] for row in rows} != {roster_id}:
        raise AssertionError("raw JSONL must contain exactly one roster")
    if {row["schema_version"] for row in rows} != {OFFICIAL_RAW_ROW_SCHEMA_VERSION}:
        raise AssertionError("raw JSONL schema version mismatch")
    if any(
        any(key in row for key in ("report", "macro_cycles", "burst_cycles", "by_source"))
        for row in rows
    ):
        raise AssertionError("compact raw rows contain verbose report payloads")

    environment_counts: dict[tuple[str, str], int] = {}
    growth_environment_keys = set()
    for row in rows:
        environment = row["environment"]
        growth = row["growth"]
        env_key = (
            environment["core_condition"],
            environment["main_advantage"],
        )
        environment_counts[env_key] = environment_counts.get(env_key, 0) + 1
        growth_environment_keys.add(
            (
                growth["b1"],
                growth["main_b3"],
                growth["secondary_b3"],
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
            f"unexpected environment coverage: {environment_counts}"
        )
    if len(growth_environment_keys) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("growth/environment cross product is incomplete")

    if parsed_manifest["schema_version"] != OFFICIAL_MANIFEST_SCHEMA_VERSION:
        raise AssertionError("manifest schema version mismatch")
    if parsed_manifest["run_kind"] != "smoke" or parsed_manifest["official_result"]:
        raise AssertionError("smoke manifest must not be marked as an official result")
    if parsed_manifest["branch"] != args.branch:
        raise AssertionError("manifest branch does not match runtime branch")
    if parsed_manifest["commit_sha"] != args.commit_sha:
        raise AssertionError("manifest commit SHA does not match runtime SHA")
    if parsed_manifest["counts"]["completed_shards"] != 1:
        raise AssertionError("smoke manifest must contain one completed shard")
    if parsed_manifest["counts"]["completed_scenarios"] != 256:
        raise AssertionError("smoke manifest must record 256 completed scenarios")
    if parsed_manifest["sharding"]["completed_shard_ids"] != [roster_id]:
        raise AssertionError("smoke manifest completed shard id mismatch")

    expected_raw_path = run_dir / "machine" / "raw" / f"{roster_id}.jsonl"
    if raw_path != expected_raw_path or not raw_path.is_file():
        raise AssertionError("raw JSONL was not written to machine/raw")
    if manifest_path != run_dir / "manifest.json" or not manifest_path.is_file():
        raise AssertionError("manifest.json was not written at run root")

    print(f"SMOKE_OK roster_id={roster_id}")
    print(f"SMOKE_OK scenarios={len(rows)} unique_cases={len({row['case_id'] for row in rows})}")
    print(f"SMOKE_OK environment_counts={environment_counts}")
    print(f"SMOKE_OK raw={raw_path}")
    print(f"SMOKE_OK manifest={manifest_path}")
    print(
        "SMOKE_OK official_result="
        f"{parsed_manifest['official_result']} run_kind={parsed_manifest['run_kind']}"
    )


if __name__ == "__main__":
    main()
