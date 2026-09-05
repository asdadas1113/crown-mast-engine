import unittest

from crown_mast_engine.models import TeamRoster
from crown_mast_engine.timeline import RAID14_TIMELINE
from crown_mast_engine.wave_a_study import (
    WAVE_A_B1_CANDIDATES,
    WAVE_A_BLOCKED_ACTORS,
    WAVE_A_CORE_HIT_RATE_PCT,
    WAVE_A_DEFENSE_ANCHORS,
    WAVE_A_ENVIRONMENT_COUNT,
    WAVE_A_EXECUTION_GATED_ACTORS,
    WAVE_A_GROWTH_POINT_COUNT,
    WAVE_A_GROWTH_PROFILES,
    WAVE_A_INVALID_DUPLICATE_ROSTER_COUNT,
    WAVE_A_MAIN_ADVANTAGE_LEVELS,
    WAVE_A_MAIN_B3_CANDIDATES,
    WAVE_A_RAW_ROSTER_COUNT,
    WAVE_A_SCENARIO_COUNT,
    WAVE_A_SCENARIOS_PER_ROSTER,
    WAVE_A_SECONDARY_B3_ANCHORS,
    WAVE_A_STUDY_ID,
    WAVE_A_VALID_ROSTER_COUNT,
    build_wave_a_roster_cases,
    iter_wave_a_rosters,
    wave_a_growth_index_triples,
    wave_a_reload_speed_ceiling_pct,
    wave_a_study_definition,
)


class WaveAStudyDesignTests(unittest.TestCase):
    def test_candidate_lists_match_frozen_study_design(self) -> None:
        self.assertEqual(
            WAVE_A_B1_CANDIDATES,
            (
                "liter",
                "anis-star",
                "moran-favorite-item",
                "little-mermaid",
                "rapi-red-hood",
            ),
        )
        self.assertEqual(
            WAVE_A_MAIN_B3_CANDIDATES,
            (
                "rapi-red-hood",
                "scarlet-black-shadow",
                "cinderella",
                "cinderella-crystal-wave",
                "liberalio",
                "neon-vision-eye",
            ),
        )
        self.assertEqual(
            WAVE_A_SECONDARY_B3_ANCHORS,
            ("epinel", "helm", "snow-white-heavy-arms"),
        )

    def test_selected_execution_gates_are_explicit(self) -> None:
        selected = {
            *WAVE_A_B1_CANDIDATES,
            *WAVE_A_MAIN_B3_CANDIDATES,
            *WAVE_A_SECONDARY_B3_ANCHORS,
        }
        self.assertFalse(selected.intersection(WAVE_A_BLOCKED_ACTORS))
        self.assertEqual(
            WAVE_A_EXECUTION_GATED_ACTORS.intersection(selected),
            {"scarlet-black-shadow"},
        )
        self.assertNotIn("raven", selected)
        self.assertNotIn("quency-escape-queen", selected)
        self.assertNotIn("milk-blooming-bunny", selected)

    def test_roster_arithmetic_and_duplicate_policy(self) -> None:
        self.assertEqual(WAVE_A_RAW_ROSTER_COUNT, 90)
        self.assertEqual(WAVE_A_INVALID_DUPLICATE_ROSTER_COUNT, 3)
        rosters = tuple(iter_wave_a_rosters())
        self.assertEqual(len(rosters), WAVE_A_VALID_ROSTER_COUNT)
        self.assertEqual(WAVE_A_VALID_ROSTER_COUNT, 87)
        self.assertTrue(all(len(set(roster.members)) == 5 for roster in rosters))
        self.assertFalse(
            any(
                roster.b1 == "rapi-red-hood"
                and roster.main_b3 == "rapi-red-hood"
                for roster in rosters
            )
        )

    def test_growth_grid_is_three_level_full_cartesian_product(self) -> None:
        triples = wave_a_growth_index_triples()
        self.assertEqual(
            tuple(profile.profile_id for profile in WAVE_A_GROWTH_PROFILES),
            (
                "g2-ol0-sr5",
                "g3-ol0-sr15-e3-a3",
                "g4-ol5-sr15-e4-a4-ammo3",
            ),
        )
        self.assertEqual(len(WAVE_A_GROWTH_PROFILES), 3)
        self.assertEqual(len(triples), WAVE_A_GROWTH_POINT_COUNT)
        self.assertEqual(WAVE_A_GROWTH_POINT_COUNT, 27)
        self.assertEqual(
            set(triples),
            {
                (b1, main, secondary)
                for b1 in range(3)
                for main in range(3)
                for secondary in range(3)
            },
        )
        self.assertEqual(len(set(triples)), 27)

    def test_environment_and_total_case_arithmetic(self) -> None:
        self.assertEqual(tuple(WAVE_A_DEFENSE_ANCHORS.values()), (140.0, 12000.0, 31784.0))
        self.assertEqual(WAVE_A_CORE_HIT_RATE_PCT, {"off": 0.0, "on": 100.0})
        self.assertEqual(WAVE_A_MAIN_ADVANTAGE_LEVELS, ("off", "on"))
        self.assertEqual(WAVE_A_ENVIRONMENT_COUNT, 12)
        self.assertEqual(WAVE_A_SCENARIOS_PER_ROSTER, 324)
        self.assertEqual(WAVE_A_SCENARIO_COUNT, 28_188)

    def test_current_candidate_list_is_certified_below_reload_speed_cap(self) -> None:
        self.assertAlmostEqual(wave_a_reload_speed_ceiling_pct(), 89.47)
        self.assertLess(wave_a_reload_speed_ceiling_pct(), 100)

    def test_one_roster_shard_is_generated_without_running_simulation(self) -> None:
        roster = next(iter_wave_a_rosters())
        cases = build_wave_a_roster_cases(roster)
        self.assertEqual(len(cases), WAVE_A_SCENARIOS_PER_ROSTER)
        self.assertEqual(len({case.case_id for case in cases}), len(cases))
        self.assertEqual(
            {case.scenario.combat_settings.boss_def for case in cases},
            set(WAVE_A_DEFENSE_ANCHORS.values()),
        )
        self.assertEqual(
            {case.scenario.combat_settings.core_hit_rate_pct for case in cases},
            set(WAVE_A_CORE_HIT_RATE_PCT.values()),
        )
        self.assertTrue(all(case.scenario.timeline == RAID14_TIMELINE for case in cases))
        self.assertTrue(all(case.labels["hit_model"] == "ideal-hit" for case in cases))
        self.assertTrue(all(case.labels["study_id"] == WAVE_A_STUDY_ID for case in cases))
        self.assertTrue(all(case.case_id.startswith(WAVE_A_STUDY_ID) for case in cases))
        self.assertEqual(
            {case.labels["growth_design"] for case in cases},
            {"full27-three-level"},
        )
        self.assertNotIn(
            "g1-base5-none",
            {
                profile
                for case in cases
                for profile in (
                    case.labels["b1_profile"],
                    case.labels["main_profile"],
                    case.labels["secondary_profile"],
                )
            },
        )

        neutral = [case for case in cases if case.labels["main_advantage"] == "off"]
        advantaged = [case for case in cases if case.labels["main_advantage"] == "on"]
        self.assertTrue(all(case.scenario.combat_settings.boss_element is None for case in neutral))
        self.assertTrue(all(case.scenario.combat_settings.boss_element is not None for case in advantaged))

    def test_outside_roster_is_rejected_fail_closed(self) -> None:
        outside = TeamRoster(main_b3="raven")
        with self.assertRaisesRegex(ValueError, "outside the Study 1 candidate sample"):
            build_wave_a_roster_cases(outside)

    def test_definition_is_self_consistent_and_execution_gated(self) -> None:
        definition = wave_a_study_definition()
        self.assertEqual(definition["study_id"], WAVE_A_STUDY_ID)
        self.assertEqual(definition["valid_roster_count"], 87)
        self.assertEqual(definition["scenario_count"], 28_188)
        self.assertEqual(definition["scenarios_per_roster"], 324)
        self.assertEqual(definition["growth_design"]["points"], 27)
        self.assertTrue(definition["growth_design"]["three_way_complete"])
        self.assertEqual(
            definition["growth_design"]["profile_ids"],
            [
                "g2-ol0-sr5",
                "g3-ol0-sr15-e3-a3",
                "g4-ol5-sr15-e4-a4-ammo3",
            ],
        )
        self.assertEqual(definition["environment_axes"]["hit_model"], "ideal-hit")
        self.assertFalse(definition["execution_ready"])
        self.assertEqual(
            set(definition["execution_gated_actors"]),
            {"scarlet-black-shadow"},
        )
        self.assertIn("explicitly approves", definition["execution_policy"])


if __name__ == "__main__":
    unittest.main()
