import unittest

from crown_mast_engine.character_mechanics.liter import LiterSkillHook
from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from crown_mast_engine.mechanics import SkillHookContext
from crown_mast_engine.models import EventType
from tests.simulation_fixtures import standard_rotation_results


class LiterMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.conventional, cls.funnel = standard_rotation_results()

    def test_liter_casts_every_burst_cycle_in_both_rotations(self) -> None:
        for result in (self.conventional, self.funnel):
            with self.subTest(policy=result.policy_name):
                casts = [
                    event
                    for event in result.events
                    if event.event_type == EventType.B1_CAST
                    and event.actor == "liter"
                ]
                self.assertEqual([event.cycle for event in casts], list(range(1, 13)))
                self.assertTrue(result.damage_events_for(actor="liter"))

    def test_first_cast_grants_max_ammo_and_burst_atk_only(self) -> None:
        buffs = self.conventional.resolved_offensive_buffs(4.0, "rapi-red-hood")
        self.assertEqual(
            self.conventional.buff_total(
                4.0,
                "rapi-red-hood",
                "max_ammo_pct",
            ),
            45.17,
        )
        self.assertEqual(buffs.atk_pct, 66)
        self.assertEqual(buffs.crit_damage_pct, 0)

    def test_second_cast_adds_crit_damage(self) -> None:
        buffs = self.conventional.resolved_offensive_buffs(18.4, "rapi-red-hood")
        self.assertEqual(
            self.conventional.buff_total(
                18.4,
                "rapi-red-hood",
                "max_ammo_pct",
            ),
            45.17,
        )
        self.assertEqual(buffs.atk_pct, 66)
        self.assertEqual(buffs.crit_damage_pct, 12.46)

    def test_third_and_later_casts_add_both_atk_buffs(self) -> None:
        for time in (32.8, 61.4, 147.7):
            with self.subTest(time=time):
                buffs = self.conventional.resolved_offensive_buffs(
                    time,
                    "rapi-red-hood",
                )
                self.assertAlmostEqual(buffs.atk_pct, 66 + 14.42)
                self.assertEqual(buffs.crit_damage_pct, 12.46)
                self.assertEqual(
                    self.conventional.buff_total(
                        time,
                        "rapi-red-hood",
                        "max_ammo_pct",
                    ),
                    45.17,
                )

    def test_five_second_buffs_expire_at_the_exact_boundary(self) -> None:
        self.assertEqual(
            self.conventional.buff_total(8.899, "crown", "atk_pct"),
            66,
        )
        self.assertEqual(
            self.conventional.buff_total(8.9, "crown", "atk_pct"),
            0,
        )
        self.assertEqual(
            self.conventional.buff_total(8.9, "crown", "max_ammo_pct"),
            0,
        )

    def test_liter_cover_repair_does_not_emit_recovery(self) -> None:
        context = SkillHookContext(
            actor="liter",
            definition=STANDARD_CHARACTER_CATALOG.require("liter"),
            roster=self.conventional.roster,
            timeline=self.conventional.timeline,
            duration_sec=180,
        )
        hook = LiterSkillHook(context)
        self.assertTrue(
            all(
                tuple(hook.on_battle_event(event, context)) == ()
                for event in self.conventional.events
            )
        )


if __name__ == "__main__":
    unittest.main()
