import json
import tempfile
import unittest
from pathlib import Path

from crown_mast_engine.models import TeamRoster
from crown_mast_engine.official_results import (
    OFFICIAL_MANIFEST_SCHEMA_VERSION,
    OFFICIAL_RAW_ROW_SCHEMA_VERSION,
    build_official_manifest,
    compact_official_row,
    write_official_manifest,
)
from crown_mast_engine.official_study import (
    OFFICIAL_SCENARIO_COUNT,
    OFFICIAL_SCENARIOS_PER_ROSTER,
    build_official_roster_cases,
    official_roster_id,
)
from crown_mast_engine.samples import run_sample_batch


class OfficialResultWriterTests(unittest.TestCase):
    def test_manifest_records_canonical_provenance_and_smoke_scope(self) -> None:
        roster = TeamRoster(
            b1="liter",
            main_b3="cinderella",
            secondary_b3="helm",
        )
        roster_id = official_roster_id(roster)
        manifest = build_official_manifest(
            run_id="smoke-test",
            branch="research/14-burst-baseline",
            commit_sha="a" * 40,
            completed_shard_ids=(roster_id,),
            run_kind="smoke",
        )

        self.assertEqual(manifest["schema_version"], OFFICIAL_MANIFEST_SCHEMA_VERSION)
        self.assertEqual(manifest["study_id"], "crown-mast-secondary-opportunity-v1")
        self.assertEqual(manifest["run_kind"], "smoke")
        self.assertFalse(manifest["official_result"])
        self.assertEqual(manifest["counts"]["valid_rosters"], 117)
        self.assertEqual(
            manifest["counts"]["scenarios_per_roster"],
            OFFICIAL_SCENARIOS_PER_ROSTER,
        )
        self.assertEqual(manifest["counts"]["official_scenarios"], OFFICIAL_SCENARIO_COUNT)
        self.assertEqual(manifest["counts"]["completed_shards"], 1)
        self.assertEqual(manifest["counts"]["completed_scenarios"], 256)
        self.assertEqual(manifest["sharding"]["completed_shard_ids"], [roster_id])
        self.assertEqual(manifest["timeline"]["cycle_count"], 14)
        self.assertEqual(manifest["timeline"]["first_b1_time"], 2.2)
        self.assertEqual(manifest["timeline"]["interval_sec"], 12.7)
        self.assertEqual(manifest["baseline_rotation"], "opening_mast_crown_mast")
        self.assertEqual(
            manifest["output_layout"]["raw"],
            "machine/raw/<roster_id>.jsonl",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_official_manifest(temp_dir, manifest)
            parsed = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(parsed, manifest)
            self.assertEqual(path, Path(temp_dir) / "manifest.json")

    def test_compact_row_keeps_analysis_fields_without_verbose_report(self) -> None:
        roster = TeamRoster(
            b1="liter",
            main_b3="cinderella",
            secondary_b3="helm",
        )
        case = build_official_roster_cases(roster)[0]
        result = run_sample_batch((case,), workers=1).results[0]
        row = compact_official_row(result, run_id="unit-smoke")

        self.assertEqual(row["schema_version"], OFFICIAL_RAW_ROW_SCHEMA_VERSION)
        self.assertEqual(row["study_id"], "crown-mast-secondary-opportunity-v1")
        self.assertEqual(row["roster_id"], official_roster_id(roster))
        self.assertEqual(row["roster"]["b1"], "liter")
        self.assertEqual(row["roster"]["main_b3"], "cinderella")
        self.assertEqual(row["roster"]["secondary_b3"], "helm")
        self.assertEqual(row["growth"]["b1"], "g1-base5-none")
        self.assertIn(row["environment"]["core_condition"], {"off", "on"})
        self.assertIn(row["environment"]["main_advantage"], {"off", "on"})
        self.assertIn("absolute_gain", row["main"])
        self.assertIn("conventional_share", row["secondary"])
        self.assertIn("rest_of_team_absolute_loss", row["opportunity"])
        self.assertIn("g", row["opportunity"])
        self.assertIn("l", row["opportunity"])
        self.assertIn("break_even_main_share_c", row["opportunity"])
        self.assertEqual(set(row["characters"]), set(roster.members))
        self.assertNotIn("report", row)
        self.assertNotIn("macro_cycles", row)
        self.assertNotIn("burst_cycles", row)
        self.assertNotIn("by_source", row)


if __name__ == "__main__":
    unittest.main()
