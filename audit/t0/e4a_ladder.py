"""M4 sub-step ladder (rule drafted in docs/tracks/track-c-plan.md before any run): for each sector alone with recorded inputs, the loop
step is 0.25 year and the sector is advanced with internal sub-steps from the ladder {RK4 0.125, RK4 0.0625, RK4 0.03125, Euler 1/64}.
Reports, per rung and scenario, the worst criterion variable (states and headline variables of the plan) and the first year above 2%.
    PYTHONPATH=. python audit/t0/e4a_ladder.py <sector> [<sector> ...]  > out.txt
"""
import re
import sys

import numpy as np

from tests.e4a_helpers import FINE, SCENARIOS, Case, compare, run_alone, worst

RUNGS = [("RK4 0.125", "rk4", 0.125), ("RK4 0.0625", "rk4", 0.0625), ("RK4 0.03125", "rk4", 0.03125), ("Euler 1/64", "euler", FINE)]


def case_of(key):
    t = open(f"tests/test_e4a_{key}.py", encoding="utf-8").read()
    m = re.search(r'CASE = Case\("(\w+)",\s*(\(.*?\)),\s*(\(.*?\))\)', t, re.S)
    return Case(m.group(1), eval(m.group(2)), eval(m.group(3)))


if __name__ == "__main__":
    for key in sys.argv[1:]:
        case = case_of(key)
        for label, method, sub in RUNGS:
            for scen in SCENARIOS:
                s, res = run_alone(key, scen, 0.25, method, sub)
                rows = compare(res, s.name, scen, case.criterion)
                w = worst(rows)
                bad = [(r.name, round(100 * r.max_err, 3), r.first_year_above) for r in rows.values() if not r.excluded and r.max_err > 0.02]
                print(f"{key} | {label} | {scen} | worst {w.name} {100 * w.max_err:.4f}% in {w.year_of_max} | above 2%: {bad}", flush=True)
