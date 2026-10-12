"""S3 AI sector: GATE's laws of motion, automation and production as a Sector of the coupling loop (Phase 2, M1 step 2).

Source: Erdil et al., arXiv:2503.04941 v2 (CC BY 4.0). Every choice the paper leaves open is written in
``research/gate-equations.md`` section 9 (committed before this file existed); this file implements that section.
No code from Epoch's playground is used. There is **no investment rule**: the investment path is an input (D-005; the
editor chooses a rule after ``docs/s3-investment-rule.md``).

One period is one year and is advanced as a block (the sector has ``period = 1.0``, so the loop advances it every fourth
0.25-year step). The value published at ``t = t0 + k + 1`` is the end of period ``k``. Stocks are values on that date.
Flows (``gwp``, ``training_compute``, ``runtime_compute``) are the totals for the period that just ended (GATE's annual
convention; a labelling difference from D-022 recorded in gate-equations section 9.3, item 1).

Order inside period k (gate-equations 9.3, item 2):
  (a) automation f_k = f(C_{T+iota}[k-1])                         one-period lag (eqs. 2, 13)
  (b) output from L[k], K[k-1] and runtime compute (1-q_train[k]) g(Q[k-1])        (eqs. 14-16, 25-28)
  (c) investments = supplied shares x output
  (d) Q, H, S, K, then the largest training run                  (eqs. 4-8, 29, 30)
The compute cap acts on usable compute g(Q) only (eq. 10, footnote 11); Q, S, effective compute and the largest training
run are not capped (D-005 A1.5(d), as corrected).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Dict, Optional

import numpy as np

from f3.core.sector import Context, Sector

LN10 = math.log(10.0)
GRID = 20000                      # midpoints on the automated part of the task space (gate-equations 9.3, item 6)
SHARE_NAMES = ("q_consumption", "q_compute", "q_capital", "q_hardware_rnd", "q_software_rnd", "q_training_compute")


@dataclass(frozen=True)
class GateParams:
    """Playground defaults (gate-equations section 3). ``T_oom`` is log10 of the AGI training requirement T."""

    T_oom: float = 36.5
    flop_gap_frac: float = 0.55           # Delta f
    f_init: float = 0.1
    iota_max_oom: float = 5.0             # iota_max = 1e5
    m: float = 2.0
    gamma_0: float = 15.0                 # log10 of the minimum runtime compute requirement
    gamma_1: float = 9.0
    runtime_compute_init: float = 1e28    # C_I(0), eFLOP/year
    chi: float = 4.0
    a_Q: float = 2.0
    delta_Q: float = 0.3
    C_L: float = 2e38
    C_T0: float = 5e25
    r_H: float = 5.2
    lam_H: float = 0.14
    gamma_H: float = 0.35
    H_max: float = 1e23
    H0: float = 1e18
    I_H0: float = 1e11
    g_H0: float = 0.275
    r_S: float = 1.25
    lam_S: float = 0.14
    gamma_S: float = 0.35
    S_max: float = 1e4
    S0: float = 1.0
    I_S0: float = 5e9
    g_S0: float = 0.70
    rho: float = -0.65
    alpha: float = 0.35
    mu: float = 0.0
    Y0: float = 110e12
    L0: float = 3.6e9
    g_L: float = 0.0025
    K0: float = 450e12
    a_K: float = 1.0
    delta_K: float = 0.065
    theta_scale: float = 1.0              # multiplies theta_H and theta_S; 0 switches R&D productivity off (test A1.5a)

    # derived ---------------------------------------------------------------------------------------------------------
    @property
    def phi_H(self) -> float:
        return (self.lam_H / self.gamma_H) / self.r_H

    @property
    def phi_S(self) -> float:
        return (self.lam_S / self.gamma_S) / self.r_S

    @property
    def theta_H(self) -> float:
        return self.theta_scale * self.g_H0 * self.H0 ** self.phi_H * self.I_H0 ** (-self.lam_H)

    @property
    def theta_S(self) -> float:
        return self.theta_scale * self.g_S0 * self.S0 ** self.phi_S * self.I_S0 ** (-self.lam_S)

    @property
    def A(self) -> float:
        """TFP: the value that gives Y(0) with no automation (gate-equations 9.1, identity 6)."""
        return self.Y0 / (self.L0 ** (1 - self.alpha) * self.K0 ** self.alpha)

    @property
    def delta_flop_oom(self) -> float:
        """Delta_FLOP in OOM = Delta f x (log10 T - log10 C_T(0)) (gate-equations 9.3, item 3)."""
        return self.flop_gap_frac * (self.T_oom - math.log10(self.C_T0))

    @property
    def inference_multiplier(self) -> float:
        """iota_max ** (1/m): the factor from the largest training run to C_{T+iota} (eq. 2)."""
        return 10.0 ** (self.iota_max_oom / self.m)


def playground_setting(T_oom: float = 36.5, r_H: float = 5.2, r_S: float = 1.25, lam_H: float = 0.14, lam_S: float = 0.14) -> GateParams:
    return GateParams(T_oom=T_oom, r_H=r_H, r_S=r_S, lam_H=lam_H, lam_S=lam_S)


def usable_compute(Q: float, C_L: float) -> float:
    """g(Q) = Q / (Q/C_L + 1) = C_L / (1 + C_L/Q); never exceeds C_L (eq. 10)."""
    if Q <= 0.0:
        return 0.0
    return C_L / (1.0 + C_L / Q)


def automated_fraction(C: float, p: GateParams) -> float:
    """Eq. 13: fraction of tasks automated by capability C (= C_{T+iota})."""
    log_T = p.T_oom * LN10
    log_lo = (p.T_oom - p.delta_flop_oom) * LN10
    lc = math.log(C)
    if lc <= log_lo:
        return p.f_init
    if lc > log_T:
        return 1.0
    return p.f_init + (1.0 - p.f_init) * (lc - log_lo) / (log_T - log_lo)


def _log_f_inverse(i: np.ndarray, p: GateParams) -> np.ndarray:
    """log of f^{-1}(i) (eq. 16), natural log; -inf where f^{-1} = 0 (i <= f_init)."""
    out = np.full(np.shape(i), -np.inf)
    hi = i > p.f_init
    out[hi] = ((p.T_oom - p.delta_flop_oom) + (i[hi] - p.f_init) / (1.0 - p.f_init) * p.delta_flop_oom) * LN10
    return out


def _log_R(i: np.ndarray, C_T: float, p: GateParams) -> np.ndarray:
    """log R_i, eq. 15: max(1, f^{-1}(i)/C_T)^m x 10^(gamma_0 + gamma_1 i)."""
    mult = np.maximum(0.0, _log_f_inverse(i, p) - math.log(C_T))
    return p.m * mult + (p.gamma_0 + p.gamma_1 * i) * LN10


def task_composite(L: float, f: float, C_I: float, C_T: float, p: GateParams) -> tuple:
    """Efficient allocation of labour and runtime compute across tasks (footnote 39) and the composite T (eq. 26).

    Maximise T = (int T_i^rho)^(1/rho) with T_i = L_i + C_i / R_i on automated tasks (i <= f), T_i = L_i otherwise, given
    total labour L and runtime compute C_I. Tasks below a threshold i* use compute only, T_i = Th (R_i/R_i*)^e with
    e = 1/(rho-1); the others use labour only, T_i = Th = L/(1-i*). If compute is abundant, i* = f and compute is left over.
    Returns (T, p/w) where p/w is the price of one eFLOP of runtime compute relative to one unit of labour.
    """
    rho = p.rho
    if C_I <= 0.0 or f <= 0.0:
        return L, 0.0
    e = 1.0 / (rho - 1.0)
    n = GRID
    edges = np.linspace(0.0, f, n + 1)
    dw = f / n
    mid = 0.5 * (edges[:-1] + edges[1:])
    logR_mid = _log_R(mid, C_T, p)
    logR_edge = _log_R(edges, C_T, p)
    P = np.concatenate(([0.0], np.cumsum(np.exp((1.0 + e) * logR_mid) * dw)))      # int_0^edge R^(1+e)
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        need = L / (1.0 - edges) * np.exp(-e * logR_edge) * P                      # compute needed if i* = edge
    if need[n] <= C_I:                                                              # compute abundant: i* = f
        Th = L / (1.0 - f)
        c = C_I / P[n]
        val = np.sum((c * np.exp(e * logR_mid)) ** rho) * dw + (1.0 - f) * Th ** rho
        return val ** (1.0 / rho), (c / Th) ** (rho - 1.0)
    j = int(np.searchsorted(need, C_I))                                             # first edge needing at least C_I
    j = max(j, 1)
    frac = (C_I - need[j - 1]) / (need[j] - need[j - 1])
    istar = edges[j - 1] + frac * dw
    logRs = logR_edge[j - 1] + frac * (logR_edge[j] - logR_edge[j - 1])
    Th = L / (1.0 - istar)
    below = np.sum((Th * np.exp(e * (logR_mid[: j - 1] - logRs))) ** rho) * dw
    partial = (istar - edges[j - 1]) * (Th * math.exp(e * (logR_mid[j - 1] - logRs))) ** rho
    val = below + partial + (1.0 - istar) * Th ** rho
    return val ** (1.0 / rho), math.exp(-logRs)


class S3AI(Sector):
    name = "s3_ai"
    period = 1.0
    inputs = {n: "1" for n in SHARE_NAMES}
    outputs = {
        "gwp": "USD/year",
        "capital": "USD",
        "labor": "persons",
        "hardware": "FLOP/year/USD",
        "software": "eFLOP/FLOP",
        "frac_automated": "1",
        "compute_stock": "FLOP/year",
        "usable_compute": "FLOP/year",
        "effective_compute": "eFLOP/year",
        "best_training_run": "eFLOP",
        "physical_best_training_run": "FLOP",
        "training_compute": "FLOP/year",
        "runtime_compute": "FLOP/year",
        "composite_tasks": "persons",
        "labor_share": "1",
        "runtime_compute_share": "1",
    }

    def __init__(self, params: Optional[GateParams] = None, name: Optional[str] = None):
        self.p = params or GateParams()
        if self.p.mu != 0.0:
            raise NotImplementedError("S3 implements mu = 0 only (gate-equations 9.3, item 7)")
        if name is not None:
            self.name = name
        self._t0 = 0.0
        self._k = 0
        self.history: Dict[str, list] = {}

    # -- Sector interface ------------------------------------------------------------------------------------------
    def reset(self, t0: float, t1: float, dt: float) -> None:
        p = self.p
        C0 = p.C_T0 + p.runtime_compute_init                    # eq. 11 with S(0) = 1: C(0) = g(Q(0))
        if C0 >= p.C_L:
            raise ValueError("initial effective compute must be below C_L")
        self._t0 = t0
        self._k = 0
        self.Q = C0 / (1.0 - C0 / p.C_L)
        self.H, self.S, self.K = p.H0, p.S0, p.K0
        self.C_T, self.C_Tphys, self.L = p.C_T0, p.C_T0, p.L0
        self._out = {
            "gwp": p.Y0, "capital": p.K0, "labor": p.L0, "hardware": p.H0, "software": p.S0,
            "frac_automated": p.f_init, "compute_stock": self.Q, "usable_compute": C0, "effective_compute": C0 * p.S0,
            "best_training_run": p.C_T0, "physical_best_training_run": p.C_T0, "training_compute": float("nan"),
            "runtime_compute": p.runtime_compute_init, "composite_tasks": p.L0, "labor_share": float("nan"),
            "runtime_compute_share": float("nan"),
        }
        self.history = {n: [] for n in list(self.outputs) + ["q_consumption_in", "Q_over_CL", "I_compute_usd", "I_compute_units"]}

    def current_outputs(self) -> Dict[str, float]:
        return dict(self._out)

    def advance(self, t: float, h: float, ctx: Context) -> None:
        p = self.p
        if abs(h - 1.0) > 1e-9:
            raise ValueError("S3 advances one whole period (1 year) at a time")
        q = {n: ctx.input(n, t) for n in SHARE_NAMES}
        if abs(sum(q[n] for n in SHARE_NAMES[:5]) - 1.0) > 1e-9 or min(q.values()) < -1e-12:
            raise ValueError(f"investment shares at t={t} must be >= 0 and the first five must sum to 1: {q}")
        k = self._k
        # (a) automation, with the one-period lag
        f = automated_fraction(self.C_T * p.inference_multiplier, p)
        # (b) output
        L_k = p.L0 * math.exp(p.g_L * (k + 1))
        gQ = usable_compute(self.Q, p.C_L)
        training = q["q_training_compute"] * gQ
        runtime = gQ - training
        T, p_over_w = task_composite(L_k, f, runtime, self.C_T, p)
        gwp = p.A * T ** (1.0 - p.alpha) * self.K ** p.alpha
        rt_share = (1.0 - p.alpha) * p_over_w * runtime / (L_k + p_over_w * runtime) if runtime > 0 else 0.0
        # (c) investments in dollars
        I_Q, I_K = q["q_compute"] * gwp, q["q_capital"] * gwp
        I_H, I_S = q["q_hardware_rnd"] * gwp, q["q_software_rnd"] * gwp
        # (d) stocks, from the start-of-period state
        Q0, H0, S0, K0 = self.Q, self.H, self.S, self.K
        I_q = Q0 / (p.a_Q * H0) * ((1.0 + p.chi * p.a_Q * H0 * I_Q / Q0) ** (1.0 / p.chi) - 1.0)    # eq. 7 inverted
        Q1 = Q0 * math.exp(-p.delta_Q) + I_q * H0                                                  # eq. 8
        H1 = self._efficiency(H0, I_H, p.theta_H, p.phi_H, p.lam_H, p.H_max, p.H0)
        S1 = self._efficiency(S0, I_S, p.theta_S, p.phi_S, p.lam_S, p.S_max, p.S0)
        a = p.a_K / (2.0 * K0)
        I_k = (-1.0 + math.sqrt(1.0 + 4.0 * a * I_K)) / (2.0 * a)                                   # eq. 29 inverted
        K1 = K0 * math.exp(-p.delta_K) + I_k                                                        # eq. 30
        self.C_T = self.C_T + training * S0
        self.C_Tphys = self.C_Tphys + training
        self.Q, self.H, self.S, self.K, self.L = Q1, H1, S1, K1, L_k
        self._k = k + 1
        gQ1 = usable_compute(Q1, p.C_L)
        self._out = {
            "gwp": gwp, "capital": K1, "labor": L_k, "hardware": H1, "software": S1, "frac_automated": f,
            "compute_stock": Q1, "usable_compute": gQ1, "effective_compute": gQ1 * S1,
            "best_training_run": self.C_T, "physical_best_training_run": self.C_Tphys, "training_compute": training,
            "runtime_compute": runtime, "composite_tasks": T, "labor_share": 1.0 - p.alpha - rt_share,
            "runtime_compute_share": rt_share,
        }
        for n in self.outputs:
            self.history[n].append(self._out[n])
        self.history["q_consumption_in"].append(q["q_consumption"])
        self.history["Q_over_CL"].append(Q1 / p.C_L)
        self.history["I_compute_usd"].append(I_Q)
        self.history["I_compute_units"].append(I_q)

    @staticmethod
    def _efficiency(x: float, invest: float, theta: float, phi: float, lam: float, x_max: float, x_init: float) -> float:
        """Eqs. 4-6 over one period: growth rate held at its start-of-period value; capped at x_max."""
        if x >= x_max:
            return x_max
        Lam = (math.log(x_max) - math.log(x)) / (math.log(x_max) - math.log(x_init))
        g = theta * x ** (-phi) * invest ** lam
        expo = g * Lam
        if expo >= math.log(x_max / x):         # same result as the cap below, without overflowing exp
            return x_max
        return min(x * math.exp(expo), x_max)

    # -- diagnostics (not part of the interface) -------------------------------------------------------------------
    def series(self) -> Dict[str, np.ndarray]:
        """Period-end values by name, index k = 0 .. n-1 (stored-index convention of the GATE playground)."""
        return {n: np.array(v, dtype=float) for n, v in self.history.items()}


def with_params(p: GateParams, **kw) -> GateParams:
    return replace(p, **kw)
