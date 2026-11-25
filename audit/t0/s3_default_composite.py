"""What changes when S3's default composite goes from variant A to variant P (D-065): S3 under F3's own investment rule R3
(central levers), with and without the data-centre electricity limit (TLTL supply, defaults of DCParams), no climate damage.

Stores F3's own outputs (audit/data/s3-default-composite.json). If F3_GATE_RUNS points at the runs Epoch sent, also stores
the RATIO of F3's output to the default GATE run's output at a few years (ratios only; none of Epoch's values).

Usage:  [F3_GATE_RUNS=<folder>] python audit/t0/s3_default_composite.py
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from dataclasses import replace
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
warnings.filterwarnings("ignore")

from f3.core.model import Coupling, Model  # noqa: E402
from f3.sectors.s3_ai import GateParams, S3AI  # noqa: E402
from f3.sectors.s3_rule_r3 import R3Rule  # noqa: E402
from f3.sectors.s4_datacentre import DataCentre, DCParams, supply_series  # noqa: E402

YEARS = (2027, 2030, 2035, 2040, 2060, 2099)


def run(variant: str, limited: bool) -> dict:
    gp, dp = replace(GateParams(), composite=variant), DCParams()
    s3 = S3AI(gp, rule=R3Rule(), electricity_limited=limited)
    sectors, cps = [s3], []
    if limited:
        sectors += [DataCentre(gp, dp), supply_series("TLTL")]
        cps = [Coupling("earth4all_supply", "supply", "s4_datacentre", "supply"),
               Coupling("s3_ai", "compute_stock", "s4_datacentre", "compute_stock"),
               Coupling("s3_ai", "hardware", "s4_datacentre", "hardware"),
               Coupling("s4_datacentre", "supply_ratio", "s3_ai", "supply_ratio")]
    res = Model(sectors, cps, t0=2025.0, t1=2100.0, dt=0.25).run()
    h = s3.series()
    yrs = 2025 + np.arange(len(h["gwp"]))                      # index k = end of year 2025 + k
    at = lambda a, y: float(a[int(np.where(yrs == y)[0][0])])
    g, f = h["gwp"], h["frac_automated"]
    growth = g[1:] / g[:-1] - 1.0
    out = {"gwp_trillion_usd": {str(y): at(g, y) / 1e12 for y in YEARS},
           "frac_automated": {str(y): at(f, y) for y in (2027, 2030, 2035)},
           "first_year_half_automated": int(yrs[np.where(f >= 0.5)[0][0]]),
           "first_year_fully_automated": int(yrs[np.where(f >= 0.999)[0][0]]) if (f >= 0.999).any() else None,
           "largest_yearly_gwp_growth": float(growth.max()), "year_of_largest_growth": int(yrs[1 + int(growth.argmax())])}
    if limited:
        t = res.time
        for name in ("e_dc_demand", "e_dc", "supply_ratio"):
            series = res.series[("s4_datacentre", name)]
            out["dc_" + name] = {str(y): float(series[int(np.where(np.isclose(t, y + 1.0))[0][0])]) for y in (2030, 2040)}
    return out


def main() -> int:
    out = {"note": "S3 under R3 (central levers), no damage; 'limited' = data-centre electricity limit on (TLTL supply)",
           "runs": {f"{'limited' if lim else 'unlimited'}_{v}": run(v, lim) for lim in (False, True) for v in ("A", "P")}}
    base = os.environ.get("F3_GATE_RUNS")
    if base and (Path(base) / "default_run.json").is_file():
        g = np.array(json.loads((Path(base) / "default_run.json").read_text(encoding="utf-8"))["gwp_path"], dtype=float)
        out["ratio_of_unlimited_gwp_to_the_default_GATE_run"] = {
            v: {str(y): out["runs"][f"unlimited_{v}"]["gwp_trillion_usd"][str(y)] * 1e12 / float(g[y - 2025]) for y in YEARS} for v in ("A", "P")}
    (REPO / "audit" / "data" / "s3-default-composite.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
