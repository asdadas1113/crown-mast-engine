import unittest

from crown_mast_engine import (
    BuildProfile,
    GearState,
    OverloadProfile,
    RotationWinner,
    analyze_rotations,
)
from crown_mast_engine.combat import CombatSettings
from crown_mast_engine.models import DamageCategory, TeamRoster


class OverloadIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.roster = TeamRoster()
        bare = BuildProfile.uniform(GearState.OL5)
        high = BuildProfile.uniform(
            GearState.OL5,
            OverloadProfile(atk_lines=4, element_lines=4, ammo_lines=3),
        )
        extreme = BuildProfile.uniform(
            GearState.OL5,
            OverloadProfile(atk_lines=10, element_lines=20, ammo_lines=100),
        )
        base = {actor: bare for actor in cls.roster.members}
        builds_by_case = {
            "all_bare": base,
            "rapi_high": {**base, "rapi-red-hood": high},
            "helm_high": {**base, "helm": high},
            "both_high": {
                **base,
                "rapi-red-hood": high,
                "helm": high,
            },
            "rapi_extreme": {**base, "rapi-red-hood": extreme},
        }
        settings = CombatSettings(boss_element="Wind")
        cls.results = {
            name: analyze_rotations(
                roster=cls.roster,
                builds=builds,
                combat_settings=settings,
                main_actor="rapi-red-hood",
            )
            for name, builds in builds_by_case.items()
        }

    def test_representative_ol_cases_cross_the_expected_boundary(self) -> None:
        bare = self.results["all_bare"].overall
        rapi_high = self.results["rapi_high"].overall
        helm_high = self.results["helm_high"].overall
        both_high = self.results["both_high"].overall

        self.assertEqual(bare.observed_winner, RotationWinner.CONVENTIONAL)
        self.assertEqual(rapi_high.observed_winner, RotationWinner.FUNNEL)
        self.assertEqual(helm_high.observed_winner, RotationWinner.CONVENTIONAL)
        self.assertEqual(both_high.observed_winner, RotationWinner.CONVENTIONAL)
        self.assertAlmostEqual(bare.team_relative_change, -0.010917, places=5)
        self.assertAlmostEqual(rapi_high.team_relative_change, 0.000269, places=5)

    def test_main_share_and_break_even_move_with_ol_distribution(self) -> None:
        bare = self.results["all_bare"].overall
        rapi_high = self.results["rapi_high"].overall
        helm_high = self.results["helm_high"].overall

        self.assertLess(bare.conventional_main_share, bare.break_even_main_share_c)
        self.assertGreater(
            rapi_high.conventional_main_share,
            rapi_high.break_even_main_share_c,
        )
        self.assertLess(
            helm_high.conventional_main_share,
            helm_high.break_even_main_share_c,
        )

    def test_unbounded_extreme_profile_runs_through_the_full_engine(self) -> None:
        bare_result = self.results["all_bare"].conventional_result
        high_result = self.results["rapi_high"].conventional_result
        extreme = self.results["rapi_extreme"]
        extreme_result = extreme.conventional_result

        self.assertGreater(extreme.overall.conventional_main_share, 0.90)
        self.assertEqual(extreme.overall.observed_winner, RotationWinner.FUNNEL)

        def rapi_normal_events(result) -> int:
            return len(
                result.damage_events_for(
                    actor="rapi-red-hood",
                    category=DamageCategory.NORMAL,
                )
            )

        self.assertGreater(rapi_normal_events(high_result), rapi_normal_events(bare_result))
        self.assertGreater(rapi_normal_events(extreme_result), rapi_normal_events(high_result))

    def test_all_cases_keep_the_same_engine_rule_revision(self) -> None:
        signatures = {
            comparison.conventional_result.mechanics_signature
            for comparison in self.results.values()
        }
        self.assertEqual(len(signatures), 1)


if __name__ == "__main__":
    unittest.main()
