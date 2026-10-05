"""T0 second check: run the World3 standard run with PyWorld3, unmodified (D-001, D-012).

PyWorld3 is installed from PyPI and only *used*; none of its code is copied into F3.
Two runs: dt = 0.5 (PyWorld3's default) and dt = 0.05 (close to the continuous
limit). PyWorld3 integrates with fixed Euler-type steps, so its own time-step error
must be known before it can serve as a yardstick for another implementation.
Outputs go to $F3_OUT (default: audit/results).
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(os.environ.get("F3_OUT", Path(__file__).resolve().parents[1] / "results"))
OUT.mkdir(parents=True, exist_ok=True)
report = ["## T0 — World3 second check (PyWorld3)", ""]

# Key World3 variables: population, nonrenewable resource fraction, industrial
# output per capita, food per capita, persistent pollution index, life expectancy.
VARIABLES = ["pop", "nrfr", "iopc", "fpc", "ppolx", "le"]


def solve(dt):
    from pyworld3 import World3
    w = World3(dt=dt)  # 1900-2100
    w.init_world3_constants()
    w.init_world3_variables()
    w.set_world3_table_functions()
    w.set_world3_delay_functions()
    w.run_world3(fast=False)
    data = {"time": np.asarray(w.time)}
    for v in VARIABLES:
        if hasattr(w, v):
            data[v] = np.asarray(getattr(w, v))
        else:
            report.append(f"- ⚠️ Variable `{v}` not found in PyWorld3 object")
    n = min(len(x) for x in data.values())  # floating-point step counts can differ by one
    return pd.DataFrame({k: x[:n] for k, x in data.items()})


try:
    df = solve(0.5)
    df.to_csv(OUT / "world3_pyworld3.csv", index=False)
    report.append(f"- ✅ Standard run solved (dt=0.5): {df['time'].iloc[0]:.0f}–{df['time'].iloc[-1]:.0f}, "
                  f"{len(df)} time points")
    peak = df.loc[df["pop"].idxmax()]
    report.append(f"- Population peak: {peak['pop'] / 1e9:.2f} billion in {peak['time']:.0f}")

    try:
        fine = solve(0.05)
        fine.to_csv(OUT / "world3_pyworld3_fine.csv", index=False)
        pf = np.interp(df["time"], fine["time"], fine["pop"])
        rel = np.abs(df["pop"].to_numpy() - pf) / pf
        report.append(f"- ✅ Fine run (dt=0.05): {len(fine)} time points")
        report.append(f"- PyWorld3's own time-step error in population (dt=0.5 vs dt=0.05): "
                      f"max {rel.max() * 100:.2f}% in {df['time'].iloc[int(rel.argmax())]:.0f}, "
                      f"mean {rel.mean() * 100:.2f}%")
    except Exception as e:
        report.append(f"- ⚠️ Fine run failed: {type(e).__name__}: {e}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 5))
        for v in VARIABLES:
            if v in df:
                ax.plot(df["time"], df[v] / df[v].max(), label=v)
        ax.set_title("World3 standard run (PyWorld3) — each variable scaled to its maximum")
        ax.set_xlabel("Year")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT / "world3_pyworld3_standard_run.png", dpi=120)
        report.append("- ✅ Figure saved: `world3_pyworld3_standard_run.png`")
    except Exception as e:  # figure is a convenience, not a test
        report.append(f"- ⚠️ Figure not produced: {e}")
except Exception as e:
    report.append(f"- ❌ PyWorld3 run failed: {type(e).__name__}: {e}")

(OUT / "t0_3_pyworld3_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
