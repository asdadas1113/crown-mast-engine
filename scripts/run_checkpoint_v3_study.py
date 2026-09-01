from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from crown_mast_engine.checkpoints_v3 import (
    CHECKPOINT_V3_ID,
    build_checkpoint_v3_cases,
    main_advantage_boss_element,
)
from crown_mast_engine.combat import CombatSettings
from crown_mast_engine.models import TeamRoster
from crown_mast_engine.samples import run_sample_batch


MAIN_CHOICES = (
    "rapi-red-hood",
    "scarlet-black-shadow",
    "snow-white-heavy-arms",
    "epinel",
)
B1_CHOICES = ("liter", "anis-star")
BOSS_MODE_CHOICES = ("neutral", "main-advantage", "both")


def _stats(values):
    prepared = [value for value in values if value is not None]
    if not prepared:
        return {"minimum": None, "average": None, "maximum": None}
    return {
        "minimum": min(prepared),
        "average": sum(prepared) / len(prepared),
        "maximum": max(prepared),
    }


def _case_digest(result):
    summary = result.summary_row()
    return {
        "case_id": result.case_id,
        "labels": dict(result.labels),
        "relative_change": summary["relative_change"],
        "main_share": summary["conventional_main_share"],
        "break_even": summary["break_even_main_share_c"],
        "g": summary["g"],
        "l": summary["l"],
        "comparison_case": summary["comparison_case"],
        "outcome_band": summary["outcome_band"],
    }


def summarize(batch):
    rows = [result.summary_row() for result in batch.results]
    finite_break_even = [
        row["break_even_main_share_c"]
        for row in rows
        if row["break_even_main_share_c"] is not None
    ]
    bands = {}
    comparison_cases = {}
    for row in rows:
        bands[row["outcome_band"]] = bands.get(row["outcome_band"], 0) + 1
        comparison_cases[row["comparison_case"]] = (
            comparison_cases.get(row["comparison_case"], 0) + 1
        )

    most_funnel = max(
        batch.results,
        key=lambda result: result.summary_row()["relative_change"],
    )
    most_conventional = min(
        batch.results,
        key=lambda result: result.summary_row()["relative_change"],
    )
    finite_margin_results = [
        result
        for result in batch.results
        if result.summary_row()["margin"] is not None
    ]
    closest = (
        None
        if not finite_margin_results
        else min(
            finite_margin_results,
            key=lambda result: abs(result.summary_row()["margin"]),
        )
    )

    funnel_wins = bands.get("clear_funnel", 0) + bands.get("marginal_funnel", 0)
    conventional_wins = (
        bands.get("clear_conventional", 0)
        + bands.get("marginal_conventional", 0)
    )

    return {
        "sample_count": len(rows),
        "funnel_wins": funnel_wins,
        "conventional_wins": conventional_wins,
        "tie_band": bands.get("tie_band", 0),
        "outcome_bands": bands,
        "comparison_cases": comparison_cases,
        "relative_change": _stats(row["relative_change"] for row in rows),
        "main_share": _stats(row["conventional_main_share"] for row in rows),
        "break_even": _stats(finite_break_even),
        "g": _stats(row["g"] for row in rows),
        "l": _stats(row["l"] for row in rows),
        "extremes": {
            "most_funnel_favorable": _case_digest(most_funnel),
            "most_conventional_favorable": _case_digest(most_conventional),
            "closest_to_break_even": (
                None if closest is None else _case_digest(closest)
            ),
        },
    }


def _combat_for(*, main: str, condition: str) -> CombatSettings:
    if condition == "neutral":
        boss_element = None
    elif condition == "main-advantage":
        boss_element = main_advantage_boss_element(main)
    else:
        raise ValueError(f"unsupported boss condition: {condition}")
    return CombatSettings(
        boss_def=140.0,
        boss_element=boss_element,
        core_hit_rate_pct=0.0,
        range_bonus_pct=0.0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run RAID14 realistic 64-point Crown/Mast study"
    )
    parser.add_argument("--b1", choices=B1_CHOICES, required=True)
    parser.add_argument("--main", choices=MAIN_CHOICES, required=True)
    parser.add_argument(
        "--boss-mode",
        choices=BOSS_MODE_CHOICES,
        default="both",
    )
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()

    roster = TeamRoster(
        b1=args.b1,
        main_b3=args.main,
        secondary_b3="helm",
    )
    conditions = (
        ("neutral", "main-advantage")
        if args.boss_mode == "both"
        else (args.boss_mode,)
    )

    condition_payloads = {}
    for condition in conditions:
        combat = _combat_for(main=args.main, condition=condition)
        cases = build_checkpoint_v3_cases(
            roster=roster,
            combat_settings=combat,
            condition_id=condition,
        )
        batch = run_sample_batch(cases, workers=args.workers)
        condition_payloads[condition] = {
            "boss_element": combat.boss_element,
            "summary": summarize(batch),
        }

    payload = {
        "checkpoint": CHECKPOINT_V3_ID,
        "b1": args.b1,
        "main": args.main,
        "secondary": "helm",
        "baseline": "opening_mast_crown_mast",
        "conditions": condition_payloads,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
