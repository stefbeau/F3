"""Shared machinery of the four World3 sectors ported in M3 (agriculture, capital, resources, pollution).

ATTRIBUTION
-----------
The table lookup (``Table``) and the switch functions (``clip``, ``switch``) re-implement the semantics of
WorldDynamics.jl v1.0.0 ``src/functions.jl`` (``interpolate`` line 11, ``clip`` line 31, ``switch`` line 45), MIT licence,
Copyright (c) 2022 Emanuele Natale, Pierluigi Crescenzi, Paulo Bruno Serafim and contributors; see ``NOTICE`` and
``licenses/WorldDynamics.jl-MIT.txt`` (decision D-012). No PyWorld3 code is used. F3 code is Apache 2.0 (D-001).

WHAT IS HERE
------------
* ``Table``: TABHL with equally spaced x values over a range, end values outside it (a scalar version of what
  ``s1_population.interpolate`` does; S1's own file is not touched, test A0.2).
* ``W3Sector``: the base class. Every M3 sector is a set of states with a right-hand side, integrated by classical RK4
  inside ``advance`` (as S1 is, D-003: loop step 0.25 year), reading its inputs through the loop context. Algebraic
  outputs are published at the END of ``advance`` from the new state and the inputs the loop gives for the end of the step
  (a recorded series gives the exact value, a coupled sector gives its start-of-step value: explicit coupling, D-022).
* Switch times: every ``clip(.., t, threshold)`` is evaluated with the time at the start of the integration segment, and the
  integration is split at each threshold inside the horizon (the S1 rule), so that no step straddles a switch. In the full
  model WorldDynamics.jl ``World3.historicalrun`` sets ``pyear`` = 1975 for capital (``world3/scenarios.jl`` line 29); the
  agriculture, resources and pollution defaults are 1975 as well.
* ``UNITS``: the unit strings of every exchanged signal (the loop refuses a coupling whose units differ).
"""

from __future__ import annotations

from bisect import bisect_right
from typing import Dict, List, Mapping, Optional, Tuple

import numpy as np

from f3.core.sector import Context, Sector

UNITS: Dict[str, str] = {
    "pop": "persons", "p2": "persons", "p3": "persons",
    "io": "dollars/year", "so": "dollars/year", "j": "jobs", "lf": "jobs", "iopc": "dollars/person-year", "sopc": "dollars/person-year",
    "ppolx": "1", "fcaor": "1", "fioaa": "1", "nrfr": "1", "cuf": "1",
    "fpc": "vegetable-equivalent kilograms/person-year", "f": "vegetable-equivalent kilograms/year",
    "al": "hectares", "aiph": "dollars/hectare-year", "pcrum": "resource units/person-year", "nrur": "resource units/year",
    "ly": "vegetable-equivalent kilograms/hectare-year", "ppgr": "pollution units/year", "ppapr": "pollution units/year", "ppasr": "pollution units/year", "ahl": "years",
}

TableData = Tuple[Tuple[float, ...], Tuple[float, float]]


class Table:
    """TABHL: ``yvalues`` at equally spaced x over ``xrange``; linear between, end values outside (functions.jl line 11)."""

    __slots__ = ("ys", "xs", "lo", "hi", "n")

    def __init__(self, data: TableData):
        yv, (lo, hi) = data
        self.ys = [float(v) for v in yv]
        self.n = len(self.ys)
        self.lo, self.hi = float(lo), float(hi)
        self.xs = [float(v) for v in np.linspace(self.lo, self.hi, self.n)]

    def __call__(self, x: float) -> float:
        if x < self.lo:
            return self.ys[0]
        if x >= self.hi:
            return self.ys[-1]
        i = bisect_right(self.xs, x) - 1
        x1, x2, y1, y2 = self.xs[i], self.xs[i + 1], self.ys[i], self.ys[i + 1]
        return y1 + (x - x1) * ((y2 - y1) / (x2 - x1))


def clip(if_gte: float, if_lt: float, x: float, threshold: float) -> float:
    """CLIP (functions.jl line 31): ``if_gte`` when ``x >= threshold``."""
    return if_gte if x >= threshold else if_lt


def switch(if_zero: float, if_not_zero: float, x: float) -> float:
    """SWITCH (functions.jl line 45): ``if_zero`` when ``x`` is within 1e-16 of zero."""
    return if_zero if abs(x) <= 1e-16 else if_not_zero


class W3Sector(Sector):
    """Base class of the M3 sectors. A subclass defines ``STATE_NAMES``, ``INPUT_ORDER``, ``PARAMETER_SETS``, ``inputs``,
    ``outputs``, ``name`` and the methods ``initial_state``, ``algebra`` and ``derivs``.

    ``algebra(tsw, y, inp)`` returns every algebraic variable of the sector at one instant (``tsw`` is the time the switches
    see), ``derivs(y, a)`` the state derivatives from those.
    """

    STATE_NAMES: Tuple[str, ...] = ()
    INPUT_ORDER: Tuple[str, ...] = ()
    PARAMETER_SETS: Mapping[str, tuple] = {}
    SWITCH_PARAMS: Tuple[str, ...] = ("pyear",)

    def __init__(self, parameter_set: str = "2004", y0: Optional[np.ndarray] = None, name: Optional[str] = None):
        if parameter_set not in self.PARAMETER_SETS:
            raise ValueError(f"unknown parameter set {parameter_set!r}; use '1974' or '2004'")
        self.parameter_set = parameter_set
        p, t = self.PARAMETER_SETS[parameter_set]
        self.params: Dict[str, float] = dict(p)
        self.tables: Dict[str, Table] = {k: Table(v) for k, v in t.items()}
        self._y0 = None if y0 is None else np.array(y0, dtype=float)
        if name is not None:
            self.name = name
        self._init_inputs: Optional[Dict[str, float]] = None
        self._y = np.empty(len(self.STATE_NAMES))
        self._out: Dict[str, float] = {}
        self._breaks: List[float] = []
        self.time_history: List[float] = []
        self.state_history: List[np.ndarray] = []
        self._ix = {n: i for i, n in enumerate(self.STATE_NAMES)}

    # -- provided by the sector ----------------------------------------------------------------------------------------
    def initial_state(self) -> np.ndarray:
        raise NotImplementedError

    def algebra(self, tsw: float, y: np.ndarray, inp: Mapping[str, float]) -> Dict[str, float]:
        raise NotImplementedError

    def derivs(self, y: np.ndarray, a: Mapping[str, float]) -> np.ndarray:
        raise NotImplementedError

    # -- helpers -------------------------------------------------------------------------------------------------------
    def set_initial_inputs(self, inp: Mapping[str, float]) -> None:
        """Inputs at the start time, needed to publish the outputs at the start (the loop publishes before it advances)."""
        self._init_inputs = {k: float(inp[k]) for k in self.inputs}

    def set_initial_state(self, y0: np.ndarray) -> None:
        self._y0 = np.array(y0, dtype=float)

    def compute_outputs(self, y: np.ndarray, inp: Mapping[str, float], tsw: float) -> Dict[str, float]:
        a = self.algebra(tsw, y, inp)
        return {k: a[k] for k in self.outputs}

    def _breakpoints(self, t0: float, t1: float) -> List[float]:
        pts = sorted({self.params[k] for k in self.SWITCH_PARAMS if k in self.params})
        return [t0] + [b for b in pts if t0 < b < t1] + [t1]

    def _segment_start(self, t: float) -> float:
        return self._breaks[max(bisect_right(self._breaks, t + 1e-9) - 1, 0)]

    # -- Sector interface ----------------------------------------------------------------------------------------------
    def reset(self, t0: float, t1: float, dt: float) -> None:
        self._y = self.initial_state() if self._y0 is None else self._y0.copy()
        bps = self._breakpoints(t0, t1)
        for b in bps[1:-1]:
            k = (b - t0) / dt
            if abs(k - round(k)) > 1e-9:
                raise ValueError(f"{self.name}: switch time {b} is not on the loop grid (t0={t0}, dt={dt}): a step would straddle it")
        self._breaks = bps
        if self._init_inputs is None:
            raise ValueError(f"{self.name}: initial inputs not set; call set_initial_inputs (f3.sectors.world3 does this)")
        self._out = self.compute_outputs(self._y, self._init_inputs, t0)
        self.time_history = [t0]
        self.state_history = [self._y.copy()]

    def current_outputs(self) -> Dict[str, float]:
        return dict(self._out)

    def _rhs(self, tsw: float, y: np.ndarray, ctx: Context, t: float) -> np.ndarray:
        inp = {n: ctx.input(n, t) for n in self.INPUT_ORDER}
        return self.derivs(y, self.algebra(tsw, y, inp))

    def advance(self, t: float, h: float, ctx: Context) -> None:
        a = self._segment_start(t)
        y = self._y
        k1 = self._rhs(a, y, ctx, t)
        k2 = self._rhs(a, y + h / 2 * k1, ctx, t + h / 2)
        k3 = self._rhs(a, y + h / 2 * k2, ctx, t + h / 2)
        k4 = self._rhs(a, y + h * k3, ctx, t + h)
        self._y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        inp_end = {n: ctx.input(n, t + h) for n in self.INPUT_ORDER}
        self._out = self.compute_outputs(self._y, inp_end, a)
        self.time_history.append(t + h)
        self.state_history.append(self._y.copy())

    # -- diagnostics ---------------------------------------------------------------------------------------------------
    def states(self) -> Dict[str, np.ndarray]:
        Y = np.array(self.state_history)
        return {n: Y[:, j] for j, n in enumerate(self.STATE_NAMES)}
