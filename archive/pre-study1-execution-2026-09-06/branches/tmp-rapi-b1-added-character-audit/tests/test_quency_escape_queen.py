import unittest

from crown_mast_engine import simulate_rotation
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


QUENCY_ROSTER = TeamRoster(main_b3="quency-escape-queen")


class QuencyEscapeQueenMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(CROWN_CROWN_MAST, roster=QUENCY_ROSTER)
        cls.actor = "quency-escape-queen"

    def test_data_matches_pinned_datamine(self) -> None:
        unit = self.result.catalog.require(self.actor)
        self.assertEqual(unit.progression_atk, 109_209)
        self.assertEqual(unit.element, "Water")
        self.assertEqual(unit.weapon.weapon_type, "SMG")
        self.assertEqual(unit.weapon.normal_attack_pct, 10.12)
        self.assertEqual(unit.weapon.core_attack_pct, 250)
        self.assertEqual(unit.weapon.ammo, 120)
        self.assertEqual(unit.weapon.reload_frames, 81)
        self.assertEqual(unit.weapon.hits_per_shot, 2)
        self.assertEqual(unit.weapon.burst_gauge_per_shot, 0.074)
        self.assertEqual(unit.skill_value("skill1", "distributed_damage_pct"), 49.58)
        self.assertEqual(unit.skill_value("burst", "damage_pct"), 1736.31)

    def test_route_stages_reach_all_three_passive_caps(self) -> None:
        windows = self.result.buffs.windows
        self.assertTrue(
            any(
                window.source == self.actor
                and window.skill == "skill1_stage1_max"
                and window.stat == "distributed_damage_pct"
                and window.value == 49.58
                for window in windows
            )
        )
        self.assertTrue(
            any(
                window.source == self.actor
                and window.skill == "skill1_stage2_max"
                and window.stat == "core_damage_pct"
                and window.value == 25.25
                for window in windows
            )
        )
        self.assertTrue(
            any(
                window.source == self.actor
                and window.skill == "skill1_stage3_max"
                and window.stat == "crit_rate_pct"
                and window.value == 16.73
                for window in windows
            )
        )

    def test_route_attack_buffs_reach_datamined_caps(self) -> None:
        windows = self.result.buffs.windows
        stage1 = [
            window.value for window in windows
            if window.source == self.actor and window.skill == "skill2_stage1"
        ]
        stage2 = [
            window.value for window in windows
            if window.source == self.actor and window.skill == "skill2_stage2"
        ]
        stage3 = [
            window.value for window in windows
            if window.source == self.actor and window.skill == "skill2_stage3"
        ]
        self.assertAlmostEqual(max(stage1), 24.5)
        self.assertAlmostEqual(max(stage2), 49.0)
        self.assertAlmostEqual(max(stage3), 36.8)

    def test_own_burst_has_reload_attack_damage_and_distributed_nuke(self) -> None:
        burst_times = tuple(
            event.time for event in self.result.events
            if event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == self.actor
        )
        reload_windows = tuple(
            window for window in self.result.buffs.windows
            if window.source == self.actor and window.skill == "burst_reload"
        )
        attack_windows = tuple(
            window for window in self.result.buffs.windows
            if window.source == self.actor and window.skill == "burst"
        )
        nukes = tuple(
            event for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.BURST,
            )
            if event.source == "burst_distributed"
        )
        self.assertEqual(tuple(window.start for window in reload_windows), burst_times)
        self.assertEqual(tuple(window.start for window in attack_windows), burst_times)
        self.assertTrue(all(window.value == 25.87 for window in reload_windows))
        self.assertTrue(all(window.value == 57.08 for window in attack_windows))
        self.assertEqual(tuple(event.time for event in nukes), burst_times)
        self.assertTrue(all(event.coefficient_pct == 1736.31 for event in nukes))
        self.assertTrue(all(event.traits.distributed for event in nukes))


if __name__ == "__main__":
    unittest.main()
