import unittest

from crown_mast_engine.character_mechanics import RapiRedHoodSkillHook
from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from crown_mast_engine.combat import DamageRequest, WeaponShot
from crown_mast_engine.engine import simulate_rotation
from crown_mast_engine.mechanics import SkillHookContext
from crown_mast_engine.models import BattleEvent, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST
from crown_mast_engine.timeline import BurstCycle
from tests.simulation_fixtures import (
    standard_conventional_result,
    standard_funnel_result,
)


class RapiRedHoodMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = standard_conventional_result()
        cls.events = cls.result.damage_events_for(actor="rapi-red-hood")

    def test_stage3_missile_fires_once_per_own_burst_and_lands_in_full_burst(self) -> None:
        missiles = [
            event
            for event in self.events
            if event.source == "burst_stage3_missile"
        ]
        own_cycles = [
            cycle
            for cycle in self.result.timeline
            if cycle.b3_slot == "main_b3"
        ]
        self.assertEqual(len(missiles), len(own_cycles))
        self.assertEqual(
            [event.time for event in missiles],
            [round(cycle.b3_time + 0.4, 6) for cycle in own_cycles],
        )
        self.assertTrue(all(event.coefficient_pct == 2808 for event in missiles))
        self.assertTrue(all(event.full_burst for event in missiles))
        self.assertTrue(all(not event.traits.core_eligible for event in missiles))
        self.assertTrue(all(not event.traits.projectile_attachment for event in missiles))

    def test_stage3_missile_requires_120_prior_normal_attacks(self) -> None:
        early_timeline = (
            BurstCycle(1, 0.2, 0.4, 0.6, 0.9, 10.9, "main_b3"),
        )
        result = simulate_rotation(CROWN_CROWN_MAST, timeline=early_timeline)
        self.assertFalse(
            any(event.source == "burst_stage3_missile" for event in result.damage_events)
        )

    def test_full_burst_self_atk_buff_applies_on_both_b3_slots(self) -> None:
        def rapi_self_atk(time: float) -> float:
            return sum(
                buff.value
                for buff in self.result.active_buffs(
                    time,
                    "rapi-red-hood",
                    "atk_pct",
                )
                if buff.source == "rapi-red-hood"
                and buff.skill == "skill1_full_burst"
            )

        self.assertAlmostEqual(rapi_self_atk(5.2), 95.04)
        self.assertAlmostEqual(rapi_self_atk(20.0), 95.04)
        self.assertEqual(rapi_self_atk(16.0), 0)

    def test_projectile_buffs_only_enter_the_matching_damage_flavor(self) -> None:
        passive_attach = next(
            event
            for event in self.events
            if event.source == "skill2_rocket_attachment" and event.time < 4.8
        )
        passive_normal = next(
            event
            for event in self.events
            if event.source == "normal_attack" and event.time == passive_attach.time
        )
        self.assertAlmostEqual(
            passive_attach.breakdown.damage_up - passive_normal.breakdown.damage_up,
            1.5072,
        )

        amplified_attach = next(
            event
            for event in self.events
            if event.source == "skill2_rocket_attachment" and 4.8 <= event.time < 14.8
        )
        amplified_normal = next(
            event
            for event in self.events
            if event.source == "normal_attack" and event.time == amplified_attach.time
        )
        self.assertAlmostEqual(
            amplified_attach.breakdown.damage_up - amplified_normal.breakdown.damage_up,
            1.5072 + 4.212,
        )

    def test_rocket_attachment_cores_but_explosion_does_not(self) -> None:
        attachments = [
            event
            for event in self.events
            if event.source == "skill2_rocket_attachment"
        ]
        explosions = [
            event
            for event in self.events
            if event.source == "skill2_rocket_explosion"
        ]
        self.assertTrue(attachments)
        self.assertTrue(explosions)
        self.assertTrue(all(event.coefficient_pct == 88.11 for event in attachments))
        self.assertTrue(all(event.traits.core_eligible for event in attachments))
        self.assertTrue(all(not event.traits.core_eligible for event in explosions))
        self.assertTrue(
            all(
                abs(
                    event.coefficient_pct / 88.11
                    - round(event.coefficient_pct / 88.11)
                )
                < 1e-9
                for event in explosions
            )
        )

    def test_stored_explosions_are_conserved_until_the_last_full_burst(self) -> None:
        attachments = [
            event
            for event in self.events
            if event.source == "skill2_rocket_attachment"
        ]
        explosions = [
            event
            for event in self.events
            if event.source == "skill2_rocket_explosion"
        ]
        exploded_rockets = sum(
            round(event.coefficient_pct / 88.11) for event in explosions
        )
        tail_attachments = sum(event.time >= 173 for event in attachments)
        self.assertEqual(exploded_rockets, len(attachments) - tail_attachments)

    def test_own_stage3_windows_use_the_lower_rocket_threshold(self) -> None:
        attachments = [
            event
            for event in self.events
            if event.source == "skill2_rocket_attachment"
        ]
        own_window_count = 0
        other_window_count = 0
        for cycle in self.result.timeline:
            count = sum(
                cycle.full_burst_start <= event.time < cycle.full_burst_end
                for event in attachments
            )
            if cycle.b3_slot == "main_b3":
                own_window_count += count
            else:
                other_window_count += count
        self.assertGreater(own_window_count, other_window_count)

    def test_two_stack_funnel_buffs_differ_between_cycles_5_and_11(self) -> None:
        funnel = standard_funnel_result()
        conventional_c5 = self.result.resolved_offensive_buffs(
            self.result.timeline[4].full_burst_start + 0.1,
            "rapi-red-hood",
        )
        conventional_c11 = self.result.resolved_offensive_buffs(
            self.result.timeline[10].full_burst_start + 0.1,
            "rapi-red-hood",
        )
        funnel_c5 = funnel.resolved_offensive_buffs(
            funnel.timeline[4].full_burst_start + 0.1,
            "rapi-red-hood",
        )
        funnel_c11 = funnel.resolved_offensive_buffs(
            funnel.timeline[10].full_burst_start + 0.1,
            "rapi-red-hood",
        )

        base_caster_flat = 78_707 * 0.6451 + 98_367 * 0.3502
        mast_two_stack_flat = 98_367 * 0.4012
        helm_and_recovery_attack_damage = 27.87 + 20.99
        for buffs in (conventional_c5, conventional_c11):
            self.assertAlmostEqual(buffs.caster_atk_flat, base_caster_flat)
            self.assertAlmostEqual(
                buffs.attack_damage_pct,
                36.24 + helm_and_recovery_attack_damage,
            )
            self.assertEqual(buffs.crit_damage_pct, 12.46)

        for buffs in (funnel_c5, funnel_c11):
            self.assertAlmostEqual(
                buffs.caster_atk_flat,
                base_caster_flat + mast_two_stack_flat,
            )
            self.assertAlmostEqual(buffs.crit_damage_pct, 40.04 + 12.46)
            self.assertAlmostEqual(buffs.distributed_damage_pct, 30.06)

        self.assertAlmostEqual(
            funnel_c5.attack_damage_pct,
            36.24 + 15.04 + helm_and_recovery_attack_damage,
        )
        self.assertAlmostEqual(
            funnel_c11.attack_damage_pct,
            15.04 + helm_and_recovery_attack_damage,
        )

    def test_both_rotations_conserve_the_same_rapi_skill_events(self) -> None:
        funnel = standard_funnel_result()
        sources = (
            "normal_attack",
            "skill2_rocket_attachment",
            "skill2_rocket_explosion",
            "burst_stage3_missile",
        )
        for source in sources:
            with self.subTest(source=source):
                conventional_count = sum(
                    event.source == source for event in self.events
                )
                funnel_count = sum(
                    event.source == source
                    for event in funnel.damage_events_for(actor="rapi-red-hood")
                )
                self.assertEqual(funnel_count, conventional_count)


class RapiRedHoodBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.timeline = (
            BurstCycle(1, 1.0, 1.2, 1.4, 10.0, 20.0, "main_b3"),
        )
        self.context = SkillHookContext(
            actor="rapi-red-hood",
            definition=STANDARD_CHARACTER_CATALOG.require("rapi-red-hood"),
            roster=TeamRoster(),
            timeline=self.timeline,
            duration_sec=180,
        )

    def _shot(self, index: int, time: float) -> WeaponShot:
        return WeaponShot(
            time=time,
            frame=round(time * 60),
            actor="rapi-red-hood",
            shot_index=index,
            magazine_index=0,
            rounds_consumed=1,
            core_eligible=True,
        )

    def _fire(
        self,
        hook: RapiRedHoodSkillHook,
        count: int,
        time: float,
        start_index: int = 0,
    ) -> list[DamageRequest]:
        effects: list[DamageRequest] = []
        for index in range(start_index, start_index + count):
            effects.extend(
                effect
                for effect in hook.on_weapon_shot(
                    self._shot(index, time),
                    self.context,
                )
                if isinstance(effect, DamageRequest)
            )
        return effects

    def test_rocket_storage_respects_full_burst_boundaries(self) -> None:
        hook = RapiRedHoodSkillHook(self.context)
        before = self._fire(hook, 120, 9.99)
        self.assertEqual(
            [effect.source for effect in before],
            ["skill2_rocket_attachment"],
        )

        released = hook.on_battle_event(
            BattleEvent(10.0, 1, EventType.FULL_BURST_ENTER),
            self.context,
        )
        self.assertEqual(
            [effect.source for effect in released if isinstance(effect, DamageRequest)],
            ["skill2_rocket_explosion"],
        )

        during = self._fire(hook, 120, 15.0, 120)
        self.assertEqual(
            [effect.source for effect in during],
            ["skill2_rocket_attachment", "skill2_rocket_explosion"],
        )

        at_end = self._fire(hook, 120, 20.0, 240)
        self.assertEqual(
            [effect.source for effect in at_end],
            ["skill2_rocket_attachment"],
        )

    def test_lower_threshold_ends_exactly_ten_seconds_after_own_burst(self) -> None:
        lowered = RapiRedHoodSkillHook(self.context)
        lowered.on_battle_event(
            BattleEvent(0.0, 1, EventType.B3_STAGE_ENTER, "rapi-red-hood"),
            self.context,
        )
        self.assertFalse(self._fire(lowered, 59, 9.99))
        sixtieth = self._fire(lowered, 1, 9.99, 59)
        self.assertTrue(
            any(effect.source == "skill2_rocket_attachment" for effect in sixtieth)
        )

        expired = RapiRedHoodSkillHook(self.context)
        expired.on_battle_event(
            BattleEvent(0.0, 1, EventType.B3_STAGE_ENTER, "rapi-red-hood"),
            self.context,
        )
        self.assertFalse(self._fire(expired, 119, 10.0))
        one_hundred_twentieth = self._fire(expired, 1, 10.0, 119)
        self.assertTrue(
            any(
                effect.source == "skill2_rocket_attachment"
                for effect in one_hundred_twentieth
            )
        )


if __name__ == "__main__":
    unittest.main()
