"""S3 against the GATE playground's shipped runs: writes audit/data/s3-gate-comparison.json (comparison figures only, D-026)
and prints the tables used in audit/s3-gate-comparison.md.

    set PYTHONUTF8=1
    uv run --group dev python audit/t0/s3_report.py

Needs the pinned local copy of the bundle (tests/gate_reference.py: F3_GATE_BUNDLE or .gate_cache/gate.js). Nothing from the bundle
is written: only relative differences, first-year indices, parameter names and the bundle's sha256.

Also runs one DIAGNOSTIC (labelled so in the output): S3 with the composite task input T replaced, period by period, by the stored
`cognitive_ces_term`. It changes no equation in S3; it only shows which differences come from the production composite.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from f3.sectors import s3_ai  # noqa: E402
from tests import gate_reference as gr  # noqa: E402
from tests.s3_checks import (COMPARED, SETTINGS_B, STRESS, TOL, a15_properties, compare, constant_shares,  # noqa: E402
                             first_year_group_b, run_s3)

OUT = REPO / "audit" / "data" / "s3-gate-comparison.json"


def year(k):
    return None if k is None else 2025 + k


def diagnostic_with_stored_T(params, run, shares):
    stored_T = gr.field(run, "cognitive_ces_term", 80)
    counter = {"k": 0}
    original = s3_ai.task_composite

    def patched(L, f, C_I, C_T, p):
        k = counter["k"]
        counter["k"] += 1
        return float(stored_T[k]), 0.0

    s3_ai.task_composite = patched
    try:
        return run_s3(params, shares)
    finally:
        s3_ai.task_composite = original


def main():
    sha = gr.check_hash()
    runs = gr.load_runs()
    report = {"bundle_sha256": sha, "attribution": "Reference values: Epoch AI, GATE playground (https://epoch.ai/gate), CC BY 4.0, "
              "read from the public page; only comparison figures are stored", "tolerance": TOL, "indices": "0..75 = end of 2025..2100",
              "settings": {}, "diagnostic_stored_T": {}, "a15": {}, "stress": {}}
    for name, (idx, params) in SETTINGS_B.items():
        shares = gr.investment_shares(runs[idx], 80)
        s3 = run_s3(params, shares)
        res = compare(s3, gr.field, runs[idx])
        k_b = first_year_group_b(s3)
        report["settings"][name] = {"first_index_Q_over_0.1CL": k_b, "first_year_Q_over_0.1CL": year(k_b), "quantities": res}
        stored_cl = gr.field(runs[idx], "compute") / gr.field(runs[idx], "software") > params.C_L / 11
        report["settings"][name]["first_year_stored_compute_over_software_gt_CL_over_11"] = year(int(np.argmax(stored_cl))) if stored_cl.any() else None
        d = compare(diagnostic_with_stored_T(params, runs[idx], shares), gr.field, runs[idx])
        report["diagnostic_stored_T"][name] = {q: {"max": r["max"], "first_index_over_tol": r["first_index_over_tol"]} for q, r in d.items()}
        report["a15"][name] = {k: {"passed": ok, "detail": det} for k, (ok, det) in a15_properties(params, shares).items()}
    first = {k: float(v[0]) for k, v in gr.investment_shares(runs[0], 80).items()}
    for name, params in STRESS.items():
        report["stress"][name] = {k: {"passed": ok, "detail": det} for k, (ok, det) in a15_properties(params, constant_shares(first)).items()}
        report["stress"][name]["_note"] = "report-only; PLACEHOLDER constant shares (period-0 shares of the shipped default run, training share 0.5); not a rule"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    # ---- print tables --------------------------------------------------------------------------------------------------
    for name, r in report["settings"].items():
        print(f"\n### {name}: first year with Q > 0.1 C_L (S3's own Q): {r['first_year_Q_over_0.1CL']}; stored compute/software > C_L/11 from {r['first_year_stored_compute_over_software_gt_CL_over_11']}")
        print("| quantity | in criterion | max diff | at year | mean diff | first year > 2% | Q<=0.1CL: years, max | Q>0.1CL: years, max | pass |")
        print("|---|---|---|---|---|---|---|---|---|")
        for q, v in r["quantities"].items():
            a, b = v["Q<=0.1CL"], v["Q>0.1CL"]
            fa = f"{a['years']}, {a['max']:.2e}" if a["years"] else "0"
            fb = f"{b['years']}, {b['max']:.2e}" if b["years"] else "0"
            print(f"| {q} | {'yes' if v['in_criterion'] else 'report'} | {v['max']:.3g} | {year(v['max_index'])} | {v['mean']:.3g} | {year(v['first_index_over_tol'])} | {fa} | {fb} | {'yes' if v['passes'] else 'NO'} |")
        print(f"diagnostic (stored T fed in): " + "; ".join(f"{q}: max {v['max']:.2e}, first>2% {year(v['first_index_over_tol'])}" for q, v in report['diagnostic_stored_T'][name].items() if q in ('gwp','capital','hardware','software','compute_stock vs compute','frac_automated')))
        print("A1.5: " + "; ".join(f"{k}: {'PASS' if v['passed'] else 'FAIL'} ({v['detail']})" for k, v in report['a15'][name].items()))
    for name, r in report["stress"].items():
        print(f"\nstress {name}: " + "; ".join(f"{k}: {'PASS' if v['passed'] else 'FAIL'} ({v['detail']})" for k, v in r.items() if k != '_note'))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
