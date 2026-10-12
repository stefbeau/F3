"""M2 step 1 report: A2.1 and the report-only items fixed in docs/m2-step1-fair.md section 4. Writes audit/data/m2-fair-comparison.json
(comparison figures only; no HadCRUT5 series or FaIR calibration data) and prints tables for audit/m2-fair-report.md.

    set PYTHONUTF8=1
    uv run --group dev python audit/t0/m2_fair_report.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from f3.sectors.s6_climate import ClimateSetup, S6Climate  # noqa: E402
from tests.fair_checks import a21, hadcrut_rebased, fair_calendar_year  # noqa: E402

OUT = REPO / "audit" / "data" / "m2-fair-comparison.json"
SCENARIOS = ["high-extension", "high-overshoot", "medium-overshoot", "medium-extension", "low", "verylow", "verylow-overshoot"]


def window(per_year, a, b):
    ys = [y for y in range(a, b + 1)]
    f = np.mean([per_year[y]["fair_mean"] for y in ys])
    lo = np.mean([per_year[y]["obs_lower"] for y in ys]); hi = np.mean([per_year[y]["obs_upper"] for y in ys])
    best = np.mean([per_year[y]["obs_best"] for y in ys])
    return {"fair_mean": float(f), "obs_lower": float(lo), "obs_upper": float(hi), "obs_best": float(best), "inside": bool(lo <= f <= hi),
            "fair_minus_best": float(f - best), "fair_minus_lower": float(f - lo)}


def main():
    rep = {"note": "comparison figures only; HadCRUT5 (OGL v3.0) and FaIR calibration data are not stored", "a21": None, "windows": {}, "sensitivity": {}, "cost": {}}
    base = a21()
    rep["a21"] = {k: v for k, v in base.items() if k != "per_year"}
    rep["per_year"] = base["per_year"]
    pyr = base["per_year"]
    rep["windows"] = {"2015-2024 (A2.1)": window(pyr, 2015, 2024), "2015-2022 (inside the calibration window)": window(pyr, 2015, 2022),
                      "2023-2024 (outside it)": window(pyr, 2023, 2024)}
    first_out = [y for y in range(2015, 2025) if not (pyr[y]["obs_lower"] <= pyr[y]["fair_mean"] <= pyr[y]["obs_upper"])]
    rep["first_year_ensemble_mean_outside_annual_interval"] = first_out[0] if first_out else None
    rep["years_outside_annual_interval"] = first_out
    # sensitivity: CO2 source (GCB 2025 for all of 2015-2024) and non-CO2 scenario
    r = a21(ClimateSetup(gcb_from=2015))
    rep["sensitivity"]["CO2 from GCB 2025 for 2015-2024"] = {k: v for k, v in r.items() if k != "per_year"}
    r = a21(ClimateSetup(gcb_from=None))
    rep["sensitivity"]["CO2 from the file only (no GCB)"] = {k: v for k, v in r.items() if k != "per_year"}
    for sc in SCENARIOS:
        r = a21(ClimateSetup(scenario=sc))
        rep["sensitivity"][f"non-CO2 scenario {sc}"] = {k: v for k, v in r.items() if k != "per_year"}
    # members: spread
    cal = fair_calendar_year()
    dec = cal.loc[2015:2024].mean(axis=0)
    obs = hadcrut_rebased()
    lo, hi = float(obs.loc[2015:2024, "lower"].mean()), float(obs.loc[2015:2024, "upper"].mean())
    rep["members"] = {"decadal_mean_p05": float(dec.quantile(.05)), "decadal_mean_p50": float(dec.quantile(.5)), "decadal_mean_p95": float(dec.quantile(.95)),
                      "share_of_members_inside_obs_interval": float(((dec >= lo) & (dec <= hi)).mean()), "n": int(len(dec))}
    # cost of the D-021 re-run rule
    for n in (20, 841):
        s = S6Climate(ClimateSetup(n_members=n))
        s.reset(2024.0, 2030.0, 0.25)
        for y in range(2024, 2030):
            s.advance(float(y), 1.0, None)
        rep["cost"][f"{n} members"] = {"seconds_per_annual_rerun_2025_to_2030": float(np.mean(s.runtime_seconds[1:]))}
    n = 841
    rep["cost"]["projection_841_members_1980_to_2100_loop"] = {"annual_reruns": 120, "seconds": 120 * rep["cost"]["841 members"]["seconds_per_annual_rerun_2025_to_2030"]}
    OUT.write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in rep.items() if k != "per_year"}, indent=1))
    print("\nper year (K above 1850-1900): year | FaIR mean (p05-p95) | HadCRUT5 best [lower, upper]")
    for y, v in pyr.items():
        print(f"{y} | {v['fair_mean']:.3f} ({v['fair_p05']:.3f}-{v['fair_p95']:.3f}) | {v['obs_best']:.3f} [{v['obs_lower']:.3f}, {v['obs_upper']:.3f}]")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
