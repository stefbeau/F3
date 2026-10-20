"""F3 sector: World3 non-renewable resources (M3), 1974 and 2004 parameter sets.

ATTRIBUTION
-----------
Port of the World3 non-renewable resources sector as implemented in WorldDynamics.jl v1.0.0
(https://github.com/worlddynamics/WorldDynamics.jl, files ``src/World3/nonrenewable/subsystems.jl`` (``non_renewable``,
lines 53 to 75), ``parameters.jl``, ``initialisations.jl``, ``tables.jl``; ``src/World3_91/world3_91/scenarios.jl`` for the
2004 table). WorldDynamics.jl is Copyright (c) 2022 Emanuele Natale, Pierluigi Crescenzi, Paulo Bruno Serafim and
contributors, MIT licence; text in ``licenses/WorldDynamics.jl-MIT.txt``, attribution in ``NOTICE`` (D-012). The equations
are those of World3 as published in Meadows et al., *Dynamics of Growth in a Finite World* (1974), Appendix A. "Line n" is
the Appendix A line number WorldDynamics.jl cites; ":n" is the line of ``src/World3/nonrenewable/subsystems.jl``. No
PyWorld3 code is used. F3 code is Apache 2.0 (D-001).

WHAT IS PORTED
--------------
``non_renewable`` only. The stand-alone run's ``population``, ``industrial_output`` and ``industrial_capital`` (lines 4 to
51) are NOT ported: the full model reads population and industrial output per capita from the other sectors. Inputs by name
(WorldDynamics.jl ``nr.pop``, ``nr.iopc``): ``pop`` [persons], ``iopc`` [dollars/person-year]. Outputs: ``fcaor`` fraction of
capital allocated to obtaining resources, ``pcrum`` per capita resource use multiplier, ``nrfr`` fraction of resources
remaining, ``nrur`` resource usage rate.

STATE (1): ``nr`` (Line 129).

PARAMETER SETS (D-015): the 2004 set differs by the ``pcrum`` table only (World3_91 scenarios.jl).

START-UP AND SWITCHES
---------------------
Initial state: ``nr`` = ``nri`` = 1e12 (Line 129.2), as in the reference. Switches: ``clip(.., t, pyear)`` in Lines 131, 134
at ``pyear`` = 1975; both branches carry identical values, so nothing changes numerically; integration is split there.
RK4, step 0.25 year (D-003).
"""

from __future__ import annotations

from typing import Dict, Mapping

import numpy as np

from f3.sectors.w3_common import UNITS, W3Sector, clip

# nonrenewable/parameters.jl
PARAMS_1974: Dict[str, float] = {
    "nri": 1e12,                  # Line 129.2  initial non-renewable resources, resource units
    "nruf1": 1.0, "nruf2": 1.0,   # Lines 131.1, 131.2  non-renewable resource usage factor
    "pyear": 1975.0,              # Line 150.1
}
PARAMS_2004: Dict[str, float] = dict(PARAMS_1974)

# nonrenewable/tables.jl
_FCAOR = ((1.0, 0.9, 0.7, 0.5, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05), (0.0, 1.0))
TABLES_1974 = {
    "pcrum": ((0.0, 0.85, 2.6, 4.4, 5.4, 6.2, 6.8, 7.0, 7.0), (0.0, 1600.0)),    # Line 132.1 / 132
    "fcaor1": _FCAOR,                                                            # Line 135.1 / 135
    "fcaor2": _FCAOR,                                                            # Line 136.1 / 136
}
# World3_91 scenario1: nonrenewable_tables[:pcrum]
TABLES_2004 = {**TABLES_1974, "pcrum": ((0.0, 0.85, 2.6, 3.4, 3.8, 4.1, 4.4, 4.7, 5.0), (0.0, 1600.0))}

PARAMETER_SETS = {"1974": (PARAMS_1974, TABLES_1974), "2004": (PARAMS_2004, TABLES_2004)}
STATE_NAMES = ("nr",)


class Resources(W3Sector):
    name = "w3_resources"
    STATE_NAMES = STATE_NAMES
    PARAMETER_SETS = PARAMETER_SETS
    INPUT_ORDER = ("pop", "iopc")
    inputs = {k: UNITS[k] for k in INPUT_ORDER}
    outputs = {k: UNITS[k] for k in ("fcaor", "pcrum", "nrfr", "nrur")}

    def initial_state(self) -> np.ndarray:
        return np.array([self.params["nri"]])

    def algebra(self, tsw: float, y: np.ndarray, inp: Mapping[str, float]) -> Dict[str, float]:
        P, T = self.params, self.tables
        nr = y[0]
        pop, iopc = inp["pop"], inp["iopc"]
        py = P["pyear"]
        nruf = clip(P["nruf2"], P["nruf1"], tsw, py)                                 # Line 131 (subsystems.jl:66)
        pcrum = T["pcrum"](iopc)                                                     # Line 132 (:67)
        nrur = pop * pcrum * nruf                                                    # Line 130 (:65)
        nrfr = nr / P["nri"]                                                         # Line 133 (:68)
        fcaor = clip(T["fcaor2"](nrfr), T["fcaor1"](nrfr), tsw, py)                  # Lines 134-136 (:69-71)
        return dict(nrur=nrur, pcrum=pcrum, nrfr=nrfr, fcaor=fcaor)

    def derivs(self, y: np.ndarray, a: Mapping[str, float]) -> np.ndarray:
        return np.array([-a["nrur"]])                                                # Line 129 (:64)
