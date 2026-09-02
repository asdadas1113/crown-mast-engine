import unittest

from crown_mast_engine.checkpoints_v3 import CHECKPOINT_V3_POINT_COUNT
from crown_mast_engine.official_study import (
    OFFICIAL_B1_CANDIDATES,
    OFFICIAL_CORE_HIT_RATE_PCT,
    OFFICIAL_INVALID_DUPLICATE_ROSTER_COUNT,
    OFFICIAL_MAIN_B3_CANDIDATES,
    OFFICIAL_RAW_ROSTER_COUNT,
    OFFICIAL_SCENARIO_COUNT,
    OFFICIAL_SCENARIOS_PER_ROSTER,
    OFFICIAL_SECONDARY_B3_ANCHORS,
    OFFICIAL_VALID_ROSTER_COUNT,
    build_official_roster_cases,
    iter_official_rosters,
    official_roster_id,
    official_study_definition,
)
from crown_mast_engine.models import TeamRoster


class OfficialStudyTests(unittest.TestCase):
    def test_final_candidate_lists_are_frozen(self) -> None:
        self.assertEqual(
            OFFICIAL_B1_CANDIDATES,
            (
                "liter",
                "anis-star",
                "moran-favorite-item",
                "little-mermaid",
                "rapi-red-hood",
            ),
        )
        self.assertEqual(
            OFFICIAL_MAIN_B3_CANDIDATES,
            (
                "rapi-red-hood",
                "scarlet-black-shadow",
                "bready",
                "cinderella-crystal-wave",
                "liberalio",
                "milk-blooming-bunny",
                "phantom",
                "quency-escape-queen",
                "raven",
            ),
        )
        self.assertEqual(
            OFFICIAL_SECONDARY_B3_ANCHORS,
            ("epinel", "helm", "snow-white-heavy-arms"),
        )

    def test_roster_count_excludes_rapi_b1_main_duplicates_up_front(self) -> None:
        raw = [
            (b1, main_b3, secondary_b3)
            for b1 in OFFICIAL_B1_CANDIDATES
            for main_b3 in OFFICIAL_MAIN_B3_CANDIDATES
            for secondary_b3 in OFFICIAL_SECONDARY_B3_ANCHORS
        ]
        invalid = [
            item
            for item in raw
            if len(
                {
                    item[0],
                    "crown",
                    "mast-romantic-maid",
                    item[1],
                    item[2],
                }
            )
            != 5
        ]
        self.assertEqual(len(raw), OFFICIAL_RAW_ROSTER_COUNT)
        self.assertEqual(len(invalid), OFFICIAL_INVALID_DUPLICATE_ROSTER_COUNT)
        self.assertEqual(
            set(invalid),
            {
                ("rapi-red-hood", "rapi-red-hood", secondary)
                for secondary in OFFICIAL_SECONDARY_B3_ANCHORS
            },
        )

        rosters = tuple(iter_official_rosters())
        self.assertEqual(len(rosters), OFFICIAL_VALID_ROSTER_COUNT)
        self.assertEqual(len({official_roster_id(roster) for roster in rosters}), 132)
        self.assertTrue(
            all(len(set(roster.members)) == len(roster.members) for roster in rosters)
        )
        self.assertFalse(
            any(
                roster.b1 == "rapi-red-hood"
                and roster.main_b3 == "rapi-red-hood"
                for roster in rosters
            )
        )

    def test_official_scenario_arithmetic(self) -> None:
        self.assertEqual(CHECKPOINT_V3_POINT_COUNT, 64)
        self.assertEqual(OFFICIAL_SCENARIOS_PER_ROSTER, 64 * 2 * 2)
        self.assertEqual(OFFICIAL_SCENARIO_COUNT, 132 * 64 * 2 * 2)
        self.assertEqual(OFFICIAL_SCENARIO_COUNT, 33_792)

    def test_one_roster_shard_contains_256_unique_scenarios(self) -> None:
        roster = TeamRoster(
            b1="liter",
            main_b3="raven",
            secondary_b3="helm",
        )
        cases = build_official_roster_cases(roster)

        self.assertEqual(len(cases), OFFICIAL_SCENARIOS_PER_ROSTER)
        self.assertEqual(len({case.case_id for case in cases}), 256)
        environment_counts = {}
        for case in cases:
            key = (
                case.labels["core_condition"],
                case.labels["main_advantage"],
            )
            environment_counts[key] = environment_counts.get(key, 0) + 1
            self.assertEqual(case.labels["study_id"], "crown-mast-secondary-opportunity-v1")
            self.assertEqual(case.labels["secondary_anchor"], "helm")
        self.assertEqual(
            environment_counts,
            {
                ("off", "off"): 64,
                ("off", "on"): 64,
                ("on", "off"): 64,
                ("on", "on"): 64,
            },
        )

        core_rates = {
            case.labels["core_condition"]: case.scenario.combat_settings.core_hit_rate_pct
            for case in cases
        }
        self.assertEqual(core_rates, OFFICIAL_CORE_HIT_RATE_PCT)

    def test_out_of_sample_duplicate_roster_is_rejected_before_case_generation(self) -> None:
        with self.assertRaises(ValueError):
            build_official_roster_cases(
                TeamRoster(
                    b1="liter",
                    main_b3="raven",
                    secondary_b3="epinel",
                )
            )

        # TeamRoster itself is the core safety net for the Rapi duplicate case.
        with self.assertRaises(ValueError):
            TeamRoster(
                b1="rapi-red-hood",
                main_b3="rapi-red-hood",
                secondary_b3="helm",
            )

    def test_definition_matches_frozen_design(self) -> None:
        definition = official_study_definition()
        self.assertEqual(definition["valid_roster_count"], 132)
        self.assertEqual(definition["scenarios_per_roster"], 256)
        self.assertEqual(definition["scenario_count"], 33_792)
        self.assertEqual(definition["environment_axes"]["core"], {"off": 0.0, "on": 100.0})


if __name__ == "__main__":
    unittest.main()
