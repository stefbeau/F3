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
    # Guard added after run #3: a one-row export produced a false "0.00% gap"
    # (it compared only the shared 1900 starting value).
    MIN_POINTS = 50
    if len(wd) < MIN_POINTS:
        raise ValueError(f"WorldDynamics.jl export has only {len(wd)} time points "
                         f"(need >= {MIN_POINTS}); comparison would be meaningless")
    if wd[time_col].min() > 1901 or wd[time_col].max() < 2099:
        raise ValueError(f"WorldDynamics.jl time range {wd[time_col].min():.0f}-"
                         f"{wd[time_col].max():.0f} does not cover 1900-2100")
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
        report.append(f"- Time points compared: {len(wd_t)} ({wd_t.min():.0f}-{wd_t.max():.0f})")
        report.append(f"- Columns used: `{cols}`")
        report.append(f"- Maximum relative gap: **{rel.max() * 100:.2f}%** in {wd_t[worst]:.0f}")
        report.append(f"- Mean relative gap: {rel.mean() * 100:.2f}%")
        flag = "within" if rel.max() <= 0.02 else "outside"
        report.append(f"- The two implementations are {flag} the ±2% band of D-004 "
                      "(informational at T0).")
        pd.DataFrame({"time": wd_t, "pop_worlddynamics": wd_pop, "pop_pyworld3": py_pop,
                      "relative_gap": rel}).to_csv(OUT / "world3_population_crosscheck.csv",
                                                   index=False)
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(wd_t, wd_pop / 1e9, label="WorldDynamics.jl (sum of 4 cohorts)")
            ax.plot(wd_t, py_pop / 1e9, "--", label="PyWorld3")
            ax.set_xlabel("Year"); ax.set_ylabel("Population (billions)")
            ax.set_title("World3 standard run: population, two implementations")
            ax.legend(); fig.tight_layout()
            fig.savefig(OUT / "world3_population_crosscheck.png", dpi=120)
            report.append("- Figure saved: `world3_population_crosscheck.png`")
        except Exception as e:
            report.append(f"- (figure not produced: {e})")
except FileNotFoundError as e:
    report.append(f"- ❌ Input missing (an earlier step failed): {e.filename}")
except Exception as e:
    report.append(f"- ❌ Comparison failed: {type(e).__name__}: {e}")

(OUT / "t0_4_crosscheck_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
