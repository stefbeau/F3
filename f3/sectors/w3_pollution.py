"""F3 sector: World3 persistent pollution (M3), 1974 and 2004 parameter sets.

ATTRIBUTION
-----------
Port of the World3 persistent pollution sector as implemented in WorldDynamics.jl v1.0.0
(https://github.com/worlddynamics/WorldDynamics.jl, files ``src/World3/pollution/subsystems.jl`` (``persistent_pollution``
lines 46 to 94, ``persistent_pollution_dummy`` lines 36 to 44), ``parameters.jl``, ``initialisations.jl``, ``tables.jl``).
WorldDynamics.jl is Copyright (c) 2022 Emanuele Natale, Pierluigi Crescenzi, Paulo Bruno Serafim and contributors, MIT
licence; text in ``licenses/WorldDynamics.jl-MIT.txt``, attribution in ``NOTICE`` (D-012). The equations are those of World3
as published in Meadows et al., *Dynamics of Growth in a Finite World* (1974), Appendix A. "Line n" is the Appendix A line
number WorldDynamics.jl cites; ":n" is the line of ``src/World3/pollution/subsystems.jl``. No PyWorld3 code is used.
F3 code is Apache 2.0 (D-001).

WHAT IS PORTED
--------------
``persistent_pollution``, with the technology-control input ``ppgf22`` fixed at 1.0 as the full model does
(``World3.historicalrun`` composes ``persistent_pollution_dummy``, subsystems.jl line 40: ``ppgf22 ~ 1.0``). The stand-alone
stand-ins (``population``, ``non_renewable``, ``agriculture``, lines 4 to 34), ``pollution_damage`` (lines 96 to 115; in the
full model the corresponding ``lmp`` and ``lfdr`` are computed inside S1 and agriculture) and the adaptive technological control
cards (lines 117 to 147, not part of ``World3.historicalrun``) are NOT ported. Inputs by name (WorldDynamics.jl ``pp.pcrum``,
``pp.pop``, ``pp.aiph``, ``pp.al``): ``pcrum``, ``pop`` [persons], ``aiph`` [dollars/hectare-year], ``al`` [hectares].
Outputs: ``ppolx`` index of persistent pollution, ``ppgr`` generation rate, ``ppapr`` appearance rate, ``ppasr``
assimilation rate, ``ahl`` assimilation half-life.

STATES (4): ``ppapr1``, ``ppapr2``, ``ppapr3`` (the third-order delay of Line 141) and ``ppol`` (Line 142).

PARAMETER SETS (D-015): identical in the 1974 and 2004 sets.

START-UP AND SWITCHES
---------------------
Initial state: ``pollution/initialisations.jl``. ``ppol`` = 2.5e7 (Line 142.1). All three stages of the ``ppapr`` delay start
at ``pptd * ppgr0 / 3`` (Line 141), where ``ppgr0`` is computed from the sector's OWN 1900 tables (pcrum 0.17, population
1.6e9, aiph 6.6, al 9e8) and not from the coupled model's 1900 values. This is the reference's convention; it differs from
PyWorld3's (``Delay3`` starts at ``input * 3 / delay``), which is what the A3.3 diagnostic matches. Switches: ``clip(.., t,
pyear)`` in Lines 138 and 141.1 at ``pyear`` = 1975 with identical branches; ``switch(ppgf21, ppgf22, swat)`` (Line 138.2)
with ``swat`` = 0 gives ``ppgf22`` = 1 (same value as ``ppgf21``). Integration is split at 1975 (S1 rule). RK4, step 0.25 year
(D-003).
"""

from __future__ import annotations

from typing import Dict, Mapping

import numpy as np

from f3.sectors.w3_common import UNITS, W3Sector, clip, switch

# pollution/parameters.jl
PARAMS_1974: Dict[str, float] = {
    "pyear": 1975.0,             # Line 150.1
    "ppgf1": 1.0,                # Line 138.1  persistent pollution generation factor
    "ppgf21": 1.0,               # Line 138.2
    "frpm": 0.02,                # Line 139.1  fraction of resources as persistent material
    "imef": 0.1,                 # Line 139.2  industrial material emission factor
    "imti": 10.0,                # Line 139.3  industrial material toxicity index
    "fipm": 0.001,               # Line 140.1  fraction of inputs as persistent material
    "amti": 1.0,                 # Line 140.2  agricultural material toxicity index
    "pptd1": 20.0, "pptd2": 20.0,  # Line 141.1  persistent pollution transmission delay, years
    "ppol70": 1.36e8,            # Line 143.1  persistent pollution in 1970
    "ahl70": 1.5,                # Line 146  assimilation half-life in 1970, years
    "swat": 0.0,                 # Line 138.2  switch for technology
    "ppgf22": 1.0,               # persistent_pollution_dummy: ppgf22 ~ 1.0 (subsystems.jl:40)
}
PARAMS_2004: Dict[str, float] = dict(PARAMS_1974)

# pollution/initialisations.jl: derived from the sector's own 1900 tables (t0 = 1900)
_PCRUM0 = 17.0 * 1e-2
_POP0 = 16.0 * 1e8
_AIPH0 = 6.6
_AL0 = 9.0 * 1e8
PPOL0 = 2.5e7                                                                       # Line 142.1

TABLES_1974 = {
    "ahlm": ((1.0, 11.0, 21.0, 31.0, 41.0), (1.0, 1001.0)),                         # Line 145.1 / 145
}
TABLES_2004 = dict(TABLES_1974)

PARAMETER_SETS = {"1974": (PARAMS_1974, TABLES_1974), "2004": (PARAMS_2004, TABLES_2004)}
STATE_NAMES = ("ppapr1", "ppapr2", "ppapr3", "ppol")


class Pollution(W3Sector):
    name = "w3_pollution"
    STATE_NAMES = STATE_NAMES
    PARAMETER_SETS = PARAMETER_SETS
    INPUT_ORDER = ("pcrum", "pop", "aiph", "al")
    inputs = {k: UNITS[k] for k in INPUT_ORDER}
    outputs = {k: UNITS[k] for k in ("ppolx", "ppgr", "ppapr", "ppasr", "ahl")}

    def initial_state(self) -> np.ndarray:
        P = self.params
        ppgio = _PCRUM0 * _POP0 * P["frpm"] * P["imef"] * P["imti"]                 # initialisations.jl (ppgio)
        ppgao = _AIPH0 * _AL0 * P["fipm"] * P["amti"]                               # initialisations.jl (ppgao)
        ppgr = (ppgio + ppgao) * P["ppgf1"]                                         # initialisations.jl (ppgr)
        ppapr3 = P["pptd1"] * ppgr / 3.0                                            # pptd(1900) = pptd1; ppapr3 = pptd * ppgr / 3
        return np.array([ppapr3, ppapr3, ppapr3, PPOL0])                            # states: ppapr1, ppapr2, ppapr3, ppol

    def algebra(self, tsw: float, y: np.ndarray, inp: Mapping[str, float]) -> Dict[str, float]:
        P, T = self.params, self.tables
        ppapr1, ppapr2, ppapr3, ppol = y
        pcrum, pop, aiph, al = inp["pcrum"], inp["pop"], inp["aiph"], inp["al"]
        py = P["pyear"]
        ppgf2 = switch(P["ppgf21"], P["ppgf22"], P["swat"])                         # Line 138.2 (subsystems.jl:78)
        ppgf = clip(ppgf2, P["ppgf1"], tsw, py)                                     # Line 138 (:77)
        ppgio = pcrum * pop * P["frpm"] * P["imef"] * P["imti"]                     # Line 139 (:79)
        ppgao = aiph * al * P["fipm"] * P["amti"]                                   # Line 140 (:80)
        ppgr = (ppgio + ppgao) * ppgf                                               # Line 137 (:76)
        pptd = clip(P["pptd2"], P["pptd1"], tsw, py)                                # Line 141.1 (:85)
        ppapr = 3.0 * ppapr3 / pptd                                                 # Line 141 (:81)
        ppolx = ppol / P["ppol70"]                                                  # Line 143 (:87)
        ahlm = T["ahlm"](ppolx)                                                     # Line 145 (:89)
        ahl = P["ahl70"] * ahlm                                                     # Line 146 (:90)
        ppasr = ppol / (1.4 * ahl)                                                  # Line 144 (:88)
        return dict(ppgr=ppgr, pptd=pptd, ppapr=ppapr, ppolx=ppolx, ahl=ahl, ppasr=ppasr)

    def derivs(self, y: np.ndarray, a: Mapping[str, float]) -> np.ndarray:
        ppapr1, ppapr2, ppapr3, ppol = y
        pptd = a["pptd"]
        d = np.empty(4)
        d[0] = a["ppgr"] - 3.0 * ppapr1 / pptd                                      # Line 141 (:84)
        d[1] = 3.0 * (ppapr1 - ppapr2) / pptd                                       # Line 141 (:83)
        d[2] = 3.0 * ppapr2 / pptd - a["ppapr"]                                     # Line 141 (:82)
        d[3] = a["ppapr"] - a["ppasr"]                                              # Line 142 (:86)
        return d
