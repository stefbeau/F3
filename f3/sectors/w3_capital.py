"""F3 sector: World3 capital (industrial, service and job subsectors) (M3), 1974 and 2004 parameter sets.

ATTRIBUTION
-----------
Port of the World3 capital sector as implemented in WorldDynamics.jl v1.0.0
(https://github.com/worlddynamics/WorldDynamics.jl, files ``src/World3/capital/subsystems.jl`` (lines 38 to 124),
``parameters.jl``, ``initialisations.jl``, ``tables.jl``; ``src/World3/world3/scenarios.jl`` line 29 for the policy year).
WorldDynamics.jl is Copyright (c) 2022 Emanuele Natale, Pierluigi Crescenzi, Paulo Bruno Serafim and contributors, MIT
licence; text in ``licenses/WorldDynamics.jl-MIT.txt``, attribution in ``NOTICE`` (D-012). The equations are those of World3
as published in Meadows et al., *Dynamics of Growth in a Finite World* (1974), Appendix A. "Line n" is the Appendix A line
number WorldDynamics.jl cites; ":n" is the line of ``src/World3/capital/subsystems.jl`` (v1.0.0). No PyWorld3 code is used.
F3 code is Apache 2.0 (D-001).

WHAT IS PORTED
--------------
``industrial_subsector``, ``service_subsector`` and ``job_subsector``. The three stand-ins of the stand-alone capital run
(``population``, ``agriculture``, ``non_renewable``, subsystems.jl lines 4 to 36) are NOT ported: in the full model the
sector reads them from the others. Inputs by name: ``pop`` (WorldDynamics.jl ``is.pop``), ``p2``, ``p3`` (``js.p2``,
``js.p3``: population 15-44 and 45-64, persons), ``fcaor`` (``is.fcaor``, fraction of capital allocated to obtaining
resources, from non-renewable resources), ``fioaa`` (``is.fioaa``, fraction of industrial output allocated to agriculture),
``aiph`` and ``al`` (``js.aiph``, ``js.al``, agricultural inputs per hectare and arable land). Outputs: industrial output
``io``, per capita ``iopc``, service output ``so`` and per capita ``sopc``, capital utilisation fraction ``cuf``, jobs ``j``,
labour force ``lf``.

STATES (3): ``ic`` (Line 52), ``sc`` (67), ``lufd`` (82).

PARAMETER SETS (D-015): identical in the 1974 and 2004 sets (no differences in the capital sector).

START-UP AND SWITCHES
---------------------
Initial state: ``inits`` of ``capital/initialisations.jl`` (Lines 52.2, 67.2, 82). Switches: the ``clip(.., t, pyear)``
equations (Lines 51, 54, 58, 60 to 65, 69, 72) switch at ``pyear``; WorldDynamics.jl ``World3.historicalrun`` sets it to 1975
(scenarios.jl line 29; its stand-alone default 4000 is not used in the full model). ``fioac`` switches at ``iet`` = 4000
(Line 57), never inside the horizon. Both branches of every switch carry identical values, so the switches change nothing
numerically; they are kept and the integration is split at 1975 (S1 rule). RK4, step 0.25 year (D-003).
"""

from __future__ import annotations

from typing import Dict, Mapping

import numpy as np

from f3.sectors.w3_common import UNITS, W3Sector, clip

# capital/parameters.jl (pyear = 1975 as set by World3.historicalrun, world3/scenarios.jl:29)
PARAMS_1974: Dict[str, float] = {
    "pyear": 1975.0,                 # Line 150.1
    "icor1": 3.0, "icor2": 3.0,      # Lines 51.1, 51.2  industrial capital-output ratio
    "alic1": 14.0, "alic2": 14.0,    # Lines 54.1, 54.2  average life of industrial capital, years
    "iet": 4000.0,                   # Line 57.1  industrial equilibrium time
    "iopcd": 400.0,                  # Line 59.2  industrial output per capita desired
    "fioac1": 0.43, "fioac2": 0.43,  # Lines 58.1, 58.2  fraction of industrial output allocated to consumption
    "alsc1": 20.0, "alsc2": 20.0,    # Lines 69.1, 69.2  average life of service capital, years
    "scor1": 1.0, "scor2": 1.0,      # Lines 72.1, 72.2  service capital-output ratio
    "lfpf": 0.75,                    # Line 80.1  labour force participation fraction
    "lufdt": 2.0,                    # Line 82.1  labour utilisation fraction delay time, years
}
PARAMS_2004: Dict[str, float] = dict(PARAMS_1974)

INITS: Dict[str, float] = {"ic": 2.1e11, "sc": 1.44e11, "lufd": 1.0}      # Lines 52.2, 67.2, 82

# capital/tables.jl: (y values, x range)
TABLES_1974 = {
    "fioas2": ((0.3, 0.2, 0.1, 0.05, 0.0), (0.0, 2.0)),                                                    # Line 65.1 / 65
    "fioas1": ((0.3, 0.2, 0.1, 0.05, 0.0), (0.0, 2.0)),                                                    # Line 64.1 / 64
    "isopc1": ((40.0, 300.0, 640.0, 1000.0, 1220.0, 1450.0, 1650.0, 1800.0, 2000.0), (0.0, 1600.0)),       # Line 61.1 / 61
    "isopc2": ((40.0, 300.0, 640.0, 1000.0, 1220.0, 1450.0, 1650.0, 1800.0, 2000.0), (0.0, 1600.0)),       # Line 62.1 / 62
    "fioacv": ((0.3, 0.32, 0.34, 0.36, 0.38, 0.43, 0.73, 0.77, 0.81, 0.82, 0.83), (0.0, 2.0)),             # Line 59.1 / 59
    "cuf": ((1.0, 0.9, 0.7, 0.3, 0.1, 0.1), (1.0, 11.0)),                                                  # Line 83.2 / 83
    "jpicu": ((0.37, 0.18, 0.12, 0.09, 0.07, 0.06), (50.0, 800.0)),                                        # Line 75.1 / 75
    "jph": ((2.0, 0.5, 0.4, 0.3, 0.27, 0.24, 0.2, 0.2), (2.0, 30.0)),                                      # Line 79.1 / 79
    "jpscu": ((1.1, 0.6, 0.35, 0.2, 0.15, 0.15), (50.0, 800.0)),                                           # Line 77.1 / 77
}
TABLES_2004 = dict(TABLES_1974)

PARAMETER_SETS = {"1974": (PARAMS_1974, TABLES_1974), "2004": (PARAMS_2004, TABLES_2004)}
STATE_NAMES = ("ic", "sc", "lufd")


class Capital(W3Sector):
    name = "w3_capital"
    STATE_NAMES = STATE_NAMES
    PARAMETER_SETS = PARAMETER_SETS
    SWITCH_PARAMS = ("pyear", "iet")
    INPUT_ORDER = ("pop", "p2", "p3", "fcaor", "fioaa", "aiph", "al")
    inputs = {k: UNITS[k] for k in INPUT_ORDER}
    outputs = {k: UNITS[k] for k in ("io", "iopc", "so", "sopc", "cuf", "j", "lf")}

    def initial_state(self) -> np.ndarray:
        return np.array([INITS[n] for n in STATE_NAMES])

    def algebra(self, tsw: float, y: np.ndarray, inp: Mapping[str, float]) -> Dict[str, float]:
        P, T = self.params, self.tables
        ic, sc, lufd = y
        pop, p2, p3, fcaor, fioaa = inp["pop"], inp["p2"], inp["p3"], inp["fcaor"], inp["fioaa"]
        aiph, al = inp["aiph"], inp["al"]
        py = P["pyear"]
        # job subsector: capacity utilisation
        cuf = T["cuf"](lufd)                                                        # Line 83 (subsystems.jl:120)
        # industrial subsector
        icor = clip(P["icor2"], P["icor1"], tsw, py)                                # Line 51 (:56)
        io = ic * (1 - fcaor) * cuf / icor                                          # Line 50 (:55)
        iopc = io / pop                                                             # Line 49 (:54)
        alic = clip(P["alic2"], P["alic1"], tsw, py)                                # Line 54 (:59)
        icdr = ic / alic                                                            # Line 53 (:58)
        # service subsector
        isopc = clip(T["isopc2"](iopc), T["isopc1"](iopc), tsw, py)                 # Lines 60-62 (:82-84)
        scor = clip(P["scor2"], P["scor1"], tsw, py)                                # Line 72 (:94)
        so = sc * cuf / scor                                                        # Line 70 (:92)
        sopc = so / pop                                                             # Line 71 (:93)
        fioas = clip(T["fioas2"](sopc / isopc), T["fioas1"](sopc / isopc), tsw, py)  # Lines 63-65 (:85-87)
        scir = io * fioas                                                           # Line 66 (:88)
        alsc = clip(P["alsc2"], P["alsc1"], tsw, py)                                # Line 69 (:91)
        scdr = sc / alsc                                                            # Line 68 (:90)
        # allocation of industrial output
        fioacc = clip(P["fioac2"], P["fioac1"], tsw, py)                            # Line 58 (:63)
        fioacv = T["fioacv"](iopc / P["iopcd"])                                     # Line 59 (:64)
        fioac = clip(fioacv, fioacc, tsw, P["iet"])                                 # Line 57 (:62)
        fioai = 1 - fioaa - fioas - fioac                                           # Line 56 (:61)
        icir = io * fioai                                                           # Line 55 (:60)
        # jobs
        jpicu = T["jpicu"](iopc) * 1e-3                                             # Line 75 (:112)
        pjis = ic * jpicu                                                           # Line 74 (:111)
        jpscu = T["jpscu"](sopc) * 1e-3                                             # Line 77 (:114)
        pjss = sc * jpscu                                                           # Line 76 (:113)
        jph = T["jph"](aiph)                                                        # Line 79 (:116)
        pjas = jph * al                                                             # Line 78 (:115)
        j = pjis + pjas + pjss                                                      # Line 73 (:110)
        lf = (p2 + p3) * P["lfpf"]                                                  # Line 80 (:117)
        luf = j / lf                                                                # Line 81 (:118)
        return dict(cuf=cuf, io=io, iopc=iopc, icdr=icdr, icir=icir, so=so, sopc=sopc, scir=scir, scdr=scdr, j=j, lf=lf,
                    luf=luf, fioas=fioas, fioai=fioai)

    def derivs(self, y: np.ndarray, a: Mapping[str, float]) -> np.ndarray:
        d = np.empty(3)
        d[0] = a["icir"] - a["icdr"]                                                # Line 52 (:57)
        d[1] = a["scir"] - a["scdr"]                                                # Line 67 (:89)
        d[2] = (a["luf"] - y[2]) / self.params["lufdt"]                             # Line 82 (:119)
        return d
