"""Supply-limited S3 diagnostic (D-054 item 3). Criteria: docs/s3-supply-limited.md section 3, committed before this script was run.
DIAGNOSTIC ONLY: reads sector outputs, changes nothing.

    set PYTHONUTF8=1
    uv run --group dev python audit/t0/s3_supply_limited.py <climate841.npz> [--cap]

Without --cap the module is as committed (cap OFF). With --cap, DCParams(eta_cap=4e15) is used (D-055; needs the cap to be implemented).
Writes audit/data/s3-supply-limited[-cap].json.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from f3.sectors.s3_ai import GateParams  # noqa: E402
from f3.sectors.s4_datacentre import DCParams  # noqa: E402
from f3.sectors.slice_m2 import ClimateReplay, SliceConfig, run_slice  # noqa: E402
from tests.s3_checks import SETTINGS_B  # noqa: E402

YEARS = [2025, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
DAMAGES = ("off", "low", "central", "high")
C_L = 2.0e38
WORLD_ENERGY_TWH = 5e20 / 3.6e15            # today's world energy use, paper D.3.2
IEA_2030_TWH = 950.0
SUPPLY_SHARE = 0.05
FACTOR_IEA, FACTOR_OUTPUT = 3.0, 10.0


def e4a_gdp() -> dict:
    rows = list(csv.DictReader(open(REPO / "tests" / "fixtures" / "e4a_signals_tltl.csv", encoding="utf-8-sig")))
    t = np.array([float(r["time"]) for r in rows])
    return {y: float(rows[int(np.argmin(np.abs(t - y)))]["inventory.GDP"]) * 1e9 for y in range(2025, 2101)}


def first(mask: np.ndarray, time: np.ndarray):
    i = np.where(mask)[0]
    return float(time[i[0]]) if len(i) else None


def one(name: str, params: GateParams, dmg: str, rep, dp: DCParams, e4: dict) -> dict:
    res = run_slice(SliceConfig(damage=dmg, gate=params, dc=dp), rep, t1=2100.0)
    t = res.time
    S = lambda sec, n: res.series[(sec, n)]                                       # noqa: E731
    at = lambda arr, y: float(arr[int(np.argmin(np.abs(t - y)))])                  # noqa: E731
    gwp, Q, eff, usable = S("s3_ai", "gwp"), S("s3_ai", "compute_stock"), S("s3_ai", "effective_compute"), S("s3_ai", "usable_compute")
    used, dem, ratio, avail = S("s4_datacentre", "e_dc"), S("s4_datacentre", "e_dc_demand"), S("s4_datacentre", "supply_ratio"), S("s4_datacentre", "dc_available")
    ok = np.isfinite(avail)                                                       # dc_available is NaN at t0 only
    binding = (ratio < 1.0 - 1e-12) & ok
    capdet = bool(binding.any()) and bool(np.all(np.abs(used[binding] / avail[binding] - 1.0) < 1e-9))
    out = {"setting": name, "damage": dmg,
           "decades": {str(y): {"gwp": at(gwp, y), "compute_stock": at(Q, y), "effective_compute": at(eff, y), "usable_compute": at(usable, y), "e_dc_used": at(used, y),
                                "e_dc_demand": at(dem, y), "supply_ratio": at(ratio, y), "dc_available": at(avail, y) if y > 2025 else None,
                                "gwp_over_e4a_gdp": at(gwp, y) / e4[y] if y <= 2100 else None} for y in YEARS},
           "checks": {
               "usable_le_CL": bool(np.all(usable <= C_L * (1 + 1e-12))), "max_Q_over_CL": float(np.max(Q) / C_L), "first_year_Q_gt_CL": first(Q > C_L, t),
               "max_effective_over_CL": float(np.max(eff) / C_L),
               "used_le_5pct_supply": bool(np.all(used[ok] <= avail[ok] * (1 + 1e-9))), "used_le_world_energy": bool(np.all(used <= WORLD_ENERGY_TWH)),
               "max_used_twh": float(np.max(used)), "used_2030": at(used, 2030), "used_2030_over_iea": at(used, 2030) / IEA_2030_TWH,
               "iea_2030_inside_factor3": bool(IEA_2030_TWH / FACTOR_IEA <= at(used, 2030) <= IEA_2030_TWH * FACTOR_IEA),
               "demand_2030": at(dem, 2030), "demand_2030_over_iea": at(dem, 2030) / IEA_2030_TWH,
               "first_year_demand_gt_available": first((dem > avail) & ok, t), "first_year_demand_gt_world_energy": first(dem > WORLD_ENERGY_TWH, t),
               "max_demand_over_world_energy": float(np.max(dem) / WORLD_ENERGY_TWH),
               "first_year_ratio_lt_0.5": first(ratio < 0.5, t), "first_year_ratio_lt_0.1": first(ratio < 0.1, t), "min_ratio": float(np.min(ratio)),
               "cap_determined": capdet,
               "gwp_within_factor10_of_e4a_all_decades": bool(all(1 / FACTOR_OUTPUT <= at(gwp, y) / e4[y] <= FACTOR_OUTPUT for y in YEARS)),
               "first_decade_gwp_outside_factor10": next((y for y in YEARS if not (1 / FACTOR_OUTPUT <= at(gwp, y) / e4[y] <= FACTOR_OUTPUT)), None),
               "all_finite": bool(all(np.all(np.isfinite(a[ok])) for a in (gwp, Q, eff, used, dem, ratio)))}}
    return out


def main() -> None:
    rec_path = Path(sys.argv[1])
    cap = "--cap" in sys.argv
    dp = DCParams(eta_cap=4.0e15) if cap else DCParams()
    z = np.load(rec_path)
    rep = ClimateReplay(z["years"], {n: z[n] for n in ("warming", "warming_p05", "warming_p95", "co2_concentration")})
    e4 = e4a_gdp()
    runs = []
    for name, (_, params) in SETTINGS_B.items():
        for dmg in DAMAGES:
            runs.append(one(name, params, dmg, rep, dp, e4))
            print("done", name, dmg, flush=True)
    out = {"eta_cap": 4.0e15 if cap else None, "years": YEARS, "bounds": {"C_L": C_L, "world_energy_twh": WORLD_ENERGY_TWH, "iea_2030_twh": IEA_2030_TWH, "supply_share": SUPPLY_SHARE,
                                                                       "factor_iea": FACTOR_IEA, "factor_output": FACTOR_OUTPUT}, "runs": runs}
    path = REPO / "audit" / "data" / ("s3-supply-limited-cap.json" if cap else "s3-supply-limited.json")
    path.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
