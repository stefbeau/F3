"""M4 A4.4, written before the run: T2 re-tested on the PORTED labour-market sector, under the definition accepted in D-016
(employed = WF, working-age = WAP; WAP = A20PA, the recorded Earth4All.jl series because population is a replaced sector, D-023).
Criterion: WF <= WAP at every 0.5-year point of 1980-2100, both scenarios, port as it runs in the loop (Euler, internal sub-step 1/64,
loop step 0.25). Reported beside the reference's own figures (maximum WF/WAP 0.8144 TLTL, 0.8248 GL; WF above AVWO by at most 0.59%):
the maximum WF/WAP and the maximum excess of WF over AVWO of the port. The effect of S3's automation input is NOT testable before M6
(S3 is not coupled) and is recorded as such. The caveat of the D-016 outcome note stands: a different pair of variables could give a
different answer.
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.e4a_helpers import SCENARIOS, grid_index, reference, run_alone

REF_MAX = {"tltl": 0.8144, "gl": 0.8248}


@pytest.mark.parametrize("scen", SCENARIOS)
def test_a44_workforce_never_exceeds_working_age_population(scen):
    s, res = run_alone("labourmarket", scen, 0.25, "euler", None)
    ref = reference(scen)
    idx = grid_index(res.time, ref["time"])
    WF = res.series[("e4a_labourmarket", "WF")][idx]
    WAP = res.series[("e4a_labourmarket", "WAP")][idx]
    AVWO = res.series[("e4a_labourmarket", "AVWO")][idx]
    ratio = WF / WAP
    ref_ratio = ref["labourmarket.WF"] / ref["labourmarket.WAP"]
    excess = np.maximum(WF / AVWO - 1.0, 0.0)
    print(f"labour market {scen}: years with WF > WAP: {int(np.sum(WF > WAP))} of {len(WF)}; max WF/WAP port {ratio.max():.4f} "
          f"(reference fixture {ref_ratio.max():.4f}; audit figure {REF_MAX[scen]}); max excess of WF over AVWO {100 * excess.max():.3f}% (audit: up to 0.59%)")
    assert np.all(WF <= WAP)
    assert abs(ratio.max() - ref_ratio.max()) <= 0.02 * ref_ratio.max()
    assert abs(ref_ratio.max() - REF_MAX[scen]) < 5e-4
