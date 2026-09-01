import unittest

from crown_mast_engine.interface import build_checkpoint_cases
from crown_mast_engine.research import analyze_research_scenario
from crown_mast_engine.timeline import RAID14_TIMELINE


class Raid14CheckpointRoutingTests(unittest.TestCase):
    @staticmethod
    def payload(baseline_rotation="crown_crown_mast"):
        return {
            "roster": {
                "b1": "liter",
                "main_b3": "rapi-red-hood",
                "secondary_b3": "helm",
            },
            "combat": {
                "boss_def": 140,
                "boss_element": None,
                "core_hit_rate_pct": 0,
                "range_bonus_pct": 0,
            },
            "baseline_rotation": baseline_rotation,
        }

    def test_checkpoint_grid_uses_raid14_timeline(self) -> None:
        cases = build_checkpoint_cases(self.payload())
        self.assertEqual(len(cases), 12)
        self.assertTrue(all(case.scenario.timeline == RAID14_TIMELINE for case in cases))
        self.assertTrue(all(len(case.scenario.timeline) == 14 for case in cases))

    def test_opening_mast_checkpoint_pairs_matching_funnel(self) -> None:
        case = build_checkpoint_cases(
            self.payload("opening_mast_crown_mast")
        )[0]
        comparison = analyze_research_scenario(case.scenario)
        self.assertEqual(
            comparison.conventional_result.policy_name,
            "opening_mast_crown_mast",
        )
        self.assertEqual(
            comparison.funnel_result.policy_name,
            "opening_mast_sustained_funnel",
        )


if __name__ == "__main__":
    unittest.main()
