import unittest

from crown_mast_engine.checkpoints_v3 import REALISTIC_GROWTH_PROFILES
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
            {
                "moran-favorite-item",
                "scarlet-black-shadow",
                "liberalio",
            },
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

    def test_growth_oa_has_pairwise_complete_four_by_four_coverage(self) -> None:
        triples = wave_a_growth_index_triples()
        self.assertEqual(len(REALISTIC_GROWTH_PROFILES), 4)
        self.assertEqual(len(triples), WAVE_A_GROWTH_POINT_COUNT)
        self.assertEqual(WAVE_A_GROWTH_POINT_COUNT, 16)

        expected_pairs = {(left, right) for left in range(4) for right in range(4)}
        self.assertEqual({(b1, main) for b1, main, _ in triples}, expected_pairs)
        self.assertEqual({(b1, secondary) for b1, _, secondary in triples}, expected_pairs)
        self.assertEqual({(main, secondary) for _, main, secondary in triples}, expected_pairs)
        self.assertEqual(len(set(triples)), 16)

    def test_environment_and_total_case_arithmetic(self) -> None:
        self.assertEqual(tuple(WAVE_A_DEFENSE_ANCHORS.values()), (140.0, 12000.0, 31784.0))
        self.assertEqual(WAVE_A_CORE_HIT_RATE_PCT, {"off": 0.0, "on": 100.0})
        self.assertEqual(WAVE_A_MAIN_ADVANTAGE_LEVELS, ("off", "on"))
        self.assertEqual(WAVE_A_ENVIRONMENT_COUNT, 12)
        self.assertEqual(WAVE_A_SCENARIOS_PER_ROSTER, 192)
        self.assertEqual(WAVE_A_SCENARIO_COUNT, 16_704)

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
            {"oa16-pairwise"},
        )

        neutral = [
            case
            for case in cases
            if case.labels["main_advantage"] == "off"
        ]
        advantaged = [
            case
            for case in cases
            if case.labels["main_advantage"] == "on"
        ]
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
        self.assertEqual(definition["scenario_count"], 16_704)
        self.assertEqual(definition["scenarios_per_roster"], 192)
        self.assertEqual(definition["growth_design"]["points"], 16)
        self.assertFalse(definition["growth_design"]["three_way_complete"])
        self.assertEqual(definition["environment_axes"]["hit_model"], "ideal-hit")
        self.assertFalse(definition["execution_ready"])
        self.assertEqual(
            set(definition["execution_gated_actors"]),
            {"moran-favorite-item", "scarlet-black-shadow", "liberalio"},
        )
        self.assertIn("explicitly approves", definition["execution_policy"])


if __name__ == "__main__":
    unittest.main()
