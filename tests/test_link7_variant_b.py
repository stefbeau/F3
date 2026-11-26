"""Link 7, variant B (POST-HOC, docs/link7-variant-b.md): reference run chosen against observed GDP, intensity fitted on it, constant join factor.
Readings fixed in that document before this form was run. The first form's failed hindcast (tests/test_link7_world3_emissions.py) is untouched."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from f3.data import fair_inputs as fi

needs_fair = pytest.mark.skipif(not fi.fair_available(), reason=fi.skip_reason("FaIR calibration files"))
REPO = Path(__file__).resolve().parents[1]
N = 8
HIND = list(range(1970, 2025))
CASES = {"standard": {}, "resources half": {"nri": 0.5e12}, "resources double": {"nri": 2e12}, "land yield 2.0": {"lyf2": 2.0}, "pollution 0.25": {"ppgf21": 0.25}}


def m():
    from f3.sectors import link7_world3_emissions as x
    return x


def gdp() -> dict:
    h = json.loads((REPO / "site" / "data" / "history.json").read_text(encoding="utf-8"))["gdp"]
    return {int(y): float(v) for y, v in zip(h["years"], h["trillion_usd_2015"])}


def test_l7bt3_stored_reference_equals_a_fresh_selection():
    x = m()
    levers, rms = x.select_reference(gdp())
    p = json.loads(x.PARAMS_B_JSON.read_text(encoding="utf-8"))
    assert p["reference_levers"] == levers and abs(p["rms_log_distance_to_gdp"] - rms) <= 1e-12


@needs_fair
def test_l7bt1_hindcast_on_the_reference_run_within_ten_percent():
    x = m()
    obs, io = x.observed_ffi_gt(), x.world3_io(**x.reference_levers())
    a, b = x.params_b()
    rel = np.array([io[y] * np.exp(a + b * y) / obs[y] - 1.0 for y in HIND])
    w = int(np.argmax(np.abs(rel)))
    assert np.max(np.abs(rel)) <= 0.10, f"largest difference {rel[w]:+.1%} in {HIND[w]}; {int((np.abs(rel) > 0.10).sum())} of {len(HIND)} years outside 10%"


@needs_fair
def test_l7bt2_join_factor_of_the_reference_run_is_within_ten_percent_of_one():
    x = m()
    assert abs(x.join_factor(x.world3_io(**x.reference_levers())) - 1.0) <= 0.10


@pytest.mark.xfail(strict=True, reason="L7B-T2 (second part) FAILED (recorded 2026-11-26, audit/link7-variant-b.md): the 2026 value is within 5% of the prescribed 2025 value "
                                       "for the reference run (+0.7%) and for resources double (+0.6%), but not for the standard run (-6.2%), resources half (-6.7%), "
                                       "land yield 2.0 (-7.3%) or pollution 0.25 (-6.4%): in those runs industrial output is already falling fast in 2025.")
@needs_fair
def test_l7bt2_join_step_within_five_percent_for_every_run():
    x = m()
    p25 = x.prescribed_ffi_gt(2025)
    for name, lv in CASES.items():
        rep = x.replacement_gt_b(x.world3_io(**lv))
        assert abs(rep[2026] / p25 - 1.0) <= 0.05, (name, rep[2026], p25)


@needs_fair
def test_l7bt4_history_mass_sign_and_control():
    from f3.sectors import link6_dc_emissions as l6
    from f3.sectors.s6_climate import ClimateSetup, inputs
    x = m()
    io = x.world3_io()
    rep = x.replacement_gt_b(io)
    assert min(rep) == 2026 and max(rep) == 2099
    base = inputs().emissions_for(ClimateSetup()).query("scenario == 'medium-extension'")
    new = inputs().emissions_for(x.setup_with(rep)).query("scenario == 'medium-extension'")
    cols = list(base.columns[4:])
    yrs = np.array([float(c) for c in cols])
    f = base["variable"] == "CO2 FFI"
    b, n = base.loc[f, cols].to_numpy(dtype=float).ravel(), new.loc[f, cols].to_numpy(dtype=float).ravel()
    assert np.array_equal(b[yrs < 2026.0], n[yrs < 2026.0])
    np.testing.assert_allclose([n[cols.index(f"{y}.5")] for y in range(2026, 2100)], [rep[y] for y in range(2026, 2100)], rtol=1e-9)
    assert np.array_equal(new.loc[~f, cols].to_numpy(dtype=float), base.loc[~f, cols].to_numpy(dtype=float), equal_nan=True)
    std = x.climate(rep, n_members=N)
    ref = l6.climate(None, n_members=N)
    i = list(ref["years"]).index(2026)
    np.testing.assert_allclose(std["warming"][: i + 1], ref["warming"][: i + 1], rtol=0, atol=1e-9)
    half = x.climate(x.replacement_gt_b({y: (v * 0.5 if y >= 2027 else v) for y, v in io.items()}), n_members=N)
    assert half["warming"][-1] < std["warming"][-1]
    assert not (std["warming"][-1] < half["warming"][-1]), "control"
