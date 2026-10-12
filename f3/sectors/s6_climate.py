"""S6 climate sector: FaIR 2.2.4 (Apache 2.0, unmodified, from PyPI) as a Sector of the coupling loop (M2 step 1).

Method and choices: ``docs/m2-step1-fair.md`` (written before this file). Rules:
* **D-021:** FaIR is re-run from its start (1750) every year; no state is carried between segments.
* **D-020 / D-022:** FaIR runs from its own history with prescribed emissions; the loop step is 0.25 year and this sector has
  ``period = 1.0``; the value published at ``t = Y`` is the time-bound value at 1 January of year Y (FaIR's temperature sits on time
  bounds), held between year boundaries.
* **Configuration:** the published fair-calibrate v1.4.1 constrained ensemble (841 members), used as published, with each member's own
  seeded internal variability; volcanic and solar forcing are scaled per member as in FaIR's example notebook. Nothing is changed.
* **Emissions are prescribed, not modelled:** every output of this sector depends on non-CO2 emissions and land-use CO2 that no F3
  sector produces. Any use of its results must carry the label "non-CO2 emissions are prescribed, not modelled" (D-021).
* The anomaly baseline is 1850-1900 (time bounds 1850 to 1901 with weights 0.5, 1, ..., 1, 0.5, as in the notebook).

Inputs in this step: none (all emissions prescribed). Outputs, published on 1 January: ``warming`` (K above 1850-1900, ensemble mean),
``warming_p05`` / ``warming_p95`` (5th and 95th percentile across members), ``co2_concentration`` (ppm, ensemble mean).

**VALIDATION STATUS: A2.1 FAILED** (ensemble-mean 2015-2024 warming 0.037 K below HadCRUT5's interval; see ``VALIDATION_STATUS`` below and
``audit/m2-fair-report.md``). Non-CO2 emissions are prescribed, not modelled. Scenario warming starts about 0.04 to 0.07 K below observed for the
current decade (D-030, Proposed).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from f3.core.sector import Context, Sector
from f3.data import fair_inputs as fi

GCB_EXTRACT = Path(__file__).resolve().parents[1] / "data" / "gcb2025_co2_2015_2024.csv"
GTC_TO_GTCO2 = 44.009 / 12.011            # molar masses of CO2 and C, as the GCB states 3.664
START_YEAR = 1750
WEIGHTS_51 = np.r_[0.5, np.ones(50), 0.5]  # time bounds 1850..1901


def gcb_co2(years=range(2015, 2025)) -> pd.DataFrame:
    """GCB 2025 CO2 in Gt CO2/yr: ``ffi`` (fossil, excluding carbonation) and ``afolu`` (land-use change)."""
    d = pd.read_csv(GCB_EXTRACT, comment="#").set_index("year")
    d = d.loc[list(years)]
    return pd.DataFrame({"ffi": d["fossil_GtC"] * GTC_TO_GTCO2, "afolu": d["land_use_change_GtC"] * GTC_TO_GTCO2})


@dataclass(frozen=True)
class ClimateSetup:
    n_members: int = 841                     # first n members of the published ensemble (all 841 by default)
    scenario: str = "medium-extension"       # prescribed non-CO2 species and all species from 2025 (D-021)
    gcb_from: Optional[int] = 2023           # CO2 FFI and AFOLU from GCB 2025 from this year (None: file only); 2015 for the sensitivity
    gcb_to: int = 2024
    co2_scale_after: Optional[int] = None    # test hook (S4): multiply CO2 emissions by ``co2_factor`` from this year
    co2_factor: float = 1.0


class _Inputs:
    """Reads and caches the pinned FaIR files."""

    def __init__(self):
        d = fi.cache_dir()
        for n in fi.FAIR_FILES:
            fi.check_fair_file(n)
        self.dir = d
        self.params = pd.read_csv(d / "calibrated_constrained_parameters_calibration1.4.1.csv", index_col=0)
        self.emissions = pd.read_csv(d / "extensions_1750-2500.csv")
        self.forcing = pd.read_csv(d / "volcanic_solar.csv")

    def emissions_for(self, setup: ClimateSetup) -> pd.DataFrame:
        e = self.emissions.copy()
        if setup.gcb_from is not None:
            g = gcb_co2(range(setup.gcb_from, setup.gcb_to + 1))
            for yr, row in g.iterrows():
                col = f"{yr}.5"
                for var, key in (("CO2 FFI", "ffi"), ("CO2 AFOLU", "afolu")):
                    e.loc[e["variable"] == var, col] = row[key]       # every scenario shares the history; set all
        if setup.co2_scale_after is not None:
            cols = [c for c in e.columns[4:] if float(c) >= setup.co2_scale_after]
            m = e["variable"].isin(["CO2 FFI", "CO2 AFOLU"])
            e.loc[m, cols] = e.loc[m, cols] * setup.co2_factor
        return e


_INPUTS: Optional[_Inputs] = None


def inputs() -> _Inputs:
    global _INPUTS
    if _INPUTS is None:
        _INPUTS = _Inputs()
    return _INPUTS


def run_fair(end_year: int, setup: ClimateSetup = ClimateSetup(), deterministic: bool = False, time_start: int = START_YEAR,
             initial: Optional[dict] = None, noise_from=None):
    """One FaIR run from ``time_start`` to ``end_year`` (time bounds) for the setup; returns the FAIR object.

    The defaults reproduce the D-021 run exactly (1750 start, the published seeded variability). The other arguments exist only for the
    D-021 measurement (``audit/t0/m2_d021_measure.py``, readings in ``docs/m2-d021-measurement.md``): ``deterministic`` switches internal
    variability off; ``initial`` starts a segment from a carried state (never used by the sector); ``noise_from`` copies the seeded noise
    rows of an exact run for the same dates, so that a segment sees the same realisation (through the array FaIR exposes, no code touched).
    """
    from fair import FAIR
    from fair.interface import fill, initialise
    from fair.io import read_properties

    inp = inputs()
    props_file = str(inp.dir / "species_configs_properties_calibration1.4.1.csv")
    cfg = inp.params.iloc[: setup.n_members]
    f = FAIR(ch4_method="Thornhill2021")
    f.define_time(time_start, end_year, 1)
    f.define_scenarios([setup.scenario])
    f.define_configs(cfg.index)
    species, properties = read_properties(filename=props_file)
    f.define_species(species, properties)
    f.allocate()
    em = inp.emissions_for(setup).query("scenario == @setup.scenario")
    if time_start > START_YEAR:
        keep = [c for c in em.columns[:4]] + [c for c in em.columns[4:] if time_start <= float(c) < end_year + 1]
        em = em[keep]
    f.fill_from_pandas(mode="emissions", df=em)
    fo = inp.forcing.query("Scenario == @setup.scenario")
    if time_start > START_YEAR:
        keep = list(fo.columns[:4]) + [c for c in fo.columns[4:] if time_start <= float(c) <= end_year + 1]
        fo = fo[keep]
    f.fill_from_pandas(mode="forcing", df=fo)
    fill(f.forcing, f.forcing.sel(specie="Volcanic") * cfg["forcing_scale[Volcanic]"].values.squeeze(), specie="Volcanic")
    fill(f.forcing, f.forcing.sel(specie="Solar") * cfg["forcing_scale[Solar]"].values.squeeze(), specie="Solar")
    f.fill_species_configs(props_file)
    f.override_defaults(str(inp.dir / "calibrated_constrained_parameters_calibration1.4.1.csv"))
    if deterministic:
        f.climate_configs["stochastic_run"][:] = False
    if initial is None:
        initialise(f.concentration, f.species_configs["baseline_concentration"])
        initialise(f.forcing, 0)
        initialise(f.temperature, 0)
        initialise(f.cumulative_emissions, 0)
        initialise(f.airborne_emissions, 0)
        initialise(f.ocean_heat_content_change, 0)
    else:
        initialise(f.concentration, initial["conc"])
        initialise(f.forcing, initial["forc"])
        initialise(f.temperature, initial["T"])
        initialise(f.cumulative_emissions, initial["cum"])
        initialise(f.airborne_emissions, initial["air"])
        initialise(f.ocean_heat_content_change, initial["ohc"])
        f.gas_partitions.values[:] = initial["gas"][None, ...] if f.gas_partitions.values.ndim == initial["gas"].ndim + 1 else initial["gas"]
    if noise_from is not None and not deterministic:
        # DIAGNOSTIC runtime override on this instance only (FaIR builds its noise array inside run(); the package code is not
        # modified): after FaIR builds its energy-balance matrices, replace the segment's noise rows with the exact run's rows for the
        # same dates, so that a segment sees the same realisation as the reference.
        ref_noise = noise_from.ebms["stochastic_d"].values
        i0 = int(np.where(np.asarray(noise_from.timebounds) == time_start)[0][0])
        n = len(f.timebounds)
        original = f._make_ebms

        def _make_ebms_with_matched_noise():
            original()
            f.ebms["stochastic_d"].values[:] = ref_noise[i0:i0 + n]

        f._make_ebms = _make_ebms_with_matched_noise
    f.run(progress=False)
    return f


def anomaly_on_bounds(f) -> np.ndarray:
    """Surface temperature (layer 0) on time bounds, shape (n_bounds, n_members), above the 1850-1900 mean (notebook method)."""
    T = f.temperature.sel(layer=0).values[:, 0, :]
    tb = np.asarray(f.timebounds)
    i0 = int(np.where(tb == 1850)[0][0])
    base = np.average(T[i0:i0 + 52], weights=WEIGHTS_51, axis=0)
    return T - base


VALIDATION_STATUS = (
    "A2.1 FAILED (audit/m2-fair-report.md): the ensemble-mean warming for 2015-2024 is 1.196 K above 1850-1900, 0.037 K below the lower "
    "edge of HadCRUT5's mean 95% interval (1.234 to 1.305 K); FaIR runs as published (fair-calibrate v1.4.1). Non-CO2 emissions are "
    "prescribed, not modelled (D-021). Scenario warming starts about 0.04 to 0.07 K below observed for the current decade (D-030, Proposed). "
    "Cost of the D-021 re-run rule with all 841 members: about 19 s per annual re-run."
)


class S6Climate(Sector):
    name = "s6_climate"
    period = 1.0
    inputs: Dict[str, str] = {}
    outputs = {"warming": "K", "warming_p05": "K", "warming_p95": "K", "co2_concentration": "ppm"}
    validation_status = VALIDATION_STATUS

    def __init__(self, setup: ClimateSetup = ClimateSetup(), name: Optional[str] = None):
        self.setup = setup
        if name is not None:
            self.name = name
        self._out: Dict[str, float] = {}
        self.runtime_seconds = []

    def reset(self, t0: float, t1: float, dt: float) -> None:
        if abs(t0 - round(t0)) > 1e-9:
            raise ValueError("S6 must start on 1 January (D-022)")
        self._year = int(round(t0))
        self._out = self._at(self._year)

    def _at(self, year: int) -> Dict[str, float]:
        """Re-run FaIR from 1750 to ``year`` and publish the values at the time bound ``year`` (D-021: nothing carried)."""
        import time
        t = time.time()
        f = run_fair(max(year, START_YEAR + 1), self.setup)
        self.runtime_seconds.append(time.time() - t)
        a = anomaly_on_bounds(f)
        i = int(np.where(np.asarray(f.timebounds) == year)[0][0])
        row = a[i]
        co2 = f.concentration.sel(specie="CO2").values[i, 0, :]
        return {"warming": float(row.mean()), "warming_p05": float(np.percentile(row, 5)), "warming_p95": float(np.percentile(row, 95)),
                "co2_concentration": float(co2.mean())}

    def current_outputs(self) -> Dict[str, float]:
        return dict(self._out)

    def advance(self, t: float, h: float, ctx: Context) -> None:
        if abs(h - 1.0) > 1e-9:
            raise ValueError("S6 advances one whole year at a time (annual coupling, D-021)")
        self._year = int(round(t)) + 1
        self._out = self._at(self._year)
