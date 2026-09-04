from __future__ import annotations

from typing import Iterator

from .checkpoints_v3 import (
    CHECKPOINT_V3_POINT_COUNT,
    build_checkpoint_v3_cases,
    main_advantage_boss_element,
)
from .combat import CombatSettings
from .models import TeamRoster
from .samples import SampleCase


OFFICIAL_STUDY_ID = "crown-mast-secondary-opportunity-v1"

# Final B1 sample. Rapi: Red Hood is allowed here through the audited
# Combat Assist B1 path even though her catalog burst stage is III.
OFFICIAL_B1_CANDIDATES = (
    "liter",
    "anis-star",
    "moran-favorite-item",
    "little-mermaid",
    "rapi-red-hood",
)

# Main B3 sample refined before the first official batch. Bready, Milk:
# Blooming Bunny, and Quency: Escape Queen remain available for diagnostic
# work but are excluded from the official Main axis. Neon: Vision Eye is
# promoted into the official Main sample. Secondary anchors stay outside this
# axis so Main and Secondary roles remain independent in the canonical grid.
OFFICIAL_MAIN_B3_CANDIDATES = (
    "rapi-red-hood",
    "scarlet-black-shadow",
    "cinderella",
    "cinderella-crystal-wave",
    "liberalio",
    "neon-vision-eye",
    "phantom",
    "raven",
)

OFFICIAL_SECONDARY_B3_ANCHORS = (
    "epinel",
    "helm",
    "snow-white-heavy-arms",
)

# Core is a controlled sensitivity axis. "on" means a fully available core:
# every otherwise core-eligible normal attack is treated as a core hit.
OFFICIAL_CORE_HIT_RATE_PCT = {
    "off": 0.0,
    "on": 100.0,
}

OFFICIAL_MAIN_ADVANTAGE_LEVELS = ("off", "on")

OFFICIAL_RAW_ROSTER_COUNT = (
    len(OFFICIAL_B1_CANDIDATES)
    * len(OFFICIAL_MAIN_B3_CANDIDATES)
    * len(OFFICIAL_SECONDARY_B3_ANCHORS)
)
OFFICIAL_INVALID_DUPLICATE_ROSTER_COUNT = 3
OFFICIAL_VALID_ROSTER_COUNT = 117
OFFICIAL_ENVIRONMENT_COUNT = (
    len(OFFICIAL_CORE_HIT_RATE_PCT) * len(OFFICIAL_MAIN_ADVANTAGE_LEVELS)
)
OFFICIAL_SCENARIOS_PER_ROSTER = CHECKPOINT_V3_POINT_COUNT * OFFICIAL_ENVIRONMENT_COUNT
OFFICIAL_SCENARIO_COUNT = OFFICIAL_VALID_ROSTER_COUNT * OFFICIAL_SCENARIOS_PER_ROSTER


def official_roster_id(roster: TeamRoster) -> str:
    return (
        f"b1-{roster.b1}"
        f"--main-{roster.main_b3}"
        f"--secondary-{roster.secondary_b3}"
    )


def iter_official_rosters() -> Iterator[TeamRoster]:
    """Yield the canonical valid rosters, excluding duplicates before construction."""
    for b1 in OFFICIAL_B1_CANDIDATES:
        for main_b3 in OFFICIAL_MAIN_B3_CANDIDATES:
            for secondary_b3 in OFFICIAL_SECONDARY_B3_ANCHORS:
                members = (
                    b1,
                    "crown",
                    "mast-romantic-maid",
                    main_b3,
                    secondary_b3,
                )
                if len(set(members)) != len(members):
                    continue
                yield TeamRoster(
                    b1=b1,
                    main_b3=main_b3,
                    secondary_b3=secondary_b3,
                )


def _combat_settings_for(
    roster: TeamRoster,
    *,
    core_condition: str,
    main_advantage: str,
) -> CombatSettings:
    try:
        core_hit_rate_pct = OFFICIAL_CORE_HIT_RATE_PCT[core_condition]
    except KeyError as exc:
        raise ValueError(f"unsupported core condition: {core_condition}") from exc
    if main_advantage not in OFFICIAL_MAIN_ADVANTAGE_LEVELS:
        raise ValueError(f"unsupported main advantage condition: {main_advantage}")

    # The advantage axis is a real boss-element condition, not a Main-only
    # artificial multiplier. Same-element teammates therefore benefit normally.
    boss_element = (
        None
        if main_advantage == "off"
        else main_advantage_boss_element(roster.main_b3)
    )
    return CombatSettings(
        core_hit_rate_pct=core_hit_rate_pct,
        boss_element=boss_element,
    )


def build_official_roster_cases(roster: TeamRoster) -> tuple[SampleCase, ...]:
    """Build one 256-scenario canonical roster shard without executing it."""
    valid_roster_ids = {official_roster_id(item) for item in iter_official_rosters()}
    roster_id = official_roster_id(roster)
    if roster_id not in valid_roster_ids:
        raise ValueError(f"roster is outside the official study sample: {roster_id}")

    cases: list[SampleCase] = []
    for core_condition in OFFICIAL_CORE_HIT_RATE_PCT:
        for main_advantage in OFFICIAL_MAIN_ADVANTAGE_LEVELS:
            environment_id = (
                f"core-{core_condition}--main-advantage-{main_advantage}"
            )
            condition_id = f"{OFFICIAL_STUDY_ID}--{roster_id}--{environment_id}"
            checkpoint_cases = build_checkpoint_v3_cases(
                roster=roster,
                combat_settings=_combat_settings_for(
                    roster,
                    core_condition=core_condition,
                    main_advantage=main_advantage,
                ),
                condition_id=condition_id,
            )
            for case in checkpoint_cases:
                labels = dict(case.labels)
                labels.update(
                    {
                        "study_id": OFFICIAL_STUDY_ID,
                        "roster_id": roster_id,
                        "b1_candidate": roster.b1,
                        "main_b3_candidate": roster.main_b3,
                        "secondary_anchor": roster.secondary_b3,
                        "core_condition": core_condition,
                        "core_hit_rate_pct": str(
                            OFFICIAL_CORE_HIT_RATE_PCT[core_condition]
                        ),
                        "main_advantage": main_advantage,
                        "boss_element": (
                            case.scenario.combat_settings.boss_element or "neutral"
                        ),
                    }
                )
                cases.append(
                    SampleCase(
                        case_id=case.case_id,
                        scenario=case.scenario,
                        labels=labels,
                    )
                )

    if len(cases) != OFFICIAL_SCENARIOS_PER_ROSTER:
        raise AssertionError("official roster shard size does not match definition")
    return tuple(cases)


def official_study_definition() -> dict[str, object]:
    valid_rosters = tuple(iter_official_rosters())
    if len(valid_rosters) != OFFICIAL_VALID_ROSTER_COUNT:
        raise AssertionError("official valid roster count does not match definition")

    return {
        "study_id": OFFICIAL_STUDY_ID,
        "b1_candidates": list(OFFICIAL_B1_CANDIDATES),
        "main_b3_candidates": list(OFFICIAL_MAIN_B3_CANDIDATES),
        "secondary_b3_anchors": list(OFFICIAL_SECONDARY_B3_ANCHORS),
        "growth_axes": {"b1": 4, "main_b3": 4, "secondary_b3": 4},
        "growth_points_per_environment": CHECKPOINT_V3_POINT_COUNT,
        "environment_axes": {
            "core": dict(OFFICIAL_CORE_HIT_RATE_PCT),
            "main_advantage": list(OFFICIAL_MAIN_ADVANTAGE_LEVELS),
        },
        "raw_roster_count": OFFICIAL_RAW_ROSTER_COUNT,
        "invalid_duplicate_rosters": OFFICIAL_INVALID_DUPLICATE_ROSTER_COUNT,
        "valid_roster_count": OFFICIAL_VALID_ROSTER_COUNT,
        "environments_per_roster": OFFICIAL_ENVIRONMENT_COUNT,
        "scenarios_per_roster": OFFICIAL_SCENARIOS_PER_ROSTER,
        "scenario_count": OFFICIAL_SCENARIO_COUNT,
        "duplicate_policy": (
            "exclude duplicate actors before TeamRoster construction; "
            "current canonical exclusions are the three Rapi B1/Main pairs"
        ),
        "main_advantage_policy": (
            "use the real boss element that the Main B3 naturally beats; "
            "same-element teammates also receive normal elemental advantage"
        ),
        "core_policy": (
            "off=0% eligible core-hit rate; on=100% eligible core-hit rate; "
            "this is a controlled sensitivity axis, not an encounter-frequency claim"
        ),
        "sharding": "one valid roster per shard, 256 scenarios per shard",
    }
