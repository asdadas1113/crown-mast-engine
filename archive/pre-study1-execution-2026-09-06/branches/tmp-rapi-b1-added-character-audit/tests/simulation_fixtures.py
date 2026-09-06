from functools import lru_cache

from crown_mast_engine.analysis import RotationComparison, analyze_rotations
from crown_mast_engine.engine import SimulationResult


@lru_cache(maxsize=1)
def standard_rotation_comparison() -> RotationComparison:
    """Return the shared, read-only default C/F comparison for regression tests."""
    return analyze_rotations()


def standard_conventional_result() -> SimulationResult:
    return standard_rotation_comparison().conventional_result


def standard_funnel_result() -> SimulationResult:
    return standard_rotation_comparison().funnel_result


def standard_rotation_results() -> tuple[SimulationResult, SimulationResult]:
    comparison = standard_rotation_comparison()
    return comparison.conventional_result, comparison.funnel_result
