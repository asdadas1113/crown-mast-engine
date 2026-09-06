import unittest

from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from crown_mast_engine.combat import CombatSettings
from crown_mast_engine.engine import simulate_rotation
from crown_mast_engine.models import TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST
from crown_mast_engine.timeline import BurstCycle, LEGACY_12_BURST_TIMELINE


def simulate_b1(slug: str, *, catalog=STANDARD_CHARACTER_CATALOG):
    return simulate_rotation(
        CROWN_CROWN_MAST,
        roster=TeamRoster(b1=slug),
        catalog=catalog,
        timeline=LEGACY_12_BURST_TIMELINE,
    )


class B1CharacterCatalogTests(unittest.TestCase):
    def test_anis_star_standard_data(self) -> None:
        anis = STANDARD_CHARACTER_CATALOG.require("anis-star")
        self.assertEqual(anis.unit_class, "Defender")
        self.assertEqual(anis.burst_stage, "I")
        self.assertEqual(anis.weapon.weapon_type, "RL")
        self.assertEqual(anis.weapon.normal_attack_pct, 61.3)
        self.assertEqual(anis.weapon.charge_release_recovery_frames, 0)

    def test_moran_favorite_item_standard_data_models_swap_at_24_per_second(self) -> None:
        moran = STANDARD_CHARACTER_CATALOG.require("moran-favorite-item")
        self.assertEqual(moran.unit_class, "Defender")
        self.assertEqual(moran.weapon.weapon_type, "AR")
        self.assertEqual(moran.weapon.normal_attack_pct, 14.71)
        self.assertEqual(moran.skill_value("burst", "weapon_swap_modeled"), 1)
        self.assertEqual(moran.skill_value("burst", "weapon_swap_fire_rate"), 24)

    def test_little_mermaid_standard_data(self) -> None:
        mermaid = STANDARD_CHARACTER_CATALOG.require("little-mermaid")
        self.assertEqual(mermaid.unit_class, "Supporter")
        self.assertEqual(mermaid.weapon.weapon_type, "SMG")
        self.assertEqual(mermaid.weapon.normal_attack_pct, 10.12)
        self.assertEqual(mermaid.weapon.core_attack_pct, 250)


class B1CharacterMechanicsTests(unittest.TestCase):
    def test_anis_star_buffs_and_damage_packets(self) -> None:
        result = simulate_b1("anis-star")
        active = result.active_buffs(6.0, result.roster.main_b3)
        anis_buffs = {
            buff.stat: buff.value for buff in active if buff.source == "anis-star"
        }
        self.assertEqual(anis_buffs["caster_atk_pct"], 35.01)
        self.assertEqual(anis_buffs["attack_damage_pct"], 34.0)
        self.assertEqual(anis_buffs["projectile_explosion_pct"], 92.03)
        self.assertEqual(result.buff_total(6.0, "anis-star", "atk_pct"), 40.01)
        self.assertEqual(
            result.buff_total(6.0, "anis-star", "charge_time_fixed_frames"),
            42.0,
        )

        stars = [
            event
            for event in result.damage_events_for(actor="anis-star")
            if event.source == "burst_shooting_star"
        ]
        normal = [
            event
            for event in result.damage_events_for(actor="anis-star")
            if event.source == "normal_attack"
        ]
        riders = [
            event
            for event in result.damage_events_for(actor="anis-star")
            if event.source == "skill1_full_charge"
        ]
        self.assertEqual(len(stars), 12 * 40)
        self.assertEqual(len(riders), len(normal))
        self.assertTrue(all(event.traits.projectile_explosion for event in stars))

    def test_moran_applies_favorite_item_buff_and_weapon_swap_damage(self) -> None:
        result = simulate_b1("moran-favorite-item")
        buffs = [
            buff
            for buff in result.active_buffs(6.0, result.roster.main_b3)
            if buff.source == "moran-favorite-item"
            and buff.stat == "caster_atk_pct"
        ]
        self.assertEqual(len(buffs), 1)
        self.assertEqual(buffs[0].value, 42.57)
        moran_events = result.damage_events_for(actor="moran-favorite-item")
        swap = [
            event for event in moran_events
            if event.source == "burst_weapon_attack"
        ]
        fifth_hits = [
            event for event in moran_events
            if event.source == "skill1_weapon_swap_fifth_hit"
        ]
        self.assertEqual(len(swap), 12 * 240)
        self.assertEqual(len(fifth_hits), 12 * 48)
        self.assertTrue(all(event.coefficient_pct == 14.7 for event in swap))
        self.assertTrue(all(event.coefficient_pct == 47.18 for event in fifth_hits))
        self.assertTrue(all(event.traits.core_eligible for event in swap))
        self.assertTrue(all(not event.traits.core_eligible for event in fifth_hits))
        self.assertTrue(all(not event.traits.range_eligible for event in fifth_hits))
        self.assertIn("normal_attack", {event.source for event in moran_events})

    def test_moran_weapon_swap_fire_rate_is_sensitivity_input(self) -> None:
        for rate, expected_shots, expected_fifth_hits in (
            (20.0, 200, 40),
            (23.0, 230, 46),
            (24.0, 240, 48),
        ):
            with self.subTest(rate=rate):
                catalog = STANDARD_CHARACTER_CATALOG.with_skill_value(
                    "moran-favorite-item",
                    "burst",
                    "weapon_swap_fire_rate",
                    rate,
                )
                result = simulate_b1("moran-favorite-item", catalog=catalog)
                moran_events = result.damage_events_for(
                    actor="moran-favorite-item"
                )
                swap = [
                    event for event in moran_events
                    if event.source == "burst_weapon_attack"
                ]
                fifth_hits = [
                    event for event in moran_events
                    if event.source == "skill1_weapon_swap_fifth_hit"
                ]
                self.assertEqual(len(swap), 12 * expected_shots)
                self.assertEqual(len(fifth_hits), 12 * expected_fifth_hits)

    def test_moran_base_weapon_returns_full_when_swap_ends(self) -> None:
        swap_start = 5.2
        swap_end = 15.2
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=TeamRoster(b1="moran-favorite-item"),
            timeline=(
                BurstCycle(1, swap_start, 5.6, 6.0, 6.3, 16.3, "main_b3"),
            ),
            combat_settings=CombatSettings(duration_sec=18.0),
        )
        first_base_shot_after_swap = next(
            event
            for event in result.damage_events_for(actor="moran-favorite-item")
            if event.source == "normal_attack" and event.time >= swap_end
        )
        self.assertLessEqual(first_base_shot_after_swap.time, swap_end + 0.1)

    def test_little_mermaid_team_buffs_damage_and_ammo_trigger(self) -> None:
        result = simulate_b1("little-mermaid")
        main = result.roster.main_b3
        active = result.active_buffs(6.0, main)
        mermaid_buffs = {
            buff.stat: buff.value
            for buff in active
            if buff.source == "little-mermaid"
        }
        self.assertEqual(mermaid_buffs["damage_taken_pct"], 5.05)
        self.assertEqual(mermaid_buffs["attack_damage_pct"], 4.0)
        burst_attack_damage = [
            buff.value
            for buff in active
            if buff.source == "little-mermaid"
            and buff.skill == "burst"
            and buff.stat == "attack_damage_pct"
        ]
        self.assertEqual(burst_attack_damage, [10.13])

        waves = [
            event
            for event in result.damage_events_for(actor="little-mermaid")
            if event.source == "skill2_bubble_wave"
        ]
        barrages = [
            event
            for event in result.damage_events_for(actor="little-mermaid")
            if event.source == "skill2_bubble_barrage"
        ]
        self.assertEqual(len(waves), 12 * 10)
        self.assertGreater(len(barrages), 0)
        self.assertTrue(all(event.breakdown.taken == 1.0505 for event in waves))
        self.assertTrue(all(event.traits.sequential for event in waves + barrages))


if __name__ == "__main__":
    unittest.main()
