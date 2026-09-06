import unittest
from collections import Counter

from crown_mast_engine import simulate_rotation
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


RAVEN_ROSTER = TeamRoster(main_b3="raven")


class RavenMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(CROWN_CROWN_MAST, roster=RAVEN_ROSTER)
        cls.actor = "raven"

    def test_standard_data_matches_pinned_raven_datamine(self) -> None:
        raven = self.result.catalog.require(self.actor)
        self.assertEqual(raven.progression_atk, 109_209)
        self.assertEqual(raven.unit_class, "Attacker")
        self.assertEqual(raven.burst_stage, "III")
        self.assertEqual(raven.element, "Iron")
        self.assertEqual(raven.weapon.weapon_type, "RL")
        self.assertEqual(raven.weapon.normal_attack_pct, 61.3)
        self.assertEqual(raven.weapon.core_attack_pct, 200)
        self.assertEqual(raven.weapon.ammo, 6)
        self.assertEqual(raven.weapon.reload_frames, 141)
        self.assertEqual(raven.weapon.charge_frames, 60)
        self.assertEqual(raven.weapon.charge_multiplier_pct, 250)
        self.assertEqual(raven.weapon.burst_gauge_per_shot, 1.4)
        self.assertEqual(raven.weapon.charge_release_recovery_frames, 22)

    def test_full_burst_caster_atk_buff_fires_on_every_team_full_burst(self) -> None:
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
            and window.stat == "caster_atk_pct"
        )
        self.assertEqual(tuple(window.start for window in windows), full_burst_starts)
        self.assertTrue(windows)
        self.assertTrue(all(window.target == self.actor for window in windows))
        self.assertTrue(all(window.caster == self.actor for window in windows))
        self.assertTrue(all(window.value == 47.52 for window in windows))
        for window in windows:
            self.assertAlmostEqual(window.end - window.start, 10)

    def test_full_charge_appends_independent_five_tick_sustained_instances(self) -> None:
        normals = self.result.damage_events_for(
            actor=self.actor,
            category=DamageCategory.NORMAL,
        )
        dots = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.SKILL,
            )
            if event.source == "skill1_sustained_dot"
        )
        self.assertTrue(normals)
        self.assertTrue(dots)
        ticks_by_shot = Counter(event.shot_index for event in dots)
        normal_by_shot = {event.shot_index: event for event in normals}

        first_shot = normals[0]
        first_ticks = tuple(
            event for event in dots if event.shot_index == first_shot.shot_index
        )
        self.assertEqual(len(first_ticks), 5)
        self.assertEqual(
            tuple(round(event.time - first_shot.time, 6) for event in first_ticks),
            (1.0, 2.0, 3.0, 4.0, 5.0),
        )

        self.assertGreaterEqual(len(dots), 4 * len(normals))
        self.assertLessEqual(max(ticks_by_shot.values()), 5)
        self.assertTrue(set(ticks_by_shot).issubset(normal_by_shot))
        self.assertTrue(all(event.coefficient_pct == 68.46 for event in dots))
        self.assertTrue(all(event.traits.sustained for event in dots))
        self.assertTrue(all(not event.traits.core_eligible for event in dots))
        self.assertTrue(all(not event.traits.range_eligible for event in dots))
        self.assertTrue(all(event.traits.crit_eligible for event in dots))
        self.assertTrue(all(event.traits.full_burst_eligible for event in dots))

    def test_burst_packet_lands_before_full_burst_and_an_mode_is_sustained_only(self) -> None:
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
        self.assertEqual(tuple(event.time for event in nukes), burst_times)
        self.assertTrue(all(event.coefficient_pct == 492.3 for event in nukes))
        self.assertTrue(all(not event.full_burst for event in nukes))

        windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "burst_an_mode"
            and window.stat == "sustained_damage_pct"
        )
        self.assertEqual(tuple(window.start for window in windows), burst_times)
        self.assertTrue(all(window.target == self.actor for window in windows))
        self.assertTrue(all(window.value == 89.44 for window in windows))
        for window in windows:
            self.assertAlmostEqual(window.end - window.start, 10)

    def test_an_mode_bonus_reaches_sustained_ticks_but_not_normal_trait(self) -> None:
        an_window = next(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "burst_an_mode"
        )
        dot = next(
            event
            for event in self.result.damage_events_for(actor=self.actor)
            if event.source == "skill1_sustained_dot"
            and an_window.active_at(event.time)
        )
        normal = next(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.NORMAL,
            )
            if an_window.active_at(event.time)
        )
        self.assertTrue(dot.traits.sustained)
        self.assertFalse(normal.traits.sustained)
        self.assertGreaterEqual(dot.breakdown.damage_up, 1 + 89.44 / 100)


if __name__ == "__main__":
    unittest.main()
