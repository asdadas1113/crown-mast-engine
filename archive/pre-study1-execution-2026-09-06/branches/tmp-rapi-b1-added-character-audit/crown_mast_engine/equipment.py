from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GearState(str, Enum):
    BASE5 = "base5"
    OL0 = "ol0"
    OL5 = "ol5"


class GearSlot(str, Enum):
    SLOT_1 = "slot_1"
    SLOT_2 = "slot_2"
    SLOT_3 = "slot_3"
    SLOT_4 = "slot_4"


GEAR_SLOTS = tuple(GearSlot)

OL_TIER_11_ATK_PCT = 11.81
OL_TIER_11_ELEMENT_PCT = 23.56
OL_TIER_11_AMMO_PCT = 68.93

COLLECTION_ATK: dict[str, tuple[int, ...]] = {
    "R": (
        638, 809, 980, 1150, 1321, 1577, 1833, 2089,
        2346, 2602, 2943, 3285, 3626, 3968, 4309, 4736,
    ),
    "SR": (
        3029, 3370, 3712, 4053, 4395, 4821, 5248, 5675,
        6102, 6529, 7041, 7554, 8066, 8578, 9090, 9688,
    ),
}

COLLECTION_WEAPON_EFFECTS: dict[str, tuple[str, dict[str, tuple[float, ...]]]] = {
    "AR": (
        "core_damage_pct",
        {"R": (5.67, 7.94, 10.22, 12.49), "SR": (10.22, 12.49, 14.77, 17.04)},
    ),
    "MG": (
        "max_ammo_pct",
        {"R": (1.56, 3.15, 4.74, 6.32), "SR": (4.74, 6.32, 7.91, 9.5)},
    ),
    "RL": (
        "charge_damage_mult_pct",
        {"R": (1.58, 3.16, 4.74, 6.31), "SR": (4.74, 6.31, 7.89, 9.47)},
    ),
    "SR": (
        "charge_damage_mult_pct",
        {"R": (1.58, 3.16, 4.74, 6.31), "SR": (4.74, 6.31, 7.89, 9.47)},
    ),
    "SG": (
        "normal_attack_pct",
        {"R": (1.57, 3.15, 4.73, 6.3), "SR": (4.73, 6.3, 7.88, 9.46)},
    ),
    "SMG": (
        "normal_attack_pct",
        {"R": (1.57, 3.15, 4.73, 6.3), "SR": (4.73, 6.3, 7.88, 9.46)},
    ),
}


# The pinned source stores three ATK-bearing pieces in this order. Slot 4 is
# retained for future per-piece OL lines but contributes no flat ATK.
GEAR_ATK_BY_CLASS: dict[str, dict[GearState, tuple[float, float, float, float]]] = {
    "Defender": {
        GearState.BASE5: (3234.0, 2057.0, 588.0, 0.0),
        GearState.OL0: (4010.0, 2551.0, 729.0, 0.0),
        GearState.OL5: (6015.0, 3827.0, 1093.0, 0.0),
    },
    "Attacker": {
        GearState.BASE5: (4849.0, 3087.0, 882.0, 0.0),
        GearState.OL0: (6014.0, 3827.0, 1093.0, 0.0),
        GearState.OL5: (9021.0, 5741.0, 1639.0, 0.0),
    },
    "Supporter": {
        GearState.BASE5: (4041.0, 2573.0, 735.0, 0.0),
        GearState.OL0: (5012.0, 3189.0, 911.0, 0.0),
        GearState.OL5: (7518.0, 4783.0, 1367.0, 0.0),
    },
}


@dataclass(frozen=True)
class GearPiece:
    slot: GearSlot
    state: GearState


@dataclass(frozen=True)
class EquipmentLoadout:
    pieces: tuple[GearPiece, ...]

    def __post_init__(self) -> None:
        slots = tuple(piece.slot for piece in self.pieces)
        if len(slots) != len(GEAR_SLOTS) or set(slots) != set(GEAR_SLOTS):
            raise ValueError("equipment loadout must define each gear slot exactly once")

    @classmethod
    def uniform(cls, state: GearState) -> EquipmentLoadout:
        return cls(tuple(GearPiece(slot, state) for slot in GEAR_SLOTS))

    @classmethod
    def from_states(
        cls,
        slot_1: GearState,
        slot_2: GearState,
        slot_3: GearState,
        slot_4: GearState,
    ) -> EquipmentLoadout:
        return cls(
            (
                GearPiece(GearSlot.SLOT_1, slot_1),
                GearPiece(GearSlot.SLOT_2, slot_2),
                GearPiece(GearSlot.SLOT_3, slot_3),
                GearPiece(GearSlot.SLOT_4, slot_4),
            )
        )

    def gear_atk(self, unit_class: str) -> float:
        try:
            table = GEAR_ATK_BY_CLASS[unit_class]
        except KeyError as exc:
            raise ValueError(f"unsupported unit class: {unit_class}") from exc

        total = 0.0
        for piece in self.pieces:
            slot_index = GEAR_SLOTS.index(piece.slot)
            total += table[piece.state][slot_index]
        return total


@dataclass(frozen=True)
class OverloadProfile:
    atk_lines: int = 0
    element_lines: int = 0
    ammo_lines: int = 0

    def __post_init__(self) -> None:
        for name, value in (
            ("atk_lines", self.atk_lines),
            ("element_lines", self.element_lines),
            ("ammo_lines", self.ammo_lines),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be non-negative")

    @property
    def atk_pct(self) -> float:
        return self.atk_lines * OL_TIER_11_ATK_PCT

    @property
    def element_pct(self) -> float:
        return self.element_lines * OL_TIER_11_ELEMENT_PCT

    @property
    def ammo_pct(self) -> float:
        return self.ammo_lines * OL_TIER_11_AMMO_PCT


@dataclass(frozen=True)
class CollectionProfile:
    stage: str = "none"

    def __post_init__(self) -> None:
        if self.stage == "none":
            return
        grade = "SR" if self.stage.startswith("SR") else "R"
        level_text = self.stage[len(grade):]
        if not level_text.isdigit() or not 0 <= int(level_text) <= 15:
            raise ValueError("collection stage must be none, R0~R15, or SR0~SR15")

    @property
    def grade(self) -> str | None:
        if self.stage == "none":
            return None
        return "SR" if self.stage.startswith("SR") else "R"

    @property
    def level(self) -> int | None:
        grade = self.grade
        return None if grade is None else int(self.stage[len(grade):])

    @property
    def flat_atk(self) -> float:
        grade = self.grade
        level = self.level
        return 0.0 if grade is None or level is None else float(COLLECTION_ATK[grade][level])

    @property
    def skill_level(self) -> int:
        level = self.level
        if level is None:
            return 0
        if level == 15:
            return 4
        return level // 5 + 1

    def weapon_effect(self, weapon_type: str) -> tuple[str, float] | None:
        grade = self.grade
        if grade is None:
            return None
        definition = COLLECTION_WEAPON_EFFECTS.get(weapon_type)
        if definition is None:
            return None
        stat, values = definition
        return stat, values[grade][self.skill_level - 1]


NO_OVERLOAD_OPTIONS = OverloadProfile()
NO_COLLECTION = CollectionProfile()
SR15_COLLECTION = CollectionProfile("SR15")


@dataclass(frozen=True)
class BuildProfile:
    equipment: EquipmentLoadout
    overload: OverloadProfile = NO_OVERLOAD_OPTIONS
    collection: CollectionProfile = NO_COLLECTION

    @classmethod
    def uniform(
        cls,
        state: GearState,
        overload: OverloadProfile = NO_OVERLOAD_OPTIONS,
        collection: CollectionProfile = NO_COLLECTION,
    ) -> BuildProfile:
        return cls(EquipmentLoadout.uniform(state), overload, collection)


STANDARD_BUILD = BuildProfile.uniform(GearState.BASE5)
BARE_OL0_BUILD = BuildProfile.uniform(GearState.OL0)
BARE_OL5_BUILD = BuildProfile.uniform(GearState.OL5)
HIGH_OL5_BUILD = BuildProfile.uniform(
    GearState.OL5,
    OverloadProfile(atk_lines=4, element_lines=4, ammo_lines=3),
)


FAVORITE_ITEM_ACTORS = frozenset({"helm", "moran-favorite-item", "phantom"})


def standard_build_for_actor(actor: str) -> BuildProfile:
    if actor in FAVORITE_ITEM_ACTORS:
        return BuildProfile(
            equipment=STANDARD_BUILD.equipment,
            overload=STANDARD_BUILD.overload,
            collection=SR15_COLLECTION,
        )
    return STANDARD_BUILD
