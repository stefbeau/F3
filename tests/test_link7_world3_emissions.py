"""Link 7 (World3 to emissions): readings in docs/link7-tests.md, written before the code. Tests that need the FaIR files are skipped without them."""
from __future__ import annotations

import json

import numpy as np
import pytest

from f3.data import fair_inputs as fi

needs_fair = pytest.mark.skipif(not fi.fair_available(), reason=fi.skip_reason("FaIR calibration files"))
N = 8
HIND = list(range(1970, 2025))
FUT = list(range(2026, 2100))


def l7():
    from f3.sectors import link7_world3_emissions as m
    return m


@needs_fair
def test_l7t1_hindcast_within_ten_percent_every_year():
    m = l7()
    obs, mod = m.observed_ffi_gt(), m.modelled_ffi_gt(m.world3_io())
    rel = np.array([mod[y] / obs[y] - 1.0 for y in HIND])
    worst = int(np.argmax(np.abs(rel)))
    assert np.max(np.abs(rel)) <= 0.10, f"largest difference {rel[worst]:+.1%} in {HIND[worst]}; {int((np.abs(rel) > 0.10).sum())} of {len(HIND)} years outside 10%"


@needs_fair
def test_l7t6_stored_parameters_equal_a_fresh_fit():
    m = l7()
    a, b = m.fit_intensity(m.observed_ffi_gt(), m.world3_io())
    p = json.loads(m.PARAMS_JSON.read_text(encoding="utf-8"))
    assert abs(p["a"] - a) <= 1e-9 * abs(a) and abs(p["b"] - b) <= 1e-9 * abs(b)


def table(setup):
    from f3.sectors.s6_climate import inputs
    return inputs().emissions_for(setup).query("scenario == 'medium-extension'")


@needs_fair
def test_l7t2_t3_t4_table_identity_history_and_mass():
    from f3.sectors.s6_climate import ClimateSetup
    m = l7()
    assert ClimateSetup().co2_ffi_replace is None
    base = table(ClimateSetup())
    assert base.equals(table(m.setup_with(None)))
    rep = m.replacement_gt(m.world3_io())
    assert min(rep) == 2026 and max(rep) == 2099
    new = table(m.setup_with(rep))
    cols = list(base.columns[4:])
    yrs = np.array([float(c) for c in cols])
    f = base["variable"] == "CO2 FFI"
    b, n = base.loc[f, cols].to_numpy(dtype=float).ravel(), new.loc[f, cols].to_numpy(dtype=float).ravel()
    assert np.array_equal(b[yrs < 2026.0], n[yrs < 2026.0])                                   # L7-T3
    want = np.array([rep[y] for y in FUT])
    got = np.array([n[np.where(np.isclose(yrs, y + 0.5))[0][0]] for y in FUT])
    np.testing.assert_allclose(got, want, rtol=1e-9)                                           # L7-T4
    assert np.array_equal(new.loc[~f, cols].to_numpy(dtype=float), base.loc[~f, cols].to_numpy(dtype=float), equal_nan=True)


@needs_fair
def test_l7t2_replacement_by_the_prescribed_values_changes_nothing():
    from f3.sectors.s6_climate import ClimateSetup
    from f3.sectors import link6_dc_emissions as l6
    m = l7()
    base = table(ClimateSetup())
    cols = list(base.columns[4:])
    row = base.loc[base["variable"] == "CO2 FFI", cols].to_numpy(dtype=float).ravel()
    same = {y: float(row[cols.index(f"{y}.5")]) for y in FUT}
    a, b = l6.climate(None, n_members=N), m.climate(same, n_members=N)
    for k in ("warming", "co2_concentration"):
        np.testing.assert_allclose(b[k], a[k], rtol=0, atol=1e-9, err_msg=k)


@needs_fair
def test_l7t3_t5_history_unchanged_and_sign_with_control():
    from f3.sectors import link6_dc_emissions as l6
    m = l7()
    io = m.world3_io()
    std = m.climate(m.replacement_gt(io), n_members=N)
    base = l6.climate(None, n_members=N)
    i = list(base["years"]).index(2026)
    np.testing.assert_allclose(std["warming"][: i + 1], base["warming"][: i + 1], rtol=0, atol=1e-9)
    half = m.climate(m.replacement_gt({y: (v * 0.5 if y >= 2026 else v) for y, v in io.items()}), n_members=N)
    lower = lambda x, y: x["warming"][-1] < y["warming"][-1]                                   # noqa: E731
    assert lower(half, std)
    assert not lower(std, half), "control: the swapped comparison must fail"


@needs_fair
def test_l7t7_with_link6_the_two_parts_add():
    from f3.sectors import link6_dc_emissions as l6
    m = l7()
    rep = m.replacement_gt(m.world3_io())
    extra = l6.extra_co2_gt(l6.electricity_used_twh(g_max=0.30))
    both = table(m.setup_with(rep, extra=extra))
    cols = list(both.columns[4:])
    row = both.loc[both["variable"] == "CO2 FFI", cols].to_numpy(dtype=float).ravel()
    for y in (2030, 2050, 2099):
        assert abs(row[cols.index(f"{y}.5")] - (rep[y] + extra[y])) <= 1e-9 * (rep[y] + extra[y])


def test_notice_names_what_is_and_is_not_done():
    n = l7().NOTICE
    for phrase in ("one-way", "replaced", "prescribed", "in-sample"):
        assert phrase in n, phrase
