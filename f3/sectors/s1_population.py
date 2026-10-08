"""F3 sector S1 - Population (World3 population sector, 1974 and 2004 parameter sets).

ATTRIBUTION
-----------
This module is a port of the World3 population sector as implemented in WorldDynamics.jl v1.0.0
(https://github.com/worlddynamics/WorldDynamics.jl, files ``src/World3/population/common_pop/*.jl`` and
``src/World3/population/pop4/*.jl``; ``src/World3_91/world3_91/scenarios.jl`` and
``src/World3_03/world3_03/scenarios.jl`` for the 2004 parameter set).
WorldDynamics.jl is Copyright (c) 2022 Emanuele Natale, Pierluigi Crescenzi, Paulo Bruno Serafim and
contributors, licensed under the MIT License; the licence text is in ``licenses/WorldDynamics.jl-MIT.txt``
and the attribution is recorded in ``NOTICE`` (decision D-012). The equations are those of World3 as
published in Meadows, Behrens, Meadows, Naill, Randers, Zahn, *Dynamics of Growth in a Finite World* (1974),
Appendix A; "Line n" below is the line number WorldDynamics.jl cites for that equation.
No PyWorld3 code is used here (PyWorld3 is CeCILL 2.1; F3 uses it unmodified from PyPI as a second check).
F3 code is licensed under Apache 2.0 (D-001).

WHAT IS PORTED
--------------
The population sector alone: four age cohorts, the death-rate block (life expectancy), the birth-rate block
(fertility) and the three smoothing and delay chains inside them. The rest of World3 (food, industrial output,
service output, pollution) is not ported here; the four time series the sector reads from it are given as
inputs: food per capita ``fpc``, service output per capita ``sopc``, industrial output per capita ``iopc`` and
the persistent-pollution index ``ppolx`` (WorldDynamics.jl names ``dr.fpc``, ``br.sopc``, ``dr.iopc``,
``dr.ppolx``). Matching is by name.

PARAMETER SETS (D-015)
----------------------
Both sets are carried in this one module, because they differ only in parameters and tables, not in equations:
``PARAMS_1974``/``TABLES_1974`` (WorldDynamics.jl ``World3``) and ``PARAMS_2004``/``TABLES_2004``
(``World3_03.scenario1``, i.e. ``World3_91.scenario1`` plus a changed ``sfsn`` table). The 2004 set is F3's
provisional default; the 1974 set is the regression test.

START-UP CONVENTIONS (kept apart from the equations)
----------------------------------------------------
1. Initial state. WorldDynamics.jl computes the initial values of the derived states (life expectancy, delay
   chains, fertility chain) once, when the package is loaded, from the **1974** tables and parameters and an
   initial population of 1.61e9, and the 2004 scenario reuses them (the 1900 rows of the two runs are
   identical). ``initial_state()`` reproduces exactly that, for both parameter sets, so that the port starts from
   the reference's own initial state. Four states are the exception: the industrial-output-per-capita chains
   (``diopc``, ``diopc2``, ``diopc1`` and ``aiopc``) start at 6.65e10 / 1.61e9, which is the value
   ``World3.historicalrun`` assigns to ``iopc`` after the derived values were computed (they used 0.7e11 / 1.61e9).
   See ``initial_state`` and the test ``test_initial_state_matches_reference``.
2. Switches. The equations contain four ``clip(.., t, threshold)`` switches: ``lmhs`` at 1940 (``iphst``;
   the only one that fires between 1900 and 2100), and ``dcfs`` (``zpgt``), ``fce`` (``fcest``) and ``br``
   (``pet``), all at 4000, which never fire in the model horizon. Integration is split at each threshold
   inside the horizon and the branch is fixed per segment, so the discontinuity lies on a step boundary and
   is never straddled by a step.
3. Integration. Fixed-step classical Runge-Kutta (RK4) with step ``dt`` = 0.25 year (decision D-003). The
   reference solves with an adaptive solver (WorldDynamics.jl default). The integrator is not part of the
   World3 equations; any step in the port that is not in the equations is listed here.

INTEGRATION OF THE EXOGENOUS INPUTS
-----------------------------------
Inputs are given as sampled time series and interpolated linearly between samples (``Inputs``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple

import numpy as np

# --------------------------------------------------------------------------------------------------------
# Parameters (WorldDynamics.jl src/World3/population/common_pop/parameters.jl and pop4/parameters.jl)
# --------------------------------------------------------------------------------------------------------
PARAMS_1974: Dict[str, float] = {
    "len": 28.0,    # Line 19.1 Appendix A  life expectancy normal, years
    "sfpc": 230.0,  # subsistence food per capita, kilograms of vegetable-equivalent per person-year
    "hsid": 20.0,   # Line 22.1 Appendix A  health services impact delay, years
    "iphst": 1940.0,  # Line 23 Appendix A  implementation of health service technology, year
    "rlt": 30.0,    # Line 30.1 Appendix A  reproductive lifetime, years
    "pet": 4000.0,  # Line 30.2 Appendix A  population equilibrium time, year
    "mtfn": 12.0,   # Line 33.1 Appendix A  maximum total fertility normal
    "lpd": 20.0,    # Line 37.1 Appendix A  perceived life expectancy delay, years
    "zpgt": 4000.0,  # Line 38.1 Appendix A  zero population growth time, year
    "dcfsn": 4.0,   # Line 38.2 Appendix A  desired completed family size normal
    "sad": 20.0,    # Line 40.1 Appendix A  social adjustment delay, years
    "ieat": 3.0,    # Line 43.1 Appendix A  income expectation averaging time, years
    "fcest": 4000.0,  # Line 45.1 Appendix A  fertility control effectiveness set time, year
}

# 2004 parameter set: World3_91.scenario1 changes dcfsn; World3_03.scenario1 builds on it.
PARAMS_2004: Dict[str, float] = {**PARAMS_1974, "dcfsn": 3.8}

# Table functions: (y values, x range). x values are equally spaced over the range, as in TABHL
# (WorldDynamics.jl ``interpolate``). Source files: common_pop/tables.jl and pop4/tables.jl.
Table = Tuple[Tuple[float, ...], Tuple[float, float]]

TABLES_1974: Dict[str, Table] = {
    "m1": ((0.0567, 0.0366, 0.0243, 0.0155, 0.0082, 0.0023, 0.001), (20.0, 80.0)),      # Line 4.1 / 4
    "m2": ((0.0266, 0.0171, 0.0110, 0.0065, 0.0040, 0.0016, 0.0008), (20.0, 80.0)),      # Line 8.1 / 8
    "m3": ((0.0562, 0.0373, 0.0252, 0.0171, 0.0118, 0.0083, 0.006), (20.0, 80.0)),       # Line 12.1 / 12
    "m4": ((0.13, 0.11, 0.09, 0.07, 0.06, 0.05, 0.04), (20.0, 80.0)),                    # Line 16.1 / 16
    "cmi": ((0.5, 0.05, -0.1, -0.08, -0.02, 0.05, 0.1, 0.15, 0.2), (0.0, 1600.0)),       # Line 27.1 / 27
    "fpu": ((0.0, 0.2, 0.4, 0.5, 0.58, 0.65, 0.72, 0.78, 0.8), (0.0, 16e9)),             # Line 26.1 / 26
    "hsapc": ((0.0, 20.0, 50.0, 95.0, 140.0, 175.0, 200.0, 220.0, 230.0), (0.0, 2000.0)),  # Line 21.1 / 21
    "lmf": ((0.0, 1.0, 1.2, 1.3, 1.35, 1.4), (0.0, 5.0)),                                # Line 20.1 / 20
    "lmhs1": ((1.0, 1.1, 1.4, 1.6, 1.7, 1.8), (0.0, 100.0)),                             # Line 24.1 / 24
    "lmhs2": ((1.0, 1.4, 1.6, 1.8, 1.95, 2.0), (0.0, 100.0)),                            # Line 25.1 / 25
    "lmp": ((1.0, 0.99, 0.97, 0.95, 0.9, 0.85, 0.75, 0.65, 0.55, 0.4, 0.2), (0.0, 100.0)),  # Line 29.1 / 29
    "fm": ((0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0, 1.05, 1.1), (0.0, 80.0)),                 # Line 34.1 / 34
    "cmple": ((3.0, 2.1, 1.6, 1.4, 1.3, 1.2, 1.1, 1.05, 1.0), (0.0, 80.0)),              # Line 35.1 / 35
    "sfsn": ((1.25, 1.0, 0.9, 0.8, 0.75), (0.0, 800.0)),                                 # Line 39.1 / 39
    "frsn": ((0.5, 0.6, 0.7, 0.85, 1.0), (-0.2, 0.2)),                                   # Line 41.1 / 41
    "fce": ((0.75, 0.85, 0.9, 0.95, 0.98, 0.99, 1.0), (0.0, 3.0)),                       # Line 45.2 / 45
    "fsafc": ((0.0, 0.005, 0.015, 0.025, 0.03, 0.035), (0.0, 10.0)),                     # Line 48.1 / 48
}

# 2004 parameter set: the tables World3_91.scenario1 (lmf, lmhs2, fm) and World3_03.scenario1 (sfsn) replace.
TABLES_2004: Dict[str, Table] = {
    **TABLES_1974,
    "lmf": ((0.0, 1.0, 1.43, 1.5, 1.5, 1.5), (0.0, 5.0)),
    "lmhs2": ((1.0, 1.5, 1.9, 2.0, 2.0, 2.0), (0.0, 100.0)),
    "fm": ((0.0, 0.2, 0.4, 0.6, 0.7, 0.75, 0.79, 0.84, 0.87), (0.0, 80.0)),
    "sfsn": ((1.25, 0.94, 0.715, 0.59, 0.5), (0.0, 800.0)),
}

PARAMETER_SETS = {
    "1974": (PARAMS_1974, TABLES_1974),
    "2004": (PARAMS_2004, TABLES_2004),
}

STATE_NAMES = (
    "p1", "p2", "p3", "p4",           # population 0-14, 15-44, 45-64, 65+ (Lines 2, 6, 10, 14)
    "ehspc",                          # effective health services per capita (Line 22)
    "ple", "ple2", "ple1",            # perceived life expectancy, third-order delay (Line 37)
    "diopc", "diopc2", "diopc1",      # delayed industrial output per capita, third-order delay (Line 40)
    "aiopc",                          # average industrial output per capita (Line 43)
    "fcfpc", "fcfpc2", "fcfpc1",      # fertility control facilities per capita, third-order delay (Line 46)
)
N_STATES = len(STATE_NAMES)
_IX = {n: i for i, n in enumerate(STATE_NAMES)}

# Constants of the initialisation (WorldDynamics.jl common_pop/initialisations.jl and pop4/initialisations.jl)
_POP_INIT = 1.61e9           # inits[:pop]
_FRSN_INIT = 0.82            # Line 41.2 Appendix A
_P_INIT = (65e7, 70e7, 19e7, 6e7)   # Lines 2.2, 6.2, 10.2, 14.2 Appendix A
_IOPC_HISTORICALRUN = 6.65e10 / _POP_INIT   # World3.historicalrun: pop_inits[:iopc] = 6.65e10 / pop


# --------------------------------------------------------------------------------------------------------
# Table lookup and switches (WorldDynamics.jl src/functions.jl)
# --------------------------------------------------------------------------------------------------------
def interpolate(x: float, table: Table) -> float:
    """TABHL: linear interpolation in a table with equally spaced x values over the range; the end values
    are returned outside the range (WorldDynamics.jl ``interpolate(x, yvalues, xrange)``)."""
    yvalues, (lo, hi) = table
    xs = np.linspace(lo, hi, len(yvalues))
    return float(np.interp(x, xs, yvalues))


def clip(if_gte: float, if_lt: float, x: float, threshold: float) -> float:
    """CLIP: ``if_gte`` when ``x >= threshold``, else ``if_lt`` (WorldDynamics.jl ``clip``)."""
    return if_gte if x >= threshold else if_lt


# --------------------------------------------------------------------------------------------------------
# Exogenous inputs
# --------------------------------------------------------------------------------------------------------
@dataclass
class Inputs:
    """Time series of the four quantities the population sector reads from the rest of World3."""

    time: np.ndarray
    fpc: np.ndarray    # food per capita
    sopc: np.ndarray   # service output per capita
    iopc: np.ndarray   # industrial output per capita
    ppolx: np.ndarray  # persistent pollution index

    def at(self, t: float) -> Tuple[float, float, float, float]:
        return (float(np.interp(t, self.time, self.fpc)), float(np.interp(t, self.time, self.sopc)),
                float(np.interp(t, self.time, self.iopc)), float(np.interp(t, self.time, self.ppolx)))


# --------------------------------------------------------------------------------------------------------
# The sector
# --------------------------------------------------------------------------------------------------------
@dataclass
class PopulationSector:
    """World3 population sector with a chosen parameter set (``"1974"`` or ``"2004"``)."""

    parameter_set: str = "2004"
    params: Dict[str, float] = field(default_factory=dict)
    tables: Dict[str, Table] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.parameter_set not in PARAMETER_SETS:
            raise ValueError(f"unknown parameter set {self.parameter_set!r}; use '1974' or '2004'")
        p, t = PARAMETER_SETS[self.parameter_set]
        self.params = dict(p) if not self.params else self.params
        self.tables = dict(t) if not self.tables else self.tables

    # ---- algebraic part of the equations ------------------------------------------------------------
    def _algebra(self, t_switch: float, y: np.ndarray, fpc: float, sopc: float, iopc: float,
                 ppolx: float) -> Dict[str, float]:
        """All algebraic variables of the sector at one instant. ``t_switch`` is the time used by the
        ``clip`` switches (the segment start during integration, so that no step straddles a switch)."""
        P, T = self.params, self.tables
        p1, p2, p3, p4 = y[_IX["p1"]], y[_IX["p2"]], y[_IX["p3"]], y[_IX["p4"]]
        ehspc, ple = y[_IX["ehspc"]], y[_IX["ple"]]
        diopc, aiopc, fcfpc = y[_IX["diopc"]], y[_IX["aiopc"]], y[_IX["fcfpc"]]

        pop = p1 + p2 + p3 + p4                                              # Line 1
        # death-rate block
        lmf = interpolate(fpc / P["sfpc"], T["lmf"])                         # Line 20
        hsapc = interpolate(sopc, T["hsapc"])                                # Line 21
        lmhs1 = interpolate(ehspc, T["lmhs1"])                               # Line 24
        lmhs2 = interpolate(ehspc, T["lmhs2"])                               # Line 25
        lmhs = clip(lmhs2, lmhs1, t_switch, P["iphst"])                      # Line 23
        fpu = interpolate(pop, T["fpu"])                                     # Line 26
        cmi = interpolate(iopc, T["cmi"])                                    # Line 27
        lmc = 1.0 - cmi * fpu                                                # Line 28
        lmp = interpolate(ppolx, T["lmp"])                                   # Line 29
        le = P["len"] * lmf * lmhs * lmp * lmc                               # Line 19
        # birth-rate block
        fm = interpolate(le, T["fm"])                                        # Line 34
        mtf = P["mtfn"] * fm                                                 # Line 33
        cmple = interpolate(ple, T["cmple"])                                 # Line 36
        sfsn = interpolate(diopc, T["sfsn"])                                 # Line 39
        dcfs = clip(2.0, P["dcfsn"] * _frsn(aiopc, iopc, T) * sfsn, t_switch, P["zpgt"])   # Line 38
        dtf = dcfs * cmple                                                   # Line 35
        nfc = mtf / dtf - 1.0                                                # Line 44
        fsafc = interpolate(nfc, T["fsafc"])                                 # Line 48
        fcapc = fsafc * sopc                                                 # Line 47
        fce = clip(1.0, interpolate(fcfpc, T["fce"]), t_switch, P["fcest"])  # Line 45
        tf = min(mtf, mtf * (1.0 - fce) + dtf * fce)                         # Line 32
        # cohorts
        m1 = interpolate(le, T["m1"])                                        # Line 4
        m2 = interpolate(le, T["m2"])                                        # Line 8
        m3 = interpolate(le, T["m3"])                                        # Line 12
        m4 = interpolate(le, T["m4"])                                        # Line 16
        d1, d2, d3, d4 = p1 * m1, p2 * m2, p3 * m3, p4 * m4                  # Lines 3, 7, 11, 15
        mat1 = p1 * (1.0 - m1) / 15.0                                        # Line 5
        mat2 = p2 * (1.0 - m2) / 30.0                                        # Line 9
        mat3 = p3 * (1.0 - m3) / 20.0                                        # Line 13
        dr = d1 + d2 + d3 + d4                                               # Line 17
        br = clip(dr, tf * p2 * 0.5 / P["rlt"], t_switch, P["pet"])          # Line 30
        return dict(pop=pop, lmf=lmf, hsapc=hsapc, lmhs=lmhs, fpu=fpu, cmi=cmi, lmc=lmc, lmp=lmp, le=le,
                    fm=fm, mtf=mtf, cmple=cmple, sfsn=sfsn, dcfs=dcfs, dtf=dtf, nfc=nfc, fsafc=fsafc,
                    fcapc=fcapc, fce=fce, tf=tf, d1=d1, d2=d2, d3=d3, d4=d4, mat1=mat1, mat2=mat2,
                    mat3=mat3, dr=dr, br=br)

    # ---- right-hand side ----------------------------------------------------------------------------
    def rhs(self, t: float, y: np.ndarray, inputs: Inputs, t_switch: Optional[float] = None) -> np.ndarray:
        P = self.params
        fpc, sopc, iopc, ppolx = inputs.at(t)
        a = self._algebra(t if t_switch is None else t_switch, y, fpc, sopc, iopc, ppolx)
        dy = np.empty(N_STATES)
        ix = _IX
        dy[ix["p1"]] = a["br"] - a["d1"] - a["mat1"]                         # Line 2
        dy[ix["p2"]] = a["mat1"] - a["d2"] - a["mat2"]                       # Line 6
        dy[ix["p3"]] = a["mat2"] - a["d3"] - a["mat3"]                       # Line 10
        dy[ix["p4"]] = a["mat3"] - a["d4"]                                   # Line 14
        dy[ix["ehspc"]] = (a["hsapc"] - y[ix["ehspc"]]) / P["hsid"]          # Line 22
        # perceived life expectancy: third-order delay of le (Line 37)
        dy[ix["ple1"]] = 3.0 * (a["le"] - y[ix["ple1"]]) / P["lpd"]
        dy[ix["ple2"]] = 3.0 * (y[ix["ple1"]] - y[ix["ple2"]]) / P["lpd"]
        dy[ix["ple"]] = 3.0 * (y[ix["ple2"]] - y[ix["ple"]]) / P["lpd"]
        # delayed industrial output per capita: third-order delay of iopc (Line 40)
        dy[ix["diopc1"]] = 3.0 * (iopc - y[ix["diopc1"]]) / P["sad"]
        dy[ix["diopc2"]] = 3.0 * (y[ix["diopc1"]] - y[ix["diopc2"]]) / P["sad"]
        dy[ix["diopc"]] = 3.0 * (y[ix["diopc2"]] - y[ix["diopc"]]) / P["sad"]
        dy[ix["aiopc"]] = (iopc - y[ix["aiopc"]]) / P["ieat"]                # Line 43
        # fertility control facilities per capita: third-order delay of fcapc (Line 46)
        dy[ix["fcfpc1"]] = 3.0 * (a["fcapc"] - y[ix["fcfpc1"]]) / P["hsid"]
        dy[ix["fcfpc2"]] = 3.0 * (y[ix["fcfpc1"]] - y[ix["fcfpc2"]]) / P["hsid"]
        dy[ix["fcfpc"]] = 3.0 * (y[ix["fcfpc2"]] - y[ix["fcfpc"]]) / P["hsid"]
        return dy

    # ---- initial state ------------------------------------------------------------------------------
    def initial_state(self) -> np.ndarray:
        """Initial state of WorldDynamics.jl (see the module docstring, start-up convention 1): derived
        values from the 1974 tables and parameters, whichever parameter set is being run."""
        P, T = PARAMS_1974, TABLES_1974
        pop = _POP_INIT
        sopc = 1.5e11 / pop
        hsapc = interpolate(sopc, T["hsapc"])
        fpc = 4e11 / pop
        lmf = interpolate(fpc / P["sfpc"], T["lmf"])
        lmhs = interpolate(hsapc, T["lmhs1"])
        lmp = interpolate(1.0, T["lmp"])                    # ppolx = 1
        iopc = 0.7e11 / pop
        cmi = interpolate(iopc, T["cmi"])
        fpu = interpolate(pop, T["fpu"])
        lmc = 1.0 - cmi * fpu
        le = P["len"] * lmf * lmhs * lmp * lmc
        fm = interpolate(le, T["fm"])
        mtf = P["mtfn"] * fm
        sfsn = interpolate(iopc, T["sfsn"])
        dcfs = P["dcfsn"] * _FRSN_INIT * sfsn
        cmple = interpolate(le, T["cmple"])
        dtf = dcfs * cmple
        nfc = mtf / dtf - 1.0
        fcapc = interpolate(nfc, T["fsafc"]) * sopc
        y0 = np.empty(N_STATES)
        y0[[_IX["p1"], _IX["p2"], _IX["p3"], _IX["p4"]]] = _P_INIT
        y0[_IX["ehspc"]] = hsapc
        y0[[_IX["ple"], _IX["ple2"], _IX["ple1"]]] = le
        y0[[_IX["diopc"], _IX["diopc2"], _IX["diopc1"], _IX["aiopc"]]] = _IOPC_HISTORICALRUN
        y0[[_IX["fcfpc"], _IX["fcfpc2"], _IX["fcfpc1"]]] = fcapc
        return y0

    # ---- integration --------------------------------------------------------------------------------
    def _breakpoints(self, t0: float, t1: float) -> list:
        P = self.params
        pts = sorted({P["iphst"], P["zpgt"], P["fcest"], P["pet"]})
        return [t0] + [b for b in pts if t0 < b < t1] + [t1]

    def run(self, inputs: Inputs, t0: float = 1900.0, t1: float = 2100.0, dt: float = 0.25,
            y0: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
        """Integrate from ``t0`` to ``t1`` with RK4 at step ``dt`` (D-003: 0.25 year), splitting at the
        switch times. Returns the time grid, the 15 states by name, and the derived variables."""
        y = self.initial_state() if y0 is None else np.array(y0, dtype=float)
        ts = [t0]
        ys = [y.copy()]
        bps = self._breakpoints(t0, t1)
        for a, b in zip(bps[:-1], bps[1:]):
            n = max(1, int(np.ceil((b - a) / dt - 1e-9)))
            h = (b - a) / n
            for i in range(n):
                t = a + i * h
                k1 = self.rhs(t, y, inputs, a)
                k2 = self.rhs(t + h / 2, y + h / 2 * k1, inputs, a)
                k3 = self.rhs(t + h / 2, y + h / 2 * k2, inputs, a)
                k4 = self.rhs(t + h, y + h * k3, inputs, a)
                y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
                ts.append(a + (i + 1) * h)
                ys.append(y.copy())
        time = np.array(ts)
        Y = np.array(ys)
        out: Dict[str, np.ndarray] = {"time": time}
        for n_, i in _IX.items():
            out[n_] = Y[:, i]
        derived: Dict[str, list] = {}
        for tk, yk in zip(time, Y):
            a = self._algebra(tk, yk, *inputs.at(tk))
            for k, v in a.items():
                derived.setdefault(k, []).append(v)
        for k, v in derived.items():
            out[k] = np.array(v)
        out["pop"] = Y[:, _IX["p1"]] + Y[:, _IX["p2"]] + Y[:, _IX["p3"]] + Y[:, _IX["p4"]]
        return out


def _frsn(aiopc: float, iopc: float, T: Dict[str, Table]) -> float:
    """Family response to social norm: Lines 41 and 42 (``fie = (iopc - aiopc) / aiopc``)."""
    fie = (iopc - aiopc) / aiopc                                             # Line 42
    return interpolate(fie, T["frsn"])                                       # Line 41
