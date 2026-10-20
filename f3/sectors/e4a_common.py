"""Shared machinery of the M4 sectors (the Earth4All.jl sectors that D-016 reuses).

ATTRIBUTION
-----------
The sector modules ``e4a_<sector>.py`` are ports of equations of Earth4All.jl (https://github.com/worlddynamics/Earth4All.jl),
commit 16f37d013a2f68135f03e7815bf861dbf47311f2, MIT licence, Copyright (c) 2023 World Dynamics; see ``NOTICE`` and
``licenses/Earth4All.jl-MIT.txt`` (decisions D-011, D-018). This file re-implements the semantics of the package's helper
functions in ``src/functions.jl``: ``ramp`` (line 30), ``smooth!`` (line 42, a first-order exponential smooth), ``clip`` (line 52),
``step`` (line 61), ``pulse`` (line 70), ``withlookup`` (line 90, linear interpolation through (x, y) pairs with end values
outside). Nothing is taken from ``vensim_source/`` or from ``VensimOutput/``. F3 code is Apache 2.0 (D-001).

HOW A SECTOR IS BUILT
---------------------
A sector module holds, transcribed from the package source (the line of each equation is in the comment beside it):
``PARAMS`` (parameters.jl, with the Giant Leap overrides of src/earth4all/scenarios.jl), ``INITS`` (initialisations.jl and the
``@variables`` defaults), ``EQ`` (algebraic equations), ``DER`` (derivatives of the states; ``smooth!(x, input, T)`` is
``D(x) = (input - x) / T``) and the names of the inputs (variables the sector reads that another sector computes). The equations
are evaluated lazily by name, so the order of the transcription does not matter, and an algebraic loop raises an error.

TIME
----
Two times are carried: ``t`` (continuous: used by ramps, exp(t - 1980), lookups of time) and ``ts`` (the time the switches see:
``t > 2022``, ``step(t, ., 2022)``, ``pulse(t, ., .)``, ``t > 1984``). With Euler (the reference's scheme) ``ts`` is the step start,
exactly as the package sees it. With RK4 one step is evaluated with ``ts`` = step start + 1e-9, so that a step that begins at a
switch time sees the switch on for the whole step (the rule of f3.sectors.w3_common); every switch time of the ported sectors
(1984, 2020, 2022, 2023, 2025) is a multiple of the step, which ``reset`` checks. Published (algebraic) values at a step boundary
are evaluated with ``ts`` = the boundary time, as the package evaluates them at that time point.

INTEGRATION
-----------
``method='euler'`` is the package's scheme; ``method='rk4'`` is the F3 default. ``substep`` (years) is the internal step inside a
loop step (D-031 pattern: the loop step stays 0.25 year, D-003 and D-022 unchanged); ``None`` means one step of the loop step.
Inputs are read through the loop context at the stage times; with a recorded series (ReplaySector) they are exact at any time,
with a coupled sector they are the start-of-step values (explicit coupling, D-022).
"""

from __future__ import annotations

import math
from typing import Callable, Dict, Mapping, Optional, Sequence

import numpy as np

from f3.core.sector import Context, Sector

MIT_SOURCE = "Earth4All.jl 16f37d013a2f68135f03e7815bf861dbf47311f2 (MIT, Copyright (c) 2023 World Dynamics)"
EPS_SWITCH = 1e-9


# -- helper functions of src/functions.jl ------------------------------------------------------------------------------------
def ramp(x, slope, startx, endx):
    """functions.jl line 30: 0 until ``startx``, then ``slope * (x - startx)`` until ``endx``, then held."""
    if x > startx:
        return slope * (x - startx) if x < endx else slope * (endx - startx)
    return 0.0


def ifelse(c, a, b):
    return a if c else b


def step(x, if_gte, threshold):
    """functions.jl line 61: 0 below the threshold, ``if_gte`` from it."""
    return if_gte if x >= threshold else 0.0 * if_gte


def pulse(x, start, width):
    """functions.jl line 70: 1 on ``[start, start + width)``, else 0."""
    return 1.0 if (x >= start and x < start + width) else 0.0


def withlookup(x, pairs):
    """functions.jl line 90: linear through the (x, y) pairs, end values outside."""
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    return float(np.interp(x, xs, ys))


_NS = {"ramp": ramp, "ifelse": ifelse, "step": step, "pulse": pulse, "withlookup": withlookup, "max": max, "min": min,
       "exp": np.exp, "log": np.log}


class Vars:
    """Lazy evaluation of the equations by name. Resolution order: cache, equations, inputs, states, parameters."""

    __slots__ = ("_c", "_eq", "_busy")

    def __init__(self, eq: Mapping[str, Callable], base: Dict[str, float]):
        self._c = dict(base)
        self._eq = eq
        self._busy = set()

    def __getattr__(self, name):
        c = self._c
        if name in c:
            return c[name]
        f = self._eq.get(name)
        if f is None:
            raise KeyError(f"unknown variable {name!r}")
        if name in self._busy:
            raise RecursionError(f"algebraic loop at {name!r}")
        self._busy.add(name)
        val = f(self)
        self._busy.discard(name)
        c[name] = val
        return val


class E4ASector(Sector):
    """Base class. A module sets ``name``, ``MODULE`` (the module-level tables below) and the unit maps."""

    # set by the generated subclass
    SECTOR_KEY = ""
    STATE_NAMES: Sequence[str] = ()
    PARAMS: Mapping[str, float] = {}
    PARAMS_GL: Mapping[str, float] = {}
    PARAM_EXPR: Mapping[str, str] = {}
    INITS: Mapping[str, float] = {}
    STATE_INIT: Mapping[str, str] = {}
    EQ: Mapping[str, Callable] = {}
    DER: Mapping[str, Callable] = {}
    INPUT_NAMES: Sequence[str] = ()
    SWITCH_TIMES = (1984.0, 2020.0, 2022.0, 2023.0, 2025.0)
    #: loop-step rule (track-c-plan.md): None = one step of the loop step; otherwise the internal sub-step in years
    SUBSTEP: Optional[float] = None

    def __init__(self, scenario: str = "tltl", method: str = "rk4", substep: Optional[float] = None,
                 switches: Optional[Mapping[str, float]] = None, params: Optional[Mapping[str, float]] = None):
        if scenario not in ("tltl", "gl"):
            raise ValueError("scenario must be 'tltl' or 'gl'")
        if method not in ("euler", "rk4"):
            raise ValueError("method must be 'euler' or 'rk4'")
        self.scenario = scenario
        self.method = method
        self._substep_arg = substep
        p = dict(self.PARAMS)
        if scenario == "gl":
            p.update(self.PARAMS_GL)
        if switches:
            for k, v in switches.items():
                if k not in p:
                    raise KeyError(f"unknown switch {k!r} for sector {self.name!r}")
                p[k] = float(v)
        if params:
            for k, v in params.items():
                if k not in p:
                    raise KeyError(f"unknown parameter {k!r} for sector {self.name!r}")
                p[k] = float(v)
        self.params = {k: np.float64(v) for k, v in p.items()}
        # derived parameters (expressions of other parameters), evaluated in file order
        for k, expr in self.PARAM_EXPR.items():
            if params and k in params:
                continue
            self.params[k] = np.float64(eval(expr, {}, {"P": self.params}))
        self._inits = {k: np.float64(eval(e, {}, {"P": self.params, "I": self.INITS})) for k, e in self.STATE_INIT.items()}
        self._y = np.array([self._inits[n] for n in self.STATE_NAMES], dtype=np.float64)
        self._ix = {n: i for i, n in enumerate(self.STATE_NAMES)}
        self._init_inputs: Optional[Dict[str, float]] = None
        self._out: Dict[str, float] = {}
        self.time_history = []
        self.state_history = []
        self._sub = None

    # -- interface of the loop ---------------------------------------------------------------------------------------------
    def set_initial_inputs(self, inp: Mapping[str, float]) -> None:
        self._init_inputs = {k: float(inp[k]) for k in self.inputs}

    def initial_state(self) -> np.ndarray:
        return np.array([self._inits[n] for n in self.STATE_NAMES], dtype=np.float64)

    def _vars(self, t: float, ts: float, y: np.ndarray, inp: Mapping[str, float]) -> Vars:
        base: Dict[str, float] = dict(self.params)
        base.update({k: np.float64(v) for k, v in inp.items()})
        for i, n in enumerate(self.STATE_NAMES):
            base[n] = y[i]
        base["t"] = t
        base["ts"] = ts
        return Vars(self.EQ, base)

    def algebra(self, t: float, ts: float, y: np.ndarray, inp: Mapping[str, float]) -> Dict[str, float]:
        v = self._vars(t, ts, y, inp)
        out = {n: float(getattr(v, n)) for n in self.EQ}
        for i, n in enumerate(self.STATE_NAMES):
            out[n] = float(y[i])
        return out

    def _f(self, t: float, ts: float, y: np.ndarray, inp: Mapping[str, float]) -> np.ndarray:
        v = self._vars(t, ts, y, inp)
        return np.array([self.DER[n](v) for n in self.STATE_NAMES], dtype=np.float64)

    def reset(self, t0: float, t1: float, dt: float) -> None:
        sub = self._substep_arg if self._substep_arg is not None else self.SUBSTEP
        sub = dt if sub is None else float(sub)
        k = dt / sub
        if abs(k - round(k)) > 1e-9 or round(k) < 1:
            raise ValueError(f"loop step {dt} is not a whole number of sub-steps of {sub}")
        self._sub = sub
        for b in self.SWITCH_TIMES:
            if t0 < b < t1:
                m = (b - t0) / sub
                if abs(m - round(m)) > 1e-9:
                    raise ValueError(f"{self.name}: switch time {b} is not on the step grid (t0={t0}, step={sub})")
        if self._init_inputs is None:
            raise ValueError(f"{self.name}: initial inputs not set; call set_initial_inputs")
        self._y = self.initial_state()
        self._out = self.algebra(t0, t0, self._y, self._init_inputs)
        self.time_history = [t0]
        self.state_history = [self._y.copy()]

    def current_outputs(self) -> Dict[str, float]:
        return dict(self._out)

    def advance(self, t: float, h: float, ctx: Context) -> None:
        n = int(round(h / self._sub))
        hh = h / n
        names = list(self.inputs)
        y = self._y
        for k in range(n):
            tau = t + k * hh
            if self.method == "euler":
                inp = {i: ctx.input(i, tau) for i in names}
                y = y + hh * self._f(tau, tau, y, inp)
            else:
                ts = tau + EPS_SWITCH
                i0 = {i: ctx.input(i, tau) for i in names}
                im = {i: ctx.input(i, tau + hh / 2) for i in names}
                i1 = {i: ctx.input(i, tau + hh) for i in names}
                k1 = self._f(tau, ts, y, i0)
                k2 = self._f(tau + hh / 2, ts, y + hh / 2 * k1, im)
                k3 = self._f(tau + hh / 2, ts, y + hh / 2 * k2, im)
                k4 = self._f(tau + hh, ts, y + hh * k3, i1)
                y = y + hh / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        self._y = y
        te = t + h
        inp_end = {i: ctx.input(i, te) for i in names}
        self._out = self.algebra(te, te, y, inp_end)
        self.time_history.append(te)
        self.state_history.append(y.copy())

    # -- diagnostics ---------------------------------------------------------------------------------------------------------
    def states(self) -> Dict[str, np.ndarray]:
        Y = np.array(self.state_history)
        return {n: Y[:, j] for j, n in enumerate(self.STATE_NAMES)}
