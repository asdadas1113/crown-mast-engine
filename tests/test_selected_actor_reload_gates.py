import unittest

from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from crown_mast_engine.combat import (
    effective_reload_frames,
    effective_weapon_reload_frames,
    generate_weapon_shots,
)


class SelectedActorReloadGateTests(unittest.TestCase):
    def test_moran_favorite_item_uses_current_one_second_raw_reload_body(self) -> None:
        weapon = STANDARD_CHARACTER_CATALOG.require("moran-favorite-item").weapon
        self.assertEqual(weapon.reload_frames, 60)
        self.assertEqual(weapon.reload_start_delay_frames, 0)

    def test_liberalio_separates_two_second_body_from_fixed_start_delay(self) -> None:
        weapon = STANDARD_CHARACTER_CATALOG.require("liberalio").weapon
        self.assertEqual(weapon.reload_frames, 120)
        self.assertEqual(weapon.reload_start_delay_frames, 12)

        for reload_speed_pct in (0.0, 44.35, 89.47):
            with self.subTest(reload_speed_pct=reload_speed_pct):
                self.assertEqual(
                    effective_weapon_reload_frames(weapon, reload_speed_pct),
                    effective_reload_frames(120, reload_speed_pct) + 12,
                )

    def test_liberalio_fixed_start_delay_is_present_in_generated_cadence(self) -> None:
        weapon = STANDARD_CHARACTER_CATALOG.require("liberalio").weapon
        for reload_speed_pct in (0.0, 50.0):
            with self.subTest(reload_speed_pct=reload_speed_pct):
                shots = generate_weapon_shots(
                    actor="liberalio",
                    weapon=weapon,
                    duration_sec=20.0,
                    reload_speed_at=lambda _time, speed=reload_speed_pct: speed,
                    startup_delay_frames=0,
                )
                first_mag = [shot for shot in shots if shot.magazine_index == 0]
                second_mag = [shot for shot in shots if shot.magazine_index == 1]
                self.assertEqual(len(first_mag), weapon.ammo)
                self.assertTrue(second_mag)
                last_first = first_mag[-1]
                first_second = second_mag[0]
                expected_gap_frames = (
                    effective_weapon_reload_frames(weapon, reload_speed_pct)
                    + weapon.charge_frames
                )
                self.assertEqual(
                    first_second.frame - last_first.frame,
                    expected_gap_frames,
                )

    def test_sbs_measured_reload_and_attack_cycle_are_decomposed(self) -> None:
        weapon = STANDARD_CHARACTER_CATALOG.require("scarlet-black-shadow").weapon
        self.assertEqual(weapon.reload_frames, 120)
        self.assertEqual(weapon.reload_start_delay_frames, 12)
        self.assertEqual(weapon.charge_frames, 18)
        self.assertEqual(weapon.charge_release_recovery_frames, 26)

        # 120 raw frames resolve to 130 frames under the shared reload formula;
        # the actor-specific fixed start delay makes the measured reload 142f,
        # or 2.3667s, matching the ~2.36s direct measurement.
        self.assertEqual(effective_weapon_reload_frames(weapon, 0.0), 142)
        self.assertAlmostEqual(effective_weapon_reload_frames(weapon, 0.0) / 60, 2.3666666667)

        # Outside reloads, 18f charge + 26f release recovery gives the measured
        # ~0.73s auto firing cycle.
        self.assertEqual(weapon.charge_frames + weapon.charge_release_recovery_frames, 44)
        self.assertAlmostEqual(44 / 60, 0.7333333333)

    def test_unmodified_weapon_has_no_new_fixed_delay(self) -> None:
        helm = STANDARD_CHARACTER_CATALOG.require("helm").weapon
        self.assertEqual(helm.reload_start_delay_frames, 0)
        self.assertEqual(
            effective_weapon_reload_frames(helm, 44.35),
            effective_reload_frames(helm.reload_frames, 44.35),
        )


if __name__ == "__main__":
    unittest.main()
