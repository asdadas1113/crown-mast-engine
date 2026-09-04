from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from crown_mast_engine.checkpoints_v3 import build_checkpoint_v3_cases, main_advantage_boss_element
from crown_mast_engine.combat import CombatSettings
from crown_mast_engine.models import TeamRoster
from crown_mast_engine.samples import run_sample_batch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--b1", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    roster = TeamRoster(
        b1=args.b1,
        main_b3="snow-white-heavy-arms",
        secondary_b3="cinderella",
    )
    rows = []
    for core_condition, core_pct in (("off", 0.0), ("on", 100.0)):
        for advantage in ("off", "on"):
            boss_element = None if advantage == "off" else main_advantage_boss_element(roster.main_b3)
            cases = build_checkpoint_v3_cases(
                roster=roster,
                combat_settings=CombatSettings(core_hit_rate_pct=core_pct, boss_element=boss_element),
                condition_id=f"explore-reversed--b1-{args.b1}--core-{core_condition}--adv-{advantage}",
            )
            batch = run_sample_batch(cases, workers=args.workers)
            for result in batch.results:
                row = result.summary_row()
                row["b1_profile"] = result.labels["b1_profile"]
                row["main_profile"] = result.labels["main_profile"]
                row["secondary_profile"] = result.labels["secondary_profile"]
                row["core_condition"] = core_condition
                row["main_advantage"] = advantage
                rows.append(row)

    if len(rows) != 256:
        raise AssertionError(f"expected 256 rows, got {len(rows)}")
    if len({row["case_id"] for row in rows}) != 256:
        raise AssertionError("case ids are not unique")

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"EXPLORATORY_SHARD_OK b1={args.b1} scenarios=256 output={path}")


if __name__ == "__main__":
    main()
