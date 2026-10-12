"""A1.4 (report only, D-005, D-028): R3 against GATE's optimised path. Writes audit/data/s3-r3-a1.4.json (comparison figures only)
and prints the tables for audit/s3-r3-a1.4.md.  Method: docs/s3-investment-rule-r3.md section 4.

    set PYTHONUTF8=1
    uv run --group dev python audit/t0/s3_r3_a14.py

Row set (a): S3 with its own production composite (variant A), driven by R3. Row set (b): the same with Epoch's stored composite T
supplied (DIAGNOSTIC input) so composite-independent quantities show the rule's own error. R3 is not tuned after seeing these numbers.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from f3.sectors.s3_ai import SHARE_NAMES, S3AI, usable_compute  # noqa: E402
from f3.sectors.s3_rule_r3 import R3Rule  # noqa: E402
from tests import gate_reference as gr  # noqa: E402
from tests.s3_checks import N_PERIODS, SETTINGS_B  # noqa: E402
from f3.core.model import Model  # noqa: E402

OUT = REPO / "audit" / "data" / "s3-r3-a1.4.json"


def run(params, rule, stored_T=None):
    s3 = S3AI(params, rule=rule, stored_T=stored_T)
    Model([s3], [], 2025.0, 2025.0 + N_PERIODS, 0.25).run()
    return s3.series()


def stats(mine, ref, kind="rel"):
    with np.errstate(divide="ignore", invalid="ignore"):
        d = np.abs(mine / ref - 1.0) if kind == "rel" else np.abs(mine - ref) * 100.0       # percentage points for shares
    d = np.where(np.isfinite(d), d, np.nan)
    first = lambda th: (None if not (d > th).any() else 2025 + int(np.argmax(d > th)))
    th5, th10 = (0.05, 0.10) if kind == "rel" else (5.0, 10.0)
    return {"max": float(np.nanmax(d)), "mean": float(np.nanmean(d)), "first_year_over_5": first(th5), "first_year_over_10": first(th10)}


def rows(s3, run_, params):
    n = N_PERIODS
    res = {}
    for sh in SHARE_NAMES:
        res["share " + sh + " (percentage points)"] = stats(s3["share_" + sh][:n], gr.field(run_, sh, n), "abs")
    res["raw stock Q vs stored compute"] = stats(s3["compute_stock"][:n], gr.field(run_, "compute", n))
    Qref = gr.field(run_, "compute", n); Sref = gr.field(run_, "software", n)
    eff_ref = np.array([usable_compute(q, params.C_L) for q in Qref]) * Sref
    res["effective compute g(Q)S vs g(stored compute) x stored software (derived)"] = stats(s3["effective_compute"][:n], eff_ref)
    for mine, theirs in (("hardware", "hardware"), ("software", "software"), ("frac_automated", "frac_automated"), ("gwp", "gwp")):
        res[mine] = stats(s3[mine][:n], gr.field(run_, theirs, n))
    return res


def main():
    gr.check_hash()
    runs = gr.load_runs()
    rule = R3Rule()
    report = {"bundle_sha256": gr.EXPECTED_SHA256, "note": "comparison figures only (D-026); report-only, no pass/fail (D-005 A1.4)", "settings": {}}
    for name, (idx, params) in SETTINGS_B.items():
        r = runs[idx]
        a = rows(run(params, rule), r, params)
        b = rows(run(params, rule, stored_T=gr.field(r, "cognitive_ces_term", 80)), r, params)
        report["settings"][name] = {"a_full_chain": a, "b_stored_T": b}
        for label, rs in (("(a) full chain, S3's own composite", a), ("(b) stored composite T supplied (diagnostic)", b)):
            print(f"\n### {name} {label}\n| quantity | max | mean | first year >5% | first year >10% |\n|---|---|---|---|---|")
            for q, v in rs.items():
                u = " pp" if "percentage points" in q else ""
                f = (lambda x: f"{x:.3g}{u}") if u else (lambda x: f"{x:.2%}")
                print(f"| {q} | {f(v['max'])} | {f(v['mean'])} | {v['first_year_over_5'] or '-'} | {v['first_year_over_10'] or '-'} |")
    OUT.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
