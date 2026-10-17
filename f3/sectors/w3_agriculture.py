"""F3 sector: World3 agriculture (M3), 1974 and 2004 parameter sets.

ATTRIBUTION
-----------
Port of the World3 agriculture sector as implemented in WorldDynamics.jl v1.0.0
(https://github.com/worlddynamics/WorldDynamics.jl, files ``src/World3/agriculture/subsystems.jl``, ``parameters.jl``,
``initialisations.jl``, ``tables.jl``; ``src/World3_91/world3_91/scenarios.jl`` for the 2004 parameter set).
WorldDynamics.jl is Copyright (c) 2022 Emanuele Natale, Pierluigi Crescenzi, Paulo Bruno Serafim and contributors,
MIT licence; text in ``licenses/WorldDynamics.jl-MIT.txt``, attribution in ``NOTICE`` (D-012). The equations are those of
World3 as published in Meadows et al., *Dynamics of Growth in a Finite World* (1974), Appendix A. "Line n" is the line
number of Appendix A that WorldDynamics.jl cites for the equation; "subsystems.jl:n" is the line of the Julia source
(v1.0.0, ``src/World3/agriculture/subsystems.jl``). No PyWorld3 code is used (CeCILL; F3 uses it unmodified as a second check).
F3 code is Apache 2.0 (D-001).

WHAT IS PORTED
--------------
The seven subsystems of ``Agriculture.historicalrun`` that are part of the full model: land development, agricultural
inputs, investment allocation decision, land erosion and urban-industrial use, land fertility degradation and
regeneration, discontinuing land maintenance. The three exogenous stand-ins of the stand-alone agriculture run
(``population``, ``industrial_output``, ``persistent_pollution``, subsystems.jl lines 4 to 50) are NOT ported: in the full
model the sector reads them from the others. Inputs by name (WorldDynamics.jl ``ld.pop``, ``ld.io``, ``ld.iopc``,
``lfd.ppolx``): ``pop`` persons, ``io`` industrial output [dollars/year], ``iopc`` [dollars/person-year], ``ppolx`` [1].
Outputs: ``fpc`` food per capita, ``f`` food, ``fioaa`` fraction of industrial output allocated to agriculture,
``aiph`` agricultural inputs per hectare, ``al`` arable land, ``ly`` land yield.

STATES (6): ``al`` (Line 85), ``pal`` (86), ``ai`` (99), ``uil`` (120), ``lfert`` (121), ``pfr`` (128).

PARAMETER SETS (D-015): the 2004 set differs by ``alln`` (6000 -> 1000, World3_91 scenarios.jl) and the ``lymc`` table.

START-UP AND SWITCHES
---------------------
Initial state: the ``inits`` of ``agriculture/initialisations.jl`` (Lines 85.2, 86.2, 99.1, 120.2, 121.2, 128.1); the
reference's own initial state, identical in both sets. Switches: the ``clip(.., t, pyear)`` equations (Lines 89, 93, 100,
104, 105, 113) switch at ``pyear`` = 1975; both branches carry identical parameters and tables, so the switch changes
nothing numerically, but it is implemented and the integration is split there (S1 rule). RK4, step 0.25 year (D-003).
"""

from __future__ import annotations

from typing import Dict, Mapping

import numpy as np

from f3.sectors.w3_common import UNITS, W3Sector, clip

# agriculture/parameters.jl
PARAMS_1974: Dict[str, float] = {
    "palt": 3.2e9,   # Line 84.1  potentially arable land total, hectares
    "lfh": 0.7,      # Line 87.1  land fraction harvested
    "pl": 0.1,       # Line 87.2  processing loss
    "alai1": 2.0, "alai2": 2.0,   # Lines 100.1, 100.2  agricultural inputs delay (years)
    "lyf1": 1.0, "lyf2": 1.0,     # Lines 104.1, 104.2  land yield factor
    "io70": 7.9e11,  # Line 107.2  industrial output in 1970
    "sd": 0.07,      # Line 109.1  social discount
    "alln": 6000.0,  # Line 112.1  average life of land normal, years
    "uildt": 10.0,   # Line 119.1  urban-industrial land development time, years
    "ilf": 600.0,    # Line 124.1  inherent land fertility
    "sfpc": 230.0,   # Line 127.1  subsistence food per capita
    "fspd": 2.0,     # Line 128.2  food shortage perception delay, years
    "pyear": 1975.0,  # Line 150.1  policy year
}
PARAMS_2004: Dict[str, float] = {**PARAMS_1974, "alln": 1000.0}      # World3_91 scenario1: agriculture_params[:alln] = 1000

# agriculture/initialisations.jl
INITS: Dict[str, float] = {"al": 0.9e9, "pal": 2.3e9, "ai": 5e9, "uil": 8.2e6, "lfert": 600.0, "pfr": 1.0}

# agriculture/tables.jl: (y values, x range)
_LYMC_1974 = ((1.0, 3.0, 3.8, 4.4, 4.9, 5.4, 5.7, 6.0, 6.3, 6.6, 6.9, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2,
               9.4, 9.6, 9.8, 10.0), (0.0, 1000.0))
TABLES_1974 = {
    "ifpc1": ((230.0, 480.0, 690.0, 850.0, 970.0, 1070.0, 1150.0, 1210.0, 1250.0), (0.0, 1600.0)),          # Line 90.1 / 90
    "ifpc2": ((230.0, 480.0, 690.0, 850.0, 970.0, 1070.0, 1150.0, 1210.0, 1250.0), (0.0, 1600.0)),          # Line 91.1 / 91
    "fioaa1": ((0.4, 0.2, 0.1, 0.025, 0.0, 0.0), (0.0, 2.5)),                                               # Line 94.1 / 94
    "fioaa2": ((0.4, 0.2, 0.1, 0.025, 0.0, 0.0), (0.0, 2.5)),                                               # Line 95.1 / 95
    "dcph": ((100000.0, 7400.0, 5200.0, 3500.0, 2400.0, 1500.0, 750.0, 300.0, 150.0, 75.0, 50.0), (0.0, 1.0)),  # Line 97.1 / 97
    "lymc": _LYMC_1974,                                                                                     # Line 102.1 / 102
    "lymap1": ((1.0, 1.0, 0.7, 0.4), (0.0, 30.0)),                                                          # Line 106.1 / 106
    "lymap2": ((1.0, 1.0, 0.7, 0.4), (0.0, 30.0)),                                                          # Line 107.1 / 107
    "fiald": ((0.0, 0.05, 0.15, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0), (0.0, 2.0)),                               # Line 108.1 / 108
    "mlymc": ((0.075, 0.03, 0.015, 0.011, 0.009, 0.008, 0.007, 0.006, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005,
               0.005), (0.0, 600.0)),                                                                       # Line 111.1 / 111
    "llmy1": ((1.2, 1.0, 0.63, 0.36, 0.16, 0.055, 0.04, 0.025, 0.015, 0.01), (0.0, 9.0)),                    # Line 114.1 / 114
    "llmy2": ((1.2, 1.0, 0.63, 0.36, 0.16, 0.055, 0.04, 0.025, 0.015, 0.01), (0.0, 9.0)),                    # Line 115.1 / 115
    "uilpc": ((0.005, 0.008, 0.015, 0.025, 0.04, 0.055, 0.07, 0.08, 0.09), (0.0, 1600.0)),                   # Line 117.1 / 117
    "lfdr": ((0.0, 0.1, 0.3, 0.5), (0.0, 30.0)),                                                             # Line 122.1 / 122
    "lfrt": ((20.0, 13.0, 8.0, 4.0, 2.0, 2.0), (0.0, 0.1)),                                                  # Line 125.1 / 125
    "falm": ((0.0, 0.04, 0.07, 0.09, 0.1), (0.0, 4.0)),                                                      # Line 126.1 / 126
}
# World3_91 scenario1 (scenarios.jl, agriculture_tables[:lymc])
_LYMC_2004 = ((1.0, 3.0, 4.5, 5.0, 5.3, 5.6, 5.9, 6.1, 6.35, 6.6, 6.9, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0,
               9.2, 9.4, 9.6, 9.8, 10.0), (0.0, 1000.0))
TABLES_2004 = {**TABLES_1974, "lymc": _LYMC_2004}

PARAMETER_SETS = {"1974": (PARAMS_1974, TABLES_1974), "2004": (PARAMS_2004, TABLES_2004)}
STATE_NAMES = ("al", "pal", "ai", "uil", "lfert", "pfr")


class Agriculture(W3Sector):
    name = "w3_agriculture"
    STATE_NAMES = STATE_NAMES
    PARAMETER_SETS = PARAMETER_SETS
    INPUT_ORDER = ("pop", "io", "iopc", "ppolx")
    inputs = {k: UNITS[k] for k in INPUT_ORDER}
    outputs = {k: UNITS[k] for k in ("fpc", "f", "fioaa", "aiph", "al", "ly")}

    def initial_state(self) -> np.ndarray:
        return np.array([INITS[n] for n in STATE_NAMES])

    def algebra(self, tsw: float, y: np.ndarray, inp: Mapping[str, float]) -> Dict[str, float]:
        P, T = self.params, self.tables
        al, pal, ai, uil, lfert, pfr = y
        pop, io, iopc, ppolx = inp["pop"], inp["io"], inp["iopc"], inp["ppolx"]
        py = P["pyear"]
        # discontinuing land maintenance
        falm = T["falm"](pfr)                                                         # Line 126 (subsystems.jl:191)
        # agricultural inputs
        aiph = ai * (1 - falm) / al                                                   # Line 101 (:101)
        lymc = T["lymc"](aiph)                                                        # Line 102 (:102)
        lymap = clip(T["lymap2"](io / P["io70"]), T["lymap1"](io / P["io70"]), tsw, py)   # Lines 105-107 (:105-107)
        lyf = clip(P["lyf2"], P["lyf1"], tsw, py)                                     # Line 104 (:104)
        ly = lyf * lfert * lymc * lymap                                               # Line 103 (:103)
        alai = clip(P["alai2"], P["alai1"], tsw, py)                                  # Line 100 (:100)
        # land development
        lfc = al / P["palt"]                                                          # Line 84 (:66)
        f = ly * al * P["lfh"] * (1 - P["pl"])                                        # Line 87 (:69)
        fpc = f / pop                                                                 # Line 88 (:70)
        ifpc = clip(T["ifpc2"](iopc), T["ifpc1"](iopc), tsw, py)                      # Lines 89-91 (:71-73)
        fioaa = clip(T["fioaa2"](fpc / ifpc), T["fioaa1"](fpc / ifpc), tsw, py)       # Lines 93-95 (:75-77)
        tai = io * fioaa                                                              # Line 92 (:74)
        dcph = T["dcph"](pal / P["palt"])                                             # Line 97 (:79)
        # investment allocation decision
        mpld = ly / (dcph * P["sd"])                                                  # Line 109 (:121)
        mlymc = T["mlymc"](aiph)                                                      # Line 111 (:123)
        mpai = alai * ly * mlymc / lymc                                               # Line 110 (:122)
        fiald = T["fiald"](mpld / mpai)                                               # Line 108 (:120)
        ldr = tai * fiald / dcph                                                      # Line 96 (:78)
        cai = tai * (1 - fiald)                                                       # Line 98 (:98)
        # land erosion and urban-industrial use
        llmy = clip(T["llmy2"](ly / P["ilf"]), T["llmy1"](ly / P["ilf"]), tsw, py)    # Lines 113-115 (:141-143)
        all_ = P["alln"] * llmy                                                       # Line 112 (:140)
        ler = al / all_                                                               # Line 116 (:144)
        uilpc = T["uilpc"](iopc)                                                      # Line 117 (:145)
        uilr = uilpc * pop                                                            # Line 118 (:146)
        lrui = max(0.0, (uilr - uil) / P["uildt"])                                    # Line 119 (:147)
        # land fertility
        lfdr = T["lfdr"](ppolx)                                                       # Line 122 (:161)
        lfd = lfert * lfdr                                                            # Line 123 (:162)
        lfrt = T["lfrt"](falm)                                                        # Line 125 (:176)
        lfr = (P["ilf"] - lfert) / lfrt                                               # Line 124 (:175)
        fr = fpc / P["sfpc"]                                                          # Line 127 (:192)
        return dict(falm=falm, aiph=aiph, lymc=lymc, ly=ly, alai=alai, lfc=lfc, f=f, fpc=fpc, fioaa=fioaa, tai=tai,
                    dcph=dcph, fiald=fiald, ldr=ldr, cai=cai, ler=ler, lrui=lrui, lfd=lfd, lfr=lfr, fr=fr, al=al)

    def derivs(self, y: np.ndarray, a: Mapping[str, float]) -> np.ndarray:
        P = self.params
        al, pal, ai, uil, lfert, pfr = y
        d = np.empty(6)
        d[0] = a["ldr"] - a["ler"] - a["lrui"]                                        # Line 85 (:67)
        d[1] = -a["ldr"]                                                              # Line 86 (:68)
        d[2] = (a["cai"] - ai) / a["alai"]                                            # Line 99 (:99)
        d[3] = a["lrui"]                                                              # Line 120 (:148)
        d[4] = a["lfr"] - a["lfd"]                                                    # Line 121 (:160)
        d[5] = (a["fr"] - pfr) / P["fspd"]                                            # Line 128 (:193)
        return d
