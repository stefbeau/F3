# F3 — T0 findings (running log)

Factual record of what each T0 run showed. Updated after every run; nothing is deleted, only superseded.

## Run #3 (2026-10-05, F3 commit c4db929)

**Environment:** Julia 1.10.12 · WorldDynamics.jl v1.0.0 · Earth4All.jl `16f37d0` (branch `master`) · PyWorld3 1.1

### Confirmed
- **Earth4All.jl runs as published.** Both scenarios solve (7,681 time points, 106 variables each) and both figures regenerate. The figures show the Julia model's own run; they do not overlay Vensim output, so they show "runs and behaves plausibly", not "matches Vensim".
- **PyWorld3 runs unmodified.** Standard run 1900–2100; population peaks at 7.06 billion in 2027.
- **WorldDynamics.jl solves World3** with `World3.historicalrun()` + `WorldDynamics.solve(system, (1900, 2100))`.

### Problems found
1. **`World3.fig_7()` fails in WorldDynamics.jl v1.0.0** with `UndefVarError: solve not defined` (`plots.jl:6`, inside `historicalrunsolution()`). `WorldDynamics.solve` exists, but is not visible inside the World3 module. Making `solve` visible at run time (no package file or equation modified) makes the figure work. Candidate upstream issue.
2. **The T0.4 cross-check result in run #3 is INVALID.** It reported a 0.00% gap, but the WorldDynamics.jl export contained a single time point (1900), so only the shared starting value was compared. Cause: `DataFrame(solution)` does not return the time series for this solution type. Fixed for run #4: the export now builds the table from the solution's time and state vectors, and the comparison refuses to run on fewer than 50 time points.
3. **WorldDynamics.jl's own test suite errors out:** 5 of 5 tests errored (0 passed, 0 failed). "Errored" means the tests could not run to a result, which is different from a numerical mismatch. Cause not yet determined; see `worlddynamics_tests.log` in the run artifact.
4. **Earth4All.jl has no test folder.** There is no automated check of its agreement with Vensim. Any such check has to be built by F3 (see D-011 for the constraint on Vensim files).

### Status of Phase 1 step 1.1 (T0)
Not passed yet. Open: valid World3 cross-check (item 2), cause of test errors (item 3), review of the World3 Figure 7.7 image, and a way to check Earth4All.jl against Vensim output (item 4).
