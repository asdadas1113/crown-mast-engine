import json
import unittest
from dataclasses import replace

from crown_mast_engine import (
    COMPARISON_REPORT_SCHEMA_VERSION,
    ComparisonReport,
    LEGACY_12_BURST_TIMELINE,
    OutcomeBand,
    OutcomeThresholds,
    ResearchScenario,
    analyze_entry_variants,
    analyze_first_burst_entry_choice,
    run_research_scenario,
)
from crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG
from tests.simulation_fixtures import standard_rotation_comparison


class ResearchScenarioTests(unittest.TestCase):
    def test_entry_variant_analysis_pairs_matching_openings(self) -> None:
        result = analyze_entry_variants(ResearchScenario.standard())

        self.assertEqual(
            result.crown_entry.conventional_result.policy_name,
            "crown_crown_mast",
        )
        self.assertEqual(
            result.crown_entry.funnel_result.policy_name,
            "sustained_funnel",
        )
        self.assertEqual(
            result.mast_entry.conventional_result.policy_name,
            "opening_mast_crown_mast",
        )
        self.assertEqual(
            result.mast_entry.funnel_result.policy_name,
            "opening_mast_sustained_funnel",
        )
        mast_prefix = tuple(
            snapshot.b2_actor
            for snapshot in result.mast_entry.conventional_result.snapshots[:4]
        )
        self.assertEqual(
            mast_prefix,
            tuple(
                snapshot.b2_actor
                for snapshot in result.mast_entry.funnel_result.snapshots[:4]
            ),
        )
        self.assertAlmostEqual(
            result.mast_entry.overall.team_c - result.crown_entry.overall.team_c,
            result.mast_entry.overall.team_f - result.crown_entry.overall.team_f,
            delta=1e-4,
        )

    def test_standard_scenario_json_round_trip_is_lossless(self) -> None:
        scenario = ResearchScenario.standard()

        restored = ResearchScenario.from_json(scenario.to_json())

        self.assertEqual(restored, scenario)
        self.assertEqual(restored.to_json(), scenario.to_json())

    def test_schema_v1_defaults_to_crown_crown_mast(self) -> None:
        payload = ResearchScenario.standard().to_dict()
        payload["schema_version"] = 1
        del payload["baseline_rotation"]

        restored = ResearchScenario.from_dict(payload)

        self.assertEqual(restored.baseline_rotation, "crown_crown_mast")

    def test_opening_rotation_is_preserved_in_json(self) -> None:
        scenario = replace(
            ResearchScenario.standard(),
            baseline_rotation="opening_mast_crown_mast",
        )

        restored = ResearchScenario.from_json(scenario.to_json())

        self.assertEqual(restored, scenario)

    def test_json_preserves_independent_equipment_and_unbounded_ol_lines(self) -> None:
        scenario = ResearchScenario.standard()
        payload = scenario.to_dict()
        rapi = payload["builds"]["rapi-red-hood"]
        rapi["equipment"]["slot_1"] = "ol5"
        rapi["overload"] = {
            "atk_lines": 10,
            "element_lines": 20,
            "ammo_lines": 100,
        }

        restored = ResearchScenario.from_dict(payload)
        build = restored.builds["rapi-red-hood"]

        self.assertEqual(build.equipment.pieces[0].state.value, "ol5")
        self.assertEqual(build.overload.atk_lines, 10)
        self.assertEqual(build.overload.element_lines, 20)
        self.assertEqual(build.overload.ammo_lines, 100)

    def test_scenario_rejects_missing_roster_build(self) -> None:
        scenario = ResearchScenario.standard()
        builds = dict(scenario.builds)
        del builds["helm"]

        with self.assertRaisesRegex(ValueError, "missing=.*helm"):
            replace(scenario, builds=builds)

    def test_scenario_json_rejects_missing_or_unknown_fields(self) -> None:
        missing = ResearchScenario.standard().to_dict()
        del missing["main_actor"]
        with self.assertRaisesRegex(ValueError, "missing=.*main_actor"):
            ResearchScenario.from_dict(missing)

        extra = ResearchScenario.standard().to_dict()
        extra["unknown"] = True
        with self.assertRaisesRegex(ValueError, "extra=.*unknown"):
            ResearchScenario.from_dict(extra)

    def test_thresholds_classify_raw_relative_change_without_altering_it(self) -> None:
        thresholds = OutcomeThresholds(tie_band_pct=0.1, clear_advantage_pct=0.5)

        self.assertEqual(thresholds.classify(0.001), OutcomeBand.TIE_BAND)
        self.assertEqual(
            thresholds.classify(0.00101),
            OutcomeBand.MARGINAL_FUNNEL,
        )
        self.assertEqual(
            thresholds.classify(-0.005),
            OutcomeBand.CLEAR_CONVENTIONAL,
        )

    def test_revision_mismatch_is_rejected_before_simulation(self) -> None:
        scenario = replace(
            ResearchScenario.standard(),
            expected_engine_rule_revision="incompatible-engine",
        )

        with self.assertRaisesRegex(ValueError, "engine revision"):
            run_research_scenario(scenario)

    def test_skill_override_catalog_requires_matching_saved_revision(self) -> None:
        base = ResearchScenario.standard()
        variant = STANDARD_CHARACTER_CATALOG.with_skill_value(
            "mast-romantic-maid",
            "skill1",
            "expected_normal_damage_loss_per_stack_pct",
            18,
        )
        with self.assertRaisesRegex(ValueError, "catalog revision"):
            run_research_scenario(base, catalog=variant)

        scenario = replace(
            base,
            timeline=(base.timeline[0],),
            combat_settings=replace(base.combat_settings, duration_sec=16),
            expected_catalog_source_revision=variant.scope.source_revision,
        )
        report = run_research_scenario(scenario, catalog=variant)
        saved = report.to_dict()["scenario"]["expected_revisions"]["catalog_source"]
        self.assertEqual(saved, variant.scope.source_revision)
        self.assertIn("skill-override:", saved)

    def test_unknown_baseline_rotation_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported baseline rotation"):
            replace(ResearchScenario.standard(), baseline_rotation="unknown")

    def test_first_entry_effect_clips_unresolved_buff_difference_to_duration(self) -> None:
        standard = ResearchScenario.standard()
        scenario = replace(
            standard,
            timeline=(standard.timeline[0],),
            combat_settings=replace(
                standard.combat_settings,
                duration_sec=16,
            ),
        )

        report = analyze_first_burst_entry_choice(scenario)

        self.assertEqual(report.cycle, 1)
        self.assertEqual(report.window_start, scenario.timeline[0].b1_time)
        self.assertEqual(report.window_end, scenario.combat_settings.duration_sec)
        self.assertNotEqual(report.team.crown_entry, report.team.mast_entry)
        self.assertAlmostEqual(
            sum(item.crown_entry for item in report.by_character.values()),
            report.team.crown_entry,
            delta=1e-3,
        )
        self.assertAlmostEqual(
            sum(item.mast_entry for item in report.by_character.values()),
            report.team.mast_entry,
            delta=1e-3,
        )

    def test_standard_entry_effect_runs_until_buff_states_converge(self) -> None:
        scenario = ResearchScenario.standard()
        variants = analyze_entry_variants(scenario)

        self.assertEqual(variants.first_burst.window_start, 2.2)
        self.assertEqual(variants.first_burst.window_end, 17.32)
        self.assertAlmostEqual(
            variants.first_burst.team.delta_mast_minus_crown,
            variants.mast_entry.overall.team_c
            - variants.crown_entry.overall.team_c,
            delta=1e-4,
        )


class ComparisonReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = replace(
            ResearchScenario.standard(),
            timeline=LEGACY_12_BURST_TIMELINE,
        )
        cls.report = ComparisonReport.from_comparison(
            cls.scenario,
            standard_rotation_comparison(),
        )

    def test_report_preserves_baseline_totals_and_research_metrics(self) -> None:
        overall = self.report.overall

        self.assertAlmostEqual(overall.team.conventional, 2_168_143_852.8701534, delta=1e-3)
        self.assertAlmostEqual(overall.team.funnel, 2_141_385_963.124464, delta=1e-3)
        self.assertAlmostEqual(overall.conventional_main_share, 0.43660107773480095)
        self.assertAlmostEqual(overall.break_even_main_share_c, 0.6732510902070452)
        self.assertEqual(overall.outcome_band, OutcomeBand.CLEAR_CONVENTIONAL)

    def test_report_contains_character_and_cycle_outputs(self) -> None:
        self.assertEqual(set(self.report.by_character), set(self.scenario.roster.members))
        self.assertAlmostEqual(
            sum(
                item.conventional_share
                for item in self.report.by_character.values()
                if item.conventional_share is not None
            ),
            1.0,
        )
        self.assertEqual(tuple(self.report.macro_cycles), (1, 2, 3, 4))
        self.assertEqual(tuple(self.report.burst_cycles), tuple(range(1, 13)))
        self.assertEqual(set(self.report.by_category), {"normal", "skill", "burst"})
        self.assertTrue(self.report.by_source)

    def test_report_json_is_deterministic_and_self_describing(self) -> None:
        first = self.report.to_json(indent=None)
        second = self.report.to_json(indent=None)
        payload = json.loads(first)

        self.assertEqual(first, second)
        self.assertEqual(payload["schema_version"], COMPARISON_REPORT_SCHEMA_VERSION)
        self.assertEqual(
            payload["break_even_methodology"],
            {
                "method": "local_main_damage_scaling",
                "scaled_components": ["main_conventional", "main_funnel"],
                "fixed_components": [
                    "non_main_damage",
                    "event_timing",
                    "buff_windows",
                    "skill_procs",
                ],
                "reported_share_basis": "conventional_total_at_break_even",
            },
        )
        self.assertEqual(payload["scenario"]["main_actor"], "rapi-red-hood")
        self.assertEqual(
            payload["overall"]["outcome_band"],
            "clear_conventional",
        )
        self.assertIn("mechanics_signature", payload)

    def test_report_compatibility_rejects_different_mechanics_revision(self) -> None:
        incompatible_signature = replace(
            self.report.mechanics_signature,
            engine_rule_revision="different-engine",
        )
        incompatible = replace(
            self.report,
            mechanics_signature=incompatible_signature,
        )

        with self.assertRaisesRegex(ValueError, "mechanics signatures"):
            self.report.assert_compatible_with(incompatible)

    def test_report_construction_rejects_scenario_revision_mismatch(self) -> None:
        scenario = replace(
            self.scenario,
            expected_engine_rule_revision="different-engine",
        )

        with self.assertRaisesRegex(ValueError, "engine revision"):
            ComparisonReport.from_comparison(
                scenario,
                standard_rotation_comparison(),
            )

    def test_short_scenario_runs_through_existing_engine(self) -> None:
        scenario = replace(
            self.scenario,
            timeline=(self.scenario.timeline[0],),
            combat_settings=replace(
                self.scenario.combat_settings,
                duration_sec=16,
            ),
        )

        report = run_research_scenario(scenario)

        self.assertEqual(tuple(report.burst_cycles), (1,))
        self.assertGreater(report.overall.team.conventional, 0)
        self.assertEqual(report.scenario, scenario)


if __name__ == "__main__":
    unittest.main()
