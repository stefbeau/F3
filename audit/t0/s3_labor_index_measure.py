"""Option B measurement (D-054 item 5): the integrated loop with World3's labour-force index driving S3 labour, against the same loop with the link OFF.
Stand-in smooth climate (no FaIR run needed; the link does not use the climate). Diagnostic: reads outputs only.

    set PYTHONUTF8=1
    uv run --group dev python audit/t0/s3_labor_index_measure.py
Writes audit/data/s3-labor-index.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from f3.sectors.m6_integrated import M6Config, run_m6  # noqa: E402
from tests.test_m6_integration import stand_in_climate  # noqa: E402

OUT = REPO / "audit" / "data" / "s3-labor-index.json"
DECADES = [2025, 2030, 2040, 2050, 2060, 2075, 2099]


def main() -> None:
    on = run_m6(M6Config(labor_from_world3=True), stand_in_climate())
    off = run_m6(M6Config(labor_from_world3=False), stand_in_climate())
    t = on.time
    at = lambda r, sec, n, y: float(r.series[(sec, n)][int(np.argmin(np.abs(t - y)))])      # noqa: E731
    rep = {"decades": DECADES, "rows": {}}
    for y in DECADES:
        rep["rows"][str(y)] = {n: {"off": at(off, "s3_ai", n, y), "on": at(on, "s3_ai", n, y)} for n in ("labor", "gwp", "capital", "frac_automated", "labor_share")}
        rep["rows"][str(y)]["world3_lf"] = at(on, "world3", "lf", y)
        rep["rows"][str(y)]["world3_lf_over_2025"] = at(on, "world3", "lf", y) / at(on, "world3", "lf", 2025)
    json.dump(rep, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1)
    print("wrote", OUT)
    for y in DECADES:
        r = rep["rows"][str(y)]
        print(y, "lf index %.3f" % r["world3_lf_over_2025"], "S3 labour on/off %.3f" % (r["labor"]["on"] / r["labor"]["off"]), "gwp on/off %.4f" % (r["gwp"]["on"] / r["gwp"]["off"]),
              "f off %.2f on %.2f" % (r["frac_automated"]["off"], r["frac_automated"]["on"]))


if __name__ == "__main__":
    main()
