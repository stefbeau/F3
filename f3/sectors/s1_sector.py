"""S1 population as a sector of the coupling loop (Phase 2, M0, acceptance tests A0.1 and A0.2).

This file is interface code only. The equations are in ``s1_population.py`` and are not touched: the adapter calls that
module's own right-hand side (``PopulationSector.rhs``) and takes the same classical RK4 step as ``PopulationSector.run``,
with the same switch handling (the switch time used inside a step is the start of the segment between two switch times).
Run inside the loop with the reference's recorded inputs (``ReplaySector``), it reproduces the stand-alone S1 run to
rounding error; the test is ``tests/test_s1_in_model.py``.

Inputs (units as PyWorld3 documents them for the same variables; matched by name to WorldDynamics.jl ``dr.fpc``, ``br.sopc``,
``dr.iopc`` and ``dr.ppolx``):
    fpc    food per capita                      [vegetable-equivalent kilograms/person-year]
    sopc   service output per capita            [dollars/person-year]
    iopc   industrial output per capita         [dollars/person-year]
    ppolx  index of persistent pollution        [1]
Outputs: the four age cohorts and the total, in persons. Life expectancy, births and deaths are algebraic functions of the
inputs at the same instant; they are not exposed because a published output must be available at the start of a step before
any input is known. To expose them, publish them at the end of ``advance`` using the end-of-step inputs (see
``docs/coupling-interface.md``, "Not in this interface").
"""

from __future__ import annotations

from bisect import bisect_right
from typing import Dict, List, Optional

import numpy as np

from f3.core.sector import Context, Sector
from f3.sectors.s1_population import N_STATES, STATE_NAMES, PopulationSector

_INPUTS = {
    "fpc": "vegetable-equivalent kilograms/person-year",
    "sopc": "dollars/person-year",
    "iopc": "dollars/person-year",
    "ppolx": "1",
}
_OUTPUTS = {"p1": "persons", "p2": "persons", "p3": "persons", "p4": "persons", "pop": "persons"}
_ORDER = ("fpc", "sopc", "iopc", "ppolx")      # the order PopulationSector.rhs expects from ``Inputs.at``


class _ContextInputs:
    """Duck-typed stand-in for ``s1_population.Inputs``: ``at(t)`` returns the four inputs at time ``t`` from the loop."""

    def __init__(self, ctx: Context):
        self._ctx = ctx

    def at(self, t: float):
        return tuple(self._ctx.input(n, t) for n in _ORDER)


class S1Population(Sector):
    name = "s1_population"
    inputs = _INPUTS
    outputs = _OUTPUTS

    def __init__(self, parameter_set: str = "2004", y0: Optional[np.ndarray] = None, name: Optional[str] = None):
        self._sector = PopulationSector(parameter_set)
        self._y0 = None if y0 is None else np.array(y0, dtype=float)
        if name is not None:
            self.name = name
        self._y: np.ndarray = np.empty(N_STATES)
        self._breaks: List[float] = []
        self.time_history: List[float] = []
        self.state_history: List[np.ndarray] = []

    # -- Sector interface ------------------------------------------------------------------------------------------
    def reset(self, t0: float, t1: float, dt: float) -> None:
        self._y = self._sector.initial_state() if self._y0 is None else self._y0.copy()
        bps = self._sector._breakpoints(t0, t1)           # [t0, switch times inside the horizon..., t1]
        for b in bps[1:-1]:
            k = (b - t0) / dt
            if abs(k - round(k)) > 1e-9:
                raise ValueError(f"S1 switch time {b} is not on the loop grid (t0={t0}, dt={dt}): a step would straddle it")
        self._breaks = bps
        self.time_history = [t0]
        self.state_history = [self._y.copy()]

    def current_outputs(self) -> Dict[str, float]:
        y = self._y
        i = STATE_NAMES.index
        p = [float(y[i("p1")]), float(y[i("p2")]), float(y[i("p3")]), float(y[i("p4")])]
        return {"p1": p[0], "p2": p[1], "p3": p[2], "p4": p[3], "pop": float(sum(p))}

    def advance(self, t: float, h: float, ctx: Context) -> None:
        s = self._sector
        inp = _ContextInputs(ctx)
        a = self._breaks[max(bisect_right(self._breaks, t + 1e-9) - 1, 0)]      # start of the current segment
        y = self._y
        k1 = s.rhs(t, y, inp, a)
        k2 = s.rhs(t + h / 2, y + h / 2 * k1, inp, a)
        k3 = s.rhs(t + h / 2, y + h / 2 * k2, inp, a)
        k4 = s.rhs(t + h, y + h * k3, inp, a)
        self._y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        self.time_history.append(t + h)
        self.state_history.append(self._y.copy())

    # -- diagnostics (not part of the interface) -------------------------------------------------------------------
    def states(self) -> Dict[str, np.ndarray]:
        """All 15 states at every step boundary, by name (used by the tests)."""
        Y = np.array(self.state_history)
        return {n: Y[:, j] for j, n in enumerate(STATE_NAMES)}
