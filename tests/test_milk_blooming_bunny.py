import unittest

from crown_mast_engine import simulate_rotation
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST


MILK_ROSTER = TeamRoster(main_b3="milk-blooming-bunny")


class MilkBloomingBunnyMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = simulate_rotation(CROWN_CROWN_MAST, roster=MILK_ROSTER)
        cls.actor = "milk-blooming-bunny"

    def test_data_matches_pinned_auto_basis(self) -> None:
        unit = self.result.catalog.require(self.actor)
        self.assertEqual(unit.progression_atk, 109_209)
        self.assertEqual(unit.element, "Iron")
        self.assertEqual(unit.weapon.weapon_type, "SR")
        self.assertEqual(unit.weapon.normal_attack_pct, 69.04)
        self.assertEqual(unit.weapon.ammo, 6)
        self.assertEqual(unit.weapon.reload_frames, 141)
        self.assertEqual(unit.weapon.charge_frames, 60)
        self.assertEqual(unit.weapon.charge_multiplier_pct, 250)
        self.assertEqual(unit.skill_value("skill2", "overconfident_distributed_damage_pct"), 447.7)
        self.assertEqual(unit.skill_value("burst", "pierce_damage_pct"), 117.64)
        self.assertEqual(unit.skill_value("burst", "atk_pct"), 220)

    def test_own_burst_applies_atk_and_collapsed_pierce_windows(self) -> None:
        burst_times = tuple(
            event.time for event in self.result.events
            if event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == self.actor
        )
        atk_windows = tuple(
            window for window in self.result.buffs.windows
            if window.source == self.actor and window.skill == "burst_atk"
        )
        pierce_windows = tuple(
            window for window in self.result.buffs.windows
            if window.source == self.actor
            and window.skill == "burst_pierce_collapsed"
        )
        self.assertEqual(tuple(window.start for window in atk_windows), burst_times)
        self.assertEqual(tuple(window.start for window in pierce_windows), burst_times)
        self.assertTrue(all(window.value == 220 for window in atk_windows))
        self.assertTrue(all(window.value == 117.64 for window in pierce_windows))

    def test_each_own_burst_emits_five_distributed_ticks(self) -> None:
        burst_times = tuple(
            event.time for event in self.result.events
            if event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == self.actor
        )
        riders = tuple(
            event for event in self.result.damage_events_for(
                actor=self.actor,
                category=DamageCategory.SKILL,
            )
            if event.source == "skill2_overconfident_distributed"
        )
        self.assertEqual(len(riders), len(burst_times) * 5)
        self.assertTrue(all(event.coefficient_pct == 447.7 for event in riders))
        self.assertTrue(all(event.traits.distributed for event in riders))
        for burst_time in burst_times:
            times = tuple(
                event.time for event in riders
                if burst_time < event.time <= burst_time + 10.000001
            )
            self.assertEqual(
                times,
                tuple(round(burst_time + 2 * tick, 6) for tick in range(1, 6)),
            )

    def test_manual_embarrassment_route_is_not_emitted(self) -> None:
        self.assertFalse(
            any(
                "embarrassment" in event.source
                for event in self.result.damage_events_for(actor=self.actor)
            )
        )
        self.assertFalse(
            any(
                "embarrassment" in window.skill
                for window in self.result.buffs.windows
                if window.source == self.actor
            )
        )


if __name__ == "__main__":
    unittest.main()
