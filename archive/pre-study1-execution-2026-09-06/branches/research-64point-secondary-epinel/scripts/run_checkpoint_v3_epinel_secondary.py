from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from crown_mast_engine.checkpoints_v3 import CHECKPOINT_V3_ID, build_checkpoint_v3_cases
from crown_mast_engine.models import TeamRoster
from crown_mast_engine.samples import run_sample_batch
from run_checkpoint_v3_study import _combat_for, summarize

B1_CHOICES = ("liter", "anis-star")
MAIN_CHOICES = (
    "rapi-red-hood",
    "scarlet-black-shadow",
    "snow-white-heavy-arms",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAID14 v3 with Epinel secondary")
    parser.add_argument("--b1", choices=B1_CHOICES, required=True)
    parser.add_argument("--main", choices=MAIN_CHOICES, required=True)
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()

    roster = TeamRoster(
        b1=args.b1,
        main_b3=args.main,
        secondary_b3="epinel",
    )
    condition_payloads = {}
    for condition in ("neutral", "main-advantage"):
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

    print(json.dumps({
        "checkpoint": CHECKPOINT_V3_ID,
        "b1": args.b1,
        "main": args.main,
        "secondary": "epinel",
        "baseline": "opening_mast_crown_mast",
        "conditions": condition_payloads,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
