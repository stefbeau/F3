"""T0 cross-check: compare World3 population between WorldDynamics.jl and PyWorld3.

Informational at T0 (D-012: gaps must be explained, not necessarily zero).
World3's population is the sum of four age cohorts (0-14, 15-44, 45-64, 65+),
named p1..p4 in the model equations. If the cohort columns cannot be found
automatically in the WorldDynamics.jl export, the report says so and lists
what was found, so the mapping can be fixed by hand.
"""
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(os.environ.get("F3_OUT", Path(__file__).resolve().parents[1] / "results"))
report = ["## T0 — World3 cross-check (WorldDynamics.jl vs PyWorld3)", ""]
COHORT = re.compile(r"(^|[₊.])p([1-4])(\(t\))?$")

try:
    wd = pd.read_csv(OUT / "world3_worlddynamics_states.csv")
    py = pd.read_csv(OUT / "world3_pyworld3.csv")
    time_col = wd.columns[0]
    cohorts = {}
    for col in wd.columns[1:]:
        m = COHORT.search(col)
        if m:
            cohorts.setdefault(m.group(2), []).append(col)
    if sorted(cohorts) != ["1", "2", "3", "4"] or any(len(v) != 1 for v in cohorts.values()):
        found = {k: v for k, v in sorted(cohorts.items())}
        report.append(f"- ⚠️ Cohort columns p1–p4 not identified unambiguously; found: `{found}`. "
                      "Manual mapping needed (see `world3_worlddynamics_columns.txt`).")
    else:
        cols = [cohorts[k][0] for k in "1234"]
        wd_pop = wd[cols].sum(axis=1).to_numpy()
        wd_t = wd[time_col].to_numpy()
        py_pop = np.interp(wd_t, py["time"], py["pop"])
        rel = np.abs(wd_pop - py_pop) / py_pop
        worst = int(np.argmax(rel))
        report.append(f"- Columns used: `{cols}`")
        report.append(f"- Maximum relative gap: **{rel.max() * 100:.2f}%** in {wd_t[worst]:.0f}")
        report.append(f"- Mean relative gap: {rel.mean() * 100:.2f}%")
        flag = "within" if rel.max() <= 0.02 else "outside"
        report.append(f"- The two implementations are {flag} the ±2% band of D-004 "
                      "(informational at T0).")
        pd.DataFrame({"time": wd_t, "pop_worlddynamics": wd_pop, "pop_pyworld3": py_pop,
                      "relative_gap": rel}).to_csv(OUT / "world3_population_crosscheck.csv",
                                                   index=False)
except FileNotFoundError as e:
    report.append(f"- ❌ Input missing (an earlier step failed): {e.filename}")
except Exception as e:
    report.append(f"- ❌ Comparison failed: {type(e).__name__}: {e}")

(OUT / "t0_4_crosscheck_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
