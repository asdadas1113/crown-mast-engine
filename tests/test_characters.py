import unittest

from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from crown_mast_engine.engine import simulate_rotation
from crown_mast_engine.equipment import BuildProfile, GearState, OverloadProfile
from crown_mast_engine.rotations import CROWN_CROWN_MAST
from tests.simulation_fixtures import (
    standard_conventional_result,
    standard_funnel_result,
)


class CharacterCatalogTests(unittest.TestCase):
    def test_standard_scope_is_pinned(self) -> None:
        scope = STANDARD_CHARACTER_CATALOG.scope
        self.assertEqual(scope.level, 400)
        self.assertEqual(scope.gear, "Base-5")
        self.assertEqual(scope.core, 7)
        self.assertEqual(scope.skill_levels, (10, 10, 10))
        self.assertIn("43308bd02276a476660e44af730785c2ae91eea3", scope.source_revision)

    def test_crown_and_mast_standard_stats(self) -> None:
        crown = STANDARD_CHARACTER_CATALOG.require("crown")
        mast = STANDARD_CHARACTER_CATALOG.require("mast-romantic-maid")
        self.assertEqual(crown.progression_atk, 72_828)
        self.assertEqual(crown.unit_class, "Defender")
        self.assertEqual(mast.progression_atk, 91_018)
        self.assertEqual(mast.unit_class, "Supporter")
        self.assertEqual(crown.weapon.normal_attack_pct, 5.57)
        self.assertEqual(mast.weapon.normal_attack_pct, 5.57)
        self.assertEqual(
            crown.skill_value("skill2", "relax_hits_per_stack"),
            43,
        )
        self.assertEqual(
            crown.skill_value("skill2", "max_relax_stacks"),
            20,
        )
        self.assertEqual(
            crown.skill_value("skill2", "heal_received_per_stack_pct"),
            4.06,
        )
        self.assertEqual(
            crown.skill_value("skill2", "self_recovery_max_hp_pct"),
            5.23,
        )
        self.assertEqual(
            mast.skill_value("skill1", "hit_rate_down_per_stack_pct"),
            20,
        )
        self.assertEqual(
            mast.skill_value(
                "skill1",
                "expected_normal_damage_loss_per_stack_pct",
            ),
            0,
        )

        result = standard_conventional_result()
        self.assertEqual(result.static_atk("crown"), 78_707)
        self.assertEqual(result.static_atk("mast-romantic-maid"), 98_367)

    def test_skill_value_variant_does_not_mutate_source_catalog(self) -> None:
        variant = STANDARD_CHARACTER_CATALOG.with_skill_value(
            "mast-romantic-maid",
            "skill1",
            "expected_normal_damage_loss_per_stack_pct",
            18,
        )
        self.assertEqual(
            variant.require("mast-romantic-maid").skill_value(
                "skill1",
                "expected_normal_damage_loss_per_stack_pct",
            ),
            18,
        )
        self.assertEqual(
            STANDARD_CHARACTER_CATALOG.require("mast-romantic-maid").skill_value(
                "skill1",
                "expected_normal_damage_loss_per_stack_pct",
            ),
            0,
        )

    def test_skill_value_variant_revision_records_override_and_catalog_hash(self) -> None:
        standard_revision = STANDARD_CHARACTER_CATALOG.scope.source_revision
        first = STANDARD_CHARACTER_CATALOG.with_skill_value(
            "mast-romantic-maid",
            "skill1",
            "expected_normal_damage_loss_per_stack_pct",
            18,
        )
        second = STANDARD_CHARACTER_CATALOG.with_skill_value(
            "mast-romantic-maid",
            "skill1",
            "expected_normal_damage_loss_per_stack_pct",
            18,
        )

        self.assertIn("catalog-sha256:", standard_revision)
        self.assertNotEqual(first.scope.source_revision, standard_revision)
        self.assertEqual(first.scope.source_revision, second.scope.source_revision)
        self.assertIn(
            "skill-override:mast-romantic-maid.skill1.expected_normal_damage_loss_per_stack_pct=18",
            first.scope.source_revision,
        )

    def test_rapi_red_hood_standard_stats(self) -> None:
        rapi = STANDARD_CHARACTER_CATALOG.require("rapi-red-hood")
        self.assertEqual(rapi.progression_atk, 109_209)
        self.assertEqual(rapi.unit_class, "Attacker")
        self.assertEqual(rapi.burst_stage, "III")
        self.assertEqual(rapi.element, "Fire")
        self.assertEqual(rapi.extra_advantage_against, ("Electric",))
        self.assertEqual(rapi.weapon.weapon_type, "MG")
        self.assertEqual(rapi.weapon.normal_attack_pct, 5.57)
        result = standard_conventional_result()
        self.assertEqual(result.static_atk("rapi-red-hood"), 118_027)

    def test_scarlet_black_shadow_standard_stats(self) -> None:
        scarlet = STANDARD_CHARACTER_CATALOG.require("scarlet-black-shadow")
        self.assertEqual(scarlet.progression_atk, 109_209)
        self.assertEqual(scarlet.unit_class, "Attacker")
        self.assertEqual(scarlet.burst_stage, "III")
        self.assertEqual(scarlet.weapon.weapon_type, "RL")
        self.assertEqual(scarlet.weapon.normal_attack_pct, 57.29)
        self.assertEqual(scarlet.weapon.ammo, 9)
        self.assertEqual(scarlet.weapon.reload_frames, 152)
        self.assertEqual(scarlet.weapon.charge_frames, 18)
        self.assertEqual(scarlet.weapon.charge_multiplier_pct, 150)
        self.assertEqual(scarlet.weapon.charge_release_recovery_frames, 26)

    def test_snow_white_heavy_arms_standard_stats(self) -> None:
        snow = STANDARD_CHARACTER_CATALOG.require("snow-white-heavy-arms")
        self.assertEqual(snow.progression_atk, 109_209)
        self.assertEqual(snow.unit_class, "Attacker")
        self.assertEqual(snow.burst_stage, "III")
        self.assertEqual(snow.element, "Water")
        self.assertEqual(snow.weapon.weapon_type, "SR")
        self.assertEqual(snow.weapon.normal_attack_pct, 69.04)
        self.assertEqual(snow.weapon.ammo, 6)
        self.assertEqual(snow.weapon.reload_frames, 120)
        self.assertEqual(snow.weapon.charge_frames, 72)
        self.assertEqual(snow.weapon.charge_multiplier_pct, 250)
        self.assertEqual(
            snow.skill_value("skill1", "auto_fire_sequential_damage_pct"),
            527.95,
        )

    def test_epinel_standard_stats(self) -> None:
        epinel = STANDARD_CHARACTER_CATALOG.require("epinel")
        self.assertEqual(epinel.progression_atk, 109_209)
        self.assertEqual(epinel.unit_class, "Attacker")
        self.assertEqual(epinel.burst_stage, "III")
        self.assertEqual(epinel.element, "Wind")
        self.assertEqual(epinel.weapon.weapon_type, "SMG")
        self.assertEqual(epinel.weapon.normal_attack_pct, 10.12)
        self.assertEqual(epinel.weapon.core_attack_pct, 250)
        self.assertEqual(epinel.weapon.ammo, 120)
        self.assertEqual(epinel.weapon.reload_frames, 60)
        self.assertEqual(epinel.skill_value("skill2", "crit_rate_pct"), 5.05)
        self.assertEqual(epinel.skill_value("burst", "damage_pct"), 457.87)

    def test_neon_vision_eye_standard_stats(self) -> None:
        neon = STANDARD_CHARACTER_CATALOG.require("neon-vision-eye")
        self.assertEqual(neon.progression_atk, 109_209)
        self.assertEqual(neon.unit_class, "Attacker")
        self.assertEqual(neon.burst_stage, "III")
        self.assertEqual(neon.element, "Electric")
        self.assertEqual(neon.weapon.weapon_type, "RL")
        self.assertEqual(neon.weapon.normal_attack_pct, 61.3)
        self.assertEqual(neon.weapon.ammo, 6)
        self.assertEqual(neon.weapon.reload_frames, 120)
        self.assertEqual(neon.weapon.charge_frames, 60)
        self.assertEqual(neon.weapon.charge_multiplier_pct, 250)
        self.assertEqual(neon.weapon.burst_gauge_per_shot, 1.5)
        self.assertEqual(neon.weapon.charge_release_recovery_frames, 0)
        self.assertEqual(
            neon.skill_value("skill1", "firepower_explosion_damage_pct"),
            437.98,
        )

    def test_helm_standard_stats(self) -> None:
        helm = STANDARD_CHARACTER_CATALOG.require("helm")
        self.assertEqual(helm.progression_atk, 109_209)
        self.assertEqual(helm.unit_class, "Attacker")
        self.assertEqual(helm.burst_stage, "III")
        self.assertEqual(helm.weapon.weapon_type, "SR")
        self.assertEqual(helm.weapon.normal_attack_pct, 69.04)
        self.assertEqual(helm.weapon.charge_multiplier_pct, 250)
        result = standard_conventional_result()
        self.assertEqual(result.static_atk("helm"), 127_715)

    def test_liter_standard_stats(self) -> None:
        liter = STANDARD_CHARACTER_CATALOG.require("liter")
        self.assertEqual(liter.progression_atk, 91_018)
        self.assertEqual(liter.unit_class, "Supporter")
        self.assertEqual(liter.burst_stage, "I")
        self.assertEqual(liter.weapon.weapon_type, "SMG")
        self.assertEqual(liter.weapon.normal_attack_pct, 8.73)
        result = standard_conventional_result()
        self.assertEqual(result.static_atk("liter"), 98_367)

    def test_caster_atk_percent_resolves_from_caster_static_atk(self) -> None:
        result = standard_conventional_result()
        main = result.roster.main_b3
        secondary = result.roster.secondary_b3

        main_buffs = result.resolved_offensive_buffs(6.0, main)
        secondary_buffs = result.resolved_offensive_buffs(6.0, secondary)

        crown_flat = 78_707 * 0.6451
        mast_flat = 98_367 * 0.3502
        self.assertAlmostEqual(main_buffs.caster_atk_flat, crown_flat + mast_flat)
        self.assertAlmostEqual(secondary_buffs.caster_atk_flat, mast_flat)

    def test_two_stack_mast_burst_uses_mast_static_atk(self) -> None:
        result = standard_funnel_result()
        main = result.roster.main_b3
        buffs = result.resolved_offensive_buffs(62.3, main)
        expected = 98_367 * (0.3502 + 0.4012)
        self.assertAlmostEqual(buffs.caster_atk_flat, expected)

    def test_ol5_gear_changes_caster_atk_flat_from_resolved_static_atk(self) -> None:
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            builds={"crown": BuildProfile.uniform(GearState.OL5)},
        )
        expected_static = 72_828 + 10_935
        self.assertEqual(result.static_atk("crown"), expected_static)

        main_buffs = result.resolved_offensive_buffs(6.0, result.roster.main_b3)
        expected = expected_static * 0.6451 + 98_367 * 0.3502
        self.assertAlmostEqual(main_buffs.caster_atk_flat, expected)

    def test_caster_atk_flat_does_not_include_caster_overload_atk_lines(self) -> None:
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            builds={
                "crown": BuildProfile.uniform(
                    GearState.OL5,
                    OverloadProfile(atk_lines=100),
                ),
            },
        )
        expected_static = 72_828 + 10_935
        main_buffs = result.resolved_offensive_buffs(6.0, result.roster.main_b3)
        expected = expected_static * 0.6451 + 98_367 * 0.3502
        self.assertAlmostEqual(main_buffs.caster_atk_flat, expected)


if __name__ == "__main__":
    unittest.main()
