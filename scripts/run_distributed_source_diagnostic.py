from __future__ import annotations

import argparse
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


DISTRIBUTED_MAINS = (
    "scarlet-black-shadow",
    "bready",
    "quency-escape-queen",
    "phantom",
    "milk-blooming-bunny",
)
CONTROL_MAINS = ("rapi-red-hood",)
ALL_MAINS = DISTRIBUTED_MAINS + CONTROL_MAINS
REPRESENTATIVE_PROFILE = "g3-ol0-sr15-e3-a3"


def _pair(pair):
    return {
        "conventional": pair.conventional,
        "funnel": pair.funnel,
        "delta": pair.delta,
        "relative_change": pair.relative_change,
    }


def _representative_case(main_actor: str):
    roster = TeamRoster(
        b1="liter",
        main_b3=main_actor,
        secondary_b3="helm",
    )
    combat = CombatSettings(
        boss_def=140.0,
        boss_element=None,
        core_hit_rate_pct=0.0,
        range_bonus_pct=0.0,
    )
    cases = build_checkpoint_v3_cases(
        roster=roster,
        combat_settings=combat,
        condition_id="distributed-source-neutral-core0",
    )
    selected = tuple(
        case
        for case in cases
        if case.labels["b1_profile"] == REPRESENTATIVE_PROFILE
        and case.labels["main_profile"] == REPRESENTATIVE_PROFILE
        and case.labels["secondary_profile"] == REPRESENTATIVE_PROFILE
    )
    if len(selected) != 1:
        raise RuntimeError(f"expected one representative case, got {len(selected)}")
    return selected[0]


def run_main(main_actor: str):
    result = run_sample_batch((_representative_case(main_actor),), workers=1).results[0]
    report = result.report
    main_total = report.by_character[main_actor].damage
    sources = [
        {
            "source": source,
            **_pair(damage),
            "share_of_main_conventional": (
                None
                if main_total.conventional == 0
                else damage.conventional / main_total.conventional
            ),
            "share_of_main_delta": (
                None if main_total.delta == 0 else damage.delta / main_total.delta
            ),
        }
        for actor, source, damage in report.by_source
        if actor == main_actor
    ]
    burst_cycles = [
        {
            "cycle": cycle,
            "main_conventional": slice_report.main_conventional,
            "main_funnel": slice_report.main_funnel,
            "main_relative_change": slice_report.g,
            "team_relative_change": slice_report.team.relative_change,
        }
        for cycle, slice_report in sorted(report.burst_cycles.items())
    ]
    return {
        "case_id": result.case_id,
        "main_total": _pair(main_total),
        "overall_g": report.overall.g,
        "overall_l": report.overall.l,
        "overall_team_relative_change": report.overall.team.relative_change,
        "sources": sources,
        "burst_cycles": burst_cycles,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect source-level funnel response for distributed Main B3 actors"
    )
    parser.add_argument("--main", choices=ALL_MAINS, required=True)
    args = parser.parse_args()
    payload = {
        "study": "distributed-main-source-diagnostic-v1",
        "status": "pretest-not-official-result",
        "fixed": {
            "b1": "liter",
            "secondary_b3": "helm",
            "growth_profile": REPRESENTATIVE_PROFILE,
            "boss_def": 140.0,
            "boss_element": None,
            "core_hit_rate_pct": 0.0,
            "range_bonus_pct": 0.0,
        },
        "main": args.main,
        "result": run_main(args.main),
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
