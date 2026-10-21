"""S7 social module (M5 step 2): a skeleton of three bounded stocks and a delayed policy response, ILLUSTRATIVE PARAMETERS.

Equations, units, bounds and the source of every parameter: ``docs/m5-s7-parameters.md`` (A5.1, written before this file; revised after the
editor's review, D-050). Tests: ``tests/test_s7_social.py`` (written before this file; plan ``docs/m5-s7-tests.md``).

**VALIDATION STATUS (D-008, D-029, D-049, D-050):** every one of the 24 parameters is **illustrative** (none is sourced; no WID, ILOSTAT or
other source has been read). **Tension is a model-internal index, not validated against history.** The output called ``inequality`` is the
**inequality index (illustrative)**: a normalised index on 0.10 to 0.90 whose scale is a convention, not an income share. **S7 results are to be
shown only as changes relative to the start of the run, never as absolute levels** (``S7Social.changes_relative_to_start``). The main driver,
S3's labour share, is **unvalidated against GATE after about 2027 (S3 failed A1.3, D-029)**; S7 uses only its **relative fall from its value at
the first step**. There is no health or yield effect of warming in the model (D-049). No calibration, no hindcast, no claim about size.

Integration: each stock relaxes toward its target with the exact exponential step ``x <- x_target + (x - x_target) * exp(-h/tau)`` with the
inputs and the other stocks held at their start-of-step values (explicit coupling, D-022); this keeps every stock between its start value and
its target, so the declared bounds hold by construction. Inputs are read by name through the coupling loop; this module imports nothing from
S3, S1 or S6.
"""
from __future__ import annotations

import math
from typing import Dict, Mapping, Optional

import numpy as np

from f3.core.sector import Context, Sector


def _clip(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


class S7Social(Sector):
    name = "s7_social"

    #: all ILLUSTRATIVE (docs/m5-s7-parameters.md, section 3): start values, time constants (years), gains
    PARAMETERS: Dict[str, float] = {
        "I0": 0.40, "Te0": 0.30, "W0": 0.60, "P0": 0.0,
        "UEmax": 0.30, "TSref": 1.5, "gref": 0.03,
        "tau_I": 30.0, "tau_Te": 5.0, "tau_W": 8.0, "tau_P": 10.0,
        "gI_LS": 0.30, "gI_UE": 0.10, "gI_R": 0.25,
        "gTe_I": 1.0, "gTe_UE": 0.30, "gTe_TS": 0.15, "gTe_W": 0.30,
        "gW_I": 0.50, "gW_Te": 0.40, "gW_TS": 0.10, "gW_g": 0.10,
        "Te_threshold": 0.40, "kP": 2.0,
    }
    I_BOUNDS = (0.10, 0.90)

    inputs = {"labor_share": "1", "unemployment": "1", "warming": "K", "gdp_per_capita_growth": "1/year", "redistribution": "1"}
    outputs = {"inequality": "1", "tension": "1", "wellbeing": "1", "policy_response": "1"}

    validation_status = (
        "S7 (social) parameters are illustrative (none is sourced). Tension is a model-internal index, not validated against history "
        "(D-008). The output 'inequality' is the inequality index (illustrative), a normalised index and not an income share. Results are shown "
        "only as changes relative to the start of the run, never as absolute levels (D-050). The labour-share driver comes from S3, whose output is "
        "unvalidated against GATE after about 2027 (S3 failed A1.3, D-029); S7 uses only its relative fall from the start. There is no health or "
        "yield effect of warming (D-049)."
    )

    def __init__(self, overrides: Optional[Mapping[str, float]] = None, name: Optional[str] = None):
        self.p = dict(self.PARAMETERS)
        if overrides:
            unknown = [k for k in overrides if k not in self.p]
            if unknown:
                raise KeyError(f"unknown S7 parameter(s): {unknown}")
            self.p.update({k: float(v) for k, v in overrides.items()})
        if name is not None:
            self.name = name
        self._ls0: Optional[float] = None
        self._state = (self.p["I0"], self.p["Te0"], self.p["W0"], self.p["P0"])

    # -- helpers -----------------------------------------------------------------------------------------------------
    @staticmethod
    def changes_relative_to_start(result: Mapping[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """The display rule (D-050): every S7 output minus its first value."""
        return {n: np.asarray(result[n], dtype=float) - float(np.asarray(result[n], dtype=float)[0]) for n in S7Social.outputs}

    def _targets(self, I: float, Te: float, W: float, P: float, ls: float, ue: float, warming: float, growth: float, red: float):
        p = self.p
        lsp = _clip((self._ls0 - ls) / self._ls0, 0.0, 1.0) if self._ls0 not in (None, 0.0) else 0.0
        uep = _clip(ue / p["UEmax"], 0.0, 1.0)
        ts = _clip(warming / p["TSref"], 0.0, 2.0) / 2.0
        R = red + P
        I_t = _clip(p["I0"] + p["gI_LS"] * lsp + p["gI_UE"] * uep - p["gI_R"] * R, *self.I_BOUNDS)
        Te_t = _clip(p["Te0"] + p["gTe_I"] * (I - p["I0"]) + p["gTe_UE"] * uep + p["gTe_TS"] * ts - p["gTe_W"] * (W - p["W0"]), 0.0, 1.0)
        W_t = _clip(p["W0"] - p["gW_I"] * (I - p["I0"]) - p["gW_Te"] * (Te - p["Te0"]) - p["gW_TS"] * ts
                    + p["gW_g"] * _clip(growth / p["gref"], -1.0, 1.0), 0.0, 1.0)
        P_t = _clip(p["kP"] * max(Te - p["Te_threshold"], 0.0), 0.0, 1.0)
        return I_t, Te_t, W_t, P_t

    # -- Sector interface --------------------------------------------------------------------------------------------
    def reset(self, t0: float, t1: float, dt: float) -> None:
        p = self.p
        self._ls0 = None
        self._state = (p["I0"], p["Te0"], p["W0"], p["P0"])

    def current_outputs(self) -> Dict[str, float]:
        I, Te, W, P = self._state
        return {"inequality": I, "tension": Te, "wellbeing": W, "policy_response": P}

    def advance(self, t: float, h: float, ctx: Context) -> None:
        ls = ctx.input("labor_share", t)
        if self._ls0 is None:
            self._ls0 = ls                                   # LS0: the input at the first step makes the driver relative (D-050 item 3)
        ue, w = ctx.input("unemployment", t), ctx.input("warming", t)
        g, red = ctx.input("gdp_per_capita_growth", t), ctx.input("redistribution", t)
        I, Te, W, P = self._state
        targets = self._targets(I, Te, W, P, ls, ue, w, g, red)
        p = self.p
        taus = (p["tau_I"], p["tau_Te"], p["tau_W"], p["tau_P"])
        new = tuple(x_t + (x - x_t) * math.exp(-h / tau) for x, x_t, tau in zip((I, Te, W, P), targets, taus))
        lo = self.I_BOUNDS[0]
        self._state = (_clip(new[0], *self.I_BOUNDS), _clip(new[1], 0.0, 1.0), _clip(new[2], 0.0, 1.0), _clip(new[3], 0.0, 1.0))
