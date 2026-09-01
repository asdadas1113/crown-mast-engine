import unittest

from crown_mast_engine.equipment import (
    BARE_OL0_BUILD,
    BARE_OL5_BUILD,
    HIGH_OL5_BUILD,
    BuildProfile,
    CollectionProfile,
    EquipmentLoadout,
    GearState,
    OverloadProfile,
    SR15_COLLECTION,
)


class EquipmentTests(unittest.TestCase):
    def test_collection_stage_resolves_flat_atk_and_weapon_effect_level(self) -> None:
        self.assertEqual(CollectionProfile("R0").flat_atk, 638)
        self.assertEqual(SR15_COLLECTION.flat_atk, 9688)
        self.assertEqual(SR15_COLLECTION.skill_level, 4)
        self.assertEqual(
            SR15_COLLECTION.weapon_effect("SR"),
            ("charge_damage_mult_pct", 9.47),
        )

    def test_collection_stage_rejects_unknown_grade_or_level(self) -> None:
        for stage in ("SSR15", "R16", "SR-1", "unknown"):
            with self.subTest(stage=stage):
                with self.assertRaises(ValueError):
                    CollectionProfile(stage)

    def test_uniform_gear_totals_match_pinned_nikke_sim(self) -> None:
        expected = {
            "Defender": {GearState.BASE5: 5_879, GearState.OL0: 7_290, GearState.OL5: 10_935},
            "Attacker": {GearState.BASE5: 8_818, GearState.OL0: 10_934, GearState.OL5: 16_401},
            "Supporter": {GearState.BASE5: 7_349, GearState.OL0: 9_112, GearState.OL5: 13_668},
        }
        for unit_class, states in expected.items():
            for state, total in states.items():
                with self.subTest(unit_class=unit_class, state=state):
                    build = BuildProfile.uniform(state)
                    self.assertEqual(build.equipment.gear_atk(unit_class), total)

    def test_mixed_piece_states_are_resolved_per_slot(self) -> None:
        loadout = EquipmentLoadout.from_states(
            GearState.OL5,
            GearState.OL0,
            GearState.BASE5,
            GearState.OL5,
        )
        self.assertEqual(loadout.gear_atk("Attacker"), 9_021 + 3_827 + 882)

    def test_tier_11_overload_lines_are_independent_from_gear_state(self) -> None:
        overload = OverloadProfile(atk_lines=4, element_lines=4, ammo_lines=3)
        ol0 = BuildProfile.uniform(GearState.OL0, overload)
        ol5 = BuildProfile.uniform(GearState.OL5, overload)

        self.assertEqual(ol0.overload, ol5.overload)
        self.assertAlmostEqual(overload.atk_pct, 47.24)
        self.assertAlmostEqual(overload.element_pct, 94.24)
        self.assertAlmostEqual(overload.ammo_pct, 206.79)

    def test_overload_line_counts_have_no_research_upper_bound(self) -> None:
        overload = OverloadProfile(atk_lines=10, element_lines=20, ammo_lines=100)
        self.assertAlmostEqual(overload.atk_pct, 118.1)
        self.assertAlmostEqual(overload.element_pct, 471.2)
        self.assertAlmostEqual(overload.ammo_pct, 6_893)

    def test_overload_line_counts_must_be_non_negative_integers(self) -> None:
        with self.assertRaises(ValueError):
            OverloadProfile(atk_lines=-1)
        with self.assertRaises(TypeError):
            OverloadProfile(ammo_lines=1.5)  # type: ignore[arg-type]

    def test_standard_research_presets_keep_gear_and_options_explicit(self) -> None:
        self.assertEqual(BARE_OL0_BUILD.equipment, EquipmentLoadout.uniform(GearState.OL0))
        self.assertEqual(BARE_OL5_BUILD.equipment, EquipmentLoadout.uniform(GearState.OL5))
        self.assertEqual(BARE_OL0_BUILD.overload, OverloadProfile())
        self.assertEqual(BARE_OL5_BUILD.overload, OverloadProfile())
        self.assertEqual(
            HIGH_OL5_BUILD.overload,
            OverloadProfile(atk_lines=4, element_lines=4, ammo_lines=3),
        )


if __name__ == "__main__":
    unittest.main()
