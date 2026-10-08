# RESEARCH PROBE for decision D-021 (Phase 2, M0): can FaIR 2.2.4 be advanced in annual segments with its state carried over,
# and does that equal one run? NOT F3 code and NOT M2 work. Run in a scratch environment outside the F3 project, which does not
# depend on FaIR yet:  uv add fair==2.2.4 numpy pandas  (then: uv run python fair_segment_probe.py)
# Result (2026-10-08, toy CO2-only case, ILLUSTRATIVE climate parameters, not a calibrated configuration):
#   one run 2000-2020: T(2020) = 0.109351 K;  20 annual segments with state carried: 0.109797 K;  difference 4.457e-04 K (0.41%).
#   One run at other steps: 0.5 y: 0.109410 K, 0.25 y: 0.109435 K (the step effect inside one run is about 6e-05 K per halving).
#   So segmenting works mechanically but is NOT equivalent to one run with the state variables carried here; the cause is not found.
"""Research probe for decision N2 (M0): can FaIR 2.2.4 be advanced in segments, carrying state, and does that equal one run?
Toy case: one scenario, one config, CO2 only (FFI + AFOLU), a ramp of emissions. Not F3 code; not M2 work."""
import numpy as np
from fair import FAIR
from fair.interface import initialise

SPECIES = ["CO2 FFI", "CO2 AFOLU", "CO2"]
PROPS = {
    "CO2 FFI": {"type": "co2 ffi", "input_mode": "emissions", "greenhouse_gas": True, "aerosol_chemistry_from_emissions": False, "aerosol_chemistry_from_concentration": False},
    "CO2 AFOLU": {"type": "co2 afolu", "input_mode": "emissions", "greenhouse_gas": True, "aerosol_chemistry_from_emissions": False, "aerosol_chemistry_from_concentration": False},
    "CO2": {"type": "co2", "input_mode": "calculated", "greenhouse_gas": True, "aerosol_chemistry_from_emissions": False, "aerosol_chemistry_from_concentration": False},
}


def build(t0, t1, step=1.0):
    f = FAIR()
    f.define_time(t0, t1, step)
    f.define_scenarios(["s"])
    f.define_configs(["c"])
    f.define_species(SPECIES, PROPS)
    f.ghg_method = 'myhre1998'      # documented alternative that does not require CH4 and N2O
    f.allocate()
    f.fill_species_configs()
    # ILLUSTRATIVE climate parameters so the probe can run (a toy, NOT a calibrated config; values of the order of the
    # published three-layer defaults). The question tested is segmenting, not climate sensitivity.
    f.climate_configs['ocean_heat_capacity'][:] = [[8.0, 14.0, 100.0]]
    f.climate_configs['ocean_heat_transfer'][:] = [[1.0, 2.0, 0.8]]
    f.climate_configs['deep_ocean_efficacy'][:] = 1.1
    return f


def emissions(t):
    return 9.0 + 0.1 * (t - 2000.0), 1.0


def fill(f):
    ffi = np.array([emissions(tp)[0] for tp in f.timepoints])
    afo = np.array([emissions(tp)[1] for tp in f.timepoints])
    f.emissions.loc[dict(specie="CO2 FFI", scenario="s")] = ffi[:, None]
    f.emissions.loc[dict(specie="CO2 AFOLU", scenario="s")] = afo[:, None]


def cold(f):
    initialise(f.concentration, 278.3, specie="CO2")
    initialise(f.forcing, 0)
    initialise(f.temperature, 0)
    initialise(f.cumulative_emissions, 0)
    initialise(f.airborne_emissions, 0)
    initialise(f.ocean_heat_content_change, 0)


# --- one run, 2000 to 2020 ---
whole = build(2000, 2020)
fill(whole)
cold(whole)
whole.run()
T_whole = whole.temperature.loc[dict(scenario="s", layer=0)].values[:, 0]
print("one run: temperature at 2020 = %.6f K, CO2 concentration = %.4f ppm" % (T_whole[-1], whole.concentration.loc[dict(scenario="s", specie="CO2")].values[-1, 0]))

# --- 20 annual segments, state carried from the end of the previous segment ---
state = None
T_seg = [0.0]
for y in range(2000, 2020):
    f = build(y, y + 1)
    fill(f)
    if state is None:
        cold(f)
    else:
        for name in ("concentration", "forcing", "temperature", "cumulative_emissions", "airborne_emissions", "ocean_heat_content_change"):
            getattr(f, name)[0] = state[name]
        f.gas_partitions.data[...] = state["gas_partitions"]      # gas-box state: no time axis, holds the state at the end of the last run
    f.run()
    state = {n: getattr(f, n)[-1].copy() for n in ("concentration", "forcing", "temperature", "cumulative_emissions", "airborne_emissions", "ocean_heat_content_change")}
    state["gas_partitions"] = f.gas_partitions.data.copy()
    T_seg.append(float(f.temperature.loc[dict(scenario="s", layer=0)].values[-1, 0]))
print("20 segments: temperature at 2020 = %.6f K" % T_seg[-1])
print("difference at 2020: %.3e K" % (T_seg[-1] - T_whole[-1]))
print("largest difference over the 21 boundaries: %.3e K" % np.max(np.abs(np.array(T_seg) - T_whole)))
