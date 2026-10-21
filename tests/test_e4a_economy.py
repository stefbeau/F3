"""M4 A4.5, written before the group existed: the coupled economy. The eight reused sectors (output, inventory, finance, labour market,
public, demand, energy, other) run together as ONE Sector of the loop (`f3.sectors.e4a_economy.E4AEconomy`, the D-031 pattern: explicit
start-of-sub-step coupling among members, sub-step per the ladder of the plan, loop step 0.25 unchanged), with the replaced sectors' signals
(POP, GDPP, EGDPP, A20PA, OW, CAC, COFO, IPP) supplied by a ReplaySector from the recorded Earth4All.jl series (D-023 option C: no adapters
here). Criterion: within 2% (D-004) of Earth4All.jl at every 0.5-year point of 1980-2100, both scenarios, of GDP (inventory), GDP per
person (port GDP / recorded POP against the reference GDPP), the inequality index (INEQ, INEQI), public spending (GS, PSP), and the energy
mix (REP, FEP, NEP, EP and the shares REP/EP, FEP/EP, NEP/EP). All states of the eight sectors are reported (not criterion). Tolerance,
error rule and ladder as in the plan; a failure is a strict xfail with size and first year, never adjusted. Earth4All.jl's own error
against Vensim is printed beside each economy variable (D-018); nothing here says the port reproduces Vensim. Initial published values
use the reference's 1980 values of the cross-sector signals (a labelled start-up input, as in D-031).
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.e4a_helpers import SCENARIOS, TOL, grid_index, reference, rel_err, signals, vensim_error

ECON = [("inventory", "GDP"), ("demand", "INEQ"), ("demand", "INEQI"), ("demand", "GS"), ("public", "PSP"),
        ("energy", "REP"), ("energy", "FEP"), ("energy", "NEP"), ("energy", "EP")]
STATES = {"output": ("CPIS", "CPUS", "CUCPIS", "CUCPUS", "ETFP", "FACNC", "OGR", "OLY", "PEDE"),
          "inventory": ("DELDI", "EPP", "INV", "PRIN", "PRI", "RS", "SSWI"), "finance": ("CBSR", "CCSD", "ELTI", "PI", "PU"),
          "labourmarket": ("ECLR", "LPR", "NHW", "PURA", "WARA", "WEOCLR", "WF", "WSO"), "public": ("TFPEE5TA", "RTFPUA"),
          "demand": ("ETF2022", "FGBW", "GD", "PGCIN", "POCI", "PWCIN", "WD"), "energy": ("EEPI2022", "REC", "ACSWCF1980", "FEC"),
          "other": ("PGDPP",)}


def _run(scen, substep=None):
    from tests.e4a_helpers import economy_run
    return economy_run(scen, substep)


def _series(res, sector, name):
    return res.series[("e4a_economy", f"{sector}.{name}")]


def _economy_rows(scen, substep=None):
    res = _run(scen, substep)
    ref = reference(scen)
    idx = grid_index(res.time, ref["time"])
    rows = {}
    for sec, n in ECON:
        rows[f"{sec}.{n}"] = rel_err(_series(res, sec, n)[idx], ref[f"{sec}.{n}"])
    gdp = _series(res, "inventory", "GDP")[idx]
    sg = signals(scen)
    popv = np.interp(ref["time"], sg["time"], sg["population.POP"])
    rows["GDP per person (GDP/POP vs GDPP)"] = rel_err(gdp / popv, np.interp(ref["time"], sg["time"], sg["population.GDPP"]))
    for a in ("REP", "FEP", "NEP"):
        rows[f"{a}/EP"] = rel_err(_series(res, "energy", a)[idx] / _series(res, "energy", "EP")[idx], ref[f"energy.{a}"] / ref["energy.EP"])
    return rows, res, idx, ref


def _report(scen, rows, tag):
    ve = vensim_error(scen)
    out = []
    for k, e in rows.items():
        sec, _, n = k.partition(".")
        v = ve.get((sec, n))
        vs = (f" [Earth4All.jl vs Vensim p95 {100 * float(v['p95']):.2f}% max {100 * float(v['maximum']):.2f}%]"
              if v and v["all_zero"] != "true" else "")
        if e is None:
            out.append(f"{k}: identically zero")
            continue
        above = np.where(e > TOL)[0]
        out.append(f"{k}: max {100 * e.max():.3f}%{vs}" + (f" FIRST ABOVE 2%: index {above[0]}" if len(above) else ""))
    print(f"economy {scen} {tag}: " + "; ".join(out))


# RECORD of the first result (one run, nothing adjusted): the group with Euler sub-step 1/64 (the rung at which every member alone is
# within 0.0000%) exceeds 2% on the economy variables in the last decades. Sizes (true relative error), TLTL: GDP 2.227% (max 2096.0,
# first above 2% 2090.5), GDP per person 2.227%, GS 2.149% (first 2096.0), PSP 2.153%; INEQ/INEQI 1.123% (pass). GL: GDP 2.514% (first
# 2088.5), GDP per person 2.514%, INEQ and INEQI 3.234% (max 2095.5, first 2076.5), GS 2.877% (first 2090.0), PSP 2.859%. Energy mix (REP,
# FEP, NEP, EP and shares) 0.000% in both. Diagnostic scan of finer group sub-steps (post-hoc, labelled, not a criterion): 1/128 and 1/256
# are WORSE (GDP 2.8% and 3.1% TLTL; INEQ 8.6% and 10.4% GL; GL FEP 13% and 20% at the 2055 kink), so no rung of the plan's ladder meets
# 2%. Inferred (not tested): members alone are 0.0000% with recorded inputs, so the gap is the one-sub-step lag of the explicit coupling
# among members (the reference solves the connections simultaneously).
_A45_X = {"tltl": "A4.5 TLTL: GDP 2.227% (first above 2%: 2090.5), GS 2.149%, PSP 2.153%, GDP per person 2.227%",
          "gl": "A4.5 GL: GDP 2.514% (first 2088.5), INEQ/INEQI 3.234% (first 2076.5), GS 2.877%, PSP 2.859%, GDP per person 2.514%"}


@pytest.mark.parametrize("scen", [pytest.param(s, marks=pytest.mark.xfail(strict=True, reason=_A45_X[s])) for s in SCENARIOS])
def test_a45_economy_variables_within_2_percent_at_loop_step_0_25(scen):
    rows, res, idx, ref = _economy_rows(scen)
    _report(scen, rows, "(group, loop step 0.25, group sub-step per the ladder)")
    bad = {k: float(e.max()) for k, e in rows.items() if e is not None and e.max() > TOL}
    assert not bad, f"{scen}: above 2%: {bad}"


@pytest.mark.parametrize("scen", SCENARIOS)
def test_a45_states_reported(scen):
    rows, res, idx, ref = _economy_rows(scen)
    worst = {}
    for sec, names in STATES.items():
        for n in names:
            e = rel_err(_series(res, sec, n)[idx], ref[f"{sec}.{n}"])
            if e is not None:
                worst[f"{sec}.{n}"] = float(e.max())
    top = sorted(worst.items(), key=lambda kv: -kv[1])[:8]
    print(f"economy {scen} states (reported, not criterion): " + ", ".join(f"{k} {100 * v:.3f}%" for k, v in top))
