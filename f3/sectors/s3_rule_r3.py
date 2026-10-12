"""R3 investment rule for S3 (D-028): AI-race budget, default calibration = R1 curves fitted to the shipped GATE runs.

Method and every choice: ``docs/s3-investment-rule-r3.md`` (written before the fit and before A1.4). The rule only generates the six
shares from two state variables S3 already has: the automated fraction ``f`` and usable compute relative to the limit
``u = g(Q)/C_L``. The fitted curve tables are in ``r3_curves.json`` (curve parameters only; no series from the bundle).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

CURVES_PATH = Path(__file__).with_name("r3_curves.json")
AI = ("q_compute", "q_hardware_rnd", "q_software_rnd")
FITTED = ("q_compute", "q_hardware_rnd", "q_software_rnd", "q_capital", "q_training_compute")
F_KNOTS = (0.1, 0.3, 0.5, 0.7, 0.9)
LOGU_KNOTS = (-5.0, -4.0, -3.0, -2.0, -1.5, -1.0, -0.5, -0.2)
F_INIT = 0.1


def load_curves(path: Path = CURVES_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class R3Levers:
    """Scenario parameters. ``None``/defaults reproduce the fitted curves exactly."""

    initial_ai_share: float = None           # total of the three AI shares at f = f_init; None = fitted value
    decay_speed: float = 1.0                 # > 1: AI shares fall faster as automation proceeds
    split: Tuple[float, float, float] = (1.0, 1.0, 1.0)   # relative weights of compute, hardware R&D, software R&D
    capital_scale: float = 1.0
    training_scale: float = 1.0


class R3Rule:
    def __init__(self, levers: R3Levers = R3Levers(), curves: dict = None):
        self.levers = levers
        self.curves = curves or load_curves()
        self._fitted_initial = sum(self._curve_f(n, F_INIT) for n in AI)

    def _curve_f(self, share: str, f: float) -> float:
        return float(np.interp(f, F_KNOTS, self.curves["f_curves"][share]))

    def _curve_u(self, share: str, u: float) -> float:
        lu = math.log10(max(u, 1e-300))
        return float(np.interp(lu, LOGU_KNOTS, self.curves["u_curves"][share]))

    def fitted(self, share: str, f: float, u: float) -> float:
        """The R1 curve for one share at (f, u): f-curve below 0.9, blend to the u-curve over 0.9..1, u-curve at 1."""
        if f < 0.9:
            return self._curve_f(share, f)
        w = min(1.0, (f - 0.9) / 0.1) if f < 1.0 - 1e-9 else 1.0
        return (1.0 - w) * self._curve_f(share, 0.9) + w * self._curve_u(share, u)

    def shares(self, f: float, u: float) -> Dict[str, float]:
        lv = self.levers
        q = {n: self.fitted(n, f, u) for n in FITTED}
        total = sum(q[n] for n in AI)
        scale = 1.0
        if lv.initial_ai_share is not None and self._fitted_initial > 0:
            scale = lv.initial_ai_share / self._fitted_initial
        prog = min(1.0, max(0.0, (f - F_INIT) / (1.0 - F_INIT)))
        scale *= math.exp(-(lv.decay_speed - 1.0) * 3.0 * prog)
        w = np.array(lv.split, dtype=float)
        base = np.array([q[n] for n in AI])
        if w.sum() > 0 and total > 0:
            mixed = base * w
            base = mixed * (total / mixed.sum())
        base = np.maximum(base * scale, 0.0)
        for n, v in zip(AI, base):
            q[n] = float(v)
        q["q_capital"] = max(0.0, q["q_capital"] * lv.capital_scale)
        q["q_training_compute"] = min(1.0, max(0.0, q["q_training_compute"] * lv.training_scale))
        for n in FITTED:
            q[n] = max(0.0, q[n])
        s = sum(q[n] for n in FITTED[:4])
        if s > 1.0:
            for n in FITTED[:4]:
                q[n] /= s
            s = 1.0
        q["q_consumption"] = 1.0 - s
        return q
