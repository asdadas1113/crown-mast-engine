import unittest

from crown_mast_engine import (
    CROWN_CROWN_MAST,
    CUSTOM_ROTATION,
    RAID14_FIRST_B1_TIME,
    RAID14_INTERVAL_SEC,
    RAID14_TIMELINE,
    ResearchScenario,
    SUSTAINED_FUNNEL,
    build_uniform_burst_timeline,
    simulate_rotation,
)
from dataclasses import replace


class UniformBurstTimelineTests(unittest.TestCase):
    def test_uniform_builder_preserves_first_cycle_offsets(self) -> None:
        timeline = build_uniform_burst_timeline(cycle_count=14, interval_sec=12.0)

        self.assertEqual(len(timeline), 14)
        self.assertEqual(tuple(cycle.cycle for cycle in timeline), tuple(range(1, 15)))
        self.assertEqual(timeline[0].b1_time, 3.9)
        self.assertAlmostEqual(timeline[13].b1_time, 159.9)
        self.assertAlmostEqual(timeline[13].full_burst_end, 171.1)
        self.assertEqual(timeline[12].b3_slot, "main_b3")
        self.assertEqual(timeline[13].b3_slot, "secondary_b3")
        for cycle in timeline:
            self.assertAlmostEqual(cycle.b2_time - cycle.b1_time, 0.4)
            self.assertAlmostEqual(cycle.b3_time - cycle.b1_time, 0.9)
            self.assertAlmostEqual(cycle.full_burst_start - cycle.b1_time, 1.2)
            self.assertAlmostEqual(cycle.full_burst_end - cycle.full_burst_start, 10.0)

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
