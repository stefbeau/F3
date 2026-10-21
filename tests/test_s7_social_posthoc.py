"""POST-HOC tests for S7, added AFTER the first run of tests/test_s7_social.py and its mutation check (audit/t0/s7_mutation_check.py).

Why they exist (recorded, not hidden): the mutation check found that three of the pre-registered tests do NOT isolate what they were written for.
 * The R2 sign test checks the END of the chain; zeroing the link inequality -> tension, or tension -> well-being, still passes because the effect
   reaches the same outputs through another path (inequality lowers well-being directly; well-being lowers the tension target).
 * The B5 'lag' assertion (b) compares the first year the response exceeds 0.05 with the first year tension exceeds the threshold. That gap exists
   even with NO delay at all (the response only reaches 0.05 once tension is 0.025 above the threshold), so assertion (b) does not test a delay.
The pre-registered tests are LEFT UNCHANGED. These two tests are additions: they test each link's sign at the equation level and the delay itself.
The numbers they use come from the first run and are therefore post-hoc (stated in each docstring); they are checks of the module's structure,
not acceptance criteria about the world, and nothing is calibrated.
"""
from __future__ import annotations

import numpy as np

from f3.sectors.s7_social import S7Social
from tests.test_s7_social import B5_KW, run


def _targets(**kw):
    s = S7Social()
    s._ls0 = 1.0
    base = dict(I=0.40, Te=0.30, W=0.60, P=0.0, ls=1.0, ue=0.0, warming=0.0, growth=0.0, red=0.0)
    base.update(kw)
    return dict(zip(("I", "Te", "W", "P"), s._targets(base["I"], base["Te"], base["W"], base["P"], base["ls"], base["ue"], base["warming"], base["growth"], base["red"])))


def test_link_signs():
    """Each link of the loops R2 and B5, at the level of the target equations, strictly in the intended direction (post-hoc, see module docstring)."""
    b = _targets()
    assert _targets(ls=0.7)["I"] > b["I"]                       # R2: falling labour share raises the inequality target
    assert _targets(I=0.50)["Te"] > b["Te"]                     # R2: inequality raises the tension target
    assert _targets(Te=0.40)["W"] < b["W"]                      # R2: tension lowers the well-being target
    assert _targets(I=0.50)["W"] < b["W"]                       # inequality lowers the well-being target
    assert _targets(W=0.70)["Te"] < b["Te"]                     # well-being lowers the tension target
    assert _targets(ue=0.2)["I"] > b["I"] and _targets(ue=0.2)["Te"] > b["Te"]
    assert _targets(warming=3.0)["Te"] > b["Te"] and _targets(warming=3.0)["W"] < b["W"]
    assert _targets(growth=0.03)["W"] > b["W"]
    assert _targets(red=0.5)["I"] < b["I"]                      # redistribution lowers the inequality target
    assert _targets(P=0.5)["I"] < b["I"]                        # B5: the policy response lowers it too
    assert _targets(Te=0.60)["P"] > _targets(Te=0.45)["P"] > 0.0 and _targets(Te=0.30)["P"] == 0.0     # B5: response only above the threshold


def test_policy_response_lags_its_own_target():
    """The delay of B5 itself (post-hoc): in the regime of the B5 test, the policy response stays measurably below the instantaneous target
    kP * max(tension - threshold, 0) at some time. First run: the largest gap is 0.135 with tau_P = 10 years and 0.011 with no delay; the bar
    0.05 sits between them and was chosen after seeing those two numbers (post-hoc, not a criterion about the world)."""
    th = S7Social.PARAMETERS["Te_threshold"]
    kP = S7Social.PARAMETERS["kP"]
    r = run(150, **B5_KW)
    target = np.clip(kP * np.maximum(r["tension"] - th, 0.0), 0.0, 1.0)
    assert float(np.max(target - r["policy_response"])) > 0.05
