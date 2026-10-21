"""S3 / World3 shared-quantity measurement (D-053 C). Method fixed in docs/s3-world3-reconciliation.md section 1 before this script was run.
DIAGNOSTIC ONLY: reads sector outputs, changes nothing.

    set PYTHONUTF8=1
    uv run --group dev python audit/t0/s3_world3_measure.py

Writes audit/data/s3-world3-measure.json and prints the tables.
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

from f3.core.model import Model  # noqa: E402
from f3.sectors.s3_ai import GateParams, S3AI  # noqa: E402
from f3.sectors.s3_rule_r3 import R3Levers, R3Rule  # noqa: E402
from f3.sectors.world3 import STATE_COLUMNS, _initial_inputs, build_world3  # noqa: E402
from f3.sectors.world3_group import World3Group  # noqa: E402

OUT = REPO / "audit" / "data" / "s3-world3-measure.json"
DATES = [2025, 2030, 2040, 2050, 2075, 2100]
LFPF = 0.75                                            # w3_capital Line 80.1, labour force participation fraction


def s3_run(levers: R3Levers) -> dict:
    s3 = S3AI(GateParams(), rule=R3Rule(levers))
    res = Model([s3], [], 2025.0, 2100.0, 0.25).run()
    t = res.time
    idx = {y: int(np.argmin(np.abs(t - y))) for y in range(2025, 2101)}
    return {n: {y: float(res.series[("s3_ai", n)][i]) for y, i in idx.items()} for n in ("gwp", "capital", "labor", "labor_share", "frac_automated")}


def world3_run() -> dict:
    """World3 group, standard 2004 set, damage off. io, so and lf are read from the capital sector's published outputs (diagnostic access)."""
    sectors, couplings = build_world3("2004")
    init = _initial_inputs(sectors, 1900.0)
    g = World3Group(sectors, couplings, init, STATE_COLUMNS)
    g.reset(1900.0, 2100.0, 0.25)
    out = {n: {} for n in ("pop", "lf", "io", "so", "iopc")}
    t = 1900.0

    def grab(year):
        st = g.current_outputs()
        cap = g._published["w3_capital"]
        out["pop"][year] = st["p1"] + st["p2"] + st["p3"] + st["p4"]
        out["lf"][year] = (st["p2"] + st["p3"]) * LFPF
        out["io"][year] = float(cap["io"])
        out["so"][year] = float(cap["so"])
        out["iopc"][year] = float(cap["iopc"])
    grab(1900)
    for k in range(800):
        g.advance(t, 0.25, None)
        t += 0.25
        if abs(t - round(t)) < 1e-9:
            grab(int(round(t)))
    return out


def earth4all() -> dict:
    rows = list(csv.DictReader(open(REPO / "tests" / "fixtures" / "e4a_signals_tltl.csv", encoding="utf-8-sig")))
    t = np.array([float(r["time"]) for r in rows])
    f = lambda c, y: float(rows[int(np.argmin(np.abs(t - y)))][c])          # noqa: E731
    return {"gdp_gdollar": {y: f("inventory.GDP", y) for y in range(2025, 2101)}, "pop_Mp": {y: f("population.POP", y) for y in range(2025, 2101)},
            "wf_Mp": {y: f("labourmarket.WF", y) for y in range(2025, 2101)}}


def cagr(d: dict, a: int, b: int) -> float:
    return (d[b] / d[a]) ** (1.0 / (b - a)) - 1.0


def main() -> None:
    s3c, s3o = s3_run(R3Levers()), s3_run(R3Levers(initial_ai_share=0.0))
    w3, e4 = world3_run(), earth4all()
    w3["io_so"] = {y: w3["io"][y] + w3["so"][y] for y in w3["io"]}
    rep = {"dates": DATES, "samples": {}, "growth": {}, "ratios": {}, "uplift": {}, "notes": ["S3 flows at a boundary are the year that just ended; World3 io/so are the values at 1 January"]}
    for y in DATES:
        rep["samples"][str(y)] = {
            "s3_gwp_usd": s3c["gwp"][y], "s3_labor": s3c["labor"][y], "s3_labor_share": s3c["labor_share"][y], "s3_frac_automated": s3c["frac_automated"][y],
            "s3_gwp_ai_off_usd": s3o["gwp"][y], "s3_frac_automated_ai_off": s3o["frac_automated"][y],
            "w3_pop": w3["pop"][y], "w3_lf": w3["lf"][y], "w3_io": w3["io"][y], "w3_so": w3["so"][y], "w3_io_so": w3["io_so"][y],
            "e4a_gdp_usd": e4["gdp_gdollar"][y] * 1e9, "e4a_pop": e4["pop_Mp"][y] * 1e6, "e4a_wf": e4["wf_Mp"][y] * 1e6}
        s = rep["samples"][str(y)]
        rep["ratios"][str(y)] = {"s3_labor/w3_pop": s["s3_labor"] / s["w3_pop"], "s3_labor/w3_lf": s["s3_labor"] / s["w3_lf"], "s3_labor/e4a_wf": s["s3_labor"] / s["e4a_wf"],
                                 "s3_gwp/w3_io": s["s3_gwp_usd"] / s["w3_io"], "s3_gwp/w3_so": s["s3_gwp_usd"] / s["w3_so"], "s3_gwp/w3_io_so": s["s3_gwp_usd"] / s["w3_io_so"],
                                 "s3_gwp/e4a_gdp": s["s3_gwp_usd"] / s["e4a_gdp_usd"]}
        rep["uplift"][str(y)] = {"gwp_central/gwp_ai_off": s["s3_gwp_usd"] / s["s3_gwp_ai_off_usd"]}
    for a, b in ((2025, 2050), (2050, 2100)):
        rep["growth"][f"{a}-{b}"] = {"s3_gwp": cagr(s3c["gwp"], a, b), "s3_gwp_ai_off": cagr(s3o["gwp"], a, b), "s3_labor": cagr(s3c["labor"], a, b),
                                     "w3_pop": cagr(w3["pop"], a, b), "w3_lf": cagr(w3["lf"], a, b), "w3_io": cagr(w3["io"], a, b), "w3_so": cagr(w3["so"], a, b),
                                     "w3_io_so": cagr(w3["io_so"], a, b), "e4a_gdp": cagr(e4["gdp_gdollar"], a, b), "e4a_pop": cagr(e4["pop_Mp"], a, b)}
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
