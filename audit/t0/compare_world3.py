"""T0 cross-check: World3 population, WorldDynamics.jl variants vs PyWorld3.

World3's population is the sum of four age cohorts (0-14, 15-44, 45-64, 65+),
named p1..p4. Every WorldDynamics.jl solver variant exported by world3_t0.jl
(world3_worlddynamics_states_<variant>.csv) is compared with PyWorld3 at its
default step (dt=0.5) and with the fine-step run (dt=0.05, near the continuous
limit). Informational at T0 (D-012: gaps must be explained, not necessarily zero).

Guards (added after run #3 produced a false "0.00% gap" from a 1-point solution):
a file with fewer than 50 time points, or not covering 1900-2100, is refused.
"""
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(os.environ.get("F3_OUT", Path(__file__).resolve().parents[1] / "results"))
COHORT = re.compile(r"(^|[₊.])p([1-4])(\(t\))?$")
MIN_POINTS = 50
BAND = 0.02  # D-004
report = ["## T0 — World3 cross-check (WorldDynamics.jl vs PyWorld3), population", ""]


def population(df):
    time_col = df.columns[0]
    if len(df) < MIN_POINTS:
        raise ValueError(f"only {len(df)} time points (need >= {MIN_POINTS})")
    if df[time_col].min() > 1901 or df[time_col].max() < 2099:
        raise ValueError(f"time range {df[time_col].min():.0f}-{df[time_col].max():.0f} "
                         "does not cover 1900-2100")
    cohorts = {}
    for col in df.columns[1:]:
        m = COHORT.search(col)
        if m:
            cohorts.setdefault(m.group(2), []).append(col)
    if sorted(cohorts) != ["1", "2", "3", "4"] or any(len(v) != 1 for v in cohorts.values()):
        raise ValueError(f"cohort columns p1-p4 not identified unambiguously; found {cohorts}")
    cols = [cohorts[k][0] for k in "1234"]
    return df[time_col].to_numpy(), df[cols].sum(axis=1).to_numpy(), cols


def gap(t, pop, ref):
    ref_i = np.interp(t, ref["time"], ref["pop"])
    rel = np.abs(pop - ref_i) / ref_i
    return rel, int(np.argmax(rel))


try:
    py = pd.read_csv(OUT / "world3_pyworld3.csv")
    fine_path = OUT / "world3_pyworld3_fine.csv"
    fine = pd.read_csv(fine_path) if fine_path.exists() else None
    files = sorted(OUT.glob("world3_worlddynamics_states_*.csv"))
    if not files:
        report.append("- ❌ No WorldDynamics.jl export found (an earlier step failed)")
    best = None
    for f in files:
        tag = f.stem.replace("world3_worlddynamics_states_", "")
        try:
            t, pop, cols = population(pd.read_csv(f))
        except Exception as e:
            report.append(f"- ❌ `{tag}`: refused: {e}")
            continue
        line = f"- `{tag}` ({len(t)} points)"
        for label, ref in [("PyWorld3 dt=0.5", py), ("PyWorld3 dt=0.05", fine)]:
            if ref is None:
                continue
            rel, k = gap(t, pop, ref)
            flag = "within" if rel.max() <= BAND else "OUTSIDE"
            line += (f"\n  - vs {label}: max **{rel.max() * 100:.2f}%** in {t[k]:.0f}, "
                     f"mean {rel.mean() * 100:.2f}% ({flag} ±2%)")
        report.append(line)
        if best is None or len(t) >= best[0]:
            best = (len(t), tag, t, pop)
    if best:
        report.append(f"- Columns used for population: `{cols}`")
        _, tag, t, pop = best
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(t, pop / 1e9, label=f"WorldDynamics.jl ({tag})")
            ax.plot(py["time"], py["pop"] / 1e9, "--", label="PyWorld3 dt=0.5")
            if fine is not None:
                ax.plot(fine["time"], fine["pop"] / 1e9, ":", label="PyWorld3 dt=0.05")
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
