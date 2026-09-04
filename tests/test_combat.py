import unittest

from crown_mast_engine.characters import WeaponProfile
from crown_mast_engine.combat import (
    CombatSettings,
    DamageRequest,
    SharedChargeWeaponMode,
    effective_charge_frames,
    effective_max_ammo,
    effective_reload_frames,
    generate_weapon_shots,
)
from crown_mast_engine.buffs import BuffWindow
from crown_mast_engine.engine import simulate_rotation
from crown_mast_engine.equipment import BuildProfile, GearState, OverloadProfile
from crown_mast_engine.mechanics import SkillHookBase, SkillHookRegistry
from crown_mast_engine.models import DamageCategory, EventType
from crown_mast_engine.damage import DamageTraits
from crown_mast_engine.rotations import CROWN_CROWN_MAST
from tests.simulation_fixtures import standard_conventional_result


def weapon(
    weapon_type: str,
    *,
    ammo: int = 300,
    reload_frames: int = 171,
    hits_per_shot: int = 1,
) -> WeaponProfile:
    return WeaponProfile(
        weapon_type=weapon_type,
        normal_attack_pct=10,
        core_attack_pct=200,
        ammo=ammo,
        reload_frames=reload_frames,
        charge_frames=0,
        charge_multiplier_pct=0,
        hits_per_shot=hits_per_shot,
        burst_gauge_per_shot=0,
    )


class WeaponTimingTests(unittest.TestCase):
    def test_default_combat_settings_use_generic_raid_defense(self) -> None:
        self.assertEqual(CombatSettings().boss_def, 12_000)

    def test_reload_formula_matches_pinned_runtime(self) -> None:
        self.assertEqual(effective_reload_frames(171, 0), 180)
        self.assertEqual(effective_reload_frames(171, 100), 13)
        self.assertEqual(effective_reload_frames(171, 89.47), 31)

    def test_ar_cadence_spends_magazine_then_reloads(self) -> None:
        shots = generate_weapon_shots(
            actor="test-ar",
            weapon=weapon("AR", ammo=2, reload_frames=0),
            duration_sec=1,
            startup_delay_frames=0,
        )
        self.assertEqual([shot.frame for shot in shots[:4]], [4, 9, 27, 32])
        self.assertEqual([shot.magazine_index for shot in shots[:4]], [0, 0, 1, 1])
        self.assertEqual(
            [shot.last_bullet for shot in shots[:4]],
            [False, True, False, True],
        )

    def test_disabled_window_freezes_reload_progress(self) -> None:
        shots = generate_weapon_shots(
            actor="test-ar",
            weapon=weapon("AR", ammo=2, reload_frames=0),
            duration_sec=1,
            disabled_at=lambda time: 10 / 60 <= time < 20 / 60,
            startup_delay_frames=0,
        )
        self.assertEqual([shot.frame for shot in shots[:4]], [4, 9, 37, 42])

    def test_instant_reload_uses_live_max_ammo(self) -> None:
        shots = generate_weapon_shots(
            actor="test-ar",
            weapon=weapon("AR", ammo=2, reload_frames=60),
            duration_sec=1,
            max_ammo_pct_at=lambda time: 50 if time >= 20 / 60 else 0,
            instant_reload_at=lambda time: round(time * 60) == 20,
            startup_delay_frames=0,
        )
        self.assertEqual(
            [shot.frame for shot in shots[:5]],
            [4, 9, 24, 29, 34],
        )
        self.assertEqual(
            [shot.magazine_index for shot in shots[:5]],
            [0, 0, 1, 1, 1],
        )

    def test_partial_ammo_charge_adds_a_fraction_of_live_max_ammo(self) -> None:
        kwargs = dict(
            actor="test-ar",
            weapon=weapon("AR", ammo=10, reload_frames=60),
            duration_sec=1.5,
            startup_delay_frames=0,
        )
        baseline = generate_weapon_shots(**kwargs)
        partial = generate_weapon_shots(
            **kwargs,
            instant_reload_at=lambda time: 50.0 if round(time * 60) == 30 else 0.0,
        )
        full = generate_weapon_shots(
            **kwargs,
            instant_reload_at=lambda time: round(time * 60) == 30,
        )
        self.assertGreater(len(partial), len(baseline))
        self.assertLessEqual(len(partial), len(full))

    def test_ammo_charge_applies_while_weapon_is_disabled(self) -> None:
        shots = generate_weapon_shots(
            actor="test-ar",
            weapon=weapon("AR", ammo=2, reload_frames=60),
            duration_sec=1,
            disabled_at=lambda time: 10 / 60 <= time < 30 / 60,
            instant_reload_at=lambda time: 50.0 if round(time * 60) == 20 else 0.0,
            startup_delay_frames=0,
        )
        self.assertEqual([shot.frame for shot in shots[:3]], [4, 9, 34])

    def test_fixed_charge_frames_override_charge_speed(self) -> None:
        charged = WeaponProfile(
            weapon_type="RL",
            normal_attack_pct=61.3,
            core_attack_pct=200,
            ammo=20,
            reload_frames=141,
            charge_frames=60,
            charge_multiplier_pct=250,
            hits_per_shot=1,
            burst_gauge_per_shot=0,
            charge_release_recovery_frames=0,
        )
        shots = generate_weapon_shots(
            actor="test-rl",
            weapon=charged,
            duration_sec=3,
            charge_speed_at=lambda _time: 90,
            fixed_charge_frames_at=lambda _time: 42,
            startup_delay_frames=0,
        )
        self.assertEqual([shot.frame for shot in shots[:4]], [41, 83, 125, 167])

    def test_mg_uses_windup_ladder(self) -> None:
        shots = generate_weapon_shots(
            actor="test-mg",
            weapon=weapon("MG"),
            duration_sec=1,
            startup_delay_frames=0,
        )
        self.assertEqual([shot.frame for shot in shots[:5]], [0, 22, 36, 46, 54])
        self.assertTrue(all(not shot.core_eligible for shot in shots[:5]))

    def test_smg_rate_uses_min_firing_rounds_adjusted_twenty_four_per_second(self) -> None:
        shots = generate_weapon_shots(
            actor="test-smg",
            weapon=weapon("SMG"),
            duration_sec=1,
            startup_delay_frames=0,
        )
        self.assertEqual(len(shots), 24)
        self.assertEqual([shot.frame for shot in shots[:4]], [2, 4, 7, 9])

    def test_charge_weapon_uses_charge_release_and_reload_frames(self) -> None:
        charged = WeaponProfile(
            weapon_type="SR",
            normal_attack_pct=69.04,
            core_attack_pct=200,
            ammo=6,
            reload_frames=141,
            charge_frames=60,
            charge_multiplier_pct=250,
            hits_per_shot=1,
            burst_gauge_per_shot=5.6,
        )
        shots = generate_weapon_shots(
            actor="test-sr",
            weapon=charged,
            duration_sec=15,
            startup_delay_frames=0,
        )
        self.assertEqual(
            [shot.frame for shot in shots[:7]],
            [59, 141, 223, 305, 387, 469, 701],
        )
        self.assertTrue(all(shot.charged for shot in shots))
        self.assertTrue(shots[5].last_bullet)
        self.assertEqual(shots[6].magazine_index, 1)

    def test_shared_charge_mode_consumes_the_base_weapon_magazine(self) -> None:
        charged = WeaponProfile(
            weapon_type="SR",
            normal_attack_pct=10,
            core_attack_pct=200,
            ammo=3,
            reload_frames=0,
            charge_frames=60,
            charge_multiplier_pct=250,
            hits_per_shot=1,
            burst_gauge_per_shot=0,
            charge_release_recovery_frames=0,
        )
        mode = SharedChargeWeaponMode(
            name="test-mode",
            start=1,
            end=5,
            charge_frames=120,
            max_shots=2,
            source="test-mode-shot",
            coefficient_pct=99,
            session=0,
        )
        shots = generate_weapon_shots(
            actor="test-sr",
            weapon=charged,
            duration_sec=8,
            startup_delay_frames=0,
            shared_charge_modes=(mode,),
        )

        self.assertEqual([shot.frame for shot in shots[:4]], [59, 179, 299, 372])
        self.assertEqual(
            [shot.weapon_mode for shot in shots[:4]],
            [None, "test-mode", "test-mode", None],
        )
        self.assertEqual(
            [shot.magazine_index for shot in shots[:4]],
            [0, 0, 0, 1],
        )
        self.assertTrue(shots[2].last_bullet)
        self.assertEqual(shots[1].coefficient_pct, 99)

    def test_charge_speed_is_subtractive_and_capped(self) -> None:
        self.assertEqual(effective_charge_frames(60, 0), 60)
        self.assertEqual(effective_charge_frames(60, 50), 30)
        self.assertEqual(effective_charge_frames(60, 100), 1)
        self.assertEqual(effective_charge_frames(60, 150), 1)
        self.assertEqual(effective_charge_frames(60, -100), 120)

    def test_max_ammo_is_resolved_when_reload_completes(self) -> None:
        self.assertEqual(effective_max_ammo(120, 45.17), 174)
        shots = generate_weapon_shots(
            actor="test-ar",
            weapon=weapon("AR", ammo=2, reload_frames=0),
            duration_sec=1,
            max_ammo_pct_at=lambda time: 50 if time < 0.5 else 0,
            startup_delay_frames=0,
        )
        second_magazine = [shot for shot in shots if shot.magazine_index == 1]
        self.assertEqual([shot.frame for shot in second_magazine], [27, 32, 37])
        self.assertTrue(second_magazine[-1].last_bullet)

    def test_max_ammo_rounds_each_source_group_before_adding(self) -> None:
        self.assertEqual(
            effective_max_ammo(
                300,
                max_ammo_pct_groups=(68.93, 9.5),
            ),
            536,
        )
        self.assertEqual(effective_max_ammo(300, 78.43), 535)

    def test_permanent_overload_ammo_applies_to_the_first_magazine(self) -> None:
        shots = generate_weapon_shots(
            actor="test-ar",
            weapon=weapon("AR", ammo=2, reload_frames=60),
            duration_sec=0.5,
            initial_max_ammo_pct_groups=(68.93,),
            max_ammo_pct_groups_at=lambda _time: (68.93,),
            startup_delay_frames=0,
        )
        self.assertEqual(len([shot for shot in shots if shot.magazine_index == 0]), 3)
        self.assertTrue(shots[2].last_bullet)


class RotationDamageTests(unittest.TestCase):
    def test_rapi_extra_advantage_activates_ol_element_against_electric(self) -> None:
        build = BuildProfile.uniform(
            GearState.BASE5,
            OverloadProfile(element_lines=4),
        )
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            builds={"rapi-red-hood": build},
            combat_settings=CombatSettings(
                boss_def=0,
                boss_element="Electric",
                duration_sec=1,
            ),
        )
        rapi = result.damage_events_for(actor="rapi-red-hood")[0]
        crown = result.damage_events_for(actor="crown")[0]
        mast = result.damage_events_for(actor="mast-romantic-maid")[0]
        self.assertAlmostEqual(rapi.breakdown.element, 2.0424)
        self.assertEqual(crown.breakdown.element, 1.1)
        self.assertEqual(mast.breakdown.element, 1.0)

    def test_overload_atk_is_independent_from_equipment_state(self) -> None:
        overload = OverloadProfile(atk_lines=1)
        for state in (GearState.BASE5, GearState.OL0, GearState.OL5):
            with self.subTest(state=state):
                result = simulate_rotation(
                    CROWN_CROWN_MAST,
                    builds={
                        "rapi-red-hood": BuildProfile.uniform(state, overload),
                    },
                    combat_settings=CombatSettings(boss_def=0, duration_sec=1),
                )
                first = result.damage_events_for(actor="rapi-red-hood")[0]
                self.assertAlmostEqual(
                    first.breakdown.effective_atk,
                    result.static_atk("rapi-red-hood") * 1.1181,
                )

    def test_overload_element_only_activates_against_weak_boss(self) -> None:
        build = BuildProfile.uniform(
            GearState.BASE5,
            OverloadProfile(element_lines=1),
        )
        neutral = simulate_rotation(
            CROWN_CROWN_MAST,
            builds={"rapi-red-hood": build},
            combat_settings=CombatSettings(boss_def=0, duration_sec=1),
        )
        advantaged = simulate_rotation(
            CROWN_CROWN_MAST,
            builds={"rapi-red-hood": build},
            combat_settings=CombatSettings(
                boss_def=0,
                boss_element="Wind",
                duration_sec=1,
            ),
        )
        self.assertAlmostEqual(
            advantaged.damage_total("rapi-red-hood")
            / neutral.damage_total("rapi-red-hood"),
            1.3356,
        )
        self.assertAlmostEqual(
            advantaged.damage_total("crown") / neutral.damage_total("crown"),
            1.0,
        )

    def test_actor_element_override_takes_priority_over_automatic_overload(self) -> None:
        build = BuildProfile.uniform(
            GearState.BASE5,
            OverloadProfile(element_lines=100),
        )
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            builds={"rapi-red-hood": build},
            combat_settings=CombatSettings(
                boss_def=0,
                boss_element="Wind",
                element_multiplier_by_actor={"rapi-red-hood": 2.0},
                duration_sec=1,
            ),
        )
        self.assertTrue(
            all(
                event.breakdown.element == 2.0
                for event in result.damage_events_for(actor="rapi-red-hood")
            )
        )

    def test_default_combat_duration_includes_the_180_second_tail(self) -> None:
        result = standard_conventional_result()
        tail = [event for event in result.damage_events if event.time > 173]
        self.assertTrue(tail)
        self.assertLess(max(event.time for event in result.damage_events), 180)

    def test_rotation_generates_normal_damage_for_catalog_members(self) -> None:
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            combat_settings=CombatSettings(duration_sec=10),
        )
        normal_events = result.damage_events_for(category=DamageCategory.NORMAL)
        actors = {event.actor for event in normal_events}
        self.assertEqual(
            actors,
            {
                result.roster.crown,
                result.roster.mast,
                result.roster.b1,
                result.roster.main_b3,
                result.roster.secondary_b3,
            },
        )
        self.assertGreater(result.damage_total(result.roster.crown), 0)
        self.assertGreater(result.damage_total(result.roster.mast), 0)
        self.assertGreater(result.damage_total(result.roster.main_b3), 0)
        self.assertLess(len(normal_events), len(result.damage_events))

    def test_actor_specific_element_multiplier_does_not_affect_teammates(self) -> None:
        base = simulate_rotation(
            CROWN_CROWN_MAST,
            combat_settings=CombatSettings(boss_def=0, duration_sec=1),
        )
        rapi_advantage = simulate_rotation(
            CROWN_CROWN_MAST,
            combat_settings=CombatSettings(
                boss_def=0,
                duration_sec=1,
                element_multiplier_by_actor={"rapi-red-hood": 1.1},
            ),
        )
        self.assertAlmostEqual(
            rapi_advantage.damage_total("rapi-red-hood")
            / base.damage_total("rapi-red-hood"),
            1.1,
        )
        self.assertEqual(
            rapi_advantage.damage_total("crown"),
            base.damage_total("crown"),
        )

    def test_boss_defense_is_applied_at_the_base_atk_layer(self) -> None:
        low_def = simulate_rotation(
            CROWN_CROWN_MAST,
            combat_settings=CombatSettings(boss_def=0, duration_sec=10),
        )
        high_def = simulate_rotation(
            CROWN_CROWN_MAST,
            combat_settings=CombatSettings(boss_def=50_000, duration_sec=10),
        )
        self.assertLess(high_def.damage_total(), low_def.damage_total())
        first = high_def.damage_events[0]
        self.assertEqual(first.breakdown.boss_def_now, 50_000)

    def test_full_burst_and_mast_crit_buffs_reach_damage_context(self) -> None:
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            combat_settings=CombatSettings(boss_def=0, duration_sec=7),
        )
        crown_events = result.damage_events_for(actor=result.roster.crown)
        before_b1 = next(event for event in crown_events if event.time < 3.9)
        in_full_burst = next(event for event in crown_events if event.full_burst)
        self.assertAlmostEqual(before_b1.breakdown.major, 1.075)
        self.assertGreater(in_full_burst.breakdown.major, before_b1.breakdown.major)
        self.assertGreater(
            in_full_burst.breakdown.effective_atk,
            before_b1.breakdown.effective_atk,
        )

    def test_mast_drunken_hit_loss_tracks_live_stack(self) -> None:
        result = standard_conventional_result()
        mast = result.roster.mast
        self.assertEqual(result.buff_total(3.8, mast, "normal_attack_pct"), 0)
        self.assertEqual(result.buff_total(4.0, mast, "normal_attack_pct"), -20)
        self.assertEqual(result.buff_total(19.0, mast, "normal_attack_pct"), -40)
        self.assertEqual(result.buff_total(34.0, mast, "normal_attack_pct"), -60)
        self.assertEqual(result.buff_total(44.3, mast, "normal_attack_pct"), 0)

        mast_normals = result.damage_events_for(
            actor=mast,
            category=DamageCategory.NORMAL,
        )
        d1 = next(event for event in mast_normals if 3.9 <= event.time < 18.3)
        d2 = next(event for event in mast_normals if 18.3 <= event.time < 32.7)
        d3 = next(event for event in mast_normals if 32.7 <= event.time < 44.3)
        self.assertAlmostEqual(d1.breakdown.coefficient, 0.0557 * 0.8)
        self.assertAlmostEqual(d2.breakdown.coefficient, 0.0557 * 0.6)
        self.assertAlmostEqual(d3.breakdown.coefficient, 0.0557 * 0.4)

    def test_mast_does_not_fire_during_hangover(self) -> None:
        result = standard_conventional_result()
        mast_normals = result.damage_events_for(
            actor=result.roster.mast,
            category=DamageCategory.NORMAL,
        )
        hangovers = [
            (event.time, event.payload["until"])
            for event in result.events
            if event.event_type == EventType.HANGOVER_START
        ]
        self.assertEqual(len(hangovers), 4)
        for start, end in hangovers:
            self.assertFalse(
                any(start <= event.time < end for event in mast_normals),
                f"Mast fired during Hangover: {start} <= shot < {end}",
            )

    def test_damage_events_are_attributed_to_burst_and_macro_cycles(self) -> None:
        result = standard_conventional_result()
        first = result.damage_events[0]
        tail = next(event for event in result.damage_events if event.time > 173)
        self.assertEqual((first.burst_cycle, first.macro_cycle), (1, 1))
        self.assertEqual((tail.burst_cycle, tail.macro_cycle), (12, 4))
        self.assertTrue(result.damage_events_for(macro_cycle=4))
        self.assertTrue(
            all(event.macro_cycle == 4 for event in result.damage_events_for(macro_cycle=4))
        )

    def test_character_skill_hook_emits_buffs_and_damage_requests(self) -> None:
        class TestHook(SkillHookBase):
            def scheduled_buffs(self, events, context):
                return (
                    BuffWindow(
                        source=context.actor,
                        skill="test_setup",
                        stat="atk_pct",
                        value=100,
                        target=context.actor,
                        start=0,
                        end=1,
                    ),
                )

            def on_battle_event(self, event, context):
                if event.event_type != EventType.FULL_BURST_ENTER or event.cycle != 1:
                    return ()
                return (
                    DamageRequest(
                        time=event.time + 0.1,
                        actor=context.actor,
                        source="test_skill",
                        category=DamageCategory.SKILL,
                        coefficient_pct=100,
                        traits=DamageTraits(category=DamageCategory.SKILL),
                    ),
                )

        result = simulate_rotation(
            CROWN_CROWN_MAST,
            combat_settings=CombatSettings(boss_def=0, duration_sec=7),
            skill_hooks=SkillHookRegistry({"crown": lambda _context: TestHook()}),
        )
        first_crown = result.damage_events_for(actor="crown")[0]
        skill = next(event for event in result.damage_events if event.source == "test_skill")
        self.assertAlmostEqual(first_crown.breakdown.effective_atk, result.static_atk("crown") * 2)
        self.assertEqual(skill.category, DamageCategory.SKILL)
        self.assertTrue(skill.full_burst)
        self.assertEqual((skill.burst_cycle, skill.macro_cycle), (1, 1))


if __name__ == "__main__":
    unittest.main()
