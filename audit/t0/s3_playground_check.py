"""T2 of docs/s3-playground-composite.md (D-062): S3 with composite="P" against the five runs Epoch AI sent in its reply.

The runs are NOT in the repository. Point F3_GATE_RUNS at the folder holding the unzipped `*_run.json` files.
Stores comparison figures only (audit/data/s3-playground-composite.json): no series, nothing that allows one to be rebuilt.
This is not test A1.3 (that is tests/test_s3_playground.py::test_t1_a13_criterion_variant_p, which needs the pinned bundle).

Usage:  F3_GATE_RUNS=<folder> python audit/t0/s3_playground_check.py [--composite A]
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tests.s3_checks import SETTINGS_B, STRESS, TOL, compare, run_s3  # noqa: E402

RUNS = {
    "default": SETTINGS_B["B0_default"][1],
    "conservative": SETTINGS_B["B1_conservative"][1],
    "aggressive": SETTINGS_B["B2_aggressive"][1],
    "T41_lam025": STRESS["slow_T41_lam0.25"],
    "T33_lam1": STRESS["fast_T33_lam1"],
}
SHARES = ("q_consumption", "q_compute", "q_capital", "q_hardware_rnd", "q_software_rnd", "q_training_compute")


def field(run: dict, name: str, n: int = 76) -> np.ndarray:
    return np.array(run[name + "_path"][:n], dtype=float)


def main() -> int:
    variant = sys.argv[sys.argv.index("--composite") + 1] if "--composite" in sys.argv else "P"
    base = os.environ.get("F3_GATE_RUNS")
    if not base or not Path(base).is_dir():
        print("F3_GATE_RUNS is not set or is not a folder: nothing run (this is a skip, not a pass)")
        return 2
    out = {"composite": variant, "tolerance": TOL, "indices": "0..75", "runs": {}}
    for name, params in RUNS.items():
        run = json.loads((Path(base) / f"{name}_run.json").read_text(encoding="utf-8"))
        shares = {k: np.array(run[k + "_path"][:80], dtype=float) for k in SHARES}
        s3 = run_s3(replace(params, composite=variant), shares)
        res = compare(s3, field, run)
        failing = {k: v["first_index_over_tol"] for k, v in res.items() if v["in_criterion"] and not v["passes"]}
        out["runs"][name] = {"passes_2pct": not failing, "failing_first_index": failing,
                             "quantities": {k: {"in_criterion": v["in_criterion"], "max": v["max"], "max_index": v["max_index"],
                                                "mean": v["mean"]} for k, v in res.items()}}
        print(f"{name:13s} {'PASS' if not failing else 'FAIL ' + str(failing)}")
        for k, v in res.items():
            print(f"    {k:32s} max {v['max']:.3e} at index {v['max_index']:2d}{'' if v['in_criterion'] else '   (reported, not in the criterion)'}")
    if "--no-write" not in sys.argv:
        target = REPO / "audit" / "data" / ("s3-playground-composite.json" if variant == "P" else f"s3-playground-check-{variant}.json")
        target.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
        print("written", target.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
