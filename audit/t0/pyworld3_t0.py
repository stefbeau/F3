"""T0 second check: run the World3 standard run with PyWorld3, unmodified (D-001, D-012).

PyWorld3 is installed from PyPI and only *used*; none of its code is copied into F3.
Two runs: dt = 0.5 (PyWorld3's default) and dt = 0.05 (close to the continuous
limit). PyWorld3 integrates with fixed Euler-type steps, so its own time-step error
must be known before it can serve as a yardstick for another implementation.
Outputs go to $F3_OUT (default: audit/results).
"""
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(os.environ.get("F3_OUT", Path(__file__).resolve().parents[1] / "results"))
OUT.mkdir(parents=True, exist_ok=True)
report = ["## T0 — World3 second check (PyWorld3)", ""]

# Plotted variables: population, nonrenewable resource fraction, industrial output
# per capita, food per capita, persistent pollution index, life expectancy.
PLOTTED = ["pop", "nrfr", "iopc", "fpc", "ppolx", "le"]
# Main stocks (levels) compared with WorldDynamics.jl: population cohorts, industrial
# and service capital, arable land, potentially arable land, urban-industrial land,
# land fertility, persistent pollution, nonrenewable resources.
STOCKS = ["p1", "p2", "p3", "p4", "ic", "sc", "al", "pal", "uil", "lfert", "ppol", "nr"]
VARIABLES = STOCKS + PLOTTED


def solve(dt, ppgr_start=None):
    """ppgr_start: DIAGNOSTIC ONLY. If given, the start value of PyWorld3's third-order
    delay on the persistent-pollution generation rate (PPGR -> PPAPR) is overridden at
    run time on the instance. No PyWorld3 code is copied or edited. The unmodified run
    (ppgr_start=None) is always reported alongside."""
    from pyworld3 import World3
    w = World3(dt=dt)  # 1900-2100
    w.init_world3_constants()
    w.init_world3_variables()
    w.set_world3_table_functions()
    w.set_world3_delay_functions()
    if ppgr_start is not None:
        d = w.delay3_ppgr
        d._init_out_arr = lambda delay, d=d: d.out_arr.__setitem__((0, slice(None)), ppgr_start)
    w.run_world3(fast=False)
    solve.last = w
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
        # Same for every stock (same gap metric as compare_world3.py: denominator floored
        # at 0.1% of the variable's maximum). Shows how far PyWorld3 at its default step
        # is from its own near-continuous limit, i.e. how good a yardstick it is.
        rows = []
        for v in STOCKS:
            if v in df and v in fine:
                ref = np.interp(df["time"], fine["time"], fine[v])
                floor = 1e-3 * np.abs(fine[v]).max()
                r = np.abs(df[v].to_numpy() - ref) / np.maximum(np.abs(ref), floor if floor > 0 else 1.0)
                rows.append(f"`{v}` {r.max() * 100:.2f}% ({df['time'].iloc[int(r.argmax())]:.0f})")
        report.append("- Time-step error by stock, max (year of max): " + "; ".join(rows))

        # Start-up of the pollution delay (found in T0 run #6, see T0-FINDINGS.md).
        solve(0.05)  # re-run to get the model object for its own ppgr(0), ppapr(0)
        w = solve.last
        own_ppgr0, own_ppapr0 = float(w.ppgr[0]), float(w.ppapr[0])
        report.append(f"- PyWorld3 as shipped: ppgr(1900) = {own_ppgr0:.4e}, but the delay output "
                      f"ppapr(1900) = {own_ppapr0:.4e}, i.e. {own_ppapr0 / own_ppgr0:.3f} of its input "
                      f"(a steady-state start would give 1.000; 3/delay = {3 / float(w.pptd1):.3f}).")
        wd_csv = next((OUT / f"world3_worlddynamics_states_{k}.csv"
                       for k in ("default_tight", "default_saveat", "default", "noinit_tight",
                                 "noinit_saveat", "noinit")
                       if (OUT / f"world3_worlddynamics_states_{k}.csv").exists()), None)
        if wd_csv is not None:
            report.append(f"- Start value taken from `{wd_csv.name}`")
            wd = pd.read_csv(wd_csv)
            cols = [c for c in wd.columns if re.search(r"ppapr3\(t\)$", c)]
            if len(cols) == 1:
                ppgr_wd = float(wd[cols[0]].iloc[0]) * 3 / float(w.pptd1)  # ppapr3(0) = pptd * ppgr / 3
                report.append(f"- WorldDynamics.jl starts the same delay chain at ppapr3(1900) = "
                              f"{float(wd[cols[0]].iloc[0]):.4e}, i.e. an implied ppgr of {ppgr_wd:.4e} "
                              f"({ppgr_wd / own_ppgr0:.3f} x PyWorld3's own ppgr(1900)).")
                diag = solve(0.05, ppgr_start=ppgr_wd)
                diag.to_csv(OUT / "world3_pyworld3_fine_wdstart.csv", index=False)
                report.append("- ✅ Diagnostic run (dt=0.05, pollution delay started at the WorldDynamics.jl value): "
                              "`world3_pyworld3_fine_wdstart.csv`. Diagnostic only, not a reference.")
            else:
                report.append(f"- ⚠️ ppapr3 column not identified unambiguously: {cols}")
        else:
            report.append("- (WorldDynamics.jl export not found; diagnostic run skipped)")
    except Exception as e:
        report.append(f"- ⚠️ Fine run failed: {type(e).__name__}: {e}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 5))
        for v in PLOTTED:
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
