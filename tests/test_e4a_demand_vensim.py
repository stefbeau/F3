"""M4 A4.3, written before the figures were read: the demand component comparison with Vensim, through the package's own mechanism
(Earth4All.jl `read_vensim_dataset`, D-014), per variable, TRUE relative error |julia - vensim| / |vensim|, median and 95th percentile
(and maximum and year of maximum), both scenarios. The figures are Earth4All.jl against Vensim and are stored as names and figures only
(`audit/data/e4a_vs_vensim_<scen>.csv`, exported by audit/t0/earth4all_m4_export.jl). D-004 (2%) is not relaxed: a variable whose 95th
percentile or maximum is above 2% is LISTED as a deviation; this test does not assert that Earth4All.jl is within 2% of Vensim (it is
known not to be, D-018) and never states that the port reproduces Vensim. It asserts completeness: every variable of the demand port
(states and algebraic) has a compared figure, or is identically zero in Vensim (excluded and listed).
"""

from __future__ import annotations

import pytest

from f3.sectors.e4a_demand import DemandSector
from tests.e4a_helpers import SCENARIOS, vensim_error


@pytest.mark.parametrize("scen", SCENARIOS)
def test_a43_every_demand_variable_has_a_compared_figure(scen):
    ve = vensim_error(scen)
    names = sorted(set(DemandSector.EQ) | set(DemandSector.STATE_NAMES))
    missing = [n for n in names if ("demand", n) not in ve]
    assert not missing, f"no Vensim comparison for {missing}"
    rows = [ve[("demand", n)] for n in names]
    zero = [r["variable"] for r in rows if r["all_zero"] == "true"]
    live = [r for r in rows if r["all_zero"] != "true"]
    above = sorted(((float(r["p95"]), float(r["maximum"]), r["variable"], r["year_of_max"]) for r in live
                    if float(r["p95"]) > 0.02 or float(r["maximum"]) > 0.02), reverse=True)
    meds = sorted(float(r["median"]) for r in live)
    print(f"demand {scen}: {len(live)} variables compared ({len(zero)} identically zero in Vensim: {zero}); "
          f"median of per-variable medians {100 * meds[len(meds) // 2]:.3f}%")
    print(f"demand {scen}: {len(above)} variables with p95 or maximum above 2% (Earth4All.jl against Vensim): " +
          "; ".join(f"{v} p95 {100 * p:.2f}% max {100 * m:.2f}% in {float(y):.1f}" for p, m, v, y in above))
    assert len(live) + len(zero) == len(names)
