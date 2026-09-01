from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DamageCategory(str, Enum):
    NORMAL = "normal"
    SKILL = "skill"
    BURST = "burst"


class EventType(str, Enum):
    B1_CAST = "b1_cast"
    B2_CAST = "b2_cast"
    B3_STAGE_ENTER = "b3_stage_enter"
    FULL_BURST_ENTER = "full_burst_enter"
    FULL_BURST_END = "full_burst_end"
    RECOVERY = "recovery"
    MAST_RESET = "mast_reset"
    HANGOVER_START = "hangover_start"


@dataclass(frozen=True)
class TeamRoster:
    b1: str = "liter"
    crown: str = "crown"
    mast: str = "mast-romantic-maid"
    main_b3: str = "rapi-red-hood"
    secondary_b3: str = "helm"

    def __post_init__(self) -> None:
        members = self.members
        if any(not isinstance(actor, str) or not actor for actor in members):
            raise TypeError("team roster members must be non-empty strings")
        if len(set(members)) != len(members):
            raise ValueError("team roster cannot assign the same character to multiple roles")

    @property
    def members(self) -> tuple[str, ...]:
        return (self.b1, self.crown, self.mast, self.main_b3, self.secondary_b3)


@dataclass(frozen=True)
class BattleEvent:
    time: float
    cycle: int
    event_type: EventType
    actor: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CycleSnapshot:
    cycle: int
    b2_actor: str
    b3_actor: str
    mast_stack_at_b2: int
    mast_stack_at_b3: int
    mast_reset_at_end: bool
    mast_hangover_at_b2: bool