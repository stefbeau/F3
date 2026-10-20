"""M4 step effect (plan A4.1, first part): per sector alone with recorded inputs, the worst criterion variable and every variable above 2% for
S1 (RK4 at 1/64 year) and S2 (RK4 at the loop step 0.25 year). Writes tests/fixtures/e4a_step_effect.json, which the sector tests read as the
RECORD of the first result (strict xfail with the sizes); a code change that makes a recorded failure pass flags itself.
    PYTHONPATH=. python audit/t0/e4a_step_effect.py
"""
import json
import sys

from audit.t0.e4a_ladder import case_of
from tests.e4a_helpers import FINE, SCENARIOS, compare, run_alone, worst

OUT = {}
for key in ["output", "inventory", "finance", "labourmarket", "public", "demand", "energy", "other"]:
    case = case_of(key)
    for tag, dt, method, sub in (("S1", FINE, "rk4", None), ("S2", 0.25, "rk4", None)):
        for scen in SCENARIOS:
            s, res = run_alone(key, scen, dt, method, sub)
            rows = compare(res, s.name, scen, case.criterion)
            w = worst(rows)
            bad = {r.name: [None if r.max_err == float("inf") else round(100 * r.max_err, 3), r.first_year_above] for r in rows.values() if not r.excluded and r.max_err > 0.02}
            OUT[f"{key}|{tag}|{scen}"] = {"worst": w.name, "worst_pct": None if w.max_err == float("inf") else round(100 * w.max_err, 4), "year": w.year_of_max, "above_2pct": bad}
            print(key, tag, scen, OUT[f"{key}|{tag}|{scen}"]["worst"], OUT[f"{key}|{tag}|{scen}"]["worst_pct"], len(bad), flush=True)
json.dump(OUT, open("tests/fixtures/e4a_step_effect.json", "w", encoding="utf-8", newline="\n"), indent=1)
