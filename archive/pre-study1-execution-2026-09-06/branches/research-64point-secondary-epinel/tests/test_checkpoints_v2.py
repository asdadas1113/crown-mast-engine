import unittest

from crown_mast_engine.checkpoints_v2 import (
    B1_CHECKPOINTS_V2,
    CHECKPOINT_V2_ID,
    CHECKPOINT_V2_POINT_COUNT,
    MAIN_CHECKPOINTS_V2,
    SECONDARY_CHECKPOINTS_V2,
    build_checkpoint_v2_cases,
    checkpoint_v2_definitions,
)
from crown_mast_engine.equipment import GearState
from crown_mast_engine.models import TeamRoster
from crown_mast_engine.timeline import RAID14_TIMELINE


class CheckpointV2Tests(unittest.TestCase):
    def test_grid_is_fully_crossed_4_by_3_by_3(self) -> None:
        cases = build_checkpoint_v2_cases()

        self.assertEqual(CHECKPOINT_V2_POINT_COUNT, 36)
        self.assertEqual(len(cases), 36)
        self.assertEqual(len({case.case_id for case in cases}), 36)
        self.assertEqual(
            {case.labels["b1_profile"] for case in cases},
            {profile.profile_id for profile in B1_CHECKPOINTS_V2},
        )
        self.assertEqual(
            {case.labels["main_profile"] for case in cases},
            {profile.profile_id for profile in MAIN_CHECKPOINTS_V2},
        )
        self.assertEqual(
            {case.labels["secondary_profile"] for case in cases},
            {profile.profile_id for profile in SECONDARY_CHECKPOINTS_V2},
        )

        combinations = {
            (
                case.labels["b1_profile"],
                case.labels["main_profile"],
                case.labels["secondary_profile"],
            )
            for case in cases
        }
        self.assertEqual(len(combinations), 36)

    def test_all_cases_use_raid14_and_fixed_b2_builds(self) -> None:
        cases = build_checkpoint_v2_cases()

        for case in cases:
            self.assertEqual(case.labels["checkpoint_version"], CHECKPOINT_V2_ID)
            self.assertEqual(case.scenario.timeline, RAID14_TIMELINE)
            for actor in (case.scenario.roster.crown, case.scenario.roster.mast):
                build = case.scenario.builds[actor]
                self.assertEqual(
                    {piece.state for piece in build.equipment.pieces},
                    {GearState.OL5},
                )
                self.assertEqual(build.collection.stage, "SR15")
                self.assertEqual(build.overload.atk_lines, 0)
                self.assertEqual(build.overload.element_lines, 0)
                self.assertEqual(build.overload.ammo_lines, 0)

    def test_main_profiles_keep_atk_and_ammo_axes_independent(self) -> None:
        cases = build_checkpoint_v2_cases()
        profiles = {}
        for case in cases:
            profiles.setdefault(
                case.labels["main_profile"],
                case.scenario.builds[case.scenario.roster.main_b3].overload,
            )

        self.assertEqual(profiles["main-o5-bare"].atk_lines, 0)
        self.assertEqual(profiles["main-o5-bare"].ammo_lines, 0)
        self.assertEqual(profiles["main-o5-atk3"].atk_lines, 3)
        self.assertEqual(profiles["main-o5-atk3"].ammo_lines, 0)
        self.assertEqual(profiles["main-o5-ammo2"].atk_lines, 0)
        self.assertEqual(profiles["main-o5-ammo2"].ammo_lines, 2)

    def test_secondary_axis_is_o5_o0_b5_with_no_ol_options(self) -> None:
        cases = build_checkpoint_v2_cases()
        expected = {
            "secondary-o5": GearState.OL5,
            "secondary-o0": GearState.OL0,
            "secondary-b5": GearState.BASE5,
        }

        for profile_id, state in expected.items():
            selected = next(
                case
                for case in cases
                if case.labels["secondary_profile"] == profile_id
            )
            build = selected.scenario.builds[selected.scenario.roster.secondary_b3]
            self.assertEqual({piece.state for piece in build.equipment.pieces}, {state})
            self.assertEqual(build.overload.atk_lines, 0)
            self.assertEqual(build.overload.element_lines, 0)
            self.assertEqual(build.overload.ammo_lines, 0)
            self.assertEqual(build.collection.stage, "SR15")

    def test_b1_progression_has_four_distinct_builds_for_liter(self) -> None:
        cases = build_checkpoint_v2_cases()
        builds = {}
        for case in cases:
            builds.setdefault(
                case.labels["b1_profile"],
                case.scenario.builds[case.scenario.roster.b1],
            )

        self.assertEqual(builds["b1-low"].collection.stage, "none")
        self.assertEqual(
            {piece.state for piece in builds["b1-low"].equipment.pieces},
            {GearState.BASE5},
        )
        self.assertEqual(builds["b1-developing"].collection.stage, "SR15")
        self.assertEqual(
            {piece.state for piece in builds["b1-developing"].equipment.pieces},
            {GearState.OL0},
        )
        self.assertEqual(builds["b1-standard"].collection.stage, "SR15")
        self.assertEqual(
            {piece.state for piece in builds["b1-standard"].equipment.pieces},
            {GearState.OL5},
        )
        high = builds["b1-high"]
        self.assertEqual(high.overload.atk_lines, 4)
        self.assertEqual(high.overload.element_lines, 4)
        self.assertEqual(high.overload.ammo_lines, 3)

    def test_opening_baseline_is_preserved_across_all_cases(self) -> None:
        cases = build_checkpoint_v2_cases(
            baseline_rotation="opening_mast_crown_mast"
        )
        self.assertEqual(
            {case.scenario.baseline_rotation for case in cases},
            {"opening_mast_crown_mast"},
        )

    def test_favorite_item_b1_keeps_sr15_at_every_stage(self) -> None:
        roster = TeamRoster(b1="moran-favorite-item")
        cases = build_checkpoint_v2_cases(roster=roster)
        self.assertEqual(
            {
                case.scenario.builds["moran-favorite-item"].collection.stage
                for case in cases
            },
            {"SR15"},
        )

    def test_definitions_match_grid_dimensions(self) -> None:
        definitions = checkpoint_v2_definitions()
        self.assertEqual(definitions["id"], CHECKPOINT_V2_ID)
        self.assertEqual(definitions["point_count"], 36)
        self.assertEqual(definitions["axes"], {"b1": 4, "main": 3, "secondary": 3})
        self.assertEqual(len(definitions["b1"]), 4)
        self.assertEqual(len(definitions["main"]), 3)
        self.assertEqual(len(definitions["secondary"]), 3)


if __name__ == "__main__":
    unittest.main()
