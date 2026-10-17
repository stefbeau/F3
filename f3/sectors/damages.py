"""Damage function with three switchable level-of-output options (D-007, approved 2026-10-12; track A, Provisional P-A3).

``damage_fraction(T, option)`` = Omega(T) = c * T^2, the share of output lost at warming ``T`` (K above 1850-1900, FaIR, NO offset, as
D-007's appended text says). Level-of-output effects only: the growth-effect case (Burke, Hsiang and Miguel 2015) is NOT represented, and
the "high" option is NOT the upper end of the literature (growth-effect estimates are larger and are not offered).

Coefficients (research/damage-functions-verified.md; [read] = printed, [derived] = computed from printed numbers):
  low     Nordhaus (2017) DICE-2016R:            c = 0.236 %/K^2 [read]; 2.1 % at 3 K [read]
  central Barrage and Nordhaus (2024) DICE-2023: c = 0.344 %/K^2 [derived from the printed anchors 3.1 % at 3 K and 7.0 % at 4.5 K;
          psi1, psi2 themselves not obtained]
  high    Howard and Sterner (2017), catastrophic term included: c = 0.595*1.25 + 0.260 = 1.00375 %/K^2 [derived from read
          coefficients]; 9.03 % at 3 K
"off" gives zero damage (used by the invariance test). Validity: DICE-2023 is stated valid to about 4 K; beyond it is extrapolation.
"""

from __future__ import annotations

OPTIONS = {
    "low": 0.236e-2,
    "central": 0.344e-2,
    "high": (0.595 * 1.25 + 0.260) * 1e-2,
    "off": 0.0,
}
DEFAULT_OPTION = "central"
SOURCES = {
    "low": "Nordhaus (2017), PNAS 114, 1518 (DICE-2016R): 0.236 % of output per K^2",
    "central": "Barrage and Nordhaus (2024), PNAS 121, e2312030121 (DICE-2023): 0.344 % per K^2, derived from the printed anchors",
    "high": "Howard and Sterner (2017), Environ. Resour. Econ. 68, 197, regression (4) with catastrophic term: (0.595 x 1.25 + 0.260) % per K^2",
}
LABEL_HIGH = ("high damage option: the highest of three level-effect functions; growth-effect estimates in the literature are larger "
              "and are not offered")


def check_option(option: str) -> None:
    if option not in OPTIONS:
        raise ValueError(f"unknown damage option {option!r}; choose one of {sorted(OPTIONS)}")


def damage_fraction(warming: float, option: str = DEFAULT_OPTION) -> float:
    """Share of output lost, in [0, 1): c * T^2 with T = max(warming, 0) in K above 1850-1900."""
    check_option(option)
    t = max(float(warming), 0.0)
    return min(OPTIONS[option] * t * t, 0.99)
