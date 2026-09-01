import unittest
from dataclasses import replace

from crown_mast_engine import simulate_rotation
from crown_mast_engine.character_mechanics import QuencyEscapeQueenSkillHook
from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from crown_mast_engine.combat import STANDARD_COMBAT_SETTINGS, WeaponShot
from crown_mast_engine.mechanics import SkillHookContext
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST
from crown_mast_engine.timeline import RAID14_TIMELINE


class RapiB1AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.actor = "rapi-red-hood"
        cls.roster = TeamRoster(
            b1=cls.actor,
            main_b3="scarlet-black-shadow",
            secondary_b3="helm",
        )
        cls.result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=cls.roster,
            timeline=RAID14_TIMELINE,
        )

    def test_combat_assist_runs_all_fourteen_fixed_cycles(self) -> None:
        casts = tuple(
            event for event in self.result.events
            if event.event_type == EventType.B1_CAST and event.actor == self.actor
        )
        self.assertEqual(len(casts), 14)
        self.assertEqual(tuple(event.time for event in casts), tuple(c.b1_time for c in RAID14_TIMELINE))

    def test_b1_and_full_burst_team_buffs_match_cross_checked_values(self) -> None:
        first = RAID14_TIMELINE[0]
        for target in dict.fromkeys(self.roster.members):
            b1 = [
                b for b in self.result.active_buffs(first.b1_time + 0.01, target)
                if b.source == self.actor and b.skill == "burst_stage1"
                and b.stat == "caster_atk_pct"
            ]
            self.assertEqual([b.value for b in b1], [18.01])
            fb = [
                b for b in self.result.active_buffs(first.full_burst_start + 0.01, target)
                if b.source == self.actor and b.skill == "skill1_combat_assist"
                and b.stat == "attack_damage_pct"
            ]
            self.assertEqual([b.value for b in fb], [8.02])

    def test_combat_assist_does_not_receive_the_dps_branch_95_04_atk(self) -> None:
        self.assertFalse(
            any(
                b.source == self.actor and b.skill == "skill1_full_burst"
                and b.stat == "atk_pct" and b.value == 95.04
                for b in self.result.buffs.windows
            )
        )
        self.assertFalse(
            any(
                e.actor == self.actor and e.source == "burst_stage3_missile"
                for e in self.result.damage_events
            )
        )


class QuencyRouteAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.actor = "quency-escape-queen"
        cls.result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=TeamRoster(main_b3=cls.actor),
        )

    def test_dual_smg_hit_count_two_means_one_pull_per_route_trigger(self) -> None:
        normals = self.result.damage_events_for(actor=self.actor, category=DamageCategory.NORMAL)
        stage1_max = next(
            w for w in self.result.buffs.windows
            if w.source == self.actor and w.skill == "skill1_stage1_max"
        )
        self.assertLessEqual(stage1_max.start, normals[9].time + 1 / 60 + 1e-6)
        self.assertGreater(stage1_max.start, normals[8].time)

    def test_stage2_and_stage3_unlock_sequentially(self) -> None:
        s1 = min(
            w.start for w in self.result.buffs.windows
            if w.source == self.actor and w.skill == "skill1_stage1_max"
        )
        s2 = min(
            w.start for w in self.result.buffs.windows
            if w.source == self.actor and w.skill == "skill1_stage2_max"
        )
        s3 = min(
            w.start for w in self.result.buffs.windows
            if w.source == self.actor and w.skill == "skill1_stage3_max"
        )
        self.assertLess(s1, s2)
        self.assertLess(s2, s3)

    def test_stage2_and_stage3_expire_after_one_second_gap_while_stage1_survives(self) -> None:
        definition = STANDARD_CHARACTER_CATALOG.require(self.actor)
        context = SkillHookContext(
            actor=self.actor,
            definition=definition,
            roster=TeamRoster(main_b3=self.actor),
            timeline=(),
            duration_sec=180.0,
        )
        hook = QuencyEscapeQueenSkillHook(context)

        def shot(index: int, time: float) -> WeaponShot:
            return WeaponShot(
                time=time,
                frame=round(time * 60),
                actor=self.actor,
                shot_index=index,
                magazine_index=0,
                rounds_consumed=1,
                core_eligible=True,
            )

        # 10 pulls fill Stage 1, next 10 fill Stage 2, next 5 fill Stage 3.
        last_time = 0.0
        for index in range(25):
            last_time = index * 0.05
            hook.on_weapon_shot(shot(index, last_time), context)

        # 1.2s is longer than Stage 2 (1s) and Stage 3 (0.5s), but shorter
        # than Stage 1 (2s). On the next pull Stage 1 must remain maxed while
        # Stage 2 restarts at one stack and Stage 3 is absent.
        effects = hook.on_weapon_shot(shot(25, last_time + 1.2), context)
        windows = [effect for effect in effects if hasattr(effect, "skill")]
        by_skill = {window.skill: window for window in windows}
        self.assertIn("skill1_stage1_max", by_skill)
        self.assertNotIn("skill1_stage2_max", by_skill)
        self.assertNotIn("skill1_stage3_max", by_skill)
        self.assertIn("skill2_stage2", by_skill)
        self.assertAlmostEqual(by_skill["skill2_stage2"].value, 4.9)


class CoreStrikeAuditTests(unittest.TestCase):
    def test_ccw_mg_core_strike_forces_core_bucket_even_with_zero_normal_core_rate(self) -> None:
        actor = "cinderella-crystal-wave"
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=TeamRoster(main_b3=actor),
        )
        rider = next(
            event for event in result.damage_events_for(actor=actor)
            if event.source == "skill2_mg_full_burst_core_strike"
        )
        self.assertTrue(rider.traits.forced_core)
        # Base crit contributes 7.5%; Mast's first Drunken stack adds 20.05%
        # crit rate, i.e. another 10.025% expected major. Then +50% FB,
        # +100% forced core, and +26% Pinpoint => 2.93525.
        self.assertAlmostEqual(rider.breakdown.major, 2.93525)


class BurstCastTimingAuditTests(unittest.TestCase):
    CASES = (
        ("liberalio", "burst_nuke"),
        ("raven", "burst_nuke"),
        ("cinderella-crystal-wave", "burst_nuke"),
        ("phantom", "burst_distributed"),
        ("quency-escape-queen", "burst_distributed"),
        ("epinel", "burst_safe_50_50"),
        ("helm", "burst_nuke"),
    )

    def test_cast_instant_burst_packets_do_not_take_fb_50_on_raid14(self) -> None:
        zero_fb = replace(STANDARD_COMBAT_SETTINGS, full_burst_bonus_pct=0.0)
        for actor, source in self.CASES:
            with self.subTest(actor=actor):
                roster = (
                    TeamRoster(main_b3="rapi-red-hood", secondary_b3="helm")
                    if actor == "helm"
                    else TeamRoster(main_b3=actor)
                )
                base = simulate_rotation(
                    CROWN_CROWN_MAST,
                    roster=roster,
                    timeline=RAID14_TIMELINE,
                )
                control = simulate_rotation(
                    CROWN_CROWN_MAST,
                    roster=roster,
                    timeline=RAID14_TIMELINE,
                    combat_settings=zero_fb,
                )
                packet = next(
                    e for e in base.damage_events_for(actor=actor)
                    if e.source == source
                )
                control_packet = next(
                    e for e in control.damage_events_for(actor=actor)
                    if e.source == source
                )
                self.assertTrue(packet.full_burst, "RAID14 timestamps overlap FB start")
                self.assertFalse(packet.traits.full_burst_eligible)
                self.assertAlmostEqual(packet.damage, control_packet.damage)

    def test_delayed_rapi_and_ccw_fb_enter_packets_remain_fb_eligible(self) -> None:
        rapi = simulate_rotation(
            CROWN_CROWN_MAST,
            timeline=RAID14_TIMELINE,
        )
        missile = next(
            e for e in rapi.damage_events_for(actor="rapi-red-hood")
            if e.source == "burst_stage3_missile"
        )
        self.assertTrue(missile.traits.full_burst_eligible)
        self.assertTrue(missile.full_burst)

        ccw = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=TeamRoster(main_b3="cinderella-crystal-wave"),
            timeline=RAID14_TIMELINE,
        )
        rider = next(
            e for e in ccw.damage_events_for(actor="cinderella-crystal-wave")
            if e.source == "skill2_mg_full_burst_core_strike"
        )
        self.assertTrue(rider.traits.full_burst_eligible)
        self.assertTrue(rider.full_burst)


if __name__ == "__main__":
    unittest.main()