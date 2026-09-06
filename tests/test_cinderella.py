import unittest

from crown_mast_engine import LEGACY_12_BURST_TIMELINE, simulate_rotation
from crown_mast_engine.character_mechanics import STANDARD_SKILL_HOOKS
from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST
from crown_mast_engine.weapon_cadence import generate_weapon_shots


CINDERELLA_ROSTER = TeamRoster(main_b3="cinderella", secondary_b3="helm")


class CinderellaMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.actor = "cinderella"
        cls.result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=CINDERELLA_ROSTER,
            timeline=LEGACY_12_BURST_TIMELINE,
        )

    def test_catalog_matches_audited_original_cinderella(self) -> None:
        definition = STANDARD_CHARACTER_CATALOG.require(self.actor)
        self.assertEqual(definition.unit_class, "Defender")
        self.assertEqual(definition.burst_stage, "III")
        self.assertEqual(definition.element, "Electric")
        self.assertEqual(definition.progression_atk, 72_828)
        self.assertEqual(definition.progression_hp, 3_001_443)
        self.assertEqual(definition.weapon.weapon_type, "RL")
        self.assertEqual(definition.weapon.normal_attack_pct, 32.11)
        self.assertEqual(definition.weapon.ammo, 24)
        self.assertEqual(definition.weapon.charge_frames, 60)
        self.assertEqual(definition.weapon.charge_multiplier_pct, 200)
        self.assertEqual(definition.weapon.full_charge_trigger_charge_speed_pct, 100)
        self.assertTrue(definition.weapon.full_charge_trigger_resets_on_reload)
        self.assertEqual(definition.weapon.charge_cycle_floor_frames, 20)
        self.assertEqual(definition.skill_value("burst", "damage_pct"), 1365.92)
        self.assertEqual(definition.skill_value("burst", "sequential_hits"), 10)

    def test_triggered_rl_cadence_accelerates_then_resets_after_real_reload(self) -> None:
        weapon = STANDARD_CHARACTER_CATALOG.require(self.actor).weapon
        shots = generate_weapon_shots(
            actor=self.actor,
            weapon=weapon,
            duration_sec=16.0,
            startup_delay_frames=8,
        )
        self.assertGreaterEqual(len(shots), 26)
        self.assertEqual(shots[1].frame - shots[0].frame, 20)
        self.assertEqual(shots[23].frame - shots[22].frame, 20)
        # The 24-round magazine reloads, then the +100% charge-speed state must
        # be earned again with a normal 1-second full charge.
        self.assertGreater(shots[24].frame - shots[23].frame, 150)
        self.assertEqual(shots[25].frame - shots[24].frame, 20)

    def test_beautiful_accumulates_every_three_seconds_to_twelve_stacks(self) -> None:
        windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor and window.skill == "skill2_beautiful"
        )
        self.assertEqual(len(windows), 12)
        self.assertEqual(tuple(window.start for window in windows), tuple(range(3, 37, 3)))
        self.assertAlmostEqual(windows[-1].value, 19.2)
        self.assertAlmostEqual(
            self.result.buff_total(36.1, self.actor, "max_hp_pct"),
            19.2,
        )

    def test_b3_stage_entry_refreshes_hp_to_atk_even_when_helm_casts(self) -> None:
        b3_events = tuple(
            event
            for event in self.result.events
            if event.event_type == EventType.B3_STAGE_ENTER
        )
        helm_times = tuple(event.time for event in b3_events if event.actor == "helm")
        self.assertTrue(helm_times)
        hp_to_atk_windows = tuple(
            window
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "skill1_flawless_glass"
            and window.stat == "max_hp_to_atk_pct"
        )
        self.assertEqual(
            tuple(window.start for window in hp_to_atk_windows),
            tuple(event.time for event in b3_events),
        )
        self.assertTrue(all(window.value == 2.71 for window in hp_to_atk_windows))
        self.assertTrue(
            all(
                abs((window.end - window.start) - 10.0) < 1e-9
                for window in hp_to_atk_windows
            )
        )

    def test_hp_to_atk_uses_final_max_hp_and_current_growth_build(self) -> None:
        # Standard Cinderella: progression HP + Base5 Defender HP.
        static_hp = 3_001_443 + 48_477 + 157_551 + 36_359
        time = next(
            window.start + 0.01
            for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "skill1_flawless_glass"
            and window.start >= 3.0
        )
        max_hp_pct = self.result.buff_total(time, self.actor, "max_hp_pct")
        resolved = self.result.resolved_offensive_buffs(time, self.actor)
        ordinary_caster_flat = self.result.buffs.caster_atk_flat(
            time,
            self.actor,
            self.result.static_atk,
        )
        expected_hp_flat = static_hp * (1 + max_hp_pct / 100) * 0.0271
        self.assertAlmostEqual(
            resolved.caster_atk_flat - ordinary_caster_flat,
            expected_hp_flat,
            places=5,
        )

    def test_full_charge_additional_packet_follows_every_cinderella_shot(self) -> None:
        normals = self.result.damage_events_for(
            actor=self.actor,
            category=DamageCategory.NORMAL,
        )
        additional = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.SKILL,
            )
            if event.source == "skill1_full_charge_additional"
        )
        self.assertEqual(len(additional), len(normals))
        self.assertTrue(all(event.coefficient_pct == 136.6 for event in additional))
        self.assertEqual(
            tuple(event.shot_index for event in additional),
            tuple(event.shot_index for event in normals),
        )

    def test_own_burst_emits_ten_hit_base_and_beautiful_packets(self) -> None:
        burst_times = tuple(
            event.time
            for event in self.result.events
            if event.event_type == EventType.B3_STAGE_ENTER and event.actor == self.actor
        )
        base = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.BURST,
            )
            if event.source == "burst_glass_slippers_full_contact"
        )
        bonus = tuple(
            event
            for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.BURST,
            )
            if event.source == "burst_beautiful_additional"
        )
        self.assertEqual(tuple(event.time for event in base), burst_times)
        self.assertTrue(all(event.coefficient_pct == 1365.92 for event in base))
        self.assertTrue(all(event.breakdown.sequential == 10 for event in base))
        self.assertTrue(all(not event.full_burst for event in base))
        # First own burst can occur before Beautiful has a stack; later ones must
        # receive the stack-scaled same-target rider.
        self.assertGreaterEqual(len(bonus), max(1, len(base) - 1))
        self.assertTrue(all(event.breakdown.sequential == 10 for event in bonus))
        for event in bonus:
            stacks = event.coefficient_pct / 28.9
            self.assertAlmostEqual(stacks, round(stacks), places=9)
            self.assertGreaterEqual(stacks, 1)
            self.assertLessEqual(stacks, 12)

    def test_standard_registry_contains_cinderella(self) -> None:
        factories = dict(STANDARD_SKILL_HOOKS.mechanics_signature.skill_hook_factories)
        self.assertIn(self.actor, factories)
        self.assertIn(
            "cinderella",
            STANDARD_SKILL_HOOKS.mechanics_signature.skill_hook_revision,
        )


if __name__ == "__main__":
    unittest.main()
