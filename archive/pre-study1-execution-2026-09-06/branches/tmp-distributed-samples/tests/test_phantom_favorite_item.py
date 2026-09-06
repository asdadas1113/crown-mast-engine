import unittest

from crown_mast_engine import CombatSettings, simulate_rotation
from crown_mast_engine.equipment import standard_build_for_actor
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


PHANTOM_ROSTER = TeamRoster(main_b3="phantom")


class PhantomFavoriteItemMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(CROWN_CROWN_MAST, roster=PHANTOM_ROSTER)
        cls.actor = "phantom"

    def test_data_matches_pinned_favorite_item_basis(self) -> None:
        unit = self.result.catalog.require(self.actor)
        self.assertEqual(unit.name, "Phantom (Favorite Item)")
        self.assertEqual(unit.progression_atk, 109_209)
        self.assertEqual(unit.element, "Water")
        self.assertEqual(unit.weapon.weapon_type, "AR")
        self.assertEqual(unit.weapon.normal_attack_pct, 15.78)
        self.assertEqual(unit.weapon.ammo, 60)
        self.assertEqual(unit.weapon.reload_frames, 141)
        self.assertEqual(unit.weapon.burst_gauge_per_shot, 0.25)
        self.assertEqual(unit.skill_value("skill2", "max_stack_distributed_damage_pct"), 250)
        self.assertEqual(unit.skill_value("burst", "damage_pct"), 1457.28)

    def test_favorite_item_forces_sr15_collection(self) -> None:
        self.assertEqual(standard_build_for_actor(self.actor).collection.stage, "SR15")
        self.assertEqual(self.result.collection_profile(self.actor).stage, "SR15")

    def test_dagger_consume_emits_plain_and_distributed_hits(self) -> None:
        skill_events = self.result.damage_events_for(
            actor=self.actor,
            category=DamageCategory.SKILL,
        )
        plain = tuple(
            event for event in skill_events
            if event.source == "skill2_max_stack_additional"
        )
        distributed = tuple(
            event for event in skill_events
            if event.source == "skill2_max_stack_distributed"
        )
        self.assertTrue(plain)
        self.assertEqual(len(plain), len(distributed))
        self.assertTrue(all(event.coefficient_pct == 84.33 for event in plain))
        self.assertTrue(all(not event.traits.distributed for event in plain))
        self.assertTrue(all(event.coefficient_pct == 250 for event in distributed))
        self.assertTrue(all(event.traits.distributed for event in distributed))

    def test_distributed_amp_builds_and_burst_resets_it(self) -> None:
        windows = tuple(
            window for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "skill2_dist_amp"
            and window.stat == "distributed_damage_pct"
        )
        self.assertTrue(any(window.value == 12.86 for window in windows))
        self.assertTrue(any(window.value == 0 for window in windows))
        self.assertLessEqual(max(window.value for window in windows), 38.58 + 1e-9)

    def test_burst_is_distributed_and_expands_magazine(self) -> None:
        burst_times = tuple(
            event.time for event in self.result.events
            if event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == self.actor
        )
        nukes = tuple(
            event for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.BURST,
            )
            if event.source == "burst_distributed"
        )
        self.assertEqual(tuple(event.time for event in nukes), burst_times)
        self.assertTrue(all(event.coefficient_pct == 1457.28 for event in nukes))
        self.assertTrue(all(event.traits.distributed for event in nukes))
        ammo_windows = tuple(
            window for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "burst_max_ammo"
        )
        self.assertEqual(tuple(window.start for window in ammo_windows), burst_times)
        self.assertTrue(all(window.value == 50 for window in ammo_windows))

    def test_fire_boss_activates_team_vulnerability(self) -> None:
        fire = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=PHANTOM_ROSTER,
            combat_settings=CombatSettings(boss_element="Fire"),
        )
        first_burst = next(
            event.time for event in fire.events
            if event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == self.actor
        )
        for member in dict.fromkeys(fire.roster.members):
            self.assertEqual(
                fire.buff_total(first_burst + 0.001, member, "damage_taken_pct"),
                18,
            )

    def test_non_fire_boss_does_not_activate_vulnerability(self) -> None:
        neutral = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=PHANTOM_ROSTER,
            combat_settings=CombatSettings(boss_element="Iron"),
        )
        self.assertFalse(
            any(
                window.source == self.actor
                and window.skill == "burst_fire_vulnerability"
                for window in neutral.buffs.windows
            )
        )


if __name__ == "__main__":
    unittest.main()
