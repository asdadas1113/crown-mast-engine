from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .characters import STANDARD_CHARACTER_CATALOG
from .combat import CombatSettings, ELEMENT_BEATS
from .equipment import (
    FAVORITE_ITEM_ACTORS,
    BuildProfile,
    CollectionProfile,
    GearState,
    OverloadProfile,
    SR15_COLLECTION,
)
from .models import TeamRoster
from .research import ResearchScenario
from .rotations import OPENING_MAST_CROWN_MAST
from .samples import SampleCase
from .timeline import RAID14_TIMELINE


CHECKPOINT_V3_ID = "raid14-64point-realistic-v3"


@dataclass(frozen=True)
class GrowthCheckpointProfile:
    profile_id: str
    label: str
    gear: GearState
    collection_stage: str
    overload: OverloadProfile

    def collection_for(self, actor: str) -> CollectionProfile:
        # Favorite-item actor definitions already model the favorite-item kit,
        # so pre-favorite collection states are not physically valid for them.
        if actor in FAVORITE_ITEM_ACTORS:
            return SR15_COLLECTION
        return CollectionProfile(self.collection_stage)

    def build_for(self, actor: str) -> BuildProfile:
        return BuildProfile.uniform(
            self.gear,
            self.overload,
            self.collection_for(actor),
        )


REALISTIC_GROWTH_PROFILES = (
    GrowthCheckpointProfile(
        profile_id="g1-base5-none",
        label="Base5 / no collection",
        gear=GearState.BASE5,
        collection_stage="none",
        overload=OverloadProfile(),
    ),
    GrowthCheckpointProfile(
        profile_id="g2-ol0-sr5",
        label="OL0 / SR5",
        gear=GearState.OL0,
        collection_stage="SR5",
        overload=OverloadProfile(),
    ),
    GrowthCheckpointProfile(
        profile_id="g3-ol0-sr15-e3-a3",
        label="OL0 / SR15 / Element3 ATK3",
        gear=GearState.OL0,
        collection_stage="SR15",
        overload=OverloadProfile(atk_lines=3, element_lines=3),
    ),
    GrowthCheckpointProfile(
        profile_id="g4-ol5-sr15-e4-a4-ammo3",
        label="OL5 / SR15 / Element4 ATK4 Ammo3",
        gear=GearState.OL5,
        collection_stage="SR15",
        overload=OverloadProfile(atk_lines=4, element_lines=4, ammo_lines=3),
    ),
)


CHECKPOINT_V3_POINT_COUNT = len(REALISTIC_GROWTH_PROFILES) ** 3


def main_advantage_boss_element(main_actor: str) -> str:
    definition = STANDARD_CHARACTER_CATALOG.require(main_actor)
    try:
        return ELEMENT_BEATS[definition.element]
    except KeyError as exc:
        raise ValueError(
            f"unsupported main element for advantage study: {definition.element}"
        ) from exc


def build_checkpoint_v3_cases(
    *,
    roster: TeamRoster = TeamRoster(),
    combat_settings: CombatSettings = CombatSettings(),
    condition_id: str = "custom",
) -> tuple[SampleCase, ...]:
    """Build the fully crossed RAID14 64-point realistic-growth grid.

    B1, Main B3, and Secondary B3 each use the same four growth states.
    Crown and Mast remain fixed at OL5/SR15 with no OL options. The study
    baseline is intentionally fixed to the M1 opener.
    """
    if not isinstance(condition_id, str) or not condition_id:
        raise ValueError("condition_id must be a non-empty string")

    fixed_b2_build = BuildProfile.uniform(
        GearState.OL5,
        collection=SR15_COLLECTION,
    )
    cases: list[SampleCase] = []

    for b1_profile in REALISTIC_GROWTH_PROFILES:
        b1_build = b1_profile.build_for(roster.b1)
        for main_profile in REALISTIC_GROWTH_PROFILES:
            main_build = main_profile.build_for(roster.main_b3)
            for secondary_profile in REALISTIC_GROWTH_PROFILES:
                secondary_build = secondary_profile.build_for(roster.secondary_b3)
                case_id = (
                    f"{condition_id}--b1-{b1_profile.profile_id}"
                    f"--main-{main_profile.profile_id}"
                    f"--secondary-{secondary_profile.profile_id}"
                )
                cases.append(
                    SampleCase(
                        case_id=case_id,
                        scenario=ResearchScenario(
                            roster=roster,
                            builds={
                                roster.b1: b1_build,
                                roster.crown: fixed_b2_build,
                                roster.mast: fixed_b2_build,
                                roster.main_b3: main_build,
                                roster.secondary_b3: secondary_build,
                            },
                            combat_settings=combat_settings,
                            main_actor=roster.main_b3,
                            baseline_rotation=OPENING_MAST_CROWN_MAST.name,
                            timeline=RAID14_TIMELINE,
                        ),
                        labels={
                            "checkpoint_version": CHECKPOINT_V3_ID,
                            "condition": condition_id,
                            "b1_profile": b1_profile.profile_id,
                            "b1_label": b1_profile.label,
                            "main_profile": main_profile.profile_id,
                            "main_label": main_profile.label,
                            "secondary_profile": secondary_profile.profile_id,
                            "secondary_label": secondary_profile.label,
                        },
                    )
                )

    if len(cases) != CHECKPOINT_V3_POINT_COUNT:
        raise AssertionError("checkpoint v3 grid size does not match definition")
    return tuple(cases)


def _profile_definition(profile: GrowthCheckpointProfile, actor: str) -> dict[str, Any]:
    return {
        "id": profile.profile_id,
        "label": profile.label,
        "gear": profile.gear.value,
        "collection": profile.collection_for(actor).stage,
        "requested_collection": profile.collection_stage,
        "favorite_item_collection_forced": actor in FAVORITE_ITEM_ACTORS,
        "overload": {
            "atk_lines": profile.overload.atk_lines,
            "element_lines": profile.overload.element_lines,
            "ammo_lines": profile.overload.ammo_lines,
        },
    }


def checkpoint_v3_definitions(
    *,
    roster: TeamRoster = TeamRoster(),
) -> dict[str, Any]:
    return {
        "id": CHECKPOINT_V3_ID,
        "point_count": CHECKPOINT_V3_POINT_COUNT,
        "baseline_rotation": OPENING_MAST_CROWN_MAST.name,
        "axes": {"b1": 4, "main": 4, "secondary": 4},
        "b1": [
            _profile_definition(profile, roster.b1)
            for profile in REALISTIC_GROWTH_PROFILES
        ],
        "main": [
            _profile_definition(profile, roster.main_b3)
            for profile in REALISTIC_GROWTH_PROFILES
        ],
        "secondary": [
            _profile_definition(profile, roster.secondary_b3)
            for profile in REALISTIC_GROWTH_PROFILES
        ],
        "fixed_b2": {
            "gear": GearState.OL5.value,
            "collection": SR15_COLLECTION.stage,
            "overload": {"atk_lines": 0, "element_lines": 0, "ammo_lines": 0},
        },
    }
