"""Climate sector and A2.1 tests (M2 step 1). Fixed in docs/m2-step1-fair.md section 4 BEFORE any comparison was run.

Data: the FaIR calibration files and HadCRUT5 are read from a pinned local cache (f3/data/fair_inputs.py): skipped with a stated reason
when absent, failing visibly if a hash changed. The A2.1 criterion is asserted as stated; a failure is a result, not a defect to tune."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from f3.core.model import Model
from f3.data import fair_inputs as fi
from f3.sectors.s6_climate import (GCB_EXTRACT, GTC_TO_GTCO2, ClimateSetup, S6Climate, anomaly_on_bounds, gcb_co2, run_fair)

needs_fair = pytest.mark.skipif(not fi.fair_available(), reason=fi.skip_reason("FaIR calibration files"))
needs_both = pytest.mark.skipif(not (fi.fair_available() and fi.hadcrut_available()), reason=fi.skip_reason())
SMALL = ClimateSetup(n_members=20)


@needs_both
def test_pinned_data_hashes():
    for n in fi.FAIR_FILES:
        fi.check_fair_file(n)
    fi.check_hadcrut()


def test_gcb_extract_matches_recorded_values():
    """S5: the committed CC BY 4.0 extract (source: GCB 2025 v1.0, sha256 in its header) holds the recorded values."""
    text = GCB_EXTRACT.read_text(encoding="utf-8")
    assert "a928cf06c57576b66761d1fec8224c9a41a781eb63442afc03ba902858dd64a9" in text and "CC BY 4.0" in text
    d = pd.read_csv(GCB_EXTRACT, comment="#").set_index("year")
    assert list(d.index) == list(range(2015, 2025))
    assert d.loc[2024, "fossil_GtC"] == pytest.approx(10.534546, abs=1e-6)
    assert d.loc[2024, "land_use_change_GtC"] == pytest.approx(1.251503, abs=1e-6)
    assert gcb_co2([2024]).loc[2024, "ffi"] == pytest.approx(10.534546 * GTC_TO_GTCO2)


@needs_fair
def test_s1_sector_equals_single_run_d021():
    """S1: the sector's value at every year boundary equals one single FaIR run's time-bound value (<= 1e-9 K)."""
    s = S6Climate(SMALL)
    Model([s], [], 2018.0, 2022.0, 0.25).run()
    f = run_fair(2030, SMALL)
    a = anomaly_on_bounds(f)
    tb = list(np.asarray(f.timebounds))
    # replay: advance publishes the value at the end of each year
    s2 = S6Climate(SMALL)
    s2.reset(2018.0, 2022.0, 0.25)
    for y in range(2018, 2022):
        s2.advance(float(y), 1.0, None)
        assert abs(s2.current_outputs()["warming"] - a[tb.index(y + 1)].mean()) <= 1e-9
    assert abs(s.current_outputs()["warming"] - a[tb.index(2022)].mean()) <= 1e-9


@needs_fair
def test_s2_time_convention_and_held_values():
    s = S6Climate(SMALL)
    res = Model([s], [], 1980.0, 1984.0, 0.25).run()
    w = res.series[("s6_climate", "warming")]
    assert res.time[0] == 1980.0
    assert np.all(w[0:4] == w[0]) and w[4] != w[0]                      # published value held for the year, changes at 1 January
    f = run_fair(1990, SMALL)
    a = anomaly_on_bounds(f)
    tb = list(np.asarray(f.timebounds))
    assert abs(w[0] - a[tb.index(1980)].mean()) <= 1e-9                 # t = Y is the 1 January time-bound value


@needs_fair
def test_s3_properties_finite_ordered_deterministic():
    runs = []
    for _ in range(2):
        s = S6Climate(SMALL)
        r = Model([s], [], 2000.0, 2004.0, 0.25).run()
        runs.append({k: r.series[("s6_climate", k)] for k in S6Climate.outputs})
    for k, v in runs[0].items():
        assert np.all(np.isfinite(v)), k
        assert np.array_equal(v, runs[1][k]), k
    assert np.all(runs[0]["warming_p05"] <= runs[0]["warming"]) and np.all(runs[0]["warming"] <= runs[0]["warming_p95"])


@needs_fair
def test_s4_sign_zero_co2_from_2026_lowers_2050_warming():
    base = anomaly_on_bounds(run_fair(2051, SMALL))
    zero = anomaly_on_bounds(run_fair(2051, ClimateSetup(n_members=20, co2_scale_after=2026, co2_factor=0.0)))
    tb = list(np.asarray(run_fair(2051, SMALL).timebounds)) if False else list(range(1750, 2052))
    assert zero[tb.index(2050)].mean() < base[tb.index(2050)].mean()


@needs_both
def test_a21_fair_mean_warming_2015_2024_within_hadcrut5_interval():
    """A2.1 as fixed in docs/m2-step1-fair.md section 4. Asserts the criterion; a failure is reported, not adjusted."""
    from tests.fair_checks import a21
    r = a21()
    assert r["passes"], (f"FaIR ensemble-mean 2015-2024 {r['fair_mean_2015_2024']:.3f} K outside HadCRUT5 mean 95% interval "
                         f"[{r['obs_lower']:.3f}, {r['obs_upper']:.3f}] K (best estimate {r['obs_best']:.3f} K)")
