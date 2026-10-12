"""Fit the R1 curves of the R3 rule (D-028) to the three shipped GATE runs. Method: docs/s3-investment-rule-r3.md section 2.

    set PYTHONUTF8=1
    uv run --group dev python audit/t0/s3_r3_fit.py

Reads the pinned local copy of the bundle (D-026) and writes ONLY the fitted curve tables to f3/sectors/r3_curves.json
(five shares x (5 f-knots + 8 log10(u)-knots)); no series from the bundle is written.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from f3.sectors.s3_ai import GateParams, usable_compute  # noqa: E402
from f3.sectors.s3_rule_r3 import F_KNOTS, FITTED, LOGU_KNOTS  # noqa: E402
from tests import gate_reference as gr  # noqa: E402

N = 76


def main():
    gr.check_hash()
    runs = gr.load_runs()
    p = GateParams()
    C0 = p.C_T0 + p.runtime_compute_init
    Q0 = C0 / (1.0 - C0 / p.C_L)
    per_run = []
    for r in runs:
        f = gr.field(r, "frac_automated", N)
        Q = gr.field(r, "compute", N)
        Qprev = np.r_[Q0, Q[:-1]]
        u = np.array([usable_compute(q, p.C_L) / p.C_L for q in Qprev])
        sh = {n: gr.field(r, n, N) for n in FITTED}
        per_run.append((f, u, sh))
    out = {"method": "docs/s3-investment-rule-r3.md section 2", "f_knots": list(F_KNOTS), "logu_knots": list(LOGU_KNOTS),
           "f_curves": {}, "u_curves": {}, "bundle_sha256": gr.EXPECTED_SHA256,
           "attribution": "fitted to runs read from Epoch AI's GATE playground (CC BY 4.0); curve parameters only"}
    mid = (np.array(LOGU_KNOTS)[1:] + np.array(LOGU_KNOTS)[:-1]) / 2
    for n in FITTED:
        fc, uc = [], []
        for kn in F_KNOTS:
            vals = []
            for f, u, sh in per_run:
                m = np.abs(f - kn) < 0.1
                if m.any():
                    vals.append(float(sh[n][m].mean()))
            fc.append(float(np.mean(vals)))
        full = []
        for f, u, sh in per_run:
            lu = np.log10(u)
            bins = np.digitize(lu[f >= 0.999], mid)
            row = [float(sh[n][f >= 0.999][bins == j].mean()) if (bins == j).any() else None for j in range(len(LOGU_KNOTS))]
            full.append(row)
        for j in range(len(LOGU_KNOTS)):
            vs = [r[j] for r in full if r[j] is not None]
            uc.append(float(np.mean(vs)) if vs else None)
        # knots with no data take the nearest filled knot's value
        filled = [j for j, v in enumerate(uc) if v is not None]
        uc = [uc[j] if uc[j] is not None else uc[min(filled, key=lambda i: abs(i - j))] for j in range(len(uc))]
        out["f_curves"][n], out["u_curves"][n] = fc, uc
    path = REPO / "f3" / "sectors" / "r3_curves.json"
    path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    for n in FITTED:
        print(n, "f:", np.round(out["f_curves"][n], 4), "u:", np.round(out["u_curves"][n], 4))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
