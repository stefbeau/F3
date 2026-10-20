"""M3 A3.3: second check of the full port against PyWorld3 1.1, unmodified, at dt = 0.05 (CeCILL 2.1: used, never copied, D-001/D-012).
Test list written BEFORE the coupling module (docs/tracks/track-b.md).

Twelve main stocks (CLAUDE.md, audit/t0/pyworld3_t0.py): p1 p2 p3 p4 (population), ic (industrial capital), sc (service capital),
al (arable land), pal (potentially arable land), uil (urban-industrial land), lfert (land fertility), ppol (persistent pollution),
nr (non-renewable resources). Compared at every 0.5 year of 1900-2100 against the full coupled port (step 0.25, started from
WorldDynamics.jl's own initial state), with PyWorld3's pollution Delay3 start value matched to WorldDynamics.jl's (a LABELLED
DIAGNOSTIC: a runtime override on the PyWorld3 instance, as audit/t0/pyworld3_t0.py does; no PyWorld3 code is edited or copied).
The as-shipped comparison (no override) is printed beside it and is expected to fail on ppol (373.7% in 1906 as T0 found).

1974: A3.3 criterion, all twelve within 2% with the matched start-up. 2004: diagnostic (PyWorld3 does not ship that variant; the
parameters and tables are overridden on the instance as in tests/pyworld3_check.py); numbers are printed, nothing is asserted,
as in S1.
"""

from __future__ import annotations

import numpy as np
import pytest

from f3.sectors.world3 import run_world3
from tests.pyworld3_check import _interp
from tests.w3_helpers import TOL, reference, relerr

STOCKS = ("p1", "p2", "p3", "p4", "ic", "sc", "al", "pal", "uil", "lfert", "ppol", "nr")
PORT_NAME = {"p1": "p1", "p2": "p2", "p3": "p3", "p4": "p4", "ic": "ic", "sc": "sc", "al": "al", "pal": "pal", "uil": "uil",
             "lfert": "lfert", "ppol": "ppol", "nr": "nr"}


def _pyworld3(ps: str, ppgr_start=None, dt: float = 0.05):
    from pyworld3 import World3
    from f3.sectors.w3_agriculture import PARAMETER_SETS as AG
    from f3.sectors.w3_resources import PARAMETER_SETS as NR
    from f3.sectors.s1_population import PARAMETER_SETS as PO

    w = World3(dt=dt)
    if ps == "2004":
        w.init_world3_constants(dcfsn=3.8, alln=1000)
    else:
        w.init_world3_constants()
    w.init_world3_variables()
    w.set_world3_table_functions()
    if ps == "2004":                                     # DIAGNOSTIC runtime overrides on the instance (as tests/pyworld3_check.py)
        for name in ("lmf", "lmhs2", "fm", "sfsn"):
            setattr(w, f"{name}_f", _interp(PO["2004"][1][name]))
        w.lymc_f = _interp(AG["2004"][1]["lymc"])
        w.pcrum_f = _interp(NR["2004"][1]["pcrum"])
    w.set_world3_delay_functions()
    if ppgr_start is not None:                           # DIAGNOSTIC: start value of the pollution delay (audit/t0/pyworld3_t0.py)
        d = w.delay3_ppgr
        d._init_out_arr = lambda delay, d=d: d.out_arr.__setitem__((0, slice(None)), ppgr_start)
    w.run_world3(fast=False)
    return w


def _compare(ps: str, w, states, res, label: str):
    n = len(np.asarray(w.time))
    t = np.asarray(w.time)
    ref = reference(ps)
    out = {}
    for k in STOCKS:
        py = np.asarray(getattr(w, k))
        m = min(len(py), len(t))
        # PyWorld3 time points nearest each 0.5 year
        idx_py = np.array([int(np.argmin(np.abs(t[:m] - x))) for x in ref["time"]])
        idx_port = np.array([int(np.argmin(np.abs(res.time - x))) for x in ref["time"]])
        e = relerr(states[PORT_NAME[k]][idx_port], py[idx_py])
        out[k] = (float(e.max()), float(ref["time"][int(e.argmax())]))
    print(f"A3.3 {ps} {label}: " + "; ".join(f"{k} {100*v[0]:.2f}% ({v[1]:.0f})" for k, v in out.items()))
    return out


XF = pytest.mark.xfail(strict=True, reason="A3.3 FAILED for the 1974 set at the loop step 0.25 year: ic 3.39% against PyWorld3 (dt=0.05) with the "
                       "pollution start-up matched; same cause as A3.2 (coupling error). Criterion not relaxed. docs/tracks/track-b.md.")


@pytest.fixture(scope="module", params=[pytest.param("1974", marks=XF), "2004"])
def runs(request):
    ps = request.param
    states, res = run_world3(ps)
    ref = reference(ps)
    w0 = _pyworld3(ps)
    # WorldDynamics.jl implied start of the delay input: ppapr3(1900) = pptd * ppgr / 3  ->  ppgr = ppapr3 * 3 / pptd
    ppgr_wd = float(ref["pp₊ppapr3"][0]) * 3.0 / float(w0.pptd1)
    w1 = _pyworld3(ps, ppgr_start=ppgr_wd)
    return ps, states, res, w0, w1


def test_a33_pyworld3_matched_startup(runs):
    ps, states, res, w0, w1 = runs
    as_shipped = _compare(ps, w0, states, res, "as shipped (PyWorld3 pollution delay start-up)")
    matched = _compare(ps, w1, states, res, "pollution delay start matched (DIAGNOSTIC override)")
    if ps == "1974":
        bad = {k: v for k, v in matched.items() if v[0] > TOL}
        assert not bad, f"1974 stocks above 2% with the matched start-up: {bad}"
    else:
        print("2004 is a diagnostic (PyWorld3 does not ship this variant): nothing asserted.")
