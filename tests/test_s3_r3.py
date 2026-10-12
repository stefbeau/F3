"""R3 investment rule tests (D-028): share validity, finiteness, A1.5 with S3 driven by R3 (three shipped settings and the two
stress settings, which now use R3 instead of the placeholder path), and a lever test. No reference data needed: the fitted
curve tables are stored (``f3/sectors/r3_curves.json``), the bundle is not read here."""

from __future__ import annotations

import itertools

import numpy as np
import pytest

from f3.sectors.s3_ai import SHARE_NAMES
from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
from tests.s3_checks import SETTINGS_B, STRESS, a15_properties_rule, run_s3_rule

LEVERS = [R3Levers(), R3Levers(initial_ai_share=0.9), R3Levers(initial_ai_share=0.0), R3Levers(decay_speed=5.0), R3Levers(decay_speed=0.2),
          R3Levers(split=(0.0, 1.0, 1.0)), R3Levers(split=(5.0, 0.1, 0.1)), R3Levers(capital_scale=50.0), R3Levers(training_scale=5.0),
          R3Levers(initial_ai_share=2.0, capital_scale=10.0)]


@pytest.mark.parametrize("lev", range(len(LEVERS)))
def test_shares_valid_everywhere(lev):
    rule = R3Rule(LEVERS[lev])
    for f, u in itertools.product(np.linspace(0.1, 1.0, 19), np.logspace(-12, 0, 25)):
        q = rule.shares(float(f), float(u))
        assert all(0.0 <= q[n] <= 1.0 for n in SHARE_NAMES), (f, u, q)
        assert abs(sum(q[n] for n in SHARE_NAMES[:5]) - 1.0) < 1e-12, (f, u, q)


@pytest.mark.parametrize("name", list(SETTINGS_B))
def test_r3_finite_and_a15_on_shipped_settings(name):
    params = SETTINGS_B[name][1]
    res = a15_properties_rule(params, lambda lev=None: R3Rule(lev or R3Levers()))
    assert all(ok for ok, _ in res.values()), {k: d for k, (ok, d) in res.items() if not ok}


@pytest.mark.parametrize("name", list(STRESS))
def test_r3_a15_on_stress_settings(name):
    res = a15_properties_rule(STRESS[name], lambda lev=None: R3Rule(lev or R3Levers()))
    assert all(ok for ok, _ in res.values()), {k: d for k, (ok, d) in res.items() if not ok}


def test_lever_higher_initial_ai_share_brings_automation_earlier():
    """Automation is further along in a fixed year (2029, index 4) the higher the initial AI share. (A first version compared the
    year f reaches 50%; at annual resolution all three runs cross in the same year, so the test was too coarse; fixed 2026-10-12.)"""
    params = SETTINGS_B["B0_default"][1]
    f4 = [run_s3_rule(params, R3Rule(R3Levers(initial_ai_share=v)))["frac_automated"][4] for v in (0.05, 0.12, None, 0.35, 0.6)]
    assert all(a < b for a, b in zip(f4, f4[1:])), f4


def test_lever_zero_ai_share_stops_automation_progress():
    params = SETTINGS_B["B0_default"][1]
    s = run_s3_rule(params, R3Rule(R3Levers(initial_ai_share=0.0)))
    assert s["frac_automated"].max() < 0.5
