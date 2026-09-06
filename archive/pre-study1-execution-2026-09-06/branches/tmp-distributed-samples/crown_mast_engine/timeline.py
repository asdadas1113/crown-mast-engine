from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class BurstCycle:
    cycle: int
    b1_time: float
    b2_time: float
    b3_time: float
    full_burst_start: float
    full_burst_end: float
    b3_slot: str


STANDARD_TIMELINE: tuple[BurstCycle, ...] = (
    BurstCycle(1, 3.9, 4.3, 4.8, 5.1, 15.1, "main_b3"),
    BurstCycle(2, 18.3, 18.7, 19.3, 19.6, 29.6, "secondary_b3"),
    BurstCycle(3, 32.7, 33.3, 33.9, 34.3, 44.3, "main_b3"),
    BurstCycle(4, 47.4, 48.0, 48.5, 48.9, 58.9, "secondary_b3"),
    BurstCycle(5, 61.3, 61.6, 62.2, 62.6, 72.6, "main_b3"),
    BurstCycle(6, 76.0, 76.4, 77.0, 77.4, 87.4, "secondary_b3"),
    BurstCycle(7, 89.7, 90.3, 90.8, 91.2, 101.2, "main_b3"),
    BurstCycle(8, 104.7, 105.1, 105.6, 106.0, 116.0, "secondary_b3"),
    BurstCycle(9, 118.3, 118.8, 119.3, 119.6, 129.6, "main_b3"),
    BurstCycle(10, 132.1, 132.4, 132.8, 133.2, 143.2, "secondary_b3"),
    BurstCycle(11, 147.6, 148.0, 148.6, 149.0, 159.0, "main_b3"),
    BurstCycle(12, 161.8, 162.1, 162.7, 163.0, 173.0, "secondary_b3"),
)


def build_uniform_burst_timeline(
    *,
    cycle_count: int,
    interval_sec: float,
    first_cycle: BurstCycle = STANDARD_TIMELINE[0],
    b3_slots: Sequence[str] = ("main_b3", "secondary_b3"),
) -> tuple[BurstCycle, ...]:
    """Build a timeline by shifting one measured first cycle at a fixed interval.

    The relative offsets inside the first cycle are preserved. Only the cycle start
    is shifted by ``interval_sec`` for each later burst. ``b3_slots`` is repeated
    as a pattern, so the default keeps the standard Main/Secondary alternation.

    This is intentionally a timeline constructor, not a claim that real raid burst
    intervals are constant. Measured values should be supplied by the caller.
    """

    if isinstance(cycle_count, bool) or not isinstance(cycle_count, int) or cycle_count <= 0:
        raise ValueError("cycle_count must be a positive integer")
    if not isfinite(interval_sec) or interval_sec <= 0:
        raise ValueError("interval_sec must be finite and positive")

    slots = tuple(b3_slots)
    if not slots:
        raise ValueError("b3_slots must not be empty")
    unsupported = sorted(set(slots) - {"main_b3", "secondary_b3"})
    if unsupported:
        raise ValueError(f"unsupported b3 slots: {unsupported}")

    return tuple(
        BurstCycle(
            cycle=index + 1,
            b1_time=first_cycle.b1_time + interval_sec * index,
            b2_time=first_cycle.b2_time + interval_sec * index,
            b3_time=first_cycle.b3_time + interval_sec * index,
            full_burst_start=first_cycle.full_burst_start + interval_sec * index,
            full_burst_end=first_cycle.full_burst_end + interval_sec * index,
            b3_slot=slots[index % len(slots)],
        )
        for index in range(cycle_count)
    )


# Practical 180 s raid baseline derived from the 2026-09-01 shooting-range run.
# The cycle interval is intentionally rounded slightly conservatively to 12.70 s.
# Manual B1->B2 and B2->B3 transitions clustered near 0.06 s each; 0.06 s is
# therefore used as the stage-input model. The first B1 is anchored at t=2.20 s
# so a theoretical c15 B1 would become ready at exactly t=180.00 s. c15 is not
# part of the normal model.
RAID14_CYCLE_COUNT = 14
RAID14_INTERVAL_SEC = 12.70
RAID14_FIRST_B1_TIME = 2.20
RAID14_STAGE_INPUT_GAP_SEC = 0.06
RAID14_FULL_BURST_DURATION_SEC = 10.0

RAID14_FIRST_CYCLE = BurstCycle(
    cycle=1,
    b1_time=RAID14_FIRST_B1_TIME,
    b2_time=RAID14_FIRST_B1_TIME + RAID14_STAGE_INPUT_GAP_SEC,
    b3_time=RAID14_FIRST_B1_TIME + RAID14_STAGE_INPUT_GAP_SEC * 2,
    full_burst_start=RAID14_FIRST_B1_TIME + RAID14_STAGE_INPUT_GAP_SEC * 2,
    full_burst_end=(
        RAID14_FIRST_B1_TIME
        + RAID14_STAGE_INPUT_GAP_SEC * 2
        + RAID14_FULL_BURST_DURATION_SEC
    ),
    b3_slot="main_b3",
)

RAID14_TIMELINE: tuple[BurstCycle, ...] = build_uniform_burst_timeline(
    cycle_count=RAID14_CYCLE_COUNT,
    interval_sec=RAID14_INTERVAL_SEC,
    first_cycle=RAID14_FIRST_CYCLE,
)
