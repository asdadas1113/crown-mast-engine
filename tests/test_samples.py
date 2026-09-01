import json
import unittest
from dataclasses import replace
from unittest.mock import patch

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
                ),
                workers=2,
            )

    def test_parallel_results_match_serial_results_exactly(self) -> None:
        cases = (
            SampleCase(
                "first",
                self.short_scenario,
                {"panel": "serial-parallel"},
            ),
            SampleCase(
                "second",
                self.short_scenario,
                {"panel": "serial-parallel"},
            ),
        )

        serial = run_sample_batch(cases, workers=1)
        parallel = run_sample_batch(cases, workers=2)

        self.assertEqual(serial.to_dict(), parallel.to_dict())
        self.assertEqual(
            serial.to_json(indent=None),
            parallel.to_json(indent=None),
        )

    def test_workers_one_uses_serial_fallback(self) -> None:
        cases = (
            SampleCase("first", self.short_scenario),
            SampleCase("second", self.short_scenario),
        )

        with patch(
            "crown_mast_engine.samples.ProcessPoolExecutor",
            side_effect=AssertionError("process pool should not be constructed"),
        ):
            batch = run_sample_batch(cases, workers=1)

        self.assertEqual(
            tuple(result.case_id for result in batch.results),
            ("first", "second"),
        )

    def test_default_workers_use_spawn_process_pool(self) -> None:
        cases = (
            SampleCase("first", self.short_scenario),
            SampleCase("second", self.short_scenario),
        )
        captured = {}

        class ImmediateExecutor:
            def __init__(self, **kwargs):
                captured.update(kwargs)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def map(self, function, payloads):
                return tuple(function(payload) for payload in payloads)

        with patch("crown_mast_engine.samples.os.cpu_count", return_value=8), patch(
            "crown_mast_engine.samples.ProcessPoolExecutor",
            ImmediateExecutor,
        ):
            batch = run_sample_batch(cases)

        self.assertEqual(captured["max_workers"], 2)
        self.assertEqual(captured["mp_context"].get_start_method(), "spawn")
        self.assertEqual(
            tuple(result.case_id for result in batch.results),
            ("first", "second"),
        )

    def test_parallel_results_preserve_input_order(self) -> None:
        cases = tuple(
            SampleCase(case_id, self.short_scenario)
            for case_id in ("third", "first", "second")
        )

        batch = run_sample_batch(cases, workers=2)

        self.assertEqual(
            tuple(result.case_id for result in batch.results),
            ("third", "first", "second"),
        )

    def test_parallel_worker_exception_propagates(self) -> None:
        invalid = replace(
            self.short_scenario,
            expected_engine_rule_revision="test-invalid-revision",
        )
        cases = (
            SampleCase("valid", self.short_scenario),
            SampleCase("invalid", invalid),
        )

        with self.assertRaisesRegex(ValueError, "engine revision"):
            run_sample_batch(cases, workers=2)

    def test_invalid_workers_are_rejected(self) -> None:
        cases = (SampleCase("valid", self.short_scenario),)
        for workers in (0, -1):
            with self.subTest(workers=workers):
                with self.assertRaisesRegex(ValueError, "at least 1"):
                    run_sample_batch(cases, workers=workers)
        for workers in (True, 1.5, "2"):
            with self.subTest(workers=workers):
                with self.assertRaisesRegex(TypeError, "integer or None"):
                    run_sample_batch(cases, workers=workers)


if __name__ == "__main__":
    unittest.main()
