"""S3 tests (M1 step 2). A1.3 against the shipped GATE runs (D-005 amendment B, D-026), A1.5 properties, finiteness.

The A1.3 tests read the playground bundle from a pinned local copy (see ``tests/gate_reference.py``): skipped with a stated
reason when the copy is absent, failing visibly if its hash changed. A1.3 asserts the approved criterion (+-2% at every period
end, indices 0 to 75) and is expected to FAIL where S3 differs from the reference: a failure is a result, not a defect to
tune away (see audit/s3-gate-comparison.md).
"""

from __future__ import annotations

import numpy as np
import pytest

from tests import gate_reference as gr
from tests.s3_checks import (COMPARED, SETTINGS_B, STRESS, TOL, a15_properties, compare, constant_shares, run_s3)

needs_bundle = pytest.mark.skipif(not gr.bundle_available(), reason=gr.skip_reason())


@needs_bundle
def test_bundle_hash_is_pinned():
    gr.check_hash()                                    # raises BundleChanged (a failure) if Epoch changed the file


@needs_bundle
@pytest.mark.xfail(strict=True, reason="A1.3 failed, see audit/s3-gate-comparison.md; production composite unresolved (D-027)")
@pytest.mark.parametrize("setting", list(SETTINGS_B))
def test_a13_criterion(setting):
    """A1.3: every criterion quantity within +-2% at every period end 2025-2100, GATE's own investment path as input."""
    idx, params = SETTINGS_B[setting]
    runs = gr.load_runs()
    s3 = run_s3(params, gr.investment_shares(runs[idx], 80))
    res = compare(s3, gr.field, runs[idx])
    failing = {k: v["first_index_over_tol"] for k, v in res.items() if v["in_criterion"] and not v["passes"]}
    assert not failing, f"{setting}: first index (year = 2025 + index) over {TOL:.0%} per quantity: {failing}"


@needs_bundle
@pytest.mark.parametrize("setting", list(SETTINGS_B))
def test_a15_properties_on_shipped_runs(setting):
    idx, params = SETTINGS_B[setting]
    runs = gr.load_runs()
    res = a15_properties(params, gr.investment_shares(runs[idx], 80))
    assert all(ok for ok, _ in res.values()), {k: d for k, (ok, d) in res.items() if not ok}


@needs_bundle
@pytest.mark.parametrize("name", list(STRESS))
def test_stress_settings_finite(name):
    """Report-only stress settings with a labelled PLACEHOLDER path (not a rule): finiteness and A1.5 properties only."""
    runs = gr.load_runs()
    first = {k: float(v[0]) for k, v in gr.investment_shares(runs[0], 80).items()}
    res = a15_properties(STRESS[name], constant_shares(first))
    assert all(ok for ok, _ in res.values()), {k: d for k, (ok, d) in res.items() if not ok}


def test_usable_compute_never_exceeds_cl():
    from f3.sectors.s3_ai import usable_compute
    for Q in (1e20, 1e30, 1e38, 2e38, 1e45, 1e300):
        assert usable_compute(Q, 2e38) <= 2e38
    assert usable_compute(1e30, 2e38) == pytest.approx(1e30, rel=1e-8)


def test_s3_in_loop_runs_without_bundle():
    """Needs no reference data: S3 with a constant labelled placeholder path stays finite for 75 years."""
    shares = {"q_consumption": 0.7, "q_compute": 0.1, "q_capital": 0.1, "q_hardware_rnd": 0.05, "q_software_rnd": 0.05,
              "q_training_compute": 0.5}
    from f3.sectors.s3_ai import playground_setting
    s3 = run_s3(playground_setting(), constant_shares(shares))
    assert all(np.all(np.isfinite(v)) for k, v in s3.items() if k not in ("training_compute", "labor_share"))
