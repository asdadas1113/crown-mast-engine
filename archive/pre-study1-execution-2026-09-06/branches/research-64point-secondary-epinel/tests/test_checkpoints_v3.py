import unittest

from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from crown_mast_engine.checkpoints_v3 import (
    CHECKPOINT_V3_ID,
    CHECKPOINT_V3_POINT_COUNT,
    REALISTIC_GROWTH_PROFILES,
    build_checkpoint_v3_cases,
    checkpoint_v3_definitions,
    main_advantage_boss_element,
)
from crown_mast_engine.combat import ELEMENT_BEATS
from crown_mast_engine.equipment import GearState
from crown_mast_engine.models import TeamRoster
from crown_mast_engine.timeline import RAID14_TIMELINE


class CheckpointV3Tests(unittest.TestCase):
    def test_grid_is_fully_crossed_4_by_4_by_4(self) -> None:
        cases = build_checkpoint_v3_cases()

        self.assertEqual(CHECKPOINT_V3_POINT_COUNT, 64)
        self.assertEqual(len(cases), 64)
        self.assertEqual(len({case.case_id for case in cases}), 64)

        expected_ids = {profile.profile_id for profile in REALISTIC_GROWTH_PROFILES}
        self.assertEqual(
            {case.labels["b1_profile"] for case in cases},
            expected_ids,
        )
        self.assertEqual(
            {case.labels["main_profile"] for case in cases},
            expected_ids,
        )
        self.assertEqual(
            {case.labels["secondary_profile"] for case in cases},
            expected_ids,
        )
        combinations = {
            (
                case.labels["b1_profile"],
                case.labels["main_profile"],
                case.labels["secondary_profile"],
            )
            for case in cases
        }
        self.assertEqual(len(combinations), 64)

    def test_regular_actor_growth_profiles_match_requested_states(self) -> None:
        roster = TeamRoster(secondary_b3="epinel")
        cases = build_checkpoint_v3_cases(roster=roster)
        selected = {}
        for case in cases:
            selected.setdefault(
                case.labels["secondary_profile"],
                case.scenario.builds[roster.secondary_b3],
            )

        g1 = selected["g1-base5-none"]
        self.assertEqual({piece.state for piece in g1.equipment.pieces}, {GearState.BASE5})
        self.assertEqual(g1.collection.stage, "none")
        self.assertEqual((g1.overload.atk_lines, g1.overload.element_lines, g1.overload.ammo_lines), (0, 0, 0))

        g2 = selected["g2-ol0-sr5"]
        self.assertEqual({piece.state for piece in g2.equipment.pieces}, {GearState.OL0})
        self.assertEqual(g2.collection.stage, "SR5")
        self.assertEqual((g2.overload.atk_lines, g2.overload.element_lines, g2.overload.ammo_lines), (0, 0, 0))

        g3 = selected["g3-ol0-sr15-e3-a3"]
        self.assertEqual({piece.state for piece in g3.equipment.pieces}, {GearState.OL0})
        self.assertEqual(g3.collection.stage, "SR15")
        self.assertEqual((g3.overload.atk_lines, g3.overload.element_lines, g3.overload.ammo_lines), (3, 3, 0))

        g4 = selected["g4-ol5-sr15-e4-a4-ammo3"]
        self.assertEqual({piece.state for piece in g4.equipment.pieces}, {GearState.OL5})
        self.assertEqual(g4.collection.stage, "SR15")
        self.assertEqual((g4.overload.atk_lines, g4.overload.element_lines, g4.overload.ammo_lines), (4, 4, 3))

    def test_favorite_item_actor_keeps_sr15_but_preserves_other_growth_changes(self) -> None:
        cases = build_checkpoint_v3_cases()
        builds = {}
        for case in cases:
            builds.setdefault(
                case.labels["secondary_profile"],
                case.scenario.builds[case.scenario.roster.secondary_b3],
            )

        self.assertEqual({build.collection.stage for build in builds.values()}, {"SR15"})
        self.assertEqual(
            {piece.state for piece in builds["g1-base5-none"].equipment.pieces},
            {GearState.BASE5},
        )
        self.assertEqual(
            {piece.state for piece in builds["g2-ol0-sr5"].equipment.pieces},
            {GearState.OL0},
        )
        self.assertEqual(builds["g3-ol0-sr15-e3-a3"].overload.atk_lines, 3)
        self.assertEqual(builds["g4-ol5-sr15-e4-a4-ammo3"].overload.ammo_lines, 3)

    def test_all_cases_use_raid14_m1_opener_and_fixed_b2(self) -> None:
        cases = build_checkpoint_v3_cases(condition_id="neutral")

        for case in cases:
            self.assertEqual(case.labels["checkpoint_version"], CHECKPOINT_V3_ID)
            self.assertEqual(case.labels["condition"], "neutral")
            self.assertEqual(case.scenario.timeline, RAID14_TIMELINE)
            self.assertEqual(case.scenario.baseline_rotation, "opening_mast_crown_mast")
            for actor in (case.scenario.roster.crown, case.scenario.roster.mast):
                build = case.scenario.builds[actor]
                self.assertEqual({piece.state for piece in build.equipment.pieces}, {GearState.OL5})
                self.assertEqual(build.collection.stage, "SR15")
                self.assertEqual((build.overload.atk_lines, build.overload.element_lines, build.overload.ammo_lines), (0, 0, 0))

    def test_main_advantage_boss_element_uses_natural_element_relation(self) -> None:
        for actor in (
            "rapi-red-hood",
            "scarlet-black-shadow",
            "snow-white-heavy-arms",
            "epinel",
        ):
            definition = STANDARD_CHARACTER_CATALOG.require(actor)
            self.assertEqual(
                main_advantage_boss_element(actor),
                ELEMENT_BEATS[definition.element],
            )

    def test_definitions_match_realistic_grid(self) -> None:
        definitions = checkpoint_v3_definitions()
        self.assertEqual(definitions["id"], CHECKPOINT_V3_ID)
        self.assertEqual(definitions["point_count"], 64)
        self.assertEqual(definitions["axes"], {"b1": 4, "main": 4, "secondary": 4})
        self.assertEqual(definitions["baseline_rotation"], "opening_mast_crown_mast")
        self.assertEqual(len(definitions["b1"]), 4)
        self.assertEqual(len(definitions["main"]), 4)
        self.assertEqual(len(definitions["secondary"]), 4)
        self.assertTrue(
            all(item["favorite_item_collection_forced"] for item in definitions["secondary"])
        )

    def test_condition_id_must_be_non_empty(self) -> None:
        with self.assertRaises(ValueError):
            build_checkpoint_v3_cases(condition_id="")


if __name__ == "__main__":
    unittest.main()
