"""Demo 0 step 1: record S6Climate once with ALL 841 members (D-021 option a: exact FaIR re-run each year, 2025-2100; about 30-34 minutes).
Prescribed emissions do not depend on any F3 lever, so this one recording is exact for every scenario of the grid (f3/sectors/slice_m2.py).
Run once, in the background: PYTHONPATH=. F3_FAIR_DATA=... python dashboard/demo0/record_climate.py <out.npz>"""
import sys, time
import numpy as np
from f3.sectors.s6_climate import ClimateSetup
from f3.sectors.slice_m2 import record_climate

t = time.time()
rec = record_climate(ClimateSetup(n_members=841))
np.savez(sys.argv[1], **rec)
print("done", time.time() - t, "s", {k: v.shape for k, v in rec.items()})
