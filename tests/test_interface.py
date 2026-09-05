import io
import tomllib
import unittest
from unittest.mock import patch

from crown_mast_engine.interface import (
    WEB_ROOT,
    _aggregate_checkpoint_results,
    calculate_interface_payload,
    build_checkpoint_cases,
    interface_metadata,
    run_server,
)


def standard_payload() -> dict:
    actors = (
        "liter",
        "crown",
        "mast-romantic-maid",
        "rapi-red-hood",
        "helm",
    )
    return {
        "roster": {
            "b1": "liter",
            "main_b3": "rapi-red-hood",
            "secondary_b3": "helm",
        },
        "builds": {
            actor: {
                "gear_states": {
                    "slot_1": "base5",
                    "slot_2": "base5",
                    "slot_3": "base5",
                    "slot_4": "base5",
                },
                "collection_stage": (
                    "SR15" if actor == "helm" else "none"
                ),
                "atk_lines": 0,
                "element_lines": 0,
                "ammo_lines": 0,
            }
            for actor in actors
        },
        "combat": {
            "boss_def": 140,
            "boss_element": None,
            "core_hit_rate_pct": 0,
            "range_bonus_pct": 0,
        },
    }


class InterfaceTests(unittest.TestCase):
    def test_batch_report_exposes_png_export_and_upright_y_axis(self) -> None:
        html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
        css = (WEB_ROOT / "styles.css").read_text(encoding="utf-8")
        script = (WEB_ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="batch-png-button"', html)
        self.assertIn('/vendor/html2canvas.min.js', html)
        self.assertIn("text-orientation: upright", css)
        self.assertNotIn(".y-axis-title { display: grid; place-items: center; color: var(--muted); font-size: 9px; writing-mode: vertical-rl; transform: rotate(180deg);", css)
        self.assertIn("async function exportBatchPng()", script)
        self.assertIn('id="baseline-options"', html)
        self.assertIn('id="first-burst-character-body"', html)
        self.assertIn('id="four-character-body"', html)
        self.assertIn('id="crown-comparison-card"', html)
        self.assertIn('id="mast-comparison-card"', html)
        self.assertIn("data-baseline-template", html)
        self.assertIn("baseline_rotation", script)
        self.assertGreater((WEB_ROOT / "vendor" / "html2canvas.min.js").stat().st_size, 100_000)
        self.assertTrue((WEB_ROOT / "vendor" / "html2canvas.LICENSE.txt").is_file())

    def test_reset_discards_visible_build_rows_before_rerender(self) -> None:
        script = (WEB_ROOT / "app.js").read_text(encoding="utf-8")
        start = script.index("function setDefaults()")
        end = script.index("function collectPayload()", start)
        reset_block = script[start:end]
        self.assertIn("state.builds.clear();", reset_block)
        self.assertIn("buildRows.replaceChildren();", reset_block)
        self.assertLess(
            reset_block.index("buildRows.replaceChildren();"),
            reset_block.index("syncB3Options"),
        )

    def test_server_banner_runs_with_cp949_stdout(self) -> None:
        buffer = io.BytesIO()
        stdout = io.TextIOWrapper(buffer, encoding="cp949")
        with patch("crown_mast_engine.interface.ThreadingHTTPServer") as server_type:
            server_type.return_value.serve_forever.side_effect = KeyboardInterrupt
            with patch("sys.stdout", stdout):
                run_server()
                stdout.flush()
        self.assertIn(b"Crown-Mast interface:", buffer.getvalue())

    def test_package_data_declares_vendor_assets(self) -> None:
        pyproject = WEB_ROOT.parents[1] / "pyproject.toml"
        payload = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        patterns = payload["tool"]["setuptools"]["package-data"]["crown_mast_engine"]
        self.assertIn("web/vendor/*.js", patterns)
        self.assertIn("web/vendor/*.txt", patterns)

    def test_checkpoint_aggregate_preserves_ranges_groups_and_extremes(self) -> None:
        def result(case_id, b1, dealer, change, share, break_even, c_share, f_share):
            margin = share - break_even
            return {
                "case_id": case_id,
                "labels": {"b1_label": b1, "dealer_label": dealer},
                "summary": {
                    "relative_change": change,
                    "conventional_main_share": share,
                    "break_even_main_share_c": break_even,
                    "margin": margin,
                    "outcome_band": (
                        "clear_funnel"
                        if change > 0
                        else "clear_conventional"
                    ),
                    "character_shares": {
                        "main": {"conventional": c_share, "funnel": f_share}
                    },
                },
                "report": {
                    "scenario": {
                        "roster": {"main_b3": "main"},
                        "baseline_rotation": "crown_crown_mast",
                        "combat_settings": {"duration_sec": 180},
                        "thresholds": {
                            "tie_band_pct": 0.1,
                            "clear_advantage_pct": 0.5,
                        },
                    },
                    "mechanics_signature": {"engine_rule_revision": "test"},
                },
            }

        aggregate = _aggregate_checkpoint_results(
            [
                result("a", "Low", "Equal", -0.02, 0.4, 0.7, 0.4, 0.45),
                result("b", "Low", "Gap", 0.01, 0.6, 0.62, 0.6, 0.65),
                result("c", "High", "Equal", -0.01, 0.5, 0.65, 0.5, 0.55),
            ]
        )
        self.assertEqual(aggregate["sample_count"], 3)
        self.assertEqual(aggregate["outcomes"]["conventional_wins"], 2)
        self.assertEqual(aggregate["outcomes"]["funnel_wins"], 1)
        self.assertEqual(
            aggregate["outcomes"]["bands"]["clear_conventional"],
            2,
        )
        self.assertAlmostEqual(aggregate["relative_change"]["average"], -0.02 / 3)
        self.assertEqual(
            aggregate["extremes"]["most_funnel_favorable"]["case_id"], "b"
        )
        self.assertEqual(
            aggregate["extremes"]["closest_to_break_even"]["case_id"], "b"
        )
        self.assertEqual(len(aggregate["by_b1_profile"]), 2)
        self.assertAlmostEqual(
            aggregate["character_shares"]["main"]["funnel"]["average"],
            0.55,
        )

    def test_metadata_exposes_only_stage_appropriate_options(self) -> None:
        metadata = interface_metadata()
        self.assertTrue(metadata["b1_options"])
        self.assertTrue(metadata["b3_options"])
        self.assertEqual(
            {item["burst_stage"] for item in metadata["b1_options"]},
            {"I"},
        )
        self.assertEqual(
            {item["burst_stage"] for item in metadata["b3_options"]},
            {"III"},
        )
        self.assertEqual(
            {item["id"] for item in metadata["baseline_rotations"]},
            {"crown_crown_mast", "opening_mast_crown_mast"},
        )

    def test_calculation_uses_existing_research_report(self) -> None:
        result = calculate_interface_payload(standard_payload())
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(
            set(result["comparisons"]),
            {"crown_entry", "mast_entry"},
        )
        crown = result["comparisons"]["crown_entry"]
        mast = result["comparisons"]["mast_entry"]
        self.assertEqual(crown["schema_version"], 3)
        self.assertEqual(mast["schema_version"], 3)
        self.assertGreater(crown["overall"]["team"]["conventional"], 0)
        self.assertGreater(mast["overall"]["team"]["funnel"], 0)
        self.assertEqual(
            set(result["display_names"]),
            set(crown["by_character"]),
        )
        self.assertEqual(result["scenario"]["baseline_rotation"], "crown_crown_mast")
        first = result["first_burst_entry_comparison"]
        self.assertEqual(first["cycle"], 1)
        self.assertEqual(
            first["window_semantics"],
            "b1_activation_inclusive_to_entry_buff_state_convergence_exclusive",
        )
        self.assertEqual(first["window_end"], 17.32)
        self.assertNotEqual(
            first["team"]["crown_entry"],
            first["team"]["mast_entry"],
        )
        self.assertAlmostEqual(
            result["entry_effects"]["conventional"]["team"][
                "delta_mast_minus_crown"
            ],
            result["entry_effects"]["funnel"]["team"][
                "delta_mast_minus_crown"
            ],
            delta=1e-4,
        )

    def test_single_calculator_returns_both_entries_regardless_of_batch_option(self) -> None:
        payload = standard_payload()
        payload["baseline_rotation"] = "opening_mast_crown_mast"

        result = calculate_interface_payload(payload)

        self.assertEqual(
            result["scenario"]["baseline_rotation"],
            "crown_crown_mast",
        )
        self.assertEqual(
            result["comparisons"]["mast_entry"]["scenario"][
                "baseline_rotation"
            ],
            "opening_mast_crown_mast",
        )

    def test_duplicate_b3_is_rejected_before_simulation(self) -> None:
        payload = standard_payload()
        payload["roster"]["secondary_b3"] = "rapi-red-hood"
        payload["builds"].pop("helm")
        with self.assertRaisesRegex(ValueError, "같은 캐릭터"):
            calculate_interface_payload(payload)

    def test_build_keys_must_follow_selected_roster(self) -> None:
        payload = standard_payload()
        payload["builds"].pop("helm")
        with self.assertRaisesRegex(ValueError, "builds fields do not match"):
            calculate_interface_payload(payload)

    def test_mixed_gear_slots_are_preserved_in_report(self) -> None:
        payload = standard_payload()
        payload["builds"]["rapi-red-hood"]["gear_states"] = {
            "slot_1": "ol5",
            "slot_2": "ol0",
            "slot_3": "base5",
            "slot_4": "ol5",
        }
        result = calculate_interface_payload(payload)
        self.assertEqual(
            result["scenario"]["builds"]["rapi-red-hood"]["equipment"],
            payload["builds"]["rapi-red-hood"]["gear_states"],
        )

    def test_collection_stage_is_preserved_in_report(self) -> None:
        payload = standard_payload()
        payload["builds"]["rapi-red-hood"]["collection_stage"] = "SR15"
        result = calculate_interface_payload(payload)
        self.assertEqual(
            result["scenario"]["builds"]["rapi-red-hood"]["collection"],
            "SR15",
        )

    def test_checkpoint_grid_combines_three_b1_and_four_dealer_profiles(self) -> None:
        payload = standard_payload()
        cases = build_checkpoint_cases(
            {"roster": payload["roster"], "combat": payload["combat"]}
        )
        self.assertEqual(len(cases), 12)
        self.assertEqual(len({case.case_id for case in cases}), 12)
        self.assertEqual(
            {case.labels["b1_profile"] for case in cases},
            {"b1-low", "b1-standard", "b1-high"},
        )
        self.assertEqual(
            len({case.labels["dealer_profile"] for case in cases}),
            4,
        )

    def test_checkpoint_grid_preserves_opening_baseline_rotation(self) -> None:
        payload = standard_payload()
        cases = build_checkpoint_cases(
            {
                "roster": payload["roster"],
                "combat": payload["combat"],
                "baseline_rotation": "opening_mast_crown_mast",
            }
        )
        self.assertEqual(
            {case.scenario.baseline_rotation for case in cases},
            {"opening_mast_crown_mast"},
        )

    def test_favorite_item_b1_keeps_sr15_in_low_checkpoint(self) -> None:
        payload = standard_payload()
        payload["roster"]["b1"] = "moran-favorite-item"
        payload["builds"].pop("liter")
        payload["builds"]["moran-favorite-item"] = payload["builds"]["helm"].copy()
        cases = build_checkpoint_cases(
            {"roster": payload["roster"], "combat": payload["combat"]}
        )
        low = next(case for case in cases if case.labels["b1_profile"] == "b1-low")
        self.assertEqual(
            low.scenario.builds["moran-favorite-item"].collection.stage,
            "SR15",
        )


if __name__ == "__main__":
    unittest.main()
