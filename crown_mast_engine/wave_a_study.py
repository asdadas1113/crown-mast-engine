from __future__ import annotations

from itertools import product
from typing import Iterator

from .characters import STANDARD_CHARACTER_CATALOG
from .checkpoints_v3 import REALISTIC_GROWTH_PROFILES, main_advantage_boss_element
from .combat import CombatSettings
from .equipment import BuildProfile, GearState, SR15_COLLECTION
from .models import TeamRoster
from .research import ResearchScenario
from .rotations import OPENING_MAST_CROWN_MAST
from .samples import SampleCase
from .timeline import RAID14_TIMELINE


WAVE_A_DRAFT_ID = "wave-a-verified-core-draft-v1"

# Verified-core allowlists only. Unresolved timing actors and hit/spread-sensitive
# Quency remain diagnostic-only until their corresponding model gate is cleared.
WAVE_A_B1_CANDIDATES = (
    "liter",
    "anis-star",
    "little-mermaid",
    "rapi-red-hood",
)

WAVE_A_MAIN_B3_CANDIDATES = (
    "rapi-red-hood",
    "cinderella",
    "cinderella-crystal-wave",
    "neon-vision-eye",
    "phantom",
    "bready",
)

WAVE_A_SECONDARY_B3_ANCHORS = (
    "epinel",
    "helm",
    "snow-white-heavy-arms",
)

WAVE_A_BLOCKED_ACTORS = frozenset(
    {
        "moran-favorite-item",
        "scarlet-black-shadow",
        "liberalio",
        "raven",
        "quency-escape-queen",
        "milk-blooming-bunny",
    }
)

# These are controlled sensitivity anchors, not encounter-frequency weights and
# not a claim that one value is the universal Solo/Union Raid defense.
WAVE_A_DEFENSE_ANCHORS = {
    "low-140": 140.0,
    "representative-12000": 12_000.0,
    "high-31784": 31_784.0,
}

WAVE_A_CORE_HIT_RATE_PCT = {
    "off": 0.0,
    "on": 100.0,
}
WAVE_A_MAIN_ADVANTAGE_LEVELS = ("off", "on")

WAVE_A_GROWTH_POINT_COUNT = 16
WAVE_A_RAW_ROSTER_COUNT = (
    len(WAVE_A_B1_CANDIDATES)
    * len(WAVE_A_MAIN_B3_CANDIDATES)
    * len(WAVE_A_SECONDARY_B3_ANCHORS)
)
WAVE_A_INVALID_DUPLICATE_ROSTER_COUNT = 3
WAVE_A_VALID_ROSTER_COUNT = 69
WAVE_A_ENVIRONMENT_COUNT = (
    len(WAVE_A_DEFENSE_ANCHORS)
    * len(WAVE_A_CORE_HIT_RATE_PCT)
    * len(WAVE_A_MAIN_ADVANTAGE_LEVELS)
)
WAVE_A_SCENARIOS_PER_ROSTER = WAVE_A_GROWTH_POINT_COUNT * WAVE_A_ENVIRONMENT_COUNT
WAVE_A_SCENARIO_COUNT = WAVE_A_VALID_ROSTER_COUNT * WAVE_A_SCENARIOS_PER_ROSTER


def wave_a_growth_index_triples() -> tuple[tuple[int, int, int], ...]:
    """Return the 16-point OA(16, 3, 4, 2)-style growth screening design.

    Each pair of role axes covers every 4x4 combination exactly once while the
    three-way 4x4x4 growth cube is intentionally reduced from 64 to 16 points.
    """
    size = len(REALISTIC_GROWTH_PROFILES)
    if size != 4:
        raise AssertionError("Wave A growth OA requires exactly four profiles")
    triples = tuple(
        (b1_index, main_index, (b1_index + main_index) % size)
        for b1_index in range(size)
        for main_index in range(size)
    )
    if len(triples) != WAVE_A_GROWTH_POINT_COUNT:
        raise AssertionError("Wave A growth OA size does not match definition")
    return triples


def wave_a_roster_id(roster: TeamRoster) -> str:
    return (
        f"b1-{roster.b1}"
        f"--main-{roster.main_b3}"
        f"--secondary-{roster.secondary_b3}"
    )


def iter_wave_a_rosters() -> Iterator[TeamRoster]:
    """Yield verified-core rosters, excluding duplicate actors before construction."""
    for b1 in WAVE_A_B1_CANDIDATES:
        for main_b3 in WAVE_A_MAIN_B3_CANDIDATES:
            for secondary_b3 in WAVE_A_SECONDARY_B3_ANCHORS:
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


def _extra_reload_speed_sources(actors: tuple[str, ...]) -> tuple[tuple[str, str, str], ...]:
    """Return modeled reload-speed skill fields outside Crown/Mast.

    This is a fail-closed design check. Adding an actor whose kit directly adds
    reload speed requires reopening the >100% reload gate instead of silently
    inheriting the current <100% certification.
    """
    sources: list[tuple[str, str, str]] = []
    for actor in actors:
        definition = STANDARD_CHARACTER_CATALOG.require(actor)
        for skill, values in definition.skills.items():
            for key in values:
                if key in {"reload_speed_pct", "reload_per_stack_pct"}:
                    sources.append((actor, skill, key))
    return tuple(sources)


def wave_a_reload_speed_ceiling_pct() -> float:
    """Return the certified Crown+Mast reload-speed ceiling for Wave A.

    The verified-core allowlist must not contain any additional modeled
    reload-speed skill source. If one is later added, this function fails until
    the >100% behavior is explicitly revalidated.
    """
    study_actors = tuple(
        dict.fromkeys(
            (
                *WAVE_A_B1_CANDIDATES,
                *WAVE_A_MAIN_B3_CANDIDATES,
                *WAVE_A_SECONDARY_B3_ANCHORS,
            )
        )
    )
    extra_sources = _extra_reload_speed_sources(study_actors)
    if extra_sources:
        raise AssertionError(
            "Wave A allowlist adds reload-speed sources outside Crown/Mast: "
            f"{extra_sources}"
        )

    crown = STANDARD_CHARACTER_CATALOG.require("crown")
    mast = STANDARD_CHARACTER_CATALOG.require("mast-romantic-maid")
    ceiling = (
        crown.skill_value("skill1", "reload_speed_pct")
        + mast.skill_value("skill2", "reload_per_stack_pct") * 3
    )
    if ceiling >= 100:
        raise AssertionError(
            f"Wave A modeled reload-speed ceiling is not certified below 100%: {ceiling}"
        )
    return ceiling


def _combat_settings_for(
    roster: TeamRoster,
    *,
    defense_condition: str,
    core_condition: str,
    main_advantage: str,
) -> CombatSettings:
    try:
        boss_def = WAVE_A_DEFENSE_ANCHORS[defense_condition]
    except KeyError as exc:
        raise ValueError(f"unsupported defense condition: {defense_condition}") from exc
    try:
        core_hit_rate_pct = WAVE_A_CORE_HIT_RATE_PCT[core_condition]
    except KeyError as exc:
        raise ValueError(f"unsupported core condition: {core_condition}") from exc
    if main_advantage not in WAVE_A_MAIN_ADVANTAGE_LEVELS:
        raise ValueError(f"unsupported main advantage condition: {main_advantage}")

    boss_element = (
        None
        if main_advantage == "off"
        else main_advantage_boss_element(roster.main_b3)
    )
    return CombatSettings(
        boss_def=boss_def,
        core_hit_rate_pct=core_hit_rate_pct,
        boss_element=boss_element,
    )


def build_wave_a_roster_cases(roster: TeamRoster) -> tuple[SampleCase, ...]:
    """Build one 192-case Wave A roster shard without executing simulations."""
    valid_roster_ids = {wave_a_roster_id(item) for item in iter_wave_a_rosters()}
    roster_id = wave_a_roster_id(roster)
    if roster_id not in valid_roster_ids:
        raise ValueError(f"roster is outside the Wave A verified-core sample: {roster_id}")

    # Re-evaluate this guard whenever the candidate allowlist changes.
    wave_a_reload_speed_ceiling_pct()

    fixed_b2_build = BuildProfile.uniform(
        GearState.OL5,
        collection=SR15_COLLECTION,
    )
    growth_profiles = REALISTIC_GROWTH_PROFILES
    cases: list[SampleCase] = []

    for defense_condition, core_condition, main_advantage in product(
        WAVE_A_DEFENSE_ANCHORS,
        WAVE_A_CORE_HIT_RATE_PCT,
        WAVE_A_MAIN_ADVANTAGE_LEVELS,
    ):
        combat_settings = _combat_settings_for(
            roster,
            defense_condition=defense_condition,
            core_condition=core_condition,
            main_advantage=main_advantage,
        )
        environment_id = (
            f"def-{defense_condition}"
            f"--core-{core_condition}"
            f"--main-advantage-{main_advantage}"
        )

        for point_index, (b1_index, main_index, secondary_index) in enumerate(
            wave_a_growth_index_triples(),
            start=1,
        ):
            b1_profile = growth_profiles[b1_index]
            main_profile = growth_profiles[main_index]
            secondary_profile = growth_profiles[secondary_index]
            case_id = (
                f"{WAVE_A_DRAFT_ID}--{roster_id}--{environment_id}"
                f"--oa-{point_index:02d}"
            )
            scenario = ResearchScenario(
                roster=roster,
                builds={
                    roster.b1: b1_profile.build_for(roster.b1),
                    roster.crown: fixed_b2_build,
                    roster.mast: fixed_b2_build,
                    roster.main_b3: main_profile.build_for(roster.main_b3),
                    roster.secondary_b3: secondary_profile.build_for(
                        roster.secondary_b3
                    ),
                },
                combat_settings=combat_settings,
                main_actor=roster.main_b3,
                baseline_rotation=OPENING_MAST_CROWN_MAST.name,
                timeline=RAID14_TIMELINE,
            )
            cases.append(
                SampleCase(
                    case_id=case_id,
                    scenario=scenario,
                    labels={
                        "study_draft_id": WAVE_A_DRAFT_ID,
                        "roster_id": roster_id,
                        "b1_candidate": roster.b1,
                        "main_b3_candidate": roster.main_b3,
                        "secondary_anchor": roster.secondary_b3,
                        "growth_design": "oa16-pairwise",
                        "growth_point": f"oa-{point_index:02d}",
                        "b1_profile": b1_profile.profile_id,
                        "main_profile": main_profile.profile_id,
                        "secondary_profile": secondary_profile.profile_id,
                        "def_condition": defense_condition,
                        "boss_def": str(combat_settings.boss_def),
                        "core_condition": core_condition,
                        "core_hit_rate_pct": str(core_hit_rate_pct := combat_settings.core_hit_rate_pct),
                        "main_advantage": main_advantage,
                        "boss_element": combat_settings.boss_element or "neutral",
                        "hit_model": "ideal-hit",
                    },
                )
            )

    if len(cases) != WAVE_A_SCENARIOS_PER_ROSTER:
        raise AssertionError("Wave A roster shard size does not match definition")
    if len({case.case_id for case in cases}) != len(cases):
        raise AssertionError("Wave A case ids must be unique within a roster shard")
    return tuple(cases)


def wave_a_study_definition() -> dict[str, object]:
    valid_rosters = tuple(iter_wave_a_rosters())
    if len(valid_rosters) != WAVE_A_VALID_ROSTER_COUNT:
        raise AssertionError("Wave A valid roster count does not match definition")

    blocked_overlap = WAVE_A_BLOCKED_ACTORS.intersection(
        {
            *WAVE_A_B1_CANDIDATES,
            *WAVE_A_MAIN_B3_CANDIDATES,
            *WAVE_A_SECONDARY_B3_ANCHORS,
        }
    )
    if blocked_overlap:
        raise AssertionError(
            f"blocked actors entered the Wave A verified-core allowlist: {sorted(blocked_overlap)}"
        )

    growth_triples = wave_a_growth_index_triples()
    reload_speed_ceiling = wave_a_reload_speed_ceiling_pct()

    return {
        "study_draft_id": WAVE_A_DRAFT_ID,
        "status": "draft-do-not-run-without-user-approval",
        "b1_candidates": list(WAVE_A_B1_CANDIDATES),
        "main_b3_candidates": list(WAVE_A_MAIN_B3_CANDIDATES),
        "secondary_b3_anchors": list(WAVE_A_SECONDARY_B3_ANCHORS),
        "blocked_actors": sorted(WAVE_A_BLOCKED_ACTORS),
        "raw_roster_count": WAVE_A_RAW_ROSTER_COUNT,
        "invalid_duplicate_rosters": WAVE_A_INVALID_DUPLICATE_ROSTER_COUNT,
        "valid_roster_count": WAVE_A_VALID_ROSTER_COUNT,
        "growth_design": {
            "name": "oa16-pairwise",
            "profiles_per_role": len(REALISTIC_GROWTH_PROFILES),
            "points": len(growth_triples),
            "index_rule": "secondary=(b1+main) mod 4",
            "three_way_complete": False,
        },
        "environment_axes": {
            "defense": dict(WAVE_A_DEFENSE_ANCHORS),
            "core": dict(WAVE_A_CORE_HIT_RATE_PCT),
            "main_advantage": list(WAVE_A_MAIN_ADVANTAGE_LEVELS),
            "hit_model": "ideal-hit",
        },
        "reload_speed_ceiling_pct": reload_speed_ceiling,
        "environments_per_roster": WAVE_A_ENVIRONMENT_COUNT,
        "scenarios_per_roster": WAVE_A_SCENARIOS_PER_ROSTER,
        "scenario_count": WAVE_A_SCENARIO_COUNT,
        "timeline": "RAID14",
        "baseline_rotation": OPENING_MAST_CROWN_MAST.name,
        "execution_policy": "case generation only until explicit user approval",
    }
