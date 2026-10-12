"""D-021 measurement (docs/m2-d021-measurement.md, readings fixed before this was run): carrying state (b) and restarting every
10 years (c) against re-running from the start (a), 1980-2100, real configuration; plus the 20-member representativeness check.
Writes audit/data/m2-d021-measurement.json (comparison figures only; no HadCRUT5 or FaIR calibration data).

    set PYTHONUTF8=1
    uv run --group dev python audit/t0/m2_d021_measure.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from fair import FAIR  # noqa: E402
from fair.interface import fill, initialise  # noqa: E402
from fair.io import read_properties  # noqa: E402

from f3.sectors.s6_climate import ClimateSetup, anomaly_on_bounds, inputs, run_fair, START_YEAR  # noqa: E402
from tests.fair_checks import hadcrut_rebased  # noqa: E402

OUT = REPO / "audit" / "data" / "m2-d021-measurement.json"
END = 2100


def exact(setup, deterministic):
    """Reference (a): one run 1750..2100; returns the FAIR object."""
    return run_fair(END, setup, deterministic=deterministic)


def state_at(f, year):
    """Everything FaIR's interface lets us carry, at time bound ``year``. ``gas_partitions`` has no time axis (it holds the final state of
    a run), so for an exact state at an intermediate year the run ``f`` must END at ``year`` (see ``exact_state``)."""
    i = int(np.where(np.asarray(f.timebounds) == year)[0][0])
    if i != len(f.timebounds) - 1:
        raise ValueError("gas_partitions is only available at the end of a run")
    return {"T": f.temperature.values[i].copy(), "conc": f.concentration.values[i].copy(), "cum": f.cumulative_emissions.values[i].copy(),
            "air": f.airborne_emissions.values[i].copy(), "gas": f.gas_partitions.values.copy(),
            "ohc": f.ocean_heat_content_change.values[i].copy(), "forc": f.forcing.values[i].copy(), "i": i}


_STATES = {}


def exact_state(setup, deterministic, year):
    """Exact state at ``year`` from a re-run from 1750 ending at ``year`` (cached)."""
    key = (setup.n_members, deterministic, year)
    if key not in _STATES:
        _STATES[key] = state_at(run_fair(year, setup, deterministic=deterministic), year)
    return _STATES[key]


def segment(setup, y0, st, f_ref, deterministic):
    """One annual segment y0 -> y0+1 as a separate FaIR run initialised with ``st``; noise rows set to the exact run's at the same dates."""
    f = run_fair(y0 + 1, setup, deterministic=deterministic, time_start=y0, initial=st, noise_from=f_ref)
    return f


def chain(setup, f_ref, start, restart_every, deterministic):  # noqa: C901
    """Annual carried segments from ``start`` to END; reset to the exact state every ``restart_every`` years (None: never)."""
    tb = np.asarray(f_ref.timebounds)
    T = {start: f_ref.temperature.sel(layer=0).values[int(np.where(tb == start)[0][0]), 0, :].copy()}
    st = exact_state(setup, deterministic, start)
    t_seg = []
    for y in range(start, END):
        t = time.time()
        f = segment(setup, y, st, f_ref, deterministic)
        t_seg.append(time.time() - t)
        st = state_at(f, y + 1)
        T[y + 1] = f.temperature.sel(layer=0).values[-1, 0, :].copy()
        if restart_every and (y + 1 - start) % restart_every == 0 and y + 1 < END:
            st = exact_state(setup, deterministic, y + 1)
    return T, float(np.mean(t_seg))


def exact_temp(f_ref):
    tb = np.asarray(f_ref.timebounds)
    return {int(y): f_ref.temperature.sel(layer=0).values[i, 0, :] for i, y in enumerate(tb)}


def baseline_shift(f_ref):
    T = f_ref.temperature.sel(layer=0).values[:, 0, :]
    tb = np.asarray(f_ref.timebounds)
    i0 = int(np.where(tb == 1850)[0][0])
    from f3.sectors.s6_climate import WEIGHTS_51
    return np.average(T[i0:i0 + 52], weights=WEIGHTS_51, axis=0)


def errors(Tx, Ta, base, lo, hi):
    ys = [y for y in range(lo, hi + 1) if y in Tx]
    d = np.array([Tx[y] - Ta[y] for y in ys])                 # (years, members)
    e = d.mean(axis=1)
    warm = np.array([(Ta[y] - base).mean() for y in ys])
    out = {"max_abs_ensemble_mean_error_K": float(np.abs(e).max()), "ensemble_mean_error_at_2100_K": float(e[-1]),
           "max_abs_member_error_K": float(np.abs(d).max()), "median_over_members_of_max_abs_error_K": float(np.median(np.abs(d).max(axis=0))),
           "p95_over_members_abs_error_at_2100_K": float(np.percentile(np.abs(d[-1]), 95)),
           "share_of_warming_at_2100": float(abs(e[-1]) / warm[-1])}
    sel = [i for i, y in enumerate(ys) if y >= 2000]
    out["max_share_of_warming_2000_2100"] = float(np.max(np.abs(e[sel]) / warm[sel]))
    return out


def main():
    rep = {"note": "comparison figures only", "readings": "docs/m2-d021-measurement.md", "runs": {}}
    inp = inputs()
    for det_name, det in (("stochastic, noise matched to the exact run", False), ("deterministic (no internal variability)", True)):
        setup = ClimateSetup(n_members=841)
        t = time.time()
        f_ref = exact(setup, det)
        t_ref = time.time() - t
        Ta = exact_temp(f_ref)
        base = baseline_shift(f_ref)
        block = {"exact_run_seconds_1750_2100": t_ref}
        for label, start in (("from 1980", 1980), ("from 2025 (realistic coupling window)", 2025)):
            for cname, every in (("(b) carry state", None), ("(c) restart every 10 years", 10)):
                Tx, secs = chain(setup, f_ref, start, every, det)
                block[f"{cname} {label}"] = {"seconds_per_segment_841": secs, "errors_window": errors(Tx, Ta, base, start, END),
                                              "errors_2025_2100": errors(Tx, Ta, base, max(start, 2025), END)}
                print(det_name, cname, label, json.dumps(block[f"{cname} {label}"]["errors_window"]), flush=True)
        rep["runs"][det_name] = block
    # representativeness (rule: every 42nd member in the ensemble's own order), stochastic, 2025-2100
    full = ClimateSetup(n_members=841)
    f841 = run_fair(END, full)
    a841 = anomaly_on_bounds(f841)
    tb = np.asarray(f841.timebounds)
    idx = np.arange(0, 841, 42)[:20]
    sub = a841[:, idx]
    rows = [i for i, y in enumerate(tb) if 2025 <= y <= END]
    stat = lambda a: {"mean": a.mean(axis=1), "p05": np.percentile(a, 5, axis=1), "p95": np.percentile(a, 95, axis=1)}
    S, F = stat(sub), stat(a841)
    rep["representativeness"] = {"rule": "every 42nd member in the ensemble's own order: rows 0, 42, ..., 798", "n_subset": int(len(idx)),
                                 "member_labels": [int(x) for x in inp.params.index[idx]]}
    for k in ("mean", "p05", "p95"):
        d = S[k][rows] - F[k][rows]
        rep["representativeness"][k] = {"max_abs_diff_K_2025_2100": float(np.abs(d).max()), "diff_at_2100_K": float(d[-1]),
                                        "subset_at_2100": float(S[k][rows][-1]), "full_at_2100": float(F[k][rows][-1])}
    obs = hadcrut_rebased()
    lo, hi = float(obs.loc[2015:2024, "lower"].mean()), float(obs.loc[2015:2024, "upper"].mean())
    cal_sub = 0.5 * (sub[:-1] + sub[1:])
    yrs = tb[:-1]
    m = float(cal_sub[(yrs >= 2015) & (yrs <= 2024)].mean())
    rep["representativeness"]["subset_mean_2015_2024"] = m
    rep["representativeness"]["hadcrut5_interval_2015_2024"] = [lo, hi]
    rep["representativeness"]["subset_mean_inside_interval"] = bool(lo <= m <= hi)
    # time cost for a full loop (a): 120 annual re-runs, measured on a sample of end years
    cost = {}
    for n in (20, 841):
        ts = []
        for end in (1981, 2040, 2099, 2100):
            t = time.time()
            run_fair(end, ClimateSetup(n_members=n))
            ts.append(time.time() - t)
        cost[f"{n} members"] = {"seconds_per_rerun_end_years_1981_2040_2099_2100": ts}
    rep["cost_exact_reruns"] = cost
    OUT.write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("done")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
