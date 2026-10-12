# D-021 measurement: carrying state (b) and restarting every 10 years (c), against re-running from the start (a)

**Status:** readings fixed 2026-10-12, **before any run**. No accept or reject threshold is set here: the numbers go to the editor, who chooses among (a), (b), (c) (D-021). Not chosen by this note.

## 1. What is compared

Same FaIR 2.2.4, same published constrained ensemble (`docs/m2-step1-fair.md`), same emissions (default setup: scenario `medium-extension`, GCB 2025 CO2 for 2023 to 2024), same members, **time bounds 1980 to 2100**. Quantity: surface temperature anomaly on time bounds (1 January), 1850-1900 baseline taken from the exact run.

- **(a) Re-run from the start each year (D-021 as approved).** One run from 1750 to 2100 gives, at every time bound, exactly what a re-run from 1750 to that bound gives (checked: difference 0.0 K at the sector tests, S1). It is the reference.
- **(b) Carry state between annual segments.** The segment for year `Y` to `Y+1` is a separate FaIR run with `define_time(Y, Y+1, 1)`, initialised with the state at `Y` that the previous segment ended with. Chain start: **1980**, from (a)'s exact state at 1980 (a coupled run is reported from 1980; history before is prescribed). 120 segments.
- **(c) Restart every 10 years.** As (b), but at 1990, 2000, ..., 2090 the chain is reset to (a)'s exact state at that year (that is: one exact re-run from 1750 per decade, annual carried segments in between). 12 exact states, 108 carried segments.

**What "state" is carried** (everything FaIR's public interface lets a user set): temperature of the three layers (`initialise` on `temperature`), `cumulative_emissions`, `airborne_emissions`, `gas_partitions`, `ocean_heat_content_change`, concentration (`baseline_concentration` replaced by the carried concentration), and the forcing of the first bound. **What cannot be carried:** FaIR's run sets its internal state vector's forcing element to the sum of the forcing at the first bound; the **autocorrelated stochastic-forcing component** (Cummins et al.) at the start of a segment is therefore reset, not carried. This is a limitation of unmodified FaIR (no private attribute is touched; the package is used as published) and is **part of what is measured**.

**Noise handling (the point that would otherwise confound the test).** Each member's seeded internal variability is drawn per run, indexed from the first time step of that run. A naive segment would replay the first rows of the noise sequence at the wrong dates. **Primary reading: the segment's noise rows are set to the rows of (a)'s noise at the same dates** (the same realisation, set through the `ebms["stochastic_d"]` array FaIR exposes, not by changing any code), so the difference is due to state carrying and not to a different noise draw. **Second reading (deterministic): internal variability switched off for all three** (`stochastic_run` false), which isolates the state-carrying error from the stochastic-forcing reset.

## 2. What is reported (no threshold)

For each of (b) and (c), and each reading (stochastic with matched noise; deterministic):
- **Ensemble-mean error** `e(t) = mean over members of T_x(t) − T_a(t)`: maximum of `|e|` over 1980 to 2100, `e` at 2100, and the same for 2025 to 2100.
- **Per-member error** `d_m(t) = T_x,m(t) − T_a,m(t)`: maximum of `|d|` over all members and times; the median over members of the maximum over time; the 95th percentile over members of `|d|` at 2100.
- **As a share of the warming since 1850** (the ensemble-mean (a) anomaly above 1850-1900): `|e|` at 2100 divided by the ensemble-mean warming at 2100; `max |e(t)| / warming(t)` over 2000 to 2100 (before 2000 the warming is small enough that the ratio is not informative).
- **The realistic coupling window**, reported separately: chains started at **2025** instead of 1980 (emissions are prescribed history before 2025, so state carrying only matters from 2025): the same measures for 2025 to 2100.
- **Time cost** per annual segment and per full chain, for 20 and 841 members, on this machine.

## 3. Representativeness of a 20-member subset

**Rule, fixed now:** the subset is **every 42nd member in the ensemble's own ordering** (the order of the rows of `calibrated_constrained_parameters_calibration1.4.1.csv`): rows 0, 42, 84, ..., 798, which is 20 members. The rule uses no property of the members (nothing about their sensitivity or their results). Because each member's noise depends only on its own seed, the 20 members' trajectories are identical to their trajectories inside the full ensemble, so any difference is sampling, not noise.

Compared with the 841-member ensemble, years **2025 to 2100**, on the same scenario: the ensemble mean, and the 5th and 95th percentiles across members of the temperature anomaly; **absolute K** (subset minus full): maximum over 2025 to 2100 and the value at 2100, for each of the three. Also reported: the same comparison for 2015 to 2024 against the HadCRUT5 mean interval of A2.1 (does the 20-member mean fall inside it?).

## 4. Not done here

No choice among (a), (b), (c); no threshold; no change to FaIR; no other subset rules (a second rule would be a search). The representativeness result is for this scenario and this rule; it says nothing about other scenarios or other subsets.
