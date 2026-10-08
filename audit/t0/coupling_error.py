"""M0 evidence for decision N3: the first-order error of start-of-step (explicit) coupling in the loop.

S1 is run inside the loop with the reference's recorded inputs, in two ways: the recorded series answers at any time inside a
step (``exact``, the Phase 1 test method) and the recorded series is only read at the start of each step and held (``held``,
what a sector coupled to a non-recorded partner would see). The difference is the coupling error of the loop for S1 and these
inputs. Run: ``uv run python audit/t0/coupling_error.py``.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from f3.core import Coupling, Model, ReplaySector  # noqa: E402
from f3.sectors.s1_population import STATE_NAMES  # noqa: E402
from f3.sectors.s1_sector import S1Population  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


class HeldReplay(ReplaySector):
    """Same recorded series, but only available at the start of each step (explicit coupling)."""
    exact_in_time = False


def load(p):
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def run(ps, cls, dt):
    inp = load(FIX / f"s1_inputs_world3_{ps}.csv")
    series = {"fpc": inp["dr₊fpc"], "sopc": inp["br₊sopc"], "iopc": inp["dr₊iopc"], "ppolx": inp["dr₊ppolx"]}
    rep = cls("recorded", inp["time"], series, S1Population.inputs)
    s1 = S1Population(ps)
    Model([rep, s1], [Coupling("recorded", n, "s1_population", n) for n in series], 1900.0, 2100.0, dt).run()
    return s1.time_history, s1.states()


out = ["# Coupling error of start-of-step coupling, S1 with recorded inputs (relative difference held vs exact)", ""]
out.append("| set | loop step | worst over 15 states | state | year | worst for total population |")
out.append("|---|---|---|---|---|---|")
for ps in ("1974", "2004"):
    for dt in (0.5, 0.25, 0.125, 0.0625):
        t_e, y_e = run(ps, ReplaySector, dt)
        t_h, y_h = run(ps, HeldReplay, dt)
        worst, wn, wt = 0.0, "", 0.0
        for n in STATE_NAMES:
            e = np.abs(y_h[n] - y_e[n]) / np.maximum(np.abs(y_e[n]), 1e-30)
            i = int(e.argmax())
            if e[i] > worst:
                worst, wn, wt = float(e[i]), n, float(t_e[i])
        pop_e = sum(y_e[k] for k in ("p1", "p2", "p3", "p4"))
        pop_h = sum(y_h[k] for k in ("p1", "p2", "p3", "p4"))
        pw = float((np.abs(pop_h - pop_e) / pop_e).max())
        out.append(f"| {ps} | {dt} | {100 * worst:.4f}% | {wn} | {wt:.2f} | {100 * pw:.4f}% |")
print("\n".join(out))
