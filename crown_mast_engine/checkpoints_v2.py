from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .combat import CombatSettings
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
from .rotations import CROWN_CROWN_MAST, baseline_rotation as resolve_baseline_rotation
from .samples import SampleCase
from .timeline import RAID14_TIMELINE


CHECKPOINT_V2_ID = "raid14-36point-v2"


@dataclass(frozen=True)
class B1CheckpointProfile:
    profile_id: str
    label: str
    gear: GearState
    overload: OverloadProfile
    collection_stage: str

    def collection_for(self, actor: str) -> CollectionProfile:
        if actor in FAVORITE_ITEM_ACTORS:
            return SR15_COLLECTION
        return CollectionProfile(self.collection_stage)


@dataclass(frozen=True)
class MainCheckpointProfile:
    profile_id: str
    label: str
    overload: OverloadProfile


@dataclass(frozen=True)
class SecondaryCheckpointProfile:
    profile_id: str
    label: str
    gear: GearState


B1_CHECKPOINTS_V2 = (
    B1CheckpointProfile(
        profile_id="b1-low",
        label="B1 Low",
        gear=GearState.BASE5,
        overload=OverloadProfile(),
        collection_stage="none",
    ),
    B1CheckpointProfile(
        profile_id="b1-developing",
        label="B1 Developing",
        gear=GearState.OL0,
        overload=OverloadProfile(),
        collection_stage="SR15",
    ),
    B1CheckpointProfile(
        profile_id="b1-standard",
        label="B1 Standard",
        gear=GearState.OL5,
        overload=OverloadProfile(),
        collection_stage="SR15",
    ),
    B1CheckpointProfile(
        profile_id="b1-high",
        label="B1 High",
        gear=GearState.OL5,
        overload=OverloadProfile(
            atk_lines=4,
            element_lines=4,
            ammo_lines=3,
        ),
        collection_stage="SR15",
    ),
)


MAIN_CHECKPOINTS_V2 = (
    MainCheckpointProfile(
        profile_id="main-o5-bare",
        label="Main O5 bare",
        overload=OverloadProfile(),
    ),
    MainCheckpointProfile(
        profile_id="main-o5-atk3",
        label="Main O5 ATK3",
        overload=OverloadProfile(atk_lines=3),
    ),
    MainCheckpointProfile(
        profile_id="main-o5-ammo2",
        label="Main O5 Ammo2",
        overload=OverloadProfile(ammo_lines=2),
    ),
)


SECONDARY_CHECKPOINTS_V2 = (
    SecondaryCheckpointProfile(
        profile_id="secondary-o5",
        label="Secondary O5 bare",
        gear=GearState.OL5,
    ),
    SecondaryCheckpointProfile(
        profile_id="secondary-o0",
        label="Secondary O0 bare",
        gear=GearState.OL0,
    ),
    SecondaryCheckpointProfile(
        profile_id="secondary-b5",
        label="Secondary B5",
        gear=GearState.BASE5,
    ),
)


CHECKPOINT_V2_POINT_COUNT = (
    len(B1_CHECKPOINTS_V2)
    * len(MAIN_CHECKPOINTS_V2)
    * len(SECONDARY_CHECKPOINTS_V2)
)


def build_checkpoint_v2_cases(
    *,
    roster: TeamRoster = TeamRoster(),
    combat_settings: CombatSettings = CombatSettings(),
    baseline_rotation: str = CROWN_CROWN_MAST.name,
) -> tuple[SampleCase, ...]:
    """Build the fully crossed RAID14 36-point controlled checkpoint grid."""
    resolve_baseline_rotation(baseline_rotation)

    fixed_b2_build = BuildProfile.uniform(
        GearState.OL5,
        collection=SR15_COLLECTION,
    )
    cases: list[SampleCase] = []

    for b1_profile in B1_CHECKPOINTS_V2:
        b1_build = BuildProfile.uniform(
            b1_profile.gear,
            b1_profile.overload,
            b1_profile.collection_for(roster.b1),
        )
        for main_profile in MAIN_CHECKPOINTS_V2:
            main_build = BuildProfile.uniform(
                GearState.OL5,
                main_profile.overload,
                SR15_COLLECTION,
            )
            for secondary_profile in SECONDARY_CHECKPOINTS_V2:
                secondary_build = BuildProfile.uniform(
                    secondary_profile.gear,
                    collection=SR15_COLLECTION,
                )
                dealer_profile = (
                    f"{main_profile.profile_id}--{secondary_profile.profile_id}"
                )
                dealer_label = (
                    f"{main_profile.label} / {secondary_profile.label}"
                )
                case_id = f"{b1_profile.profile_id}--{dealer_profile}"
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
                            baseline_rotation=baseline_rotation,
                            timeline=RAID14_TIMELINE,
                        ),
                        labels={
                            "checkpoint_version": CHECKPOINT_V2_ID,
                            "b1_profile": b1_profile.profile_id,
                            "b1_label": b1_profile.label,
                            "main_profile": main_profile.profile_id,
                            "main_label": main_profile.label,
                            "secondary_profile": secondary_profile.profile_id,
                            "secondary_label": secondary_profile.label,
                            "dealer_profile": dealer_profile,
                            "dealer_label": dealer_label,
                        },
                    )
                )

    if len(cases) != CHECKPOINT_V2_POINT_COUNT:
        raise AssertionError("checkpoint v2 grid size does not match definition")
    return tuple(cases)


def checkpoint_v2_definitions(*, b1_actor: str = TeamRoster().b1) -> dict[str, Any]:
    return {
        "id": CHECKPOINT_V2_ID,
        "point_count": CHECKPOINT_V2_POINT_COUNT,
        "axes": {
            "b1": len(B1_CHECKPOINTS_V2),
            "main": len(MAIN_CHECKPOINTS_V2),
            "secondary": len(SECONDARY_CHECKPOINTS_V2),
        },
        "b1": [
            {
                "id": profile.profile_id,
                "label": profile.label,
                "gear": profile.gear.value,
                "collection": profile.collection_for(b1_actor).stage,
                "overload": {
                    "atk_lines": profile.overload.atk_lines,
                    "element_lines": profile.overload.element_lines,
                    "ammo_lines": profile.overload.ammo_lines,
                },
            }
            for profile in B1_CHECKPOINTS_V2
        ],
        "main": [
            {
                "id": profile.profile_id,
                "label": profile.label,
                "gear": GearState.OL5.value,
                "collection": SR15_COLLECTION.stage,
                "overload": {
                    "atk_lines": profile.overload.atk_lines,
                    "element_lines": profile.overload.element_lines,
                    "ammo_lines": profile.overload.ammo_lines,
                },
            }
            for profile in MAIN_CHECKPOINTS_V2
        ],
        "secondary": [
            {
                "id": profile.profile_id,
                "label": profile.label,
                "gear": profile.gear.value,
                "collection": SR15_COLLECTION.stage,
                "overload": {
                    "atk_lines": 0,
                    "element_lines": 0,
                    "ammo_lines": 0,
                },
            }
            for profile in SECONDARY_CHECKPOINTS_V2
        ],
    }
