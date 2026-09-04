import unittest
from dataclasses import replace

from crown_mast_engine import (
    RAID14_TIMELINE,
    ResearchScenario,
    analyze_entry_variants,
)


class Raid14ResearchTests(unittest.TestCase):
    @staticmethod
    def scenario() -> ResearchScenario:
        return replace(ResearchScenario.standard(), timeline=RAID14_TIMELINE)

    def test_entry_window_tracks_full_opening_influence(self) -> None:
        scenario = self.scenario()
        variants = analyze_entry_variants(scenario)

        self.assertAlmostEqual(variants.first_burst.window_start, 2.20)
        self.assertAlmostEqual(variants.first_burst.window_end, 17.32)
        self.assertGreater(
            variants.first_burst.window_end,
            scenario.timeline[0].full_burst_end,
        )

        crown_burst_end = scenario.timeline[0].b2_time + 15.0
        self.assertAlmostEqual(crown_burst_end, 17.26)
        self.assertAlmostEqual(
            variants.first_burst.window_end - crown_burst_end,
            0.06,
        )

    def test_mast_opener_is_better_in_standard_raid14_case(self) -> None:
        variants = analyze_entry_variants(self.scenario())
        entry = variants.first_burst.team

        self.assertGreater(entry.mast_entry, entry.crown_entry)
        self.assertAlmostEqual(entry.relative_change, 0.02034706170578149)
        self.assertGreater(entry.delta_mast_minus_crown, 0.0)

    def test_entry_choice_is_independent_of_later_rotation_choice(self) -> None:
        variants = analyze_entry_variants(self.scenario())
        entry_delta = variants.first_burst.team.delta_mast_minus_crown
        conventional_delta = (
            variants.mast_entry.overall.team_c
            - variants.crown_entry.overall.team_c
        )
        funnel_delta = (
            variants.mast_entry.overall.team_f
            - variants.crown_entry.overall.team_f
        )

        self.assertAlmostEqual(conventional_delta, entry_delta, delta=1e-4)
        self.assertAlmostEqual(funnel_delta, entry_delta, delta=1e-4)

    def test_raid14_changes_break_even_without_changing_winner(self) -> None:
        legacy = analyze_entry_variants(ResearchScenario.standard()).crown_entry.overall
        raid14 = analyze_entry_variants(self.scenario()).crown_entry.overall

        self.assertLess(legacy.team_relative_change, 0.0)
        self.assertLess(raid14.team_relative_change, 0.0)
        self.assertAlmostEqual(legacy.break_even_main_share_c, 0.7101138178090082)
        self.assertAlmostEqual(raid14.break_even_main_share_c, 0.6508108735117237)


if __name__ == "__main__":
    unittest.main()
