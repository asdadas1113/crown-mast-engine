import unittest

from crown_mast_engine import simulate_rotation
from crown_mast_engine.combat import FPS
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


LIBERALIO_ROSTER = TeamRoster(main_b3="liberalio")


class LiberalioMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(CROWN_CROWN_MAST, roster=LIBERALIO_ROSTER)
        cls.actor = "liberalio"

    def test_standard_data_matches_pinned_liberalio_datamine(self) -> None:
        liberalio = self.result.catalog.require(self.actor)
        self.assertEqual(liberalio.progression_atk, 109_209)
        self.assertEqual(liberalio.unit_class, "Attacker")
        self.assertEqual(liberalio.burst_stage, "III")
        self.assertEqual(liberalio.element, "Wind")
        self.assertEqual(liberalio.weapon.weapon_type, "SR")
        self.assertEqual(liberalio.weapon.normal_attack_pct, 69.04)
        self.assertEqual(liberalio.weapon.core_attack_pct, 200)
        self.assertEqual(liberalio.weapon.ammo, 6)
        self.assertEqual(liberalio.weapon.reload_frames, 141)
        self.assertEqual(liberalio.weapon.charge_frames, 90)
        self.assertEqual(liberalio.weapon.charge_multiplier_pct, 250)
        self.assertEqual(liberalio.weapon.burst_gauge_per_shot, 2.8)
        self.assertEqual(liberalio.weapon.charge_release_recovery_frames, 0)

    def test_full_burst_buffs_self_and_the_other_b3_only(self) -> None:
        first_fb = next(
            event.time
            for event in self.result.events
            if event.event_type == EventType.FULL_BURST_ENTER
        )
        self_atk = next(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "skill1_full_burst"
            and window.stat == "atk_pct"
            and window.start == first_fb
        )
        other_b3_charge = next(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "skill1_other_b3_charge_speed"
            and window.stat == "charge_speed_pct"
            and window.start == first_fb
        )
        self.assertEqual(self_atk.target, self.actor)
        self.assertEqual(self_atk.value, 160)
        self.assertAlmostEqual(self_atk.end - self_atk.start, 3)
        self.assertEqual(other_b3_charge.target, LIBERALIO_ROSTER.secondary_b3)
        self.assertEqual(other_b3_charge.value, 12.74)
        self.assertAlmostEqual(other_b3_charge.end - other_b3_charge.start, 10)
        self.assertFalse(
            any(
                window.source == self.actor
                and window.skill == "skill1_other_b3_charge_speed"
                and window.target == self.actor
                for window in self.result.buffs.windows
            )
        )

    def test_raging_current_is_earned_after_the_first_full_charge(self) -> None:
        first_normal = self.result.damage_events_for(
            actor=self.actor,
            category=DamageCategory.NORMAL,
        )[0]
        windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "skill2_raging_current"
            and window.stat == "attack_damage_pct"
        )
        self.assertTrue(windows)
        expected_start = round(first_normal.time + 1 / FPS, 6)
        self.assertEqual(windows[0].start, expected_start)
        self.assertEqual(windows[0].value, 231)
        self.assertFalse(windows[0].active_at(first_normal.time))
        self.assertTrue(windows[0].active_at(expected_start + 0.001))

    def test_every_full_charge_emits_five_hit_aggregate_rider(self) -> None:
        normals = self.result.damage_events_for(
            actor=self.actor,
            category=DamageCategory.NORMAL,
        )
        riders = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.SKILL,
            )
            if event.source == "skill1_full_charge_additional"
        )
        self.assertTrue(normals)
        self.assertEqual(
            {event.shot_index for event in riders},
            {event.shot_index for event in normals},
        )
        self.assertTrue(all(event.coefficient_pct == 202.5 for event in riders))
        self.assertTrue(all(not event.traits.core_eligible for event in riders))
        self.assertTrue(all(not event.traits.range_eligible for event in riders))

    def test_burst_packet_lands_after_delay_and_uses_full_burst(self) -> None:
        burst_times = tuple(
            event.time
            for event in self.result.events
            if event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == self.actor
        )
        nukes = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.BURST,
            )
            if event.source == "burst_nuke"
        )
        expected_nuke_times = tuple(round(time + 1.1, 6) for time in burst_times)
        self.assertEqual(tuple(event.time for event in nukes), expected_nuke_times)
        self.assertTrue(all(event.coefficient_pct == 925 for event in nukes))
        self.assertTrue(all(event.full_burst for event in nukes))

        buffs = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "burst"
            and window.stat == "attack_damage_pct"
        )
        self.assertEqual(tuple(window.start for window in buffs), burst_times)
        self.assertTrue(all(window.value == 50 for window in buffs))
        for window in buffs:
            self.assertAlmostEqual(window.end - window.start, 10)


if __name__ == "__main__":
    unittest.main()
