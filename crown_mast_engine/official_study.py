"""Compatibility names for the current official Study 1 definition.

The superseded 29,952-case design is preserved only in Git history and the
pre-revalidation archive. Active callers of ``official_study`` are routed to
the frozen 28,188-case RAID14 Study 1 design so an old import cannot silently
select the retired sample space.
"""

from __future__ import annotations

from .wave_a_study import (
    WAVE_A_B1_CANDIDATES,
    WAVE_A_CORE_HIT_RATE_PCT,
    WAVE_A_DEFENSE_ANCHORS,
    WAVE_A_ENVIRONMENT_COUNT,
    WAVE_A_GROWTH_POINT_COUNT,
    WAVE_A_INVALID_DUPLICATE_ROSTER_COUNT,
    WAVE_A_MAIN_ADVANTAGE_LEVELS,
    WAVE_A_MAIN_B3_CANDIDATES,
    WAVE_A_RAW_ROSTER_COUNT,
    WAVE_A_SCENARIO_COUNT,
    WAVE_A_SCENARIOS_PER_ROSTER,
    WAVE_A_SECONDARY_B3_ANCHORS,
    WAVE_A_STUDY_ID,
    WAVE_A_VALID_ROSTER_COUNT,
    build_wave_a_roster_cases,
    iter_wave_a_rosters,
    wave_a_roster_id,
    wave_a_study_definition,
)


OFFICIAL_STUDY_ID = WAVE_A_STUDY_ID
OFFICIAL_B1_CANDIDATES = WAVE_A_B1_CANDIDATES
OFFICIAL_MAIN_B3_CANDIDATES = WAVE_A_MAIN_B3_CANDIDATES
OFFICIAL_SECONDARY_B3_ANCHORS = WAVE_A_SECONDARY_B3_ANCHORS
OFFICIAL_DEFENSE_ANCHORS = WAVE_A_DEFENSE_ANCHORS
OFFICIAL_CORE_HIT_RATE_PCT = WAVE_A_CORE_HIT_RATE_PCT
OFFICIAL_MAIN_ADVANTAGE_LEVELS = WAVE_A_MAIN_ADVANTAGE_LEVELS
OFFICIAL_RAW_ROSTER_COUNT = WAVE_A_RAW_ROSTER_COUNT
OFFICIAL_INVALID_DUPLICATE_ROSTER_COUNT = WAVE_A_INVALID_DUPLICATE_ROSTER_COUNT
OFFICIAL_VALID_ROSTER_COUNT = WAVE_A_VALID_ROSTER_COUNT
OFFICIAL_GROWTH_POINT_COUNT = WAVE_A_GROWTH_POINT_COUNT
OFFICIAL_ENVIRONMENT_COUNT = WAVE_A_ENVIRONMENT_COUNT
OFFICIAL_SCENARIOS_PER_ROSTER = WAVE_A_SCENARIOS_PER_ROSTER
OFFICIAL_SCENARIO_COUNT = WAVE_A_SCENARIO_COUNT

# Preserve the earlier public names while routing every active official-study
# call to the current frozen design.
official_roster_id = wave_a_roster_id
iter_official_rosters = iter_wave_a_rosters
build_official_roster_cases = build_wave_a_roster_cases
official_study_definition = wave_a_study_definition
