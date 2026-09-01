import unittest

from crown_mast_engine import simulate_rotation
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


BREADY_ROSTER = TeamRoster(main_b3="bready")


class BreadyMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(CROWN_CROWN_MAST, roster=BREADY_ROSTER)
        cls.actor = "bready"
        cls.first_taste_event = next(
            event
            for event in cls.result.events
            if event.event_type == EventType.B3_STAGE_ENTER
            and int(event.payload.get("mast_stacks", 0)) > 0
        )

    def test_standard_data_matches_pinned_bready_datamine(self) -> None:
        bready = self.result.catalog.require(self.actor)
        self.assertEqual(bready.progression_atk, 109_209)
        self.assertEqual(bready.unit_class, "Attacker")
        self.assertEqual(bready.burst_stage, "III")
        self.assertEqual(bready.element, "Water")
        self.assertEqual(bready.weapon.weapon_type, "SR")
        self.assertEqual(bready.weapon.normal_attack_pct, 69.04)
        self.assertEqual(bready.weapon.core_attack_pct, 200)
        self.assertEqual(bready.weapon.ammo, 6)
        self.assertEqual(bready.weapon.reload_frames, 141)
        self.assertEqual(bready.weapon.charge_frames, 60)
        self.assertEqual(bready.weapon.charge_multiplier_pct, 250)
        self.assertEqual(bready.weapon.burst_gauge_per_shot, 2.8)
        self.assertEqual(bready.weapon.charge_release_recovery_frames, 22)

    def test_mast_distributed_buff_auto_enters_recommended_taste(self) -> None:
        start = self.first_taste_event.time
        self.assertEqual(
            self.result.buff_total(start - 0.001, self.actor, "charge_speed_pct"),
            0,
        )
        self.assertEqual(
            self.result.buff_total(start + 0.001, self.actor, "charge_speed_pct"),
            -20,
        )
        taste_windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "skill1_recommended_taste"
            and window.stat == "charge_speed_pct"
        )
        self.assertTrue(taste_windows)
        self.assertEqual(taste_windows[0].start, start)
        self.assertEqual(taste_windows[0].value, -20)

    def test_full_burst_entry_applies_unconditional_self_atk(self) -> None:
        full_burst_starts = tuple(
            event.time
            for event in self.result.events
            if event.event_type == EventType.FULL_BURST_ENTER
        )
        windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "skill1_full_burst"
            and window.stat == "atk_pct"
        )
        self.assertEqual(tuple(window.start for window in windows), full_burst_starts)
        self.assertTrue(windows)
        self.assertTrue(all(window.value == 70.01 for window in windows))
        for window in windows:
            self.assertAlmostEqual(window.end - window.start, 10)

    def test_own_burst_gets_unconditional_and_recommended_buffs(self) -> None:
        burst_time = next(
            event.time
            for event in self.result.events
            if event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == self.actor
        )
        burst_attack = next(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "burst"
            and window.stat == "attack_damage_pct"
            and window.start == burst_time
        )
        burst_recommended = next(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "burst_recommended_taste"
            and window.stat == "atk_pct"
            and window.start == burst_time
        )
        self.assertEqual(burst_attack.value, 60.19)
        self.assertEqual(burst_recommended.value, 70.09)
        self.assertAlmostEqual(burst_attack.end - burst_attack.start, 10)
        self.assertAlmostEqual(
            burst_recommended.end - burst_recommended.start,
            10,
        )

    def test_every_recommended_full_charge_emits_distributed_rider(self) -> None:
        start = self.first_taste_event.time
        normals = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.NORMAL,
            )
            if event.time >= start
        )
        riders = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.SKILL,
            )
            if event.source == "skill2_recommended_distributed"
        )
        self.assertTrue(normals)
        self.assertEqual(
            {event.shot_index for event in riders},
            {event.shot_index for event in normals},
        )
        self.assertTrue(all(event.coefficient_pct == 265.07 for event in riders))
        self.assertTrue(all(event.traits.distributed for event in riders))
        self.assertTrue(all(not event.traits.core_eligible for event in riders))
        self.assertTrue(all(not event.traits.range_eligible for event in riders))

    def test_recommended_full_charge_refreshes_attack_damage_buff(self) -> None:
        riders = tuple(
            event
            for event in self.result.damage_events_for(actor=self.actor)
            if event.source == "skill2_recommended_distributed"
        )
        windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "skill2_recommended_taste"
            and window.stat == "attack_damage_pct"
        )
        self.assertEqual(len(windows), len(riders))
        self.assertTrue(all(window.value == 60.01 for window in windows))
        self.assertEqual(
            tuple(window.start for window in windows),
            tuple(event.time for event in riders),
        )
        for current, following in zip(windows, windows[1:]):
            self.assertEqual(current.end, following.start)
        self.assertAlmostEqual(windows[-1].end - windows[-1].start, 5)

    def test_mast_distributed_amp_applies_to_recommended_rider(self) -> None:
        first_rider = next(
            event
            for event in self.result.damage_events_for(actor=self.actor)
            if event.source == "skill2_recommended_distributed"
            and event.time >= self.first_taste_event.time
        )
        self.assertGreater(first_rider.breakdown.distributed, 1)


if __name__ == "__main__":
    unittest.main()
