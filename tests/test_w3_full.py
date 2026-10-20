"""M3, step 5: the full World3 run, S1 plus the four ported sectors in the coupling loop (acceptance tests A3.2, A3.4, A3.5 of
docs/phase-2-plan.md). Test list written BEFORE the coupling module (docs/tracks/track-b.md); the reading of each test was
fixed there too.

A3.2  all 29 states within 2% (D-004) of the default WorldDynamics.jl reference at every 0.5-year point of 1900-2100, both sets,
      loop step 0.25 year (D-003). If a state exceeds 2%, the size and first year are reported and the same state is compared with
      the tight-tolerance reference; the criterion is NOT relaxed (a test that fails stays failing or is a documented strict xfail).
A3.4  (b) S1's 15 states inside the full run equal S1's 15 states run alone with the recorded inputs (the reference's own series of
      its four inputs) within 0.25% (the plan's number, the largest S1 gap with the 2004 set), both sets, 1900-2100.
      Prediction written before the run: D-022 measured start-of-step coupling error of S1 at step 0.25 year as 1.04% (1974) and
      0.93% (2004) on the worst state, so this test is expected to fail for the 1974 set on at least one delay stage.
A3.5  the wall-clock time of one full run (1900-2100 and 1970-2100, step 0.25) is measured and printed; the test only checks that
      the run completes and the figure is positive and finite (there is no pass level in the plan).
Also: the loop wiring is complete and unit-checked; the 1970 restart from the reference's 1970 state runs; the number of states is 29.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

from f3.sectors.world3 import STATE_COLUMNS, build_world3, run_world3
from f3.sectors.s1_population import STATE_NAMES as S1_STATES, Inputs, PopulationSector
from tests.w3_helpers import TOL, grid_index, reference, relerr, signals


@pytest.fixture(scope="module", params=["1974", "2004"])
def full(request):
    ps = request.param
    states, res = run_world3(ps)
    return ps, states, res


def test_there_are_29_states_by_name():
    assert len(STATE_COLUMNS) == 29 and len(set(STATE_COLUMNS.values())) == 29


@pytest.mark.xfail(strict=True, reason="A3.2 FAILED at the plan's step 0.25 year, both sets (docs/tracks/track-b.md, audit/m3-world3-port-report.md): "
                   "explicit start-of-step coupling (D-022) is first order; worst state lufd 6.9% (1974), 8.0% (2004). Criterion not relaxed.")
def test_a32_all_29_states_within_2_percent(full):
    ps, states, res = full
    ref, tight = reference(ps), reference(ps, "tight")
    idx = grid_index(res.time, ref["time"])
    bad = []
    for n, col in STATE_COLUMNS.items():
        e = relerr(states[n][idx], ref[col])
        et = relerr(states[n][idx], tight[col])
        er = relerr(ref[col], tight[col])
        first = float(ref["time"][np.argmax(e > TOL)]) if e.max() > TOL else None
        print(f"A3.2 {ps} {n}: max {100*e.max():.3f}% (year {ref['time'][int(e.argmax())]}, mean {100*e.mean():.3f}%); vs tight "
              f"{100*et.max():.3f}%; reference default vs tight {100*er.max():.3f}%; first year above 2%: {first}")
        if e.max() > TOL:
            bad.append((n, float(e.max()), first))
    assert not bad, f"{ps}: states above 2%: {bad}"


@pytest.mark.xfail(strict=True, reason="A3.4(b) FAILED, as predicted before the run: start-of-step coupling error of S1 inside the full "
                   "run exceeds 0.25% (docs/tracks/track-b.md). Criterion not relaxed.")
def test_a34b_s1_inside_the_full_run_equals_s1_alone_within_0_25_percent(full):
    ps, states, res = full
    s = signals(ps)
    alone = PopulationSector(ps).run(Inputs(s["time"], s["dr₊fpc"], s["br₊sopc"], s["dr₊iopc"], s["dr₊ppolx"]), dt=0.25)
    worst = {}
    for n in S1_STATES:
        e = relerr(states[n], alone[n])
        worst[n] = (float(e.max()), float(res.time[int(e.argmax())]))
        print(f"A3.4b {ps} {n}: S1 in full run vs S1 alone, max {100*e.max():.3f}% (year {worst[n][1]})")
    over = {n: v for n, v in worst.items() if v[0] > 0.0025}
    assert not over, f"{ps}: S1 states above 0.25%: {over}"


def test_a35_run_time_is_measured():
    for ps, t0 in (("2004", 1900.0), ("2004", 1970.0), ("1974", 1900.0)):
        run_world3(ps, t0=t0)                       # warm-up
        ts = []
        for _ in range(3):
            a = time.perf_counter()
            run_world3(ps, t0=t0)
            ts.append(time.perf_counter() - a)
        print(f"A3.5 full World3 run, set {ps}, {t0:.0f}-2100, step 0.25: median {np.median(ts):.2f} s (min {min(ts):.2f}, max {max(ts):.2f})")
        assert np.isfinite(np.median(ts)) and np.median(ts) > 0


def test_wiring_is_complete_and_unit_checked():
    sectors, couplings = build_world3("2004")
    names = {s.name for s in sectors}
    assert names == {"s1_population", "w3_agriculture", "w3_capital", "w3_resources", "w3_pollution"}
    wired = {(c.target, c.target_input) for c in couplings}
    for s in sectors:
        for i in s.inputs:
            assert (s.name, i) in wired, (s.name, i)


@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_restart_in_1970_from_the_reference_state_stays_within_2_percent_for_40_years(ps):
    """D-019 mechanics inside the loop. Not an acceptance test of the plan: a diagnostic of how fast coupling error grows."""
    ref = reference(ps)
    i70 = int(np.where(np.isclose(ref["time"], 1970.0))[0][0])
    y0 = {n: ref[col][i70] for n, col in STATE_COLUMNS.items()}
    states, res = run_world3(ps, t0=1970.0, y0=y0)
    sel = ref["time"] >= 1970.0
    idx = grid_index(res.time, ref["time"][sel])
    horizon = ref["time"][sel] <= 2010.0
    worst = 0.0
    for n, col in STATE_COLUMNS.items():
        e = relerr(states[n][idx], ref[col][sel])
        worst = max(worst, float(e[horizon].max()))
    print(f"1970 restart {ps}: worst of 29 states over 1970-2010: {100*worst:.3f}%")
    assert worst <= TOL


# ---------------------------------------------------------------------------------------------------------------
# POST-HOC DIAGNOSTIC (written after A3.2 and A3.4(b) failed at dt = 0.25; NOT acceptance tests, not a revised criterion).
# They measure how the failure depends on the loop step. A passing diagnostic does not turn A3.2 into a pass.
# ---------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("ps", ["1974", "2004"])
def test_diagnostic_a32_criterion_applied_at_dt_0_0625(ps):
    states, res = run_world3(ps, dt=0.0625)
    ref = reference(ps)
    idx = grid_index(res.time, ref["time"])
    worst = {n: float(relerr(states[n][idx], ref[col]).max()) for n, col in STATE_COLUMNS.items()}
    k = max(worst, key=worst.get)
    print(f"DIAGNOSTIC A3.2 criterion at dt=0.0625, {ps}: worst {100*worst[k]:.3f}% ({k})")
    assert worst[k] <= TOL


def test_diagnostic_run_time_at_dt_0_0625():
    run_world3("2004", dt=0.0625)
    a = time.perf_counter()
    run_world3("2004", dt=0.0625)
    print(f"DIAGNOSTIC A3.5 at dt=0.0625, 2004, 1900-2100: {time.perf_counter() - a:.2f} s")
