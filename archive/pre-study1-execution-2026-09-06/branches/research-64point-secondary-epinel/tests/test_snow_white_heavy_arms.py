import unittest

from crown_mast_engine import CombatSettings, simulate_rotation
from crown_mast_engine.models import DamageCategory, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


ACTOR = "snow-white-heavy-arms"
ROSTER = TeamRoster(main_b3=ACTOR)


class SnowWhiteHeavyArmsMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=ROSTER,
            combat_settings=CombatSettings(boss_def=0, duration_sec=30),
        )

    def test_lock_on_damage_taken_is_permanent_for_the_single_boss_scope(self) -> None:
        for target in self.result.roster.members:
            with self.subTest(target=target):
                self.assertEqual(
                    self.result.buff_total(0, target, "damage_taken_pct"),
                    4.2,
                )
                self.assertEqual(
                    self.result.buff_total(29.9, target, "damage_taken_pct"),
                    4.2,
                )

    def test_every_full_charge_emits_both_baseline_auto_fire_riders(self) -> None:
        normals = self.result.damage_events_for(
            actor=ACTOR,
            category=DamageCategory.NORMAL,
        )
        aoe = tuple(
            event
            for event in self.result.damage_events_for(actor=ACTOR)
            if event.source == "skill1_auto_fire_aoe"
        )
        sequential = tuple(
            event
            for event in self.result.damage_events_for(actor=ACTOR)
            if event.source == "skill1_auto_fire_sequential"
        )
        self.assertEqual(len(aoe), len(normals))
        self.assertEqual(len(sequential), len(normals))
        self.assertEqual({event.coefficient_pct for event in aoe}, {41.9})
        self.assertEqual(
            {event.coefficient_pct for event in sequential},
            {527.95},
        )
        self.assertEqual(
            [event.shot_index for event in sequential],
            [event.shot_index for event in normals],
        )

    def test_full_charge_atk_buff_applies_before_the_triggering_shot(self) -> None:
        first = self.result.damage_events_for(
            actor=ACTOR,
            category=DamageCategory.NORMAL,
        )[0]
        self.assertEqual(
            self.result.buff_total(first.time, ACTOR, "atk_pct"),
            46.84,
        )
        self.assertAlmostEqual(
            first.breakdown.effective_atk,
            self.result.static_atk(ACTOR) * 1.4684,
        )

    def test_b3_stage_atk_buff_activates_for_another_b3(self) -> None:
        foreign_b3_time = self.result.timeline[1].b3_time
        windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == ACTOR
            and window.skill == "skill2_b3_stage"
            and window.start == foreign_b3_time
        )
        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0].value, 73.92)
        self.assertEqual(windows[0].end, foreign_b3_time + 10)

    def test_fully_active_ends_after_two_shots_and_restores_base_charge(self) -> None:
        own_b3_time = self.result.timeline[0].b3_time
        end = own_b3_time + 10
        normals = tuple(
            event
            for event in self.result.damage_events_for(
                actor=ACTOR,
                category=DamageCategory.NORMAL,
            )
            if own_b3_time <= event.time < end
        )
        empowered = tuple(
            event for event in normals if event.breakdown.charge == 7.78
        )
        restored = tuple(
            event for event in normals if event.breakdown.charge == 2.5
        )
        self.assertEqual(len(empowered), 2)
        self.assertTrue(restored)
        self.assertGreater(restored[0].time, empowered[-1].time)
        self.assertEqual(
            [event.magazine_index for event in empowered],
            [0, 0],
        )
        self.assertEqual(restored[0].magazine_index, 0)
        next_magazine = next(
            event
            for event in self.result.damage_events_for(
                actor=ACTOR,
                category=DamageCategory.NORMAL,
            )
            if event.magazine_index == 1
        )
        self.assertGreater(next_magazine.time, restored[0].time)

        extra = tuple(
            event
            for event in self.result.damage_events_for(actor=ACTOR)
            if event.source == "skill1_fully_active_extra_sequential"
        )
        self.assertEqual(len(extra), 2)
        self.assertEqual({event.coefficient_pct for event in extra}, {1055.9})

    def test_sequential_bonus_only_applies_to_the_two_fully_active_shots(self) -> None:
        own_b3_time = self.result.timeline[0].b3_time
        events = tuple(
            event
            for event in self.result.damage_events_for(actor=ACTOR)
            if event.source == "skill1_auto_fire_sequential"
            if own_b3_time <= event.time < own_b3_time + 10
        )
        self.assertGreater(len(events), 2)
        boosted = tuple(
            event
            for event in events
            if event.breakdown.damage_up
            > events[-1].breakdown.damage_up + 1.5
        )
        self.assertEqual(len(boosted), 2)
        for event in boosted:
            ordinary_same_shot = next(
                candidate
                for candidate in self.result.damage_events_for(actor=ACTOR)
                if candidate.source == "skill1_auto_fire_aoe"
                if candidate.shot_index == event.shot_index
            )
            self.assertAlmostEqual(
                event.breakdown.damage_up
                - ordinary_same_shot.breakdown.damage_up,
                1.584,
            )


if __name__ == "__main__":
    unittest.main()
