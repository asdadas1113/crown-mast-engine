import json
import unittest
from dataclasses import replace

from crown_mast_engine import (
    SAMPLE_BATCH_SCHEMA_VERSION,
    ResearchScenario,
    SampleCase,
    run_sample_batch,
)


class SampleBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        standard = ResearchScenario.standard()
        cls.short_scenario = replace(
            standard,
            timeline=(standard.timeline[0],),
            combat_settings=replace(
                standard.combat_settings,
                duration_sec=16,
            ),
        )

    def test_batch_emits_research_summary_and_character_shares(self) -> None:
        batch = run_sample_batch(
            (
                SampleCase(
                    "rapi-baseline",
                    self.short_scenario,
                    {"panel": "diagnostic"},
                ),
            )
        )
        payload = json.loads(batch.to_json(indent=None))
        result = payload["results"][0]
        summary = result["summary"]

        self.assertEqual(payload["schema_version"], SAMPLE_BATCH_SCHEMA_VERSION)
        self.assertEqual(result["case_id"], "rapi-baseline")
        self.assertEqual(summary["main_actor"], "rapi-red-hood")
        self.assertEqual(summary["secondary_b3"], "helm")
        self.assertIn("break_even_main_share_c", summary)
        self.assertIn("margin", summary)
        self.assertEqual(
            set(summary["character_shares"]),
            set(self.short_scenario.roster.members),
        )
        self.assertEqual(
            result["report"]["break_even_methodology"]["method"],
            "local_main_damage_scaling",
        )

    def test_duplicate_case_ids_are_rejected_before_execution(self) -> None:
        cases = (
            SampleCase("duplicate", self.short_scenario),
            SampleCase("duplicate", self.short_scenario),
        )
        with self.assertRaisesRegex(ValueError, "unique"):
            run_sample_batch(cases)

    def test_batch_rejects_mixed_baseline_rotations(self) -> None:
        opening = replace(
            self.short_scenario,
            baseline_rotation="opening_mast_crown_mast",
        )
        with self.assertRaisesRegex(ValueError, "baseline rotations"):
            run_sample_batch(
                (
                    SampleCase("default", self.short_scenario),
                    SampleCase("opening", opening),
                )
            )


if __name__ == "__main__":
    unittest.main()
