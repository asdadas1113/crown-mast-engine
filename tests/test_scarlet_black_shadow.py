import unittest

from crown_mast_engine import analyze_rotations, simulate_rotation
from crown_mast_engine.combat import FPS
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


SBS_ROSTER = TeamRoster(secondary_b3="scarlet-black-shadow")


class ScarletBlackShadowMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(CROWN_CROWN_MAST, roster=SBS_ROSTER)

    def test_skill1_cycles_three_distinct_phases_outside_own_burst(self) -> None:
        procs = [
            event
            for event in self.result.damage_events_for(actor="scarlet-black-shadow")
            if event.source.startswith("skill1_phase")
        ]
        self.assertEqual(
            [(event.time, event.source) for event in procs[:3]],
            [
                (1.75, "skill1_phase1"),
                (3.75, "skill1_phase2"),
                (5.75, "skill1_phase3"),
            ],
        )
        self.assertEqual(
            [event.coefficient_pct for event in procs[:3]],
            [283.03, 565.0, 848.03],
        )
        self.assertEqual(
            [event.traits.distributed for event in procs[:3]],
            [False, True, True],
        )

    def test_own_burst_window_triggers_one_phase_per_full_charge(self) -> None:
        start = next(
            snapshot
            for snapshot in self.result.snapshots
            if snapshot.b3_actor == "scarlet-black-shadow"
        ).cycle
        cycle = self.result.timeline[start - 1]
        end = cycle.b3_time + 10
        normals = {
            event.shot_index
            for event in self.result.damage_events_for(
                actor="scarlet-black-shadow",
                category=DamageCategory.NORMAL,
            )
            if cycle.b3_time <= event.time < end
        }
        procs = {
            event.shot_index
            for event in self.result.damage_events_for(
                actor="scarlet-black-shadow",
                category=DamageCategory.SKILL,
            )
            if cycle.b3_time <= event.time < end
            and event.source.startswith("skill1_phase")
        }
        self.assertEqual(procs, normals)

    def test_full_burst_ammo_and_own_burst_damage_buffs_are_timed(self) -> None:
        actor = "scarlet-black-shadow"
        self.assertEqual(
            self.result.buff_total(5.0, actor, "max_ammo_pct"),
            45.17,
        )
        self.assertEqual(
            self.result.buff_total(6.0, actor, "max_ammo_pct"),
            45.17 + 60,
        )
        self.assertEqual(self.result.buff_total(19.0, actor, "atk_pct"), 66)
        self.assertEqual(
            self.result.buff_total(20.0, actor, "atk_pct"),
            66 + 115.12,
        )
        self.assertEqual(
            self.result.buff_total(20.0, actor, "charge_damage_pct"),
            169.63,
        )

    def test_only_distributed_phases_receive_mast_stack_buff(self) -> None:
        phase1 = next(
            event
            for event in self.result.damage_events
            if event.actor == "scarlet-black-shadow"
            and event.source == "skill1_phase1"
            and 19.3 <= event.time < 29.3
        )
        phase2 = next(
            event
            for event in self.result.damage_events
            if event.actor == "scarlet-black-shadow"
            and event.source == "skill1_phase2"
            and 19.3 <= event.time < 29.3
        )
        self.assertEqual(phase1.breakdown.taken, 1)
        self.assertEqual(phase1.breakdown.distributed, 1)
        self.assertAlmostEqual(phase2.breakdown.taken, 1.3006)
        self.assertEqual(phase2.breakdown.distributed, 1)


class ScarletBlackShadowAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analysis = analyze_rotations(roster=SBS_ROSTER)

    def test_strong_distributed_secondary_still_favors_conventional(self) -> None:
        overall = self.analysis.overall
        self.assertAlmostEqual(overall.team_c, 2_101_149_975.2309287)
        self.assertAlmostEqual(overall.team_f, 2_094_367_146.9837704, delta=1e-3)
        self.assertAlmostEqual(overall.team_relative_change, -0.0032281504543300032)
        self.assertAlmostEqual(overall.break_even_main_share_c, 0.4907435342798073)
        self.assertLess(
            overall.conventional_main_share,
            overall.break_even_main_share_c,
        )

    def test_secondary_outdamages_main_in_conventional_rotation(self) -> None:
        main = self.analysis.by_character["rapi-red-hood"].conventional
        secondary = self.analysis.by_character[
            "scarlet-black-shadow"
        ].conventional
        self.assertGreater(secondary, main)
        self.assertIn(
            ("scarlet-black-shadow", "skill1_phase2"),
            self.analysis.by_source,
        )
        self.assertIn(
            ("scarlet-black-shadow", "skill1_phase3"),
            self.analysis.by_source,
        )

    def test_crown_relax_self_recovery_occurs_every_860_normal_attacks(self) -> None:
        crown = self.analysis.conventional_result.roster.crown
        skill2 = self.analysis.conventional_result.catalog.require(crown).skills[
            "skill2"
        ]
        threshold = int(
            skill2["relax_hits_per_stack"] * skill2["max_relax_stacks"]
        )
        recovery_times_by_policy: list[tuple[float, ...]] = []

        for result in (
            self.analysis.conventional_result,
            self.analysis.funnel_result,
        ):
            crown_normals = result.damage_events_for(
                actor=crown,
                category=DamageCategory.NORMAL,
            )
            expected = tuple(
                recovery_time
                for index in range(threshold - 1, len(crown_normals), threshold)
                if (
                    recovery_time := round(
                        crown_normals[index].time + 1 / FPS,
                        6,
                    )
                )
                < result.combat_settings.duration_sec
            )
            actual = tuple(
                event.time
                for event in result.events
                if event.event_type == EventType.RECOVERY and event.actor == crown
            )
            self.assertTrue(actual)
            self.assertEqual(actual, expected)
            recovery_times_by_policy.append(actual)

        self.assertEqual(*recovery_times_by_policy)

    def test_crown_relax_recovery_starts_seven_second_team_buff_after_hit(self) -> None:
        result = self.analysis.conventional_result
        crown = result.roster.crown
        target = result.roster.main_b3
        first_recovery = next(
            event.time
            for event in result.events
            if event.event_type == EventType.RECOVERY and event.actor == crown
        )
        windows = tuple(
            window
            for window in result.buffs.windows
            if window.source == crown
            and window.skill == "skill2_recovery"
            and window.target == target
        )

        self.assertEqual(windows[0].start, first_recovery)
        self.assertEqual(windows[0].end, first_recovery + 7)
        self.assertFalse(
            any(
                window.source == crown and window.skill == "skill2_recovery"
                for window in result.active_buffs(
                    first_recovery - 1 / (FPS * 2),
                    target,
                    "attack_damage_pct",
                )
            )
        )


if __name__ == "__main__":
    unittest.main()