from __future__ import annotations

import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from crown_mast_engine.checkpoints_v3 import build_checkpoint_v3_cases
from crown_mast_engine.combat import CombatSettings
from crown_mast_engine.models import TeamRoster
from crown_mast_engine.samples import run_sample_batch


# Official-v1 Main B3 candidates whose audited hooks emit distributed packets.
# They intentionally cover different structures: frequent skill riders, burst-only
# packets, mixed normal/distributed packets, and self-stacking distributed amp.
DISTRIBUTED_MAINS = (
    "scarlet-black-shadow",
    "bready",
    "quency-escape-queen",
    "phantom",
    "milk-blooming-bunny",
)
CONTROL_MAINS = ("rapi-red-hood",)
ALL_MAINS = DISTRIBUTED_MAINS + CONTROL_MAINS


def _stats(values):
    prepared = [float(value) for value in values if value is not None]
    return {
        "minimum": min(prepared),
        "average": sum(prepared) / len(prepared),
        "maximum": max(prepared),
    }


def _digest(result):
    row = result.summary_row()
    return {
        "case_id": result.case_id,
        "relative_change": row["relative_change"],
        "conventional_main_share": row["conventional_main_share"],
        "break_even_main_share_c": row["break_even_main_share_c"],
        "g": row["g"],
        "l": row["l"],
        "margin": row["margin"],
        "outcome_band": row["outcome_band"],
        "labels": dict(result.labels),
    }


def summarize(batch):
    rows = [result.summary_row() for result in batch.results]
    bands = {}
    for row in rows:
        bands[row["outcome_band"]] = bands.get(row["outcome_band"], 0) + 1

    most_funnel = max(
        batch.results,
        key=lambda result: result.summary_row()["relative_change"],
    )
    most_conventional = min(
        batch.results,
        key=lambda result: result.summary_row()["relative_change"],
    )
    finite_margin = [
        result
        for result in batch.results
        if result.summary_row()["margin"] is not None
    ]
    closest = min(
        finite_margin,
        key=lambda result: abs(result.summary_row()["margin"]),
    )

    return {
        "sample_count": len(rows),
        "funnel_wins": bands.get("clear_funnel", 0)
        + bands.get("marginal_funnel", 0),
        "outcome_bands": bands,
        "relative_change": _stats(row["relative_change"] for row in rows),
        "conventional_main_share": _stats(
            row["conventional_main_share"] for row in rows
        ),
        "g": _stats(row["g"] for row in rows),
        "l": _stats(row["l"] for row in rows),
        "break_even_main_share_c": _stats(
            row["break_even_main_share_c"]
            for row in rows
            if row["break_even_main_share_c"] is not None
        ),
        "extremes": {
            "most_funnel_favorable": _digest(most_funnel),
            "most_conventional_favorable": _digest(most_conventional),
            "closest_to_break_even": _digest(closest),
        },
    }


def main() -> None:
    # Isolation pass: neutral boss, no core, no range bonus. This deliberately
    # removes axes that can favor ordinary weapon packets and asks whether the
    # weak-funnel pattern is shared across distinct distributed-damage structures.
    combat = CombatSettings(
        boss_def=140.0,
        boss_element=None,
        core_hit_rate_pct=0.0,
        range_bonus_pct=0.0,
    )

    payload = {
        "study": "distributed-main-isolation-pretest-v1",
        "purpose": (
            "Check whether Scarlet: Black Shadow's weak sustained-funnel result "
            "is shared by other distributed-damage Main B3 structures before the "
            "official research batch."
        ),
        "fixed": {
            "b1": "liter",
            "secondary_b3": "helm",
            "boss_def": 140.0,
            "boss_element": None,
            "core_hit_rate_pct": 0.0,
            "range_bonus_pct": 0.0,
            "growth_grid": "checkpoint-v3 4x4x4 = 64 per main",
        },
        "distributed_mains": list(DISTRIBUTED_MAINS),
        "control_mains": list(CONTROL_MAINS),
        "results": {},
    }

    for main_actor in ALL_MAINS:
        roster = TeamRoster(
            b1="liter",
            main_b3=main_actor,
            secondary_b3="helm",
        )
        cases = build_checkpoint_v3_cases(
            roster=roster,
            combat_settings=combat,
            condition_id="distributed-pretest-neutral-core0",
        )
        batch = run_sample_batch(cases)
        payload["results"][main_actor] = summarize(batch)

    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
