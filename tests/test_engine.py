import unittest

from crown_mast_engine.engine import CrownMastEngine, simulate_rotation
from crown_mast_engine.models import EventType, TeamRoster
from crown_mast_engine.rotations import (
    CROWN_CROWN_MAST,
    OPENING_MAST_CROWN_MAST,
    OPENING_MAST_SUSTAINED_FUNNEL,
    SUSTAINED_FUNNEL,
)
from crown_mast_engine.timeline import LEGACY_12_BURST_TIMELINE
from tests.simulation_fixtures import (
    standard_conventional_result,
    standard_funnel_result,
    standard_rotation_results,
)


class CrownMastEngineTests(unittest.TestCase):
    def test_opening_funnel_only_replaces_the_first_b2(self) -> None:
        self.assertEqual(
            OPENING_MAST_SUSTAINED_FUNNEL.b2_slot_by_cycle,
            ("mast",) + SUSTAINED_FUNNEL.b2_slot_by_cycle[1:],
        )
        self.assertEqual(
            OPENING_MAST_SUSTAINED_FUNNEL.b2_slot_by_cycle[:4],
            OPENING_MAST_CROWN_MAST.b2_slot_by_cycle[:4],
        )
        self.assertNotEqual(
            OPENING_MAST_SUSTAINED_FUNNEL.b2_slot_by_cycle[4],
            OPENING_MAST_CROWN_MAST.b2_slot_by_cycle[4],
        )

    def test_opening_mast_crown_mast_only_changes_first_macro_cycle(self) -> None:
        self.assertEqual(
            OPENING_MAST_CROWN_MAST.b2_slot_by_cycle,
            ("mast", "crown", "mast")
            + ("crown", "crown", "mast") * 3
            + ("crown", "mast"),
        )
        result = simulate_rotation(
            OPENING_MAST_CROWN_MAST,
            timeline=LEGACY_12_BURST_TIMELINE,
        )
        mast_casts = [snapshot for snapshot in result.snapshots if snapshot.b2_actor == result.roster.mast]
        self.assertEqual([snapshot.cycle for snapshot in mast_casts], [1, 3, 6, 9, 12])
        self.assertEqual([snapshot.mast_stack_at_b2 for snapshot in mast_casts], [1, 3, 3, 3, 3])
        self.assertEqual(
            [snapshot.cycle for snapshot in result.snapshots if snapshot.mast_reset_at_end],
            [3, 6, 9, 12],
        )

    def test_crown_crown_mast_uses_mast_at_three_stacks(self) -> None:
        result = standard_conventional_result()
        mast_casts = [s for s in result.snapshots if s.b2_actor == result.roster.mast]
        self.assertEqual([s.cycle for s in mast_casts], [3, 6, 9, 12])
        self.assertEqual([s.mast_stack_at_b2 for s in mast_casts], [3, 3, 3, 3])

    def test_sustained_funnel_has_two_stack_mast_casts(self) -> None:
        result = standard_funnel_result()
        mast_casts = [s for s in result.snapshots if s.b2_actor == result.roster.mast]
        self.assertEqual([s.cycle for s in mast_casts], [3, 5, 9, 11])
        self.assertEqual([s.mast_stack_at_b2 for s in mast_casts], [3, 2, 3, 2])

    def test_mast_resets_at_every_third_full_burst_in_both_rotations(self) -> None:
        for result in standard_rotation_results():
            with self.subTest(policy=result.policy_name):
                resets = [s.cycle for s in result.snapshots if s.mast_reset_at_end]
                self.assertEqual(resets, [3, 6, 9, 12])

    def test_two_stack_burst_does_not_reset_mast(self) -> None:
        result = standard_funnel_result()
        cycle5 = result.snapshots[4]
        self.assertEqual(cycle5.mast_stack_at_b2, 2)
        self.assertFalse(cycle5.mast_reset_at_end)

    def test_mast_s2_uses_live_stack_value(self) -> None:
        result = standard_funnel_result()
        target = result.roster.main_b3
        self.assertAlmostEqual(
            result.buff_total(34.0, target, "distributed_damage_pct"),
            45.09,
        )
        self.assertAlmostEqual(
            result.buff_total(62.3, target, "distributed_damage_pct"),
            30.06,
        )

    def test_crown_burst_refreshes_without_double_stacking(self) -> None:
        result = standard_conventional_result()
        target = result.roster.main_b3
        crown_burst = [
            buff
            for buff in result.active_buffs(19.0, target, "attack_damage_pct")
            if buff.source == result.roster.crown and buff.skill == "burst"
        ]
        self.assertEqual(len(crown_burst), 1)
        self.assertAlmostEqual(crown_burst[0].value, 36.24)

    def test_crown_s1_only_grants_caster_atk_to_burst_casters(self) -> None:
        result = standard_conventional_result()
        self.assertAlmostEqual(
            result.buff_total(6.0, result.roster.main_b3, "caster_atk_pct"),
            64.51 + 35.02,
        )
        self.assertAlmostEqual(
            result.buff_total(6.0, result.roster.secondary_b3, "caster_atk_pct"),
            35.02,
        )

    def test_mast_hangover_starts_only_after_three_stack_full_burst(self) -> None:
        result = standard_conventional_result()
        starts = [e for e in result.events if e.event_type == EventType.HANGOVER_START]
        self.assertEqual([e.cycle for e in starts], [3, 6, 9, 12])
        self.assertAlmostEqual(starts[0].payload["until"], 54.3)

    def test_recovery_on_crown_applies_team_attack_damage(self) -> None:
        engine = CrownMastEngine(CROWN_CROWN_MAST)
        engine.apply_recovery(1.0, engine.roster.crown)
        self.assertAlmostEqual(
            engine.buffs.total(2.0, engine.roster.main_b3, "attack_damage_pct"),
            20.99,
        )
        self.assertEqual(
            engine.buffs.total(8.0, engine.roster.main_b3, "attack_damage_pct"),
            0,
        )

    def test_timeline_resolves_custom_b3_roster_slots(self) -> None:
        roster = TeamRoster(main_b3="Main", secondary_b3="Secondary")
        result = simulate_rotation(CROWN_CROWN_MAST, roster=roster)
        self.assertEqual(result.snapshots[0].b3_actor, "Main")
        self.assertEqual(result.snapshots[1].b3_actor, "Secondary")


if __name__ == "__main__":
    unittest.main()
