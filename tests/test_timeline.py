import unittest

from crown_mast_engine import (
    CROWN_CROWN_MAST,
    CUSTOM_ROTATION,
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

    def test_baseline_rotations_continue_beyond_cycle_12(self) -> None:
        self.assertEqual(CROWN_CROWN_MAST.b2_slot(13), "crown")
        self.assertEqual(CROWN_CROWN_MAST.b2_slot(14), "crown")
        self.assertEqual(CROWN_CROWN_MAST.b2_slot(15), "mast")
        self.assertEqual(SUSTAINED_FUNNEL.b2_slot(13), "crown")
        self.assertEqual(SUSTAINED_FUNNEL.b2_slot(14), "crown")
        self.assertEqual(SUSTAINED_FUNNEL.b2_slot(15), "mast")

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
        timeline = build_uniform_burst_timeline(cycle_count=14, interval_sec=12.0)
        result = simulate_rotation(CROWN_CROWN_MAST, timeline=timeline)
        scenario = replace(ResearchScenario.standard(), timeline=timeline)

        self.assertEqual(len(result.snapshots), 14)
        self.assertEqual(result.snapshots[-1].cycle, 14)
        self.assertEqual(result.macro_cycle_at(timeline[-1].b1_time), 5)
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
