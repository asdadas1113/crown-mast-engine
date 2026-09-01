from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


_VALID_B2_SLOTS = {"crown", "mast"}


@dataclass(frozen=True)
class RotationPolicy:
    name: str
    b2_slot_by_cycle: tuple[str, ...]
    repeat_pattern: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("rotation policy name must not be empty")
        if not self.b2_slot_by_cycle and not self.repeat_pattern:
            raise ValueError("rotation policy must define explicit cycles or a repeat pattern")
        unsupported = sorted(
            (set(self.b2_slot_by_cycle) | set(self.repeat_pattern)) - _VALID_B2_SLOTS
        )
        if unsupported:
            raise ValueError(f"unsupported B2 roster slots: {unsupported}")

    def b2_slot(self, cycle: int) -> str:
        if isinstance(cycle, bool) or not isinstance(cycle, int) or cycle < 1:
            raise ValueError(f"cycle out of range for {self.name}: {cycle}")
        if cycle <= len(self.b2_slot_by_cycle):
            return self.b2_slot_by_cycle[cycle - 1]
        if self.repeat_pattern:
            return self.repeat_pattern[(cycle - 1) % len(self.repeat_pattern)]
        raise ValueError(f"cycle out of range for {self.name}: {cycle}")


_CCM_PATTERN = ("crown", "crown", "mast")
_FUNNEL_PATTERN = (
    "crown",
    "crown",
    "mast",
    "crown",
    "mast",
    "crown",
)

CROWN_CROWN_MAST = RotationPolicy(
    name="crown_crown_mast",
    b2_slot_by_cycle=_CCM_PATTERN * 4,
    repeat_pattern=_CCM_PATTERN,
)

OPENING_MAST_CROWN_MAST = RotationPolicy(
    name="opening_mast_crown_mast",
    b2_slot_by_cycle=("mast", "crown", "mast") + _CCM_PATTERN * 3,
    repeat_pattern=_CCM_PATTERN,
)

SUSTAINED_FUNNEL = RotationPolicy(
    name="sustained_funnel",
    b2_slot_by_cycle=_FUNNEL_PATTERN * 2,
    repeat_pattern=_FUNNEL_PATTERN,
)

OPENING_MAST_SUSTAINED_FUNNEL = RotationPolicy(
    name="opening_mast_sustained_funnel",
    b2_slot_by_cycle=("mast",) + SUSTAINED_FUNNEL.b2_slot_by_cycle[1:],
    repeat_pattern=_FUNNEL_PATTERN,
)

BASELINE_ROTATIONS = MappingProxyType(
    {
        CROWN_CROWN_MAST.name: CROWN_CROWN_MAST,
        OPENING_MAST_CROWN_MAST.name: OPENING_MAST_CROWN_MAST,
    }
)


def baseline_rotation(name: str) -> RotationPolicy:
    try:
        return BASELINE_ROTATIONS[name]
    except KeyError as exc:
        raise ValueError(f"unsupported baseline rotation: {name}") from exc


def CUSTOM_ROTATION(name: str, b2_slot_by_cycle: Mapping[int, str]) -> RotationPolicy:
    if not b2_slot_by_cycle:
        raise ValueError("custom rotation must define at least one cycle")
    keys = set(b2_slot_by_cycle)
    if any(isinstance(cycle, bool) or not isinstance(cycle, int) or cycle <= 0 for cycle in keys):
        raise ValueError("custom rotation cycle ids must be positive integers")
    final_cycle = max(keys)
    expected = set(range(1, final_cycle + 1))
    if keys != expected:
        missing = sorted(expected - keys)
        extra = sorted(keys - expected)
        raise ValueError(
            f"custom rotation must define contiguous cycles 1..{final_cycle}; "
            f"missing={missing}, extra={extra}"
        )
    slots = tuple(b2_slot_by_cycle[i] for i in range(1, final_cycle + 1))
    unsupported = sorted(set(slots) - _VALID_B2_SLOTS)
    if unsupported:
        raise ValueError(f"unsupported B2 roster slots: {unsupported}")
    return RotationPolicy(name=name, b2_slot_by_cycle=slots)
