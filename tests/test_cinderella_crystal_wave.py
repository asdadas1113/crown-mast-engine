import unittest
from dataclasses import replace

from crown_mast_engine import simulate_rotation
from crown_mast_engine.combat import STANDARD_COMBAT_SETTINGS
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


CCW_ROSTER = TeamRoster(main_b3="cinderella-crystal-wave")


class CinderellaCrystalWaveMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(CROWN_CROWN_MAST, roster=CCW_ROSTER)
        cls.actor = "cinderella-crystal-wave"

    def test_standard_data_matches_pinned_mg_datamine(self) -> None:
        ccw = self.result.catalog.require(self.actor)
        self.assertEqual(ccw.progression_atk, 109_209)
        self.assertEqual(ccw.unit_class, "Attacker")
        self.assertEqual(ccw.burst_stage, "III")
        self.assertEqual(ccw.element, "Iron")
        self.assertEqual(ccw.weapon.weapon_type, "MG")
        self.assertEqual(ccw.weapon.normal_attack_pct, 5.57)
        self.assertEqual(ccw.weapon.core_attack_pct, 200)
        self.assertEqual(ccw.weapon.ammo, 300)
        self.assertEqual(ccw.weapon.reload_frames, 171)
        self.assertEqual(ccw.weapon.charge_frames, 0)
        self.assertEqual(ccw.weapon.burst_gauge_per_shot, 0.05)

    def test_mg_mode_passives_are_permanent(self) -> None:
        windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill in {
                "skill1_beauty_full",
                "skill2_passive_atk",
                "skill2_pinpoint",
            }
        )
        self.assertEqual(len(windows), 3)
        values = {(window.stat, window.value) for window in windows}
        self.assertEqual(
            values,
            {
                ("attack_damage_pct", 24.0),
                ("atk_pct", 29.0),
                ("core_damage_pct", 26.0),
            },
        )
        self.assertTrue(all(window.start == 0 for window in windows))
        self.assertEqual(
            self.result.resolved_offensive_buffs(1.0, self.actor).core_damage_pct,
            26.0,
        )

    def test_pinpoint_reaches_core_damage_major_bucket(self) -> None:
        core_result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=CCW_ROSTER,
            combat_settings=replace(STANDARD_COMBAT_SETTINGS, core_hit_rate_pct=100.0),
        )
        normal = next(
            event
            for event in core_result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.NORMAL,
            )
            if event.traits.core_eligible and not event.full_burst
        )
        # 7.5% expected crit major + 100% base core bonus + 26% Pinpoint.
        self.assertAlmostEqual(normal.breakdown.major, 2.335)

    def test_every_five_seconds_emits_900_percent_packet(self) -> None:
        packets = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.SKILL,
            )
            if event.source == "skill1_interval_damage"
        )
        expected_times = tuple(float(value) for value in range(5, 180, 5))
        self.assertEqual(tuple(event.time for event in packets), expected_times)
        self.assertTrue(all(event.coefficient_pct == 900 for event in packets))
        self.assertTrue(all(not event.traits.core_eligible for event in packets))
        self.assertTrue(all(not event.traits.range_eligible for event in packets))

    def test_mg_core_strike_only_fires_after_own_burst(self) -> None:
        own_fb_times = tuple(
            event.time
            for event in self.result.events
            if event.event_type == EventType.FULL_BURST_ENTER
            and self.actor in tuple(event.payload.get("burst_casters", ()))
        )
        riders = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.SKILL,
            )
            if event.source == "skill2_mg_full_burst_core_strike"
        )
        self.assertEqual(tuple(event.time for event in riders), own_fb_times)
        self.assertTrue(all(event.coefficient_pct == 833.79 for event in riders))
        self.assertTrue(all(event.traits.core_eligible for event in riders))
        self.assertTrue(all(not event.traits.range_eligible for event in riders))
        self.assertTrue(all(event.full_burst for event in riders))

    def test_own_burst_applies_two_self_buffs_and_6000_nuke(self) -> None:
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
        self.assertTrue(all(event.coefficient_pct == 6000 for event in nukes))
        self.assertTrue(all(not event.full_burst for event in nukes))

        burst_windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor and window.skill == "burst"
        )
        attack_damage = tuple(
            window for window in burst_windows if window.stat == "attack_damage_pct"
        )
        atk = tuple(window for window in burst_windows if window.stat == "atk_pct")
        self.assertEqual(tuple(window.start for window in attack_damage), burst_times)
        self.assertEqual(tuple(window.start for window in atk), burst_times)
        self.assertTrue(all(window.value == 92 for window in attack_damage))
        self.assertTrue(all(window.value == 65 for window in atk))
        for window in burst_windows:
            self.assertAlmostEqual(window.end - window.start, 10.0)

    def test_mg_only_scope_never_emits_snipe_sources(self) -> None:
        self.assertFalse(
            any("snipe" in event.source.lower() for event in self.result.damage_events)
        )


if __name__ == "__main__":
    unittest.main()
