"""Are the three preset runs Epoch AI sent (reply of November 2026) the same series as the runs the playground shipped?

The shipped bundle can no longer be fetched (D-026 outcome note, 2026-11-25), so the series cannot be compared directly.
This script recomputes, from the runs Epoch sent, every comparison figure that was stored in October 2026 from the shipped
bundle (audit/data/s3-gate-comparison.json: S3 variant A, and the stored-composite diagnostic) and reports how far the two
sets of figures differ. Agreement supports identity for the fields those figures depend on; it is not a field-by-field proof.

Usage:  F3_GATE_RUNS=<folder with the unzipped *_run.json> python audit/t0/gate_runs_identity_check.py
Stores figures only (audit/data/gate-runs-identity.json).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from f3.core.model import Coupling, Model  # noqa: E402
from f3.core.replay import ReplaySector  # noqa: E402
from f3.sectors.s3_ai import SHARE_NAMES, S3AI  # noqa: E402
from tests.s3_checks import SETTINGS_B, compare, run_s3  # noqa: E402

NAMES = {"B0_default": "default", "B1_conservative": "conservative", "B2_aggressive": "aggressive"}
NOISE_FLOOR = 1e-12      # a stored figure below this is rounding noise; only "the new figure is also below it" is checked


def field(run: dict, name: str, n: int = 76) -> np.ndarray:
    return np.array(run[name + "_path"][:n], dtype=float)


def main() -> int:
    base = os.environ.get("F3_GATE_RUNS")
    if not base or not Path(base).is_dir():
        print("F3_GATE_RUNS is not set or is not a folder: nothing run (a skip, not a pass)")
        return 2
    stored = json.loads((REPO / "audit" / "data" / "s3-gate-comparison.json").read_text(encoding="utf-8"))
    rows, index_mismatch, noise_fail = [], 0, 0
    hashes = {}
    for key, (_, params) in SETTINGS_B.items():
        path = Path(base) / f"{NAMES[key]}_run.json"
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        run = json.loads(path.read_text(encoding="utf-8"))
        shares = {k: np.array(run[k + "_path"][:80], dtype=float) for k in SHARE_NAMES}
        res = compare(run_s3(params, shares), field, run)
        for q, rec in stored["settings"][key]["quantities"].items():
            index_mismatch += rec["max_index"] != res[q]["max_index"]
            for stat in ("max", "mean"):
                a, b = rec[stat], res[q][stat]
                if not (np.isfinite(a) and np.isfinite(b)):
                    continue
                if abs(a) < NOISE_FLOOR:
                    noise_fail += not abs(b) < NOISE_FLOOR
                else:
                    rows.append((abs(b / a - 1.0), f"variant A / {key} / {q} / {stat}"))
        t = 2025.0 + np.arange(80)
        rep = ReplaySector("investment_path", t, dict(shares), {k: "1" for k in shares})
        s3 = S3AI(params, stored_T=np.array(run["cognitive_ces_term_path"], dtype=float))
        Model([rep, s3], [Coupling("investment_path", k, "s3_ai", k) for k in SHARE_NAMES], 2025.0, 2101.0, 0.25).run()
        res2 = compare(s3.series(), field, run)
        for q, rec in stored["diagnostic_stored_T"][key].items():
            a, b = rec["max"], res2[q]["max"]
            if not (np.isfinite(a) and np.isfinite(b)):
                continue
            if abs(a) < NOISE_FLOOR:
                noise_fail += not abs(b) < NOISE_FLOOR
            else:
                rows.append((abs(b / a - 1.0), f"stored composite / {key} / {q} / max"))
    rows.sort(reverse=True)
    out = {"figures_compared": len(rows), "largest_relative_difference": rows[0][0], "largest_at": rows[0][1],
           "figures_identical_to_1e-9": sum(1 for r in rows if r[0] < 1e-9), "max_index_mismatches": int(index_mismatch),
           "noise_floor": NOISE_FLOOR, "figures_below_noise_floor_that_disagree": int(noise_fail), "sha256": hashes,
           "stored_figures_from_bundle_sha256": stored["bundle_sha256"]}
    print(json.dumps(out, indent=1))
    (REPO / "audit" / "data" / "gate-runs-identity.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
