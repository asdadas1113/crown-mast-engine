import unittest
from dataclasses import replace
from pathlib import Path

from crown_mast_engine import (
    BurstCycle,
    CROWN_CROWN_MAST,
    CUSTOM_ROTATION,
    LEGACY_12_BURST_TIMELINE,
    RAID14_FIRST_B1_TIME,
    RAID14_INTERVAL_SEC,
    RAID14_TIMELINE,
    ResearchScenario,
    STANDARD_TIMELINE,
    SUSTAINED_FUNNEL,
    build_uniform_burst_timeline,
    simulate_rotation,
)


class UniformBurstTimelineTests(unittest.TestCase):
    def test_repository_policy_forbids_unrequested_legacy_timeline(self) -> None:
        root = Path(__file__).parents[1]
        policy = (root / "AGENTS.md").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")

        for document in (policy, readme):
            self.assertIn("명시적으로", document)
            self.assertIn("LEGACY_12_BURST_TIMELINE", document)
            self.assertIn("절대 사용하지 않는다", document)

    def test_uniform_builder_preserves_first_cycle_offsets(self) -> None:
        timeline = build_uniform_burst_timeline(cycle_count=14, interval_sec=12.0)

        self.assertEqual(len(timeline), 14)
        self.assertEqual(tuple(cycle.cycle for cycle in timeline), tuple(range(1, 15)))
        self.assertEqual(timeline[0].b1_time, 2.2)
        self.assertAlmostEqual(timeline[13].b1_time, 158.2)
        self.assertAlmostEqual(timeline[13].full_burst_end, 168.32)
        self.assertEqual(timeline[12].b3_slot, "main_b3")
        self.assertEqual(timeline[13].b3_slot, "secondary_b3")
        for cycle in timeline:
            self.assertAlmostEqual(cycle.b2_time - cycle.b1_time, 0.06)
            self.assertAlmostEqual(cycle.b3_time - cycle.b1_time, 0.12)
            self.assertAlmostEqual(cycle.full_burst_start - cycle.b1_time, 0.12)
            self.assertAlmostEqual(cycle.full_burst_end - cycle.full_burst_start, 10.0)

    def test_public_defaults_use_raid14_and_legacy_requires_explicit_selection(self) -> None:
        self.assertIs(STANDARD_TIMELINE, RAID14_TIMELINE)
        self.assertEqual(len(ResearchScenario.standard().timeline), 14)
        self.assertEqual(len(simulate_rotation(CROWN_CROWN_MAST).snapshots), 14)
        self.assertEqual(len(LEGACY_12_BURST_TIMELINE), 12)

        legacy = simulate_rotation(
            CROWN_CROWN_MAST,
            timeline=LEGACY_12_BURST_TIMELINE,
        )
        self.assertEqual(len(legacy.snapshots), 12)

    def test_raid14_timeline_matches_practical_baseline(self) -> None:
        self.assertEqual(len(RAID14_TIMELINE), 14)
        self.assertAlmostEqual(RAID14_TIMELINE[0].b1_time, 2.20)
        self.assertAlmostEqual(RAID14_TIMELINE[0].b2_time, 2.26)
        self.assertAlmostEqual(RAID14_TIMELINE[0].b3_time, 2.32)
        self.assertAlmostEqual(RAID14_TIMELINE[0].full_burst_start, 2.32)
        self.assertAlmostEqual(RAID14_TIMELINE[0].full_burst_end, 12.32)
        self.assertAlmostEqual(RAID14_TIMELINE[-1].b1_time, 167.30)
        self.assertAlmostEqual(RAID14_TIMELINE[-1].full_burst_end, 177.42)
        self.assertAlmostEqual(
            RAID14_FIRST_B1_TIME + RAID14_INTERVAL_SEC * 14,
            180.0,
        )

    def test_raid14_baselines_finish_with_two_stack_mast(self) -> None:
        self.assertEqual(CROWN_CROWN_MAST.b2_slot(13), "crown")
        self.assertEqual(CROWN_CROWN_MAST.b2_slot(14), "mast")
        self.assertEqual(SUSTAINED_FUNNEL.b2_slot(13), "crown")
        self.assertEqual(SUSTAINED_FUNNEL.b2_slot(14), "mast")
        with self.assertRaises(ValueError):
            CROWN_CROWN_MAST.b2_slot(15)
        with self.assertRaises(ValueError):
            SUSTAINED_FUNNEL.b2_slot(15)

        conventional = simulate_rotation(CROWN_CROWN_MAST, timeline=RAID14_TIMELINE)
        funnel = simulate_rotation(SUSTAINED_FUNNEL, timeline=RAID14_TIMELINE)
        for result in (conventional, funnel):
            final = result.snapshots[-1]
            self.assertEqual(final.cycle, 14)
            self.assertEqual(final.b2_actor, result.roster.mast)
            self.assertEqual(final.mast_stack_at_b2, 2)

    def test_custom_rotation_accepts_any_contiguous_cycle_count(self) -> None:
        policy = CUSTOM_ROTATION(
            "fourteen-cycle-test",
            {cycle: ("mast" if cycle % 3 == 0 else "crown") for cycle in range(1, 15)},
        )

        self.assertEqual(len(policy.b2_slot_by_cycle), 14)
        self.assertEqual(policy.b2_slot(14), "crown")
        with self.assertRaises(ValueError):
            policy.b2_slot(15)

    def test_fourteen_cycle_timeline_runs_through_engine_and_scenario_validation(self) -> None:
        result = simulate_rotation(CROWN_CROWN_MAST, timeline=RAID14_TIMELINE)
        scenario = replace(ResearchScenario.standard(), timeline=RAID14_TIMELINE)

        self.assertEqual(len(result.snapshots), 14)
        self.assertEqual(result.snapshots[-1].cycle, 14)
        self.assertEqual(result.macro_cycle_at(RAID14_TIMELINE[-1].b1_time), 5)
        self.assertEqual(len(scenario.timeline), 14)

    def test_overlapping_cycles_fail_in_scenario_and_direct_engine(self) -> None:
        overlapping = (
            BurstCycle(1, 1.0, 1.1, 1.2, 1.2, 11.2, "main_b3"),
            BurstCycle(2, 10.0, 10.1, 10.2, 10.2, 20.2, "secondary_b3"),
        )
        with self.assertRaisesRegex(ValueError, "overlap"):
            replace(ResearchScenario.standard(), timeline=overlapping)
        with self.assertRaisesRegex(ValueError, "overlap"):
            simulate_rotation(CROWN_CROWN_MAST, timeline=overlapping)

    def test_invalid_builder_inputs_fail_fast(self) -> None:
        with self.assertRaises(ValueError):
            build_uniform_burst_timeline(cycle_count=0, interval_sec=12.0)
        with self.assertRaises(ValueError):
            build_uniform_burst_timeline(cycle_count=14, interval_sec=0.0)
        with self.assertRaises(ValueError):
            build_uniform_burst_timeline(
                cycle_count=14,
                interval_sec=12.0,
                b3_slots=("unsupported",),
            )


if __name__ == "__main__":
    unittest.main()
