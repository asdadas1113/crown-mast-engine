import unittest

from crown_mast_engine import CombatSettings, simulate_rotation
from crown_mast_engine.models import DamageCategory, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


ACTOR = "neon-vision-eye"
ROSTER = TeamRoster(main_b3=ACTOR)


class NeonVisionEyeMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=ROSTER,
            combat_settings=CombatSettings(boss_def=0),
        )
        cls.secondary_result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=TeamRoster(secondary_b3=ACTOR),
            combat_settings=CombatSettings(boss_def=0),
        )

    def test_unique_rl_has_no_release_recovery(self) -> None:
        normals = self.result.damage_events_for(
            actor=ACTOR,
            category=DamageCategory.NORMAL,
        )
        self.assertEqual(normals[1].time - normals[0].time, 1.0)

    def test_every_full_charge_emits_stage_target_bonus_damage(self) -> None:
        normals = self.result.damage_events_for(
            actor=ACTOR,
            category=DamageCategory.NORMAL,
        )
        bonus = tuple(
            event
            for event in self.result.damage_events_for(actor=ACTOR)
            if event.source == "skill1_firepower_explosion"
        )
        self.assertEqual(len(bonus), len(normals))
        self.assertEqual({event.coefficient_pct for event in bonus}, {437.98})
        self.assertEqual(
            [event.shot_index for event in bonus],
            [event.shot_index for event in normals],
        )

    def test_super_firepower_returns_after_two_charge_bursts(self) -> None:
        expected_cycles = (1, 7)
        expected_times = [
            self.result.timeline[cycle - 1].b3_time
            for cycle in expected_cycles
        ]
        windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == ACTOR
            and window.skill == "burst_super_firepower"
        )
        self.assertEqual([window.start for window in windows], expected_times)
        self.assertEqual({window.value for window in windows}, {45.03})

    def test_secondary_b3_keeps_the_same_three_cast_gauge_cycle(self) -> None:
        windows = tuple(
            window
            for window in self.secondary_result.buffs.windows
            if window.source == ACTOR
            and window.skill == "burst_super_firepower"
        )
        self.assertEqual(
            [window.start for window in windows],
            [
                self.secondary_result.timeline[1].b3_time,
                self.secondary_result.timeline[7].b3_time,
            ],
        )

    def test_full_burst_atk_buff_and_super_bonus_have_distinct_windows(self) -> None:
        base = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == ACTOR
            and window.skill == "skill2_maximum_firepower"
        )
        super_bonus = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == ACTOR
            and window.skill == "skill2_super_firepower"
        )
        self.assertEqual(len(base), 12)
        self.assertEqual({window.value for window in base}, {80.04})
        self.assertEqual(
            [window.start for window in super_bonus],
            [self.result.timeline[0].full_burst_start,
             self.result.timeline[6].full_burst_start],
        )
        self.assertEqual({window.value for window in super_bonus}, {35.05})

    def test_super_firepower_extra_damage_only_occurs_in_super_windows(self) -> None:
        extra = tuple(
            event
            for event in self.result.damage_events_for(actor=ACTOR)
            if event.source == "skill1_super_firepower_extra"
        )
        self.assertTrue(extra)
        self.assertEqual({event.coefficient_pct for event in extra}, {262.79})
        super_windows = (
            (self.result.timeline[0].b3_time, self.result.timeline[0].b3_time + 10),
            (self.result.timeline[6].b3_time, self.result.timeline[6].b3_time + 10),
        )
        self.assertTrue(
            all(
                any(start <= event.time < end for start, end in super_windows)
                for event in extra
            )
        )


if __name__ == "__main__":
    unittest.main()
