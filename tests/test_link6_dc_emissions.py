"""Link 6 (data-centre electricity to emissions): readings in docs/link6-tests.md, written before the code. FaIR tests use a small ensemble and are
skipped when the FaIR calibration files are not in the cache (as the other climate tests are)."""
from __future__ import annotations

import numpy as np
import pytest

from f3.data import fair_inputs as fi

needs_fair = pytest.mark.skipif(not fi.fair_available(), reason=fi.skip_reason("FaIR calibration files"))
N = 8                                                   # small ensemble for the tests; the report uses all 841 members
YEARS = list(range(2026, 2100))


def link():
    from f3.sectors import link6_dc_emissions as l6
    return l6


def test_l6t5_intensity_is_finite_positive_and_below_one():
    k = link().intensity_kg_per_kwh()
    assert set(range(2025, 2101)) <= set(k)
    v = np.array([k[y] for y in range(2025, 2101)])
    assert np.all(np.isfinite(v)) and np.all(v > 0.0) and np.all(v < 1.0)


def test_l6t3_mass_conservation_and_no_addition_before_2026():
    l6 = link()
    used = l6.electricity_used_twh(g_max=0.30)
    extra = l6.extra_co2_gt(used)
    k = l6.intensity_kg_per_kwh()
    assert min(extra) >= 2026 and max(extra) <= 2099 and all(v >= 0.0 for v in extra.values())
    want = sum(max(0.0, used[y] - l6.BASELINE_TWH) * k[y] * 1e-3 for y in YEARS)          # TWh x kg/kWh = 1e9 kg = 1e-3 Gt
    assert abs(sum(extra.values()) - want) <= 1e-9 * want
    from f3.sectors.s6_climate import ClimateSetup, inputs
    base = inputs().emissions_for(ClimateSetup()).query("scenario == 'medium-extension'")
    new = inputs().emissions_for(l6.setup_with(extra)).query("scenario == 'medium-extension'")
    cols = [c for c in base.columns[4:]]
    m = base["variable"] == "CO2 FFI"
    d = (new.loc[m, cols].to_numpy(dtype=float) - base.loc[m, cols].to_numpy(dtype=float)).ravel()
    yrs = np.array([float(c) for c in cols])
    assert np.all(d[yrs < 2026.0] == 0.0)                                                  # L6-T2: nothing up to and including 2025
    assert abs(d.sum() - sum(extra.values())) <= 1e-9 * want
    other = new.loc[~m, cols].to_numpy(dtype=float)
    assert np.array_equal(other, base.loc[~m, cols].to_numpy(dtype=float), equal_nan=True)  # every other species untouched


def test_l6_faster_build_gives_at_least_as_much_cumulative_co2():
    l6 = link()
    tot = [sum(l6.extra_co2_gt(l6.electricity_used_twh(g_max=g)).values()) for g in (0.15, 0.30, 0.50)]
    assert tot[0] <= tot[1] <= tot[2] and tot[0] > 0.0


def test_l6t1_no_addition_leaves_the_emissions_table_identical():
    from f3.sectors.s6_climate import ClimateSetup, inputs
    assert ClimateSetup().co2_ffi_extra is None
    a = inputs().emissions_for(ClimateSetup())
    b = inputs().emissions_for(link().setup_with({}))
    assert a.equals(b)


@needs_fair
def test_l6t1_t2_zero_addition_and_history_unchanged():
    l6 = link()
    base = l6.climate(None, n_members=N)
    zero = l6.climate({y: 0.0 for y in YEARS}, n_members=N)
    for k in ("warming", "co2_concentration"):
        np.testing.assert_allclose(zero[k], base[k], rtol=0, atol=1e-9, err_msg=k)
    on = l6.climate(l6.extra_co2_gt(l6.electricity_used_twh(g_max=0.30)), n_members=N)
    i = list(base["years"]).index(2026)
    for k in ("warming", "co2_concentration"):
        np.testing.assert_allclose(on[k][: i + 1], base[k][: i + 1], rtol=0, atol=1e-9, err_msg=k)


@needs_fair
def test_l6t4_sign_and_control():
    l6 = link()
    base = l6.climate(None, n_members=N)["warming"][-1]
    w = [l6.climate(l6.extra_co2_gt(l6.electricity_used_twh(g_max=g)), n_members=N)["warming"][-1] for g in (0.15, 0.50)]
    assert w[0] >= base - 1e-9 and w[1] >= w[0] - 1e-9
    neg = l6.climate({y: -1.0 for y in YEARS}, n_members=N)["warming"][-1]                 # control: one Gt CO2 a year less must cool
    assert neg < base


@needs_fair
def test_l6t6_one_run_equals_the_yearly_re_runs():
    from f3.sectors.s6_climate import ClimateSetup, S6Climate
    l6 = link()
    extra = l6.extra_co2_gt(l6.electricity_used_twh(g_max=0.30))
    one = l6.climate(extra, n_members=N)
    sec = S6Climate(l6.setup_with(extra, n_members=N))
    for y in (2030, 2050, 2100):
        ref = sec._at(y)
        i = list(one["years"]).index(y)
        for k in ("warming", "warming_p05", "warming_p95", "co2_concentration"):
            assert abs(one[k][i] - ref[k]) <= 1e-9, (y, k, one[k][i], ref[k])


def test_notice_names_what_is_and_is_not_done():
    n = link().NOTICE
    for phrase in ("one-way", "prescribed", "upper reading", "485"):
        assert phrase in n, phrase
