"""S3 variant P, the playground's production block (D-062). Readings fixed in docs/s3-playground-composite.md before the code.

T1 needs the pinned playground bundle (D-026) and is skipped with a stated reason without it. T3 needs no reference data.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from tests import gate_reference as gr
from tests.s3_checks import SETTINGS_B, TOL, compare, run_s3

needs_bundle = pytest.mark.skipif(not gr.bundle_available(), reason=gr.skip_reason())


@needs_bundle
@pytest.mark.parametrize("setting", list(SETTINGS_B))
def test_t1_a13_criterion_variant_p(setting):
    """T1: the A1.3 criterion, unchanged, with composite="P". A failure is a result to record, not to tune away."""
    idx, params = SETTINGS_B[setting]
    runs = gr.load_runs()
    s3 = run_s3(replace(params, composite="P"), gr.investment_shares(runs[idx], 80))
    res = compare(s3, gr.field, runs[idx])
    failing = {k: v["first_index_over_tol"] for k, v in res.items() if v["in_criterion"] and not v["passes"]}
    assert not failing, f"P/{setting}: first index (year = 2025 + index) over {TOL:.0%} per quantity: {failing}"


def test_t3a_no_automation_gives_labour():
    from f3.sectors.s3_ai import playground_composite, playground_setting
    T, share = playground_composite(3.6e9, 0.1, 1e20, 5e25, playground_setting())
    assert T == pytest.approx(3.6e9, rel=1e-12)
    assert share == 0.0


@pytest.mark.parametrize("T_oom", [33.0, 36.5, 38.0, 41.0])
def test_t3b_tabulated_inverse_never_exceeds_exact(T_oom):
    from f3.sectors.s3_ai import LN10, _log_f_inverse, playground_setting, playground_training_oom
    p = playground_setting(T_oom=T_oom)
    i = np.linspace(p.f_init + 1e-6, 1.0, 2001)
    exact = _log_f_inverse(i, p) / LN10
    assert np.all(playground_training_oom(i, p) <= exact + 1e-9)


@pytest.mark.parametrize("f", [0.1, 0.3333, 0.5, 0.875, 1.0])
def test_t3c_composite_does_not_fall_when_compute_rises(f):
    from f3.sectors.s3_ai import playground_composite, playground_setting
    p = playground_setting()
    vals = [playground_composite(3.6e9, f, c, 1e30, p)[0] for c in np.logspace(24, 40, 33)]
    assert np.all(np.diff(vals) >= -1e-6 * np.array(vals[:-1]))


def test_t3d_default_composite_is_still_a():
    from f3.sectors.s3_ai import GateParams, playground_setting
    assert GateParams().composite == "A" and playground_setting().composite == "A"
