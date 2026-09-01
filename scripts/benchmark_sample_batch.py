from __future__ import annotations

import os
import time

from crown_mast_engine.interface import build_checkpoint_cases
from crown_mast_engine.samples import run_sample_batch


CHECKPOINT_PAYLOAD = {
    "roster": {
        "b1": "liter",
        "main_b3": "rapi-red-hood",
        "secondary_b3": "helm",
    },
    "combat": {
        "boss_def": 140.0,
        "boss_element": None,
        "core_hit_rate_pct": 0.0,
        "range_bonus_pct": 0.0,
    },
}


def _run(cases, *, workers: int | None):
    started = time.perf_counter()
    result = run_sample_batch(cases, workers=workers)
    return result, time.perf_counter() - started


def main() -> None:
    cases = build_checkpoint_cases(CHECKPOINT_PAYLOAD)
    serial, serial_sec = _run(cases, workers=1)
    parallel, parallel_sec = _run(cases, workers=None)

    if serial.to_dict() != parallel.to_dict():
        raise AssertionError("serial and parallel sample batches differ")

    speedup = serial_sec / parallel_sec if parallel_sec else float("inf")
    print(f"cpu_count={os.cpu_count() or 1}")
    print(f"case_count={len(cases)}")
    print(f"serial_seconds={serial_sec:.6f}")
    print(f"parallel_seconds={parallel_sec:.6f}")
    print(f"speedup={speedup:.4f}x")
    print("results_identical=true")


if __name__ == "__main__":
    main()
