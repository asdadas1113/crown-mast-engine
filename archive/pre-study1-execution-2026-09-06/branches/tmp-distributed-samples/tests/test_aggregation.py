import math
import unittest

from crown_mast_engine.models import DamageCategory
from tests.simulation_fixtures import standard_rotation_results


class DamageAggregationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = standard_rotation_results()

    def assertDamageEqual(self, left: float, right: float) -> None:
        self.assertTrue(
            math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-6),
            f"damage totals differ: {left} != {right}",
        )

    def test_team_total_equals_character_totals(self) -> None:
        for result in self.results:
            with self.subTest(policy=result.policy_name):
                self.assertDamageEqual(
                    result.damage_total(),
                    sum(result.damage_by_character.values()),
                )

    def test_team_total_equals_damage_category_totals(self) -> None:
        for result in self.results:
            with self.subTest(policy=result.policy_name):
                category_total = sum(
                    sum(
                        event.damage
                        for event in result.damage_events_for(category=category)
                    )
                    for category in DamageCategory
                )
                self.assertDamageEqual(result.damage_total(), category_total)

    def test_team_total_equals_four_macro_cycle_totals(self) -> None:
        for result in self.results:
            with self.subTest(policy=result.policy_name):
                macro_total = sum(
                    sum(
                        event.damage
                        for event in result.damage_events_for(macro_cycle=macro_cycle)
                    )
                    for macro_cycle in range(1, 5)
                )
                self.assertDamageEqual(result.damage_total(), macro_total)

    def test_character_total_equals_its_category_totals(self) -> None:
        for result in self.results:
            for actor in result.roster.members:
                with self.subTest(policy=result.policy_name, actor=actor):
                    category_total = sum(
                        sum(
                            event.damage
                            for event in result.damage_events_for(
                                actor=actor,
                                category=category,
                            )
                        )
                        for category in DamageCategory
                    )
                    self.assertDamageEqual(result.damage_total(actor), category_total)


if __name__ == "__main__":
    unittest.main()
