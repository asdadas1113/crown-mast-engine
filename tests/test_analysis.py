import math
import unittest
from dataclasses import replace

from crown_mast_engine.analysis import (
    BreakEvenDirection,
    ComparisonCase,
    RotationWinner,
    analyze_mast_expected_hit_loss_sensitivity,
    analyze_rotations,
    compare_damage_totals,
    compare_rotation_results,
)
from crown_mast_engine.combat import CombatSettings
from crown_mast_engine.engine import simulate_rotation
from crown_mast_engine.mechanics import SkillHookRegistry
from crown_mast_engine.models import DamageCategory
from crown_mast_engine.rotations import CROWN_CROWN_MAST, SUSTAINED_FUNNEL
from tests.simulation_fixtures import standard_rotation_comparison


class RotationAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analysis = standard_rotation_comparison()

    def assertDamageEqual(self, left: float, right: float) -> None:
        self.assertTrue(
            math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-6),
            f"damage totals differ: {left} != {right}",
        )

    def test_default_liter_baseline_has_standard_break_even(self) -> None:
        overall = self.analysis.overall
        self.assertEqual(
            overall.comparison_case,
            ComparisonCase.STANDARD_BREAK_EVEN,
        )
        self.assertEqual(overall.observed_winner, RotationWinner.CONVENTIONAL)
        self.assertAlmostEqual(overall.team_c, 2_168_143_852.8701534, delta=1e-3)
        self.assertAlmostEqual(overall.team_f, 2_141_385_963.124464, delta=1e-3)
        self.assertAlmostEqual(overall.g, 0.01704007028958876)
        self.assertAlmostEqual(overall.l, 0.035110280572748453)
        self.assertAlmostEqual(
            overall.team_relative_change,
            -0.012341381182004008,
        )
        self.assertAlmostEqual(
            overall.break_even_main_share_c,
            0.6732510902070452,
        )
        self.assertLess(
            overall.conventional_main_share,
            overall.break_even_main_share_c,
        )

    def test_break_even_forms_are_algebraically_equivalent(self) -> None:
        overall = self.analysis.overall
        self.assertIsNotNone(overall.lambda_star)
        self.assertIsNotNone(overall.g)
        self.assertIsNotNone(overall.l)
        self.assertAlmostEqual(
            overall.lambda_star * overall.delta_r + overall.delta_o,
            0,
            places=6,
        )
        self.assertAlmostEqual(
            overall.break_even_main_share_c,
            overall.l / (overall.g + overall.l),
        )
        self.assertAlmostEqual(overall.local_slope, overall.g + overall.l)
        self.assertEqual(overall.local_extreme_upside, overall.g)
        self.assertAlmostEqual(
            overall.team_relative_change,
            overall.conventional_main_share * overall.g
            - (1 - overall.conventional_main_share) * overall.l,
        )

    def test_character_category_and_source_splits_conserve_totals(self) -> None:
        overall = self.analysis.overall
        self.assertDamageEqual(
            sum(item.conventional for item in self.analysis.by_character.values()),
            overall.team_c,
        )
        self.assertDamageEqual(
            sum(item.funnel for item in self.analysis.by_character.values()),
            overall.team_f,
        )
        self.assertDamageEqual(
            sum(item.conventional for item in self.analysis.by_category.values()),
            overall.team_c,
        )
        self.assertDamageEqual(
            sum(item.funnel for item in self.analysis.by_category.values()),
            overall.team_f,
        )
        self.assertDamageEqual(
            sum(item.conventional for item in self.analysis.by_source.values()),
            overall.team_c,
        )
        self.assertDamageEqual(
            sum(item.funnel for item in self.analysis.by_source.values()),
            overall.team_f,
        )
        for actor, categories in self.analysis.by_character_category.items():
            self.assertDamageEqual(
                sum(item.conventional for item in categories.values()),
                self.analysis.by_character[actor].conventional,
            )
            self.assertDamageEqual(
                sum(item.funnel for item in categories.values()),
                self.analysis.by_character[actor].funnel,
            )
        self.assertEqual(set(self.analysis.by_category), set(DamageCategory))

    def test_macro_cycles_conserve_totals_and_show_local_variation(self) -> None:
        macros = self.analysis.macro_cycles
        self.assertEqual(tuple(macros), (1, 2, 3, 4))
        self.assertDamageEqual(
            sum(item.team_c for item in macros.values()),
            self.analysis.overall.team_c,
        )
        self.assertDamageEqual(
            sum(item.team_f for item in macros.values()),
            self.analysis.overall.team_f,
        )
        self.assertEqual(macros[1].comparison_case, ComparisonCase.EQUAL)
        self.assertEqual(
            macros[2].comparison_case,
            ComparisonCase.STANDARD_BREAK_EVEN,
        )
        local_thresholds = {
            round(item.break_even_main_share_c, 9)
            for item in macros.values()
            if item.break_even_main_share_c is not None
        }
        self.assertGreater(len(local_thresholds), 1)

    def test_burst_cycles_conserve_team_and_character_totals(self) -> None:
        bursts = self.analysis.burst_cycles
        self.assertEqual(tuple(bursts), tuple(range(1, 13)))
        self.assertDamageEqual(
            sum(item.team_c for item in bursts.values()),
            self.analysis.overall.team_c,
        )
        self.assertDamageEqual(
            sum(item.team_f for item in bursts.values()),
            self.analysis.overall.team_f,
        )
        for actor, cycles in self.analysis.by_character_burst_cycle.items():
            self.assertEqual(tuple(cycles), tuple(range(1, 13)))
            self.assertDamageEqual(
                sum(item.conventional for item in cycles.values()),
                self.analysis.by_character[actor].conventional,
            )
            self.assertDamageEqual(
                sum(item.funnel for item in cycles.values()),
                self.analysis.by_character[actor].funnel,
            )

    def test_secondary_b3_and_damage_sources_expose_helm_loss(self) -> None:
        helm = self.analysis.secondary_b3
        self.assertLess(helm.delta, 0)
        self.assertLess(helm.relative_change, 0)
        self.assertGreater(helm.loss_from_funnel, 0)
        self.assertGreater(helm.relative_loss_from_funnel, 0)
        self.assertIn(("helm", "normal_attack"), self.analysis.by_source)
        self.assertIn(("helm", "skill2_full_charge"), self.analysis.by_source)
        self.assertIn(("helm", "burst_nuke"), self.analysis.by_source)

    def test_secondary_b3_mast3_burst_omission_damage_isolated_to_cycles_6_and_12(
        self,
    ) -> None:
        self.assertEqual(
            self.analysis.secondary_b3_mast3_burst_omission_cycles,
            (6, 12),
        )
        cycle_damage = self.analysis.secondary_b3_mast3_burst_omission_cycle_damage
        self.assertEqual(
            self.analysis.secondary_b3_mast3_deprivation_cycles,
            self.analysis.secondary_b3_mast3_burst_omission_cycles,
        )
        self.assertEqual(
            self.analysis.secondary_b3_mast3_deprivation,
            cycle_damage,
        )
        self.assertAlmostEqual(cycle_damage.conventional, 200_320_497.83517963)
        self.assertAlmostEqual(cycle_damage.funnel, 160_607_148.9064402, delta=1e-3)
        self.assertAlmostEqual(cycle_damage.loss_from_funnel, 39_713_348.92873943, delta=1e-3)
        self.assertAlmostEqual(
            cycle_damage.relative_loss_from_funnel,
            0.19824905268264115,
            delta=1e-12,
        )

    def test_mismatched_results_are_rejected(self) -> None:
        mismatched = replace(
            self.analysis.funnel_result,
            combat_settings=CombatSettings(boss_def=999),
        )
        with self.assertRaisesRegex(ValueError, "combat_settings"):
            compare_rotation_results(
                self.analysis.conventional_result,
                mismatched,
            )

    def test_mismatched_mechanics_signatures_are_rejected(self) -> None:
        settings = CombatSettings(duration_sec=7)
        conventional = simulate_rotation(
            CROWN_CROWN_MAST,
            combat_settings=settings,
        )
        incompatible = simulate_rotation(
            SUSTAINED_FUNNEL,
            combat_settings=settings,
            skill_hooks=SkillHookRegistry(),
        )

        self.assertNotEqual(
            conventional.mechanics_signature,
            incompatible.mechanics_signature,
        )
        with self.assertRaisesRegex(ValueError, "mechanics_signature"):
            compare_rotation_results(conventional, incompatible)

    def test_damage_events_are_identical_before_first_policy_divergence(self) -> None:
        conventional = self.analysis.conventional_result
        funnel = self.analysis.funnel_result
        first_divergent_cycle = next(
            conventional_snapshot.cycle
            for conventional_snapshot, funnel_snapshot in zip(
                conventional.snapshots,
                funnel.snapshots,
                strict=True,
            )
            if conventional_snapshot.b2_actor != funnel_snapshot.b2_actor
        )
        divergence_time = conventional.timeline[first_divergent_cycle - 1].b2_time
        conventional_prefix = tuple(
            event for event in conventional.damage_events if event.time < divergence_time
        )
        funnel_prefix = tuple(
            event for event in funnel.damage_events if event.time < divergence_time
        )

        self.assertEqual(len(conventional_prefix), len(funnel_prefix))
        for index, (conventional_event, funnel_event) in enumerate(
            zip(conventional_prefix, funnel_prefix, strict=True)
        ):
            self.assertEqual(
                conventional_event,
                funnel_event,
                f"damage event differs before policy divergence at index {index}",
            )

    def test_damage_event_breakdowns_recompose_final_damage(self) -> None:
        for result in (
            self.analysis.conventional_result,
            self.analysis.funnel_result,
        ):
            for event in result.damage_events:
                breakdown = event.breakdown
                expected_base_atk = max(
                    0.0,
                    breakdown.effective_atk - breakdown.boss_def_now,
                )
                expected_damage = (
                    breakdown.base_atk
                    * breakdown.coefficient
                    * breakdown.major
                    * breakdown.element
                    * breakdown.charge
                    * breakdown.damage_up
                    * breakdown.sequential
                    * breakdown.taken
                    * breakdown.distributed
                )
                self.assertTrue(
                    math.isclose(
                        breakdown.base_atk,
                        expected_base_atk,
                        rel_tol=1e-12,
                        abs_tol=1e-6,
                    ),
                    f"base ATK does not recompose: {event}",
                )
                self.assertTrue(
                    math.isclose(
                        event.damage,
                        expected_damage,
                        rel_tol=1e-12,
                        abs_tol=1e-6,
                    ),
                    f"damage does not recompose: {event}",
                )

    def test_common_damage_scalar_preserves_relative_analysis(self) -> None:
        scalar = 1.37
        scaled = analyze_rotations(
            combat_settings=replace(
                self.analysis.conventional_result.combat_settings,
                element_multiplier=scalar,
            )
        )

        for baseline_result, scaled_result in (
            (self.analysis.conventional_result, scaled.conventional_result),
            (self.analysis.funnel_result, scaled.funnel_result),
        ):
            self.assertEqual(
                len(baseline_result.damage_events),
                len(scaled_result.damage_events),
            )
            for baseline_event, scaled_event in zip(
                baseline_result.damage_events,
                scaled_result.damage_events,
                strict=True,
            ):
                self.assertEqual(
                    (
                        baseline_event.time,
                        baseline_event.actor,
                        baseline_event.source,
                        baseline_event.category,
                        baseline_event.coefficient_pct,
                        baseline_event.traits,
                        baseline_event.shot_index,
                        baseline_event.magazine_index,
                        baseline_event.full_burst,
                        baseline_event.burst_cycle,
                        baseline_event.macro_cycle,
                    ),
                    (
                        scaled_event.time,
                        scaled_event.actor,
                        scaled_event.source,
                        scaled_event.category,
                        scaled_event.coefficient_pct,
                        scaled_event.traits,
                        scaled_event.shot_index,
                        scaled_event.magazine_index,
                        scaled_event.full_burst,
                        scaled_event.burst_cycle,
                        scaled_event.macro_cycle,
                    ),
                )
                self.assertTrue(
                    math.isclose(
                        scaled_event.damage,
                        baseline_event.damage * scalar,
                        rel_tol=1e-12,
                        abs_tol=1e-6,
                    )
                )

        self.assertDamageEqual(
            scaled.overall.team_c,
            self.analysis.overall.team_c * scalar,
        )
        self.assertDamageEqual(
            scaled.overall.team_f,
            self.analysis.overall.team_f * scalar,
        )
        for attribute in (
            "g",
            "l",
            "lambda_star",
            "break_even_main_share_c",
            "conventional_main_share",
            "funnel_main_share",
        ):
            self.assertAlmostEqual(
                getattr(scaled.overall, attribute),
                getattr(self.analysis.overall, attribute),
            )

    def test_short_duration_matches_long_duration_prefix(self) -> None:
        cutoff = 173.0
        long_result = self.analysis.conventional_result
        short_result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=long_result.roster,
            timeline=long_result.timeline,
            catalog=long_result.catalog,
            builds=long_result.builds,
            combat_settings=replace(
                long_result.combat_settings,
                duration_sec=cutoff,
            ),
        )
        long_prefix = tuple(
            event for event in long_result.damage_events if event.time < cutoff
        )

        self.assertEqual(len(short_result.damage_events), len(long_prefix))
        for index, (short_event, long_event) in enumerate(
            zip(short_result.damage_events, long_prefix, strict=True)
        ):
            self.assertEqual(
                short_event,
                long_event,
                f"duration prefix differs at index {index}",
            )


class MastExpectedHitLossSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = analyze_mast_expected_hit_loss_sensitivity()

    def test_default_sweep_preserves_baseline_and_order(self) -> None:
        self.assertEqual(tuple(self.results), (0.0, 18.0, 20.0, 22.0))
        baseline = standard_rotation_comparison()
        self.assertAlmostEqual(
            self.results[0.0].overall.team_c,
            baseline.overall.team_c,
        )
        self.assertAlmostEqual(
            self.results[0.0].overall.team_f,
            baseline.overall.team_f,
        )

    def test_more_expected_hit_loss_reduces_totals_without_flipping_result(self) -> None:
        conventional_totals = [
            result.overall.team_c for result in self.results.values()
        ]
        funnel_totals = [result.overall.team_f for result in self.results.values()]
        self.assertEqual(conventional_totals, sorted(conventional_totals, reverse=True))
        self.assertEqual(funnel_totals, sorted(funnel_totals, reverse=True))
        self.assertTrue(
            all(
                result.overall.observed_winner == RotationWinner.CONVENTIONAL
                for result in self.results.values()
            )
        )

    def test_invalid_or_duplicate_sensitivity_values_are_rejected(self) -> None:
        for values in ((-1,), (34,), (math.nan,), (20, 20)):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    analyze_mast_expected_hit_loss_sensitivity(values)


class BreakEvenCaseTests(unittest.TestCase):
    def test_standard_break_even(self) -> None:
        result = compare_damage_totals(r_c=100, r_f=110, o_c=100, o_f=80)
        self.assertEqual(result.comparison_case, ComparisonCase.STANDARD_BREAK_EVEN)
        self.assertEqual(result.lambda_star, 2)
        self.assertAlmostEqual(result.break_even_main_share_c, 2 / 3)
        self.assertTrue(result.has_scaling_break_even)
        self.assertTrue(result.has_share_break_even)
        self.assertEqual(
            result.break_even_direction,
            BreakEvenDirection.FUNNEL_ABOVE,
        )
        self.assertAlmostEqual(result.require_break_even_main_share_c(), 2 / 3)
        self.assertTrue(result.funnel_wins_above_break_even)

    def test_funnel_dominates(self) -> None:
        result = compare_damage_totals(r_c=100, r_f=110, o_c=100, o_f=105)
        self.assertEqual(result.comparison_case, ComparisonCase.FUNNEL_DOMINATES)
        self.assertEqual(result.observed_winner, RotationWinner.FUNNEL)
        self.assertIsNone(result.lambda_star)
        self.assertIsNone(result.break_even_main_share_c)
        self.assertFalse(result.has_scaling_break_even)
        self.assertFalse(result.has_share_break_even)
        with self.assertRaisesRegex(ValueError, "does not have a standard break-even"):
            result.require_break_even_main_share_c()
        with self.assertRaisesRegex(ValueError, "does not have a standard break-even"):
            _ = result.funnel_wins_above_break_even

    def test_conventional_dominates(self) -> None:
        result = compare_damage_totals(r_c=100, r_f=90, o_c=100, o_f=95)
        self.assertEqual(result.comparison_case, ComparisonCase.CONVENTIONAL_DOMINATES)
        self.assertEqual(result.observed_winner, RotationWinner.CONVENTIONAL)
        self.assertIsNone(result.lambda_star)
        self.assertIsNone(result.break_even_main_share_c)
        self.assertFalse(result.has_scaling_break_even)
        self.assertFalse(result.has_share_break_even)

    def test_tied_policy_response_without_global_tie(self) -> None:
        result = compare_damage_totals(r_c=100, r_f=100, o_c=110, o_f=100)
        self.assertEqual(result.comparison_case, ComparisonCase.NO_SCALING_BREAK_EVEN)
        self.assertEqual(result.observed_winner, RotationWinner.CONVENTIONAL)
        self.assertIsNone(result.lambda_star)
        self.assertIsNone(result.break_even_main_share_c)
        self.assertFalse(result.has_scaling_break_even)
        self.assertFalse(result.has_share_break_even)

    def test_equal_rotations(self) -> None:
        result = compare_damage_totals(r_c=100, r_f=100, o_c=100, o_f=100)
        self.assertEqual(result.comparison_case, ComparisonCase.EQUAL)
        self.assertEqual(result.observed_winner, RotationWinner.EQUAL)
        self.assertIsNone(result.lambda_star)
        self.assertIsNone(result.break_even_main_share_c)

    def test_scaling_break_even_without_valid_share_break_even(self) -> None:
        result = compare_damage_totals(r_c=0, r_f=10, o_c=100, o_f=90)
        self.assertEqual(result.comparison_case, ComparisonCase.SCALING_BREAK_EVEN_ONLY)
        self.assertEqual(result.lambda_star, 1)
        self.assertIsNone(result.break_even_main_share_c)
        self.assertTrue(result.has_scaling_break_even)
        self.assertFalse(result.has_share_break_even)

    def test_observed_tie_uses_explicit_epsilon(self) -> None:
        result = compare_damage_totals(r_c=100, r_f=100 + 1e-10, o_c=0, o_f=0)
        self.assertEqual(result.observed_winner, RotationWinner.EQUAL)

    def test_negative_scaling_is_rejected(self) -> None:
        result = compare_damage_totals(r_c=100, r_f=90, o_c=100, o_f=120)
        self.assertEqual(result.comparison_case, ComparisonCase.NO_SCALING_BREAK_EVEN)
        self.assertEqual(result.observed_winner, RotationWinner.FUNNEL)
        self.assertIsNone(result.lambda_star)
        self.assertIsNone(result.break_even_main_share_c)
        self.assertFalse(result.has_scaling_break_even)
        self.assertFalse(result.has_share_break_even)


if __name__ == "__main__":
    unittest.main()
