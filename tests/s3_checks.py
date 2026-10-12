"""Shared helpers for the S3 tests and the S3 report: run S3 in the coupling loop on a supplied investment path, compare
with the shipped GATE runs by name, and check S3's own properties (A1.5). No data from the bundle is stored here."""

from __future__ import annotations

from typing import Dict, Mapping

import numpy as np

from f3.core.model import Coupling, Model
from f3.core.replay import ReplaySector
from f3.sectors.s3_ai import SHARE_NAMES, GateParams, S3AI, automated_fraction, playground_setting, usable_compute

N_PERIODS = 76                       # indices 0..75 = end of 2025 .. end of 2100
TOL = 0.02

#: D-005 amendment B: setting name -> (stored run index, parameters)
SETTINGS_B = {
    "B0_default": (0, playground_setting()),
    "B1_conservative": (1, playground_setting(T_oom=38.0, r_H=1.0, r_S=1.0)),
    "B2_aggressive": (2, playground_setting(T_oom=33.0, r_H=7.1, r_S=2.0)),
}
#: report-only stress settings (D-005 amendment B, "Report-only stress runs"); lambda changed directly
STRESS = {
    "slow_T41_lam0.25": playground_setting(T_oom=41.0, lam_H=0.25, lam_S=0.25),
    "fast_T33_lam1": playground_setting(T_oom=33.0, lam_H=1.0, lam_S=1.0),
}
#: (S3 output, stored GATE field, in the criterion?)
COMPARED = (
    ("gwp", "gwp", True),
    ("capital", "capital", True),
    ("labor", "labor", True),
    ("hardware", "hardware", True),
    ("software", "software", True),
    ("frac_automated", "frac_automated", True),
    ("compute_stock", "compute", True),            # stored `compute` is the raw stock Q (gate-equations 9.1, identity 1)
    ("effective_compute", "compute", True),        # the pairing as amendment B words it; not like for like (9.2, item 2)
    ("labor_share", "labor_share", False),
    ("runtime_compute_share", "runtime_compute_share", False),
    ("composite_tasks", "cognitive_ces_term", False),
)


def run_s3(params: GateParams, shares: Mapping[str, np.ndarray], n: int = N_PERIODS) -> Dict[str, np.ndarray]:
    """S3 inside the loop (0.25-year step, period 1.0), investment path supplied as a replayed input."""
    t = 2025.0 + np.arange(len(next(iter(shares.values()))))
    rep = ReplaySector("investment_path", t, dict(shares), {k: "1" for k in shares})
    s3 = S3AI(params)
    Model([rep, s3], [Coupling("investment_path", k, "s3_ai", k) for k in SHARE_NAMES], 2025.0, 2025.0 + n, 0.25).run()
    return s3.series()


def constant_shares(first: Mapping[str, float], n: int = N_PERIODS + 2, training: float = 0.5) -> Dict[str, np.ndarray]:
    """LABELLED PLACEHOLDER investment path for the stress runs: not a behavioural rule."""
    d = {k: np.full(n, float(first[k])) for k in SHARE_NAMES}
    d["q_training_compute"] = np.full(n, training)
    return d


def compare(s3: Mapping[str, np.ndarray], ref_field, runs_run, tol: float = TOL) -> Dict[str, dict]:
    """Relative differences by name; two year groups by S3's own Q against 0.1 C_L."""
    out = {}
    group_b = s3["Q_over_CL"] > 0.1
    for mine, theirs, counts in COMPARED:
        ref = ref_field(runs_run, theirs)
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.abs(s3[mine] / ref - 1.0)
        bad = np.where(~(rel <= tol))[0]
        rec = {"in_criterion": counts, "max": float(np.nanmax(rel)), "max_index": int(np.nanargmax(rel)),
               "mean": float(np.nanmean(rel)), "first_index_over_tol": int(bad[0]) if len(bad) else None,
               "passes": bool(len(bad) == 0)}
        for g, mask in (("Q<=0.1CL", ~group_b), ("Q>0.1CL", group_b)):
            if mask.any():
                rec[g] = {"years": int(mask.sum()), "max": float(np.nanmax(rel[mask])), "mean": float(np.nanmean(rel[mask])),
                          "first_index_over_tol": (int(np.where(mask & ~(rel <= tol))[0][0]) if (mask & ~(rel <= tol)).any() else None)}
            else:
                rec[g] = {"years": 0}
        out[mine + (" vs compute" if mine in ("compute_stock", "effective_compute") else "")] = rec
    return out


def first_year_group_b(s3: Mapping[str, np.ndarray]):
    idx = np.where(s3["Q_over_CL"] > 0.1)[0]
    return int(idx[0]) if len(idx) else None


# -- A1.5 ---------------------------------------------------------------------------------------------------------------
def a15_properties(params: GateParams, shares: Mapping[str, np.ndarray]) -> Dict[str, object]:
    """The four A1.5 properties, each on S3's own variables. Returns {name: (passed, detail)}."""
    res = {}
    base = run_s3(params, shares)
    # (a) R&D productivity zero: H and S constant; effective compute grows only through the stock; f never falls
    off = run_s3(GateParams(**{**params.__dict__, "theta_scale": 0.0}), shares)
    hs_const = bool(np.all(off["hardware"] == params.H0) and np.all(off["software"] == params.S0))
    ec_ratio = off["effective_compute"] / off["usable_compute"]
    res["a_no_RD_growth"] = (hs_const and bool(np.all(ec_ratio == params.S0)) and bool(np.all(np.diff(off["frac_automated"]) >= -1e-15)),
                             f"H, S constant: {hs_const}; effective/usable == S(0): {bool(np.all(ec_ratio == params.S0))}")
    # (b) zero investment in compute and R&D: stock falls by depreciation, nothing negative
    z = {k: np.zeros_like(v) for k, v in shares.items()}
    z["q_consumption"] = np.ones_like(shares["q_consumption"])
    z["q_training_compute"] = shares["q_training_compute"].copy()
    zr = run_s3(params, z)
    Q = zr["compute_stock"]
    expect = (params.C_T0 + params.runtime_compute_init) / (1 - (params.C_T0 + params.runtime_compute_init) / params.C_L)
    expect = expect * np.exp(-params.delta_Q * (np.arange(len(Q)) + 1))
    err = float(np.max(np.abs(Q / expect - 1)))
    res["b_zero_investment"] = (bool(np.all(np.diff(np.r_[expect[0] / np.exp(-params.delta_Q), Q]) < 0)) and err < 1e-12 and bool(Q.min() >= 0),
                                f"Q equals Q(0) exp(-delta t) to {err:.1e}; min Q {Q.min():.3e}")
    # (c) automation fraction non-decreasing in effective compute
    grid = np.logspace(20, 48, 2000)
    fg = np.array([automated_fraction(c, params) for c in grid])
    res["c_monotone"] = (bool(np.all(np.diff(fg) >= 0)) and bool(np.all(np.diff(base["frac_automated"]) >= -1e-15)),
                         f"f(C) monotone on a 2000-point grid: {bool(np.all(np.diff(fg) >= 0))}; f over time non-decreasing: {bool(np.all(np.diff(base['frac_automated']) >= -1e-15))}")
    # (d) finiteness, no negative stock, g(Q) <= C_L
    stocks = ("capital", "hardware", "software", "compute_stock", "usable_compute", "effective_compute", "best_training_run", "labor")
    finite = all(bool(np.all(np.isfinite(base[k]))) for k in list(base) if k not in ("training_compute", "labor_share"))
    nonneg = all(bool(base[k].min() >= 0) for k in stocks)
    gq_ok = bool(base["usable_compute"].max() <= params.C_L)
    res["d_finite_nonneg_gQ"] = (finite and nonneg and gq_ok,
                                 f"finite {finite}; stocks >= 0 {nonneg}; max g(Q)/C_L = {base['usable_compute'].max() / params.C_L:.6f}; "
                                 f"max Q/C_L = {base['compute_stock'].max() / params.C_L:.3g}; max effective compute/C_L = {base['effective_compute'].max() / params.C_L:.3g}")
    return res


# -- R3 (D-028) ---------------------------------------------------------------------------------------------------------
def run_s3_rule(params: GateParams, rule, n: int = N_PERIODS) -> Dict[str, np.ndarray]:
    """S3 driven by an investment rule instead of a supplied path (no inputs, no replay sector)."""
    s3 = S3AI(params, rule=rule)
    Model([s3], [], 2025.0, 2025.0 + n, 0.25).run()
    return s3.series()


def a15_properties_rule(params: GateParams, rule_factory) -> Dict[str, object]:
    """The four A1.5 properties with S3 driven by R3. (b) switches AI and capital investment off through the levers."""
    from f3.sectors.s3_rule_r3 import R3Levers
    res = {}
    base = run_s3_rule(params, rule_factory())
    off = run_s3_rule(GateParams(**{**params.__dict__, "theta_scale": 0.0}), rule_factory())
    hs_const = bool(np.all(off["hardware"] == params.H0) and np.all(off["software"] == params.S0))
    ratio_ok = bool(np.all(off["effective_compute"] / off["usable_compute"] == params.S0))
    res["a_no_RD_growth"] = (hs_const and ratio_ok and bool(np.all(np.diff(off["frac_automated"]) >= -1e-15)), f"H, S constant: {hs_const}; effective/usable == S(0): {ratio_ok}")
    zr = run_s3_rule(params, rule_factory(R3Levers(initial_ai_share=0.0, capital_scale=0.0)))
    Q = zr["compute_stock"]
    C0 = params.C_T0 + params.runtime_compute_init
    expect = C0 / (1 - C0 / params.C_L) * np.exp(-params.delta_Q * (np.arange(len(Q)) + 1))
    err = float(np.max(np.abs(Q / expect - 1)))
    res["b_zero_investment"] = (err < 1e-12 and bool(Q.min() >= 0), f"Q equals Q(0) exp(-delta t) to {err:.1e}; min Q {Q.min():.3e}")
    fo = base["frac_automated"]
    res["c_monotone"] = (bool(np.all(np.diff(fo) >= -1e-15)), f"f over time non-decreasing: {bool(np.all(np.diff(fo) >= -1e-15))}")
    stocks = ("capital", "hardware", "software", "compute_stock", "usable_compute", "effective_compute", "best_training_run", "labor")
    finite = all(bool(np.all(np.isfinite(base[k]))) for k in base if k not in ("training_compute", "labor_share"))
    nonneg = all(bool(base[k].min() >= 0) for k in stocks)
    gq = bool(base["usable_compute"].max() <= params.C_L)
    res["d_finite_nonneg_gQ"] = (finite and nonneg and gq, f"finite {finite}; stocks >= 0 {nonneg}; max g(Q)/C_L = {base['usable_compute'].max() / params.C_L:.6f}; max Q/C_L = {base['compute_stock'].max() / params.C_L:.3g}")
    return res
