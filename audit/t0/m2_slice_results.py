"""Track A: sizes and first years of the failures in tests/test_m2_slice.py (report only; changes no test). Uses the 20-member development
climate subset. Run: PYTHONPATH=. F3_FAIR_DATA=... python audit/t0/m2_slice_results.py <out json>"""
import json, sys
import numpy as np
from f3.sectors.s3_rule_r3 import R3Levers, R3Rule
from f3.sectors.s4_datacentre import DCParams
from f3.sectors.s6_climate import ClimateSetup
from f3.sectors.slice_m2 import SliceConfig, climate_replay, record_climate, run_slice

rec = record_climate(ClimateSetup(n_members=20))
yr = lambda r: [i for i, t in enumerate(r.time) if abs(t - round(t)) < 1e-9]
S = lambda r, s, n: r.series[(s, n)]
out = {}
a = run_slice(SliceConfig(), climate_replay(rec), dt=0.25); b = run_slice(SliceConfig(), climate_replay(rec), dt=0.125)
ia, ib = yr(a), yr(b); years = a.time[ia]
for s, n in (("s3_ai", "gwp"), ("s3_ai", "compute_stock"), ("s3_ai", "frac_automated"), ("s4_datacentre", "e_dc"), ("s6_climate", "warming")):
    x, y = S(a, s, n)[ia], S(b, s, n)[ib]; rel = np.abs(x - y) / np.maximum(np.abs(x), 1e-300)
    bad = np.where(rel > 1e-3)[0]
    out["a26_" + n] = {"max_rel": float(rel.max()), "year_of_max": float(years[rel.argmax()]), "first_year_over_0.1%": float(years[bad[0]]) if len(bad) else None}
f0 = R3Rule()._fitted_initial
lo = run_slice(SliceConfig(levers=R3Levers(initial_ai_share=0.9 * f0)), climate_replay(rec)); hi = run_slice(SliceConfig(levers=R3Levers(initial_ai_share=1.1 * f0)), climate_replay(rec))
for n in ("compute_stock", "frac_automated"):
    d = S(hi, "s3_ai", n)[ia] - S(lo, "s3_ai", n)[ia]
    out["r1_" + n] = {"hi_minus_lo_at_2065": float(d[40]), "years_hi_not_above_lo": [float(y) for y in years[d <= 0]][:5], "first_year_equal_or_below": float(years[d <= 0][0]) if (d <= 0).any() else None,
                      "hi_greater_at_2035": bool(d[10] > 0), "hi_greater_at_2045": bool(d[20] > 0)}
base = a; low = run_slice(SliceConfig(dc=DCParams(supply_scale=0.5)), climate_replay(rec))
cb, cl = S(base, "s3_ai", "compute_stock")[ia], S(low, "s3_ai", "compute_stock")[ia]
over = np.where(cl > cb * (1 + 1e-12))[0]
out["b1_lower_supply_has_more_compute"] = {"years": [float(y) for y in years[over]], "max_ratio": float((cl / cb).max()), "year_max": float(years[(cl / cb).argmax()])}
gb, gl = np.diff(np.log(cb)), np.diff(np.log(cl))
out["b1_growth_2026_2040_mean_base_low"] = [float(gb[:15].mean()), float(gl[:15].mean())]
out["b1_first_year_ratio_below_1"] = {"base": float(years[np.where(S(base, "s4_datacentre", "supply_ratio")[ia] < 1)[0][0]]), "low": float(years[np.where(S(low, "s4_datacentre", "supply_ratio")[ia] < 1)[0][0]])}
out["b1_growth_next_5y_after_low_binds"] = None
k = int(np.where(S(low, "s4_datacentre", "supply_ratio")[ia] < 1)[0][0])
out["b1_growth_5y_after_low_binds_base_low"] = [float(gb[k:k + 5].mean()), float(gl[k:k + 5].mean())]
hd = run_slice(SliceConfig(damage="high"), climate_replay(rec)); ld = run_slice(SliceConfig(damage="low"), climate_replay(rec))
out["b2_gwp2100_low_high"] = [float(S(ld, "s3_ai", "gwp")[-1]), float(S(hd, "s3_ai", "gwp")[-1])]
out["e_dc_2025_demand"] = float(S(a, "s4_datacentre", "e_dc_demand")[0])
for y in (2030, 2040, 2050, 2100):
    i = ia[y - 2025]; out[f"e_dc_{y}"] = {"demand": float(S(a, "s4_datacentre", "e_dc_demand")[i]), "used": float(S(a, "s4_datacentre", "e_dc")[i]), "ratio": float(S(a, "s4_datacentre", "supply_ratio")[i])}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
