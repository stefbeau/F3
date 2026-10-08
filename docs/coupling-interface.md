# F3 — Sector interface and coupling loop (M0, deliverable 1)

**Status:** implemented and tested in M0 of `docs/phase-2-plan.md`; the choices below are recorded as the Proposed decision **N3** in `DECISIONS.md` and are not final until the editor-in-chief approves N3. Code: `f3/core/` (`sector.py`, `model.py`, `replay.py`) and `f3/sectors/s1_sector.py`. Tests: `tests/test_s1_in_model.py`.

## What it is, in one screen

```python
class Sector:
    name: str
    inputs:  {input_name:  unit}      # what it reads
    outputs: {output_name: unit}      # what it publishes
    period:  float | None             # advance every `period` years (a multiple of the loop step); None = every step
    def reset(self, t0, t1, dt): ...            # initial state at t0
    def current_outputs(self) -> {name: value}  # outputs at the sector's current time
    def advance(self, t, h, ctx): ...           # integrate from t to t+h, reading inputs through ctx.input(name, t')

Model(sectors, couplings, t0, t1, dt=0.25).run() -> Results        # time, series[(sector, output)], inputs[(sector, input)]
Coupling(source_sector, source_output, target_sector, target_input)
Results.to_csv(folder)                                               # every exchanged series, with units in the header
```

A sector integrates itself inside `advance` (S1 uses RK4, exactly the step of `PopulationSector.run`); the loop only moves values between sectors.

## The coupling rules

1. **Fixed step 0.25 year** (D-003). `t1 - t0` must be a whole number of steps.
2. **Explicit coupling at step boundaries.** All sectors read the outputs published at the *start* of the step, held constant across the step. The order sectors are advanced in does not matter. This is first-order accurate in the loop step; a sector whose inputs change quickly inside a step (S1 against the recorded World3 series) would see a small difference from the stand-alone run, which is why the tests use a replay sector that answers at any time inside the step.
3. **Units are checked, not converted.** A coupling whose source and target units differ is refused at construction. A missing, doubly wired or misnamed input is refused too.
4. **Slow sectors.** A sector with `period = m·dt` (FaIR, annual, `m = 4`) is advanced every m-th step with `h = period`, sees the values at the start of its period (no averaging of fast inputs), and publishes its new outputs at the end of the period. Between publications its value is held. Requirement: the horizon is a whole number of periods.
5. **Everything exchanged is recorded**: each output at every step boundary, and the input values each sector saw at the start of every step. `Results.to_csv` writes them with units in the header: this is the Phase 1 test method (recorded inputs by name) built in.
6. **Switch times.** S1 splits its integration at its switch times (1940 for the health-service switch). The loop refuses a grid on which a switch time falls inside a step.
7. **Replay sector.** `ReplaySector` serves recorded series by name, interpolated linearly in time, and answers at any time inside a step. It is how every ported sector is tested alone against a reference.

## What S1, S3 and FaIR need, and where it is covered

| Need | Covered how |
|---|---|
| S1 reads food, services and industrial output per capita and the pollution index; publishes cohorts and total | `S1Population`: inputs `fpc`, `sopc`, `iopc`, `ppolx` with units as PyWorld3 documents them; outputs `p1`–`p4`, `pop` in persons |
| S3 and others read population, S1 reads income per person | Named couplings; units checked |
| FaIR advances annually, needs the whole emissions history | `period = 1.0`; it reads emissions at the start of the year. **How FaIR carries its state from year to year is not decided here** (see N2 and the FaIR note below) |
| Any series can be replaced by a recorded one | `ReplaySector` |
| Switching a coupling off (A2.4, A6.3) | Replace the source with a `ReplaySector` holding the stand-alone values, or leave the input at a constant: a coupling is data, not code |

## Measured

- A0.1: S1 inside the loop with the reference's recorded inputs equals stand-alone S1 on all 15 states, both parameter sets, with a worst relative difference of **0.0** (bitwise identical), against the criterion of 1e-9. The same holds for a restart in 1970 from the recorded 1970 state (D-019 mechanics).
- A0.2: `f3/sectors/s1_population.py` is unchanged since commit `cc9f791` (checked by `git diff` in a test; a deliberate edit makes the test fail, which was tried).
- All 28 tests pass (22 from Phase 1, 6 new).

## FaIR note (what is and is not known)

From the FaIR documentation (docs.fairmodel.net, "Introduction", read 2026-10-08): time is defined by `define_time(start, end, step)` and need not be integer years (a quarter-year step is shown); only emissions sit on `timepoints`, everything else on `timebounds`; a run is one `f.run()` call over the defined horizon; initial conditions can be set for concentration, forcing, temperature, airborne and cumulative emissions at the first timebound. **The documentation page read does not describe running in segments or restarting from a previous run's final state.** A search found no documented restart workflow; carrying the last-timebound state of the previous segment into the initial conditions of the next is a plausible method (an inference, not confirmed). It was **not tried**. This is the M2 risk the plan names, and N2's research covers it. The interface does not depend on the answer: FaIR is an annual sector whose `advance` can call whatever method works.

## Not in this interface (left out on purpose, with what would add it)

- **Algebraic outputs available at the start of a step** (S1's life expectancy, births, deaths): they depend on the same step's inputs, so under start-of-step coupling they would be a step late. Add by publishing them at the end of `advance` with the end-of-step inputs, if a sector needs them.
- **Iteration within a step** (implicit coupling, to remove the first-order coupling error): not needed until a test shows the loop step matters (A2.6 tests it). Adding it means calling `advance` twice per step with updated inputs, on a copy of the state.
- **Different steps per sector below the loop step** (sub-stepping): a sector can sub-step inside its own `advance`; the loop does not.
- **Automatic unit conversion**, **vector-valued outputs** (regions are a later phase), **events and discrete policy switches** other than a sector's own, **parallel advance**, **state save and restore** (needed for Monte Carlo restarts and implicit coupling): none of S1, S3 or FaIR needs them in Phase 2.
- **Error handling for NaN or negative stocks**: tested per sector, not in the loop (A2.5, A6.4 are written for the sectors).
