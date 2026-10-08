"""Second check of the S1 port against PyWorld3 (unmodified, from PyPI; CeCILL 2.1 - used, never copied, D-001/D-012).

PyWorld3 implements the 1974 World3 model only. Two uses:

* ``run_pyworld3("1974")``: PyWorld3 exactly as shipped (its own constants and tables, nothing overridden).
* ``run_pyworld3("2004", ...)``: **DIAGNOSTIC ONLY.** The 2004 parameter set is imposed on a PyWorld3 *instance* at
  run time: ``dcfsn`` and ``alln`` through the documented arguments of ``init_world3_constants``, and the tables
  ``lmf``, ``lmhs2``, ``fm`` (population), ``sfsn`` (population), ``lymc`` (agriculture) and ``pcrum`` (non-renewable
  resources) by assigning new interpolators to the instance, as ``set_world3_table_functions`` does. No PyWorld3
  code is edited or copied. PyWorld3 does not ship this variant, so this check is not an independent
  implementation of the 2004 model; it only tests that the port's population equations agree with PyWorld3's
  population equations when both are given the same parameters and the same inputs.

The comparison feeds the port with the four inputs taken from the PyWorld3 run itself (food per capita, service
output per capita, industrial output per capita, persistent pollution index) and, where stated, PyWorld3's own
initial state, so that only the population equations are being compared.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np

from f3.sectors.s1_population import PARAMETER_SETS, Inputs, Table


def _interp(table: Table):
    from scipy.interpolate import interp1d

    y, (lo, hi) = table
    return interp1d(np.linspace(lo, hi, len(y)), list(y), bounds_error=False, fill_value=(y[0], y[-1]))


# World3_91 / World3_03 overrides outside the population sector (WorldDynamics.jl World3_91/world3_91/scenarios.jl)
_LYMC_2004: Table = ((1.0, 3.0, 4.5, 5.0, 5.3, 5.6, 5.9, 6.1, 6.35, 6.6, 6.9, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4,
                      8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 10.0), (0.0, 1000.0))
_PCRUM_2004: Table = ((0.0, 0.85, 2.6, 3.4, 3.8, 4.1, 4.4, 4.7, 5.0), (0.0, 1600.0))


def run_pyworld3(parameter_set: str, dt: float = 0.05):
    """Run PyWorld3 over 1900-2100 and return (world, time, Inputs, initial-state dict)."""
    from pyworld3 import World3

    w = World3(dt=dt)
    if parameter_set == "2004":
        w.init_world3_constants(dcfsn=3.8, alln=1000)
    else:
        w.init_world3_constants()
    w.init_world3_variables()
    w.set_world3_table_functions()
    if parameter_set == "2004":      # DIAGNOSTIC: runtime override on the instance only
        _, tables = PARAMETER_SETS["2004"]
        for name in ("lmf", "lmhs2", "fm", "sfsn"):
            setattr(w, f"{name}_f", _interp(tables[name]))
        w.lymc_f = _interp(_LYMC_2004)
        w.pcrum_f = _interp(_PCRUM_2004)
    w.set_world3_delay_functions()
    w.run_world3(fast=False)
    n = min(len(w.time), len(w.fpc), len(w.p1), len(w.ppolx), len(w.sopc), len(w.iopc))
    t = np.asarray(w.time)[:n]
    inputs = Inputs(t, np.asarray(w.fpc)[:n], np.asarray(w.sopc)[:n], np.asarray(w.iopc)[:n],
                    np.asarray(w.ppolx)[:n])
    return w, t, inputs, n


def pyworld3_initial_state(w) -> np.ndarray:
    """PyWorld3's own state at 1900, in the port's state order (delay stages equal, as PyWorld3 starts them)."""
    from f3.sectors.s1_population import STATE_NAMES, _IX

    y0 = np.zeros(len(STATE_NAMES))
    for k in ("p1", "p2", "p3", "p4", "ehspc", "ple", "diopc", "aiopc", "fcfpc"):
        y0[_IX[k]] = float(np.asarray(getattr(w, k))[0])
    for a, b, c in (("ple", "ple2", "ple1"), ("diopc", "diopc2", "diopc1"), ("fcfpc", "fcfpc2", "fcfpc1")):
        y0[_IX[b]] = y0[_IX[c]] = y0[_IX[a]]
    return y0


def compare(out: Dict[str, np.ndarray], w, n: int, names=("p1", "p2", "p3", "p4", "pop", "ple", "ehspc", "aiopc",
                                                          "fcfpc"), stride: int = 10) -> Dict[str, Tuple[float, float]]:
    """Max relative difference (and the year) of the port against PyWorld3, on every ``stride``-th PyWorld3 step."""
    t = np.asarray(w.time)[:n]
    sel = np.arange(0, n, stride)
    idx = np.array([int(np.argmin(np.abs(out["time"] - x))) for x in t[sel]])
    res = {}
    for k in names:
        a = out[k][idx]
        b = np.asarray(getattr(w, k))[:n][sel]
        e = np.abs(a - b) / np.maximum(np.abs(b), 1e-30)
        i = int(np.argmax(e))
        res[k] = (float(e[i]), float(t[sel][i]))
    return res
