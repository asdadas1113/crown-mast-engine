import unittest

from crown_mast_engine.buffs import BuffBook, BuffWindow


def make_buff(*, start: float, end: float, value: float = 10) -> BuffWindow:
    return BuffWindow(
        source="crown",
        skill="skill2_recovery",
        stat="attack_damage_pct",
        value=value,
        target="rapi-red-hood",
        start=start,
        end=end,
    )


class BuffBookRefreshTests(unittest.TestCase):
    def test_same_start_refresh_replaces_window_without_zero_duration_entry(self) -> None:
        book = BuffBook()
        book.apply(make_buff(start=10, end=17, value=10))
        book.apply(make_buff(start=10, end=18, value=20))

        self.assertEqual(book.windows, (make_buff(start=10, end=18, value=20),))
        self.assertTrue(all(window.start < window.end for window in book.windows))
        self.assertEqual(book.total(10, "rapi-red-hood", "attack_damage_pct"), 20)

    def test_later_refresh_closes_previous_window_and_appends_new_window(self) -> None:
        book = BuffBook()
        book.apply(make_buff(start=10, end=17, value=10))
        book.apply(make_buff(start=12, end=19, value=20))

        self.assertEqual(
            book.windows,
            (
                make_buff(start=10, end=12, value=10),
                make_buff(start=12, end=19, value=20),
            ),
        )

    def test_zero_duration_window_is_not_recorded(self) -> None:
        book = BuffBook()
        book.apply(make_buff(start=10, end=10))

        self.assertEqual(book.windows, ())

    def test_negative_duration_window_is_rejected(self) -> None:
        book = BuffBook()
        with self.assertRaisesRegex(ValueError, "end before start"):
            book.apply(make_buff(start=10, end=9))

    def test_close_uses_source_skill_without_affecting_other_windows(self) -> None:
        book = BuffBook()
        book.apply(make_buff(start=10, end=20, value=10))
        book.apply(
            BuffWindow(
                source="liter",
                skill="burst",
                stat="attack_damage_pct",
                value=20,
                target="rapi-red-hood",
                start=10,
                end=20,
            )
        )

        book.close("crown", "skill2_recovery", 15)

        self.assertEqual(book.total(16, "rapi-red-hood", "attack_damage_pct"), 20)

    def test_single_pass_offensive_resolution_matches_individual_totals(self) -> None:
        book = BuffBook()
        windows = (
            BuffWindow("self", "skill", "atk_pct", 12, "rapi", 1, 10),
            BuffWindow("team", "burst", "attack_damage_pct", 20, "rapi", 1, 10),
            BuffWindow("team", "burst", "crit_rate_pct", 8, "rapi", 1, 10),
            BuffWindow(
                "liter",
                "burst",
                "caster_atk_pct",
                30,
                "rapi",
                1,
                10,
                caster="liter",
            ),
            BuffWindow("expired", "skill", "atk_pct", 99, "rapi", 0, 1),
            BuffWindow("other", "skill", "atk_pct", 99, "helm", 1, 10),
        )
        for window in windows:
            book.apply(window)

        resolved = book.resolve_offensive(
            5,
            "rapi",
            lambda actor: {"liter": 1_000}[actor],
        )

        self.assertEqual(resolved.atk_pct, book.total(5, "rapi", "atk_pct"))
        self.assertEqual(
            resolved.attack_damage_pct,
            book.total(5, "rapi", "attack_damage_pct"),
        )
        self.assertEqual(resolved.crit_rate_pct, 8)
        self.assertEqual(resolved.caster_atk_flat, 300)


if __name__ == "__main__":
    unittest.main()
