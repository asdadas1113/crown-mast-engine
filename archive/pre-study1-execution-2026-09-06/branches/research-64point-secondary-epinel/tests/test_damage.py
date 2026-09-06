import unittest

from crown_mast_engine.damage import DamageContext, DamageTraits, calculate_damage
from crown_mast_engine.models import DamageCategory


class DamageFormulaTests(unittest.TestCase):
    def test_sequential_damage_shares_damage_up_bucket(self) -> None:
        context = DamageContext(
            static_atk=1000,
            coefficient_pct=100,
            boss_def=0,
            attack_damage_pct=50,
            sequential_damage_pct=25,
        )
        sequential = calculate_damage(
            context,
            DamageTraits(category=DamageCategory.SKILL, sequential=True),
        )
        ordinary = calculate_damage(
            context,
            DamageTraits(category=DamageCategory.SKILL),
        )
        self.assertEqual(sequential.damage_up, 1.75)
        self.assertEqual(ordinary.damage_up, 1.5)

    def test_boss_def_is_subtracted_before_multipliers(self) -> None:
        result = calculate_damage(
            DamageContext(static_atk=1_000, boss_def=100, coefficient_pct=200),
            DamageTraits(category=DamageCategory.SKILL),
        )
        self.assertEqual(result.base_atk, 900)
        self.assertEqual(result.total, 1_800)

    def test_projectile_terms_share_damage_up_bucket(self) -> None:
        result = calculate_damage(
            DamageContext(
                static_atk=1_000,
                boss_def=0,
                coefficient_pct=100,
                attack_damage_pct=20,
                projectile_attachment_pct=150,
                projectile_explosion_pct=100,
            ),
            DamageTraits(
                category=DamageCategory.SKILL,
                projectile_attachment=True,
                projectile_explosion=True,
            ),
        )
        self.assertAlmostEqual(result.damage_up, 3.7)
        self.assertAlmostEqual(result.total, 3_700)

    def test_distributed_buff_only_applies_to_distributed_damage(self) -> None:
        context = DamageContext(
            static_atk=1_000,
            boss_def=0,
            coefficient_pct=100,
            ally_distributed_damage_pct=45.09,
        )
        normal = calculate_damage(context, DamageTraits(category=DamageCategory.SKILL))
        distributed = calculate_damage(
            context,
            DamageTraits(category=DamageCategory.SKILL, distributed=True),
        )
        self.assertEqual(normal.distributed, 1)
        self.assertAlmostEqual(distributed.distributed, 1.4509)
        self.assertAlmostEqual(distributed.total / normal.total, 1.4509)

    def test_boss_distributed_taken_requires_damage_taken_in_runtime_profile(self) -> None:
        traits = DamageTraits(category=DamageCategory.SKILL, distributed=True)
        without_taken = calculate_damage(
            DamageContext(
                static_atk=1_000,
                coefficient_pct=100,
                boss_def=0,
                boss_distributed_taken_pct=30,
            ),
            traits,
        )
        with_taken = calculate_damage(
            DamageContext(
                static_atk=1_000,
                coefficient_pct=100,
                boss_def=0,
                boss_damage_taken_pct=5,
                boss_distributed_taken_pct=30,
            ),
            traits,
        )
        self.assertEqual(without_taken.taken, 1)
        self.assertAlmostEqual(with_taken.taken, 1.35)


if __name__ == "__main__":
    unittest.main()
