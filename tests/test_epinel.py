import unittest

from crown_mast_engine import CombatSettings, LEGACY_12_BURST_TIMELINE, simulate_rotation
from crown_mast_engine.models import DamageCategory, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


ACTOR = "epinel"
ROSTER = TeamRoster(main_b3=ACTOR)


class EpinelMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=ROSTER,
            timeline=LEGACY_12_BURST_TIMELINE,
            combat_settings=CombatSettings(boss_def=0, duration_sec=40),
        )
        cls.normals = cls.result.damage_events_for(
            actor=ACTOR,
            category=DamageCategory.NORMAL,
        )

    def test_last_bullet_opens_one_five_second_crit_window_per_magazine(self) -> None:
        last_bullets = tuple(event for event in self.normals if event.shot_index in {119})
        self.assertEqual(len(last_bullets), 1)
        first = last_bullets[0]
        windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == ACTOR
            and window.skill == "skill2_last_bullet"
            and window.start == round(first.time + 1 / 60, 6)
        )
        self.assertEqual(len(windows), 2)
        self.assertEqual(
            {(window.stat, window.value) for window in windows},
            {("crit_rate_pct", 5.05), ("crit_damage_pct", 6.4)},
        )
        self.assertTrue(all(window.end - window.start == 5 for window in windows))

    def test_last_bullet_does_not_receive_its_own_crit_buff(self) -> None:
        triggering = self.normals[119]
        following = self.normals[120]
        self.assertAlmostEqual(
            following.breakdown.major - triggering.breakdown.major,
            0.050914,
        )

    def test_burst_nuke_fires_only_on_epinel_casts_before_full_burst(self) -> None:
        own_casts = tuple(
            snapshot
            for snapshot in self.result.snapshots
            if snapshot.b3_actor == ACTOR
            and self.result.timeline[snapshot.cycle - 1].b3_time
            < self.result.combat_settings.duration_sec
        )
        nukes = self.result.damage_events_for(
            actor=ACTOR,
            category=DamageCategory.BURST,
        )
        self.assertEqual(len(nukes), len(own_casts))
        self.assertEqual({event.coefficient_pct for event in nukes}, {457.87})
        self.assertTrue(all(not event.full_burst for event in nukes))
        self.assertEqual(
            [event.time for event in nukes],
            [self.result.timeline[item.cycle - 1].b3_time for item in own_casts],
        )

    def test_single_immortal_boss_never_grants_total_noob(self) -> None:
        epinel_atk_buffs = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == ACTOR and window.stat == "atk_pct"
        )
        self.assertEqual(epinel_atk_buffs, ())
        self.assertFalse(
            any(
                event.source == "burst_total_noob_extra"
                for event in self.result.damage_events_for(actor=ACTOR)
            )
        )


if __name__ == "__main__":
    unittest.main()
