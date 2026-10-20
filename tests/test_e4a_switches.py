"""M4 A4.2, test list written BEFORE the switches were exercised (docs/tracks/track-c-plan.md, section 2).

The warming channels are switchable inputs: `SW_OWECC`, `SW_OWELC` (output) and `SW_OWTFP` (public), default 1 (Earth4All.jl exactly), 0 = off.
(a) Earth4All.jl has no switched-off reference, so "with the channels off the sector still passes A4.1" is tested only where a reference
    exists: for t <= 2022 the channels are inactive (the equations say `t > 2022`), so the off run must equal the reference there to 1e-9;
    after 2022 the SIZE of the channel effect on every criterion variable is printed (not judged), and the variables the channel does not
    touch (identical to 1e-12 in the on and off runs) are listed.
(b) switches on with OW held at OW2022 (1.35) equal the off run (relative difference <= 1e-9), both scenarios.
(c) EDROTA2022 is a documented parameter of public: setting it to 0 changes DRTA after 2022 by exactly EDROTA2022 * (1 + SCROTA * (SC/SC1980 - 1)).
Both scenarios. The OW input is the recorded Earth4All.jl `OW` series unless overridden.
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.e4a_helpers import SCENARIOS, grid_index, reference, rel_err, run_alone, signals
from tests.test_e4a_output import CASE as OUT_CASE
from tests.test_e4a_public import CASE as PUB_CASE

OW2022 = 1.35


def _ow_held(scen):
    s = signals(scen)
    return {"OW": np.full_like(s["time"], OW2022)}


def _run(key, scen, **kw):
    return run_alone(key, scen, 0.25, "euler", None, **kw)


CHANNELS = {"output": {"OWECC": "SW_OWECC", "OWELC": "SW_OWELC"}, "public": {"OWTFP": "SW_OWTFP"}}
CASES = {"output": OUT_CASE, "public": PUB_CASE}


@pytest.mark.parametrize("scen", SCENARIOS)
@pytest.mark.parametrize("key", ["output", "public"])
def test_a42_b_on_with_warming_at_2022_equals_off(key, scen):
    off = {sw: 0.0 for sw in CHANNELS[key].values()}
    s_off, r_off = _run(key, scen, switches=off, overrides=_ow_held(scen))
    s_on, r_on = _run(key, scen, overrides=_ow_held(scen))
    nm = s_on.name
    worst = 0.0
    for n in s_on.outputs:
        if (nm, n) in r_on.series:
            a, b = r_on.series[(nm, n)], r_off.series[(nm, n)]
            scale = max(float(np.max(np.abs(b))), 1e-300)
            worst = max(worst, float(np.max(np.abs(a - b))) / scale)
    print(f"{key} {scen}: on(OW=2022 value) vs off, worst difference relative to series scale {worst:.3e}")
    assert worst <= 1e-9


@pytest.mark.parametrize("scen", SCENARIOS)
@pytest.mark.parametrize("key", ["output", "public"])
def test_a42_a_off_equals_reference_until_2022_and_effect_size_after(key, scen):
    off = {sw: 0.0 for sw in CHANNELS[key].values()}
    s_off, r_off = _run(key, scen, switches=off)
    s_on, r_on = _run(key, scen)
    nm = s_on.name
    ref = reference(scen)
    idx = grid_index(r_off.time, ref["time"])
    early = ref["time"] <= 2022.0 + 1e-9
    case = CASES[key]
    worst_early = 0.0
    untouched, effect = [], {}
    for n in case.criterion:
        a_off = r_off.series[(nm, n)]
        a_on = r_on.series[(nm, n)]
        b = ref[f"{key}.{n}"]
        e = rel_err(a_off[idx], b)
        if e is not None:
            worst_early = max(worst_early, float(e[early].max()))
        if np.max(np.abs(a_off - a_on)) <= 1e-12 * max(np.max(np.abs(a_on)), 1e-300):
            untouched.append(n)
        else:
            d = rel_err(a_off[idx], a_on[idx])
            effect[n] = None if d is None else float(d.max())
    print(f"{key} {scen}: off vs reference up to 2022: worst {100 * worst_early:.3e}%; untouched by the channels: {untouched}")
    print(f"{key} {scen}: effect of switching the channels off, max |off - on| / |on| over 1980-2100: " +
          ", ".join(f"{n} {100 * v:.2f}%" for n, v in effect.items() if v is not None))
    assert worst_early <= 1e-9


@pytest.mark.parametrize("scen", SCENARIOS)
def test_a42_c_edrota2022_is_a_documented_parameter_and_acts_as_documented(scen):
    import f3.sectors.e4a_public as pub
    assert "EDROTA2022" in pub.PARAMS and pub.PARAMS["EDROTA2022"] == 0.003
    assert "EDROTA2022" in (pub.__doc__ or "") and "DOCUMENTED PARAMETER" in pub.__doc__
    s_def, r_def = _run("public", scen)
    s_0, r_0 = _run("public", scen, params={"EDROTA2022": 0.0})
    t = r_def.time
    d_def = r_def.series[("e4a_public", "DRTA")]
    d_0 = r_0.series[("e4a_public", "DRTA")]
    SC = r_def.series[("e4a_public", "SC")]
    term = 0.003 * (1 + 0.5 * (SC / 0.3 - 1))
    post = t > 2022.0 + 1e-9
    assert np.allclose(d_def[post] - d_0[post], term[post], rtol=1e-9, atol=1e-12)
    assert np.allclose(d_def[~post], d_0[~post], rtol=0, atol=0)
    print(f"public {scen}: EDROTA2022 raises DRTA after 2022 by {term[post].min():.5f} to {term[post].max():.5f} per year; effect on TFPEE5TA in 2100: "
          f"{100 * (r_def.series[('e4a_public', 'TFPEE5TA')][-1] / r_0.series[('e4a_public', 'TFPEE5TA')][-1] - 1):.2f}%")
