from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from crown_mast_engine.official_results import (
    OFFICIAL_MANIFEST_SCHEMA_VERSION,
    OFFICIAL_RAW_ROW_SCHEMA_VERSION,
    build_official_manifest,
    write_official_manifest,
)
from crown_mast_engine.official_study import (
    OFFICIAL_SCENARIOS_PER_ROSTER,
    iter_official_rosters,
    official_roster_id,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and assemble one official-study execution wave."
    )
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--start-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
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
            f"official wave shard set mismatch; missing={missing}, unexpected={unexpected}"
        )

    all_case_ids: set[str] = set()
    total_rows = 0
    output_raw_dir = Path(args.output_dir) / "machine" / "raw"
    output_raw_dir.mkdir(parents=True, exist_ok=True)

    for roster_id in expected_ids:
        source = raw_dir / f"{roster_id}.jsonl"
        rows = [
            _strict_json(line)
            for line in source.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(rows) != OFFICIAL_SCENARIOS_PER_ROSTER:
            raise AssertionError(f"{roster_id} does not contain exactly 256 rows")
        if {row["roster_id"] for row in rows} != {roster_id}:
            raise AssertionError(f"{roster_id} contains the wrong roster_id")
        if {row["run_id"] for row in rows} != {args.run_id}:
            raise AssertionError(f"{roster_id} contains the wrong run_id")
        if {row["schema_version"] for row in rows} != {OFFICIAL_RAW_ROW_SCHEMA_VERSION}:
            raise AssertionError(f"{roster_id} contains the wrong schema version")

        shard_case_ids = {str(row["case_id"]) for row in rows}
        if len(shard_case_ids) != OFFICIAL_SCENARIOS_PER_ROSTER:
            raise AssertionError(f"{roster_id} contains duplicate case ids")
        overlap = all_case_ids & shard_case_ids
        if overlap:
            raise AssertionError(
                f"official wave contains cross-shard duplicate case ids: {sorted(overlap)[:5]}"
            )
        all_case_ids.update(shard_case_ids)
        total_rows += len(rows)
        shutil.copy2(source, output_raw_dir / source.name)

    expected_rows = args.shard_count * OFFICIAL_SCENARIOS_PER_ROSTER
    if total_rows != expected_rows or len(all_case_ids) != expected_rows:
        raise AssertionError("official wave scenario total/uniqueness mismatch")

    manifest = build_official_manifest(
        run_id=args.run_id,
        branch=args.branch,
        commit_sha=args.commit_sha,
        completed_shard_ids=expected_ids,
        run_kind="official",
    )
    manifest_path = write_official_manifest(args.output_dir, manifest)
    parsed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if parsed_manifest["schema_version"] != OFFICIAL_MANIFEST_SCHEMA_VERSION:
        raise AssertionError("official wave manifest schema version mismatch")
    if parsed_manifest["run_kind"] != "official" or not parsed_manifest["official_result"]:
        raise AssertionError("official wave manifest must be marked official")
    if parsed_manifest["branch"] != args.branch:
        raise AssertionError("official wave manifest branch mismatch")
    if parsed_manifest["commit_sha"] != args.commit_sha:
        raise AssertionError("official wave manifest commit SHA mismatch")
    if parsed_manifest["counts"]["completed_shards"] != args.shard_count:
        raise AssertionError("official wave manifest completed shard count mismatch")
    if parsed_manifest["counts"]["completed_scenarios"] != expected_rows:
        raise AssertionError("official wave manifest completed scenario count mismatch")
    if parsed_manifest["sharding"]["completed_shard_ids"] != list(expected_ids):
        raise AssertionError("official wave manifest completed shard order mismatch")

    print(
        "OFFICIAL_WAVE_OK "
        f"range=[{args.start_index},{stop_index}) shards={args.shard_count} "
        f"scenarios={total_rows} unique_cases={len(all_case_ids)}"
    )
    print(f"OFFICIAL_WAVE_OK output={args.output_dir}")
    print(f"OFFICIAL_WAVE_OK manifest={manifest_path}")


if __name__ == "__main__":
    main()
