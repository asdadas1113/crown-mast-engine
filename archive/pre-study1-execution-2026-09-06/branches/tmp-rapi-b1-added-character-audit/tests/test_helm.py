import unittest

from crown_mast_engine.models import DamageCategory, EventType
from tests.simulation_fixtures import (
    standard_conventional_result,
    standard_funnel_result,
)


class HelmMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = standard_conventional_result()
        cls.helm_events = cls.result.damage_events_for(actor="helm")
        cls.normals = [
            event for event in cls.helm_events if event.source == "normal_attack"
        ]
        cls.riders = [
            event
            for event in cls.helm_events
            if event.source == "skill2_full_charge"
        ]
        cls.nukes = [
            event for event in cls.helm_events if event.source == "burst_nuke"
        ]

    def test_full_charge_rider_fires_once_per_pull(self) -> None:
        self.assertEqual(len(self.riders), len(self.normals))
        self.assertTrue(self.normals)
        self.assertEqual(
            {event.coefficient_pct for event in self.riders},
            {178.98},
        )
        self.assertTrue(
            all(event.category == DamageCategory.SKILL for event in self.riders)
        )
        self.assertTrue(all(not event.traits.core_eligible for event in self.riders))

    def test_both_rotations_conserve_helm_event_counts(self) -> None:
        funnel = standard_funnel_result()
        funnel_events = funnel.damage_events_for(actor="helm")
        for source in ("normal_attack", "skill2_full_charge", "burst_nuke"):
            with self.subTest(source=source):
                self.assertEqual(
                    sum(event.source == source for event in funnel_events),
                    sum(event.source == source for event in self.helm_events),
                )

    def test_same_frame_recoveries_leave_no_zero_duration_buff_windows(self) -> None:
        funnel = standard_funnel_result()
        for result in (self.result, funnel):
            with self.subTest(policy=result.policy_name):
                self.assertTrue(result.buffs.windows)
                self.assertTrue(
                    all(window.start < window.end for window in result.buffs.windows)
                )

    def test_burst_nuke_is_before_full_burst_and_uses_kit_value(self) -> None:
        self.assertEqual(len(self.nukes), 6)
        self.assertEqual(
            {event.coefficient_pct for event in self.nukes},
            {8236.8},
        )
        self.assertTrue(all(not event.full_burst for event in self.nukes))

    def test_charge_multiplier_applies_to_exactly_next_ten_rounds(self) -> None:
        after_first_burst = [
            event for event in self.normals if 19.3 <= event.time < 48.5
        ]
        self.assertGreaterEqual(len(after_first_burst), 11)
        self.assertTrue(
            all(event.breakdown.charge == 6.69675 for event in after_first_burst[:10])
        )
        self.assertEqual(after_first_burst[10].breakdown.charge, 2.73675)
        self.assertEqual(
            {event.magazine_index for event in after_first_burst[:10]},
            {2, 3},
        )

    def test_last_bullet_crit_rate_only_affects_normal_attacks(self) -> None:
        normal = next(event for event in self.normals if event.shot_index == 6)
        rider = next(event for event in self.riders if event.shot_index == 6)
        self.assertAlmostEqual(normal.breakdown.major, 1.74845)
        self.assertAlmostEqual(rider.breakdown.major, 1.67525)
        self.assertAlmostEqual(
            normal.breakdown.major - rider.breakdown.major,
            14.64 * 0.5 / 100,
        )

    def test_full_charge_recovery_refreshes_crown_skill2(self) -> None:
        crown_recovery = [
            buff
            for buff in self.result.active_buffs(
                2.0,
                self.result.roster.main_b3,
                "attack_damage_pct",
            )
            if buff.source == self.result.roster.crown
            and buff.skill == "skill2_recovery"
        ]
        self.assertEqual(len(crown_recovery), 1)
        self.assertEqual(crown_recovery[0].value, 20.99)
        recoveries = [
            event
            for event in self.result.events
            if event.event_type == EventType.RECOVERY
        ]
        crown = self.result.roster.crown
        crown_skill2 = self.result.catalog.require(crown).skills["skill2"]
        crown_threshold = int(
            crown_skill2["relax_hits_per_stack"]
            * crown_skill2["max_relax_stacks"]
        )
        crown_normals = self.result.damage_events_for(
            actor=crown,
            category=DamageCategory.NORMAL,
        )
        crown_self_recoveries = len(crown_normals) // crown_threshold
        expected = (
            len(self.normals) * len(self.result.roster.members)
            + 6 * 10 * len(self.result.roster.members)
            + crown_self_recoveries
        )
        self.assertEqual(len(recoveries), expected)

    def test_full_burst_attack_damage_buff_reaches_all_allies(self) -> None:
        for target in self.result.roster.members:
            helm_buffs = [
                buff
                for buff in self.result.active_buffs(
                    6.0,
                    target,
                    "attack_damage_pct",
                )
                if buff.source == "helm"
                and buff.skill == "skill2_full_burst"
            ]
            self.assertEqual(len(helm_buffs), 1)
            self.assertEqual(helm_buffs[0].value, 27.87)


if __name__ == "__main__":
    unittest.main()
