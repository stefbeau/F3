# S7 tests (A5.2, A5.3, A5.5 for R2 and B5): fixed before any S7 code and before any result

**Status:** written 2026-10-21 on branch `m5-s7`, with `docs/m5-s7-parameters.md`. Tests are in `tests/test_s7_social.py`. The module `f3/sectors/s7_social.py` **does not exist yet**, so every test below is expected to fail at collection or at import until the code is written; that is the point of writing them first. No result has been produced.

## Rules
- **Inputs are given paths, not S3 output.** S3's level is unvalidated (D-029), so every test drives S7 with **explicit input series** (labour share, unemployment, warming, growth, redistribution), by name, through the coupling loop's `ReplaySector`. No test uses S3, S1 or S6 output.
- **Outputs are named here, before the tests run.** Nothing is compared in absolute terms against the world; every test is about **direction, bounds, invariance or a fixed arithmetic identity**.
- **A test must be able to fail.** For each sign test a **control run** is defined in which the cause is absent, and a **mutation check** (below) shows the test fails when the module is deliberately broken. The mutation check is itself a test (`test_mutations_are_caught`) that runs S7 with its R2 gain set to zero and expects the R2 sign test's assertion to fail.
- **No threshold is tuned after seeing results.** Tolerances are the ones written here.

## A5.2 balance and bounds
- **B-1** for every scenario in a fixed grid (labour-share fall 0, 0.3, 0.8; unemployment 0, 0.15, 0.6; warming 0, 2, 6 K; redistribution 0, 0.5, 1; growth -0.05, 0, 0.05; 81 combinations of three of the five axes chosen in the file) over 200 years: **every stock stays within its declared bounds** (inequality 0.10 to 0.90; trust, tension, well-being, policy response 0 to 1) at every step, and **no value is NaN or infinite**.
- **B-2** extreme inputs (labour share 0 and 1, unemployment 1, warming 20 K, growth +-1) do not break the bounds.

## A5.3 extreme conditions (spec 7.5, the S7 part)
- **E-1 no automation:** with the labour share constant at its starting value (so `LSP = 0`), unemployment 0, warming 0, growth 0 and redistribution 0, **every stock stays at its starting value** (the declared start is a fixed point), to 1e-12.
- **E-2 invariance (A6.3 style):** with `redistribution` the only input set to 0 and `policy_response` start 0, switching the B5 gain `kP` to 0 gives a run identical to the run with the policy loop removed, to 1e-12.

## A5.5 sign tests, outputs named in advance

### R2 (automation, falling labour share, rising inequality, rising tension, lower well-being)
- **Named outputs:** `inequality`, `tension`, `wellbeing` at **year 40 of the run** (and the whole path for monotonicity).
- **Setup:** two runs with the same unemployment 0, warming 0, growth 0, redistribution 0; **cause run** labour share falling linearly from 1.0 to 0.7 over 40 years then constant; **control run** labour share constant at 1.0.
- **Expected direction:** at year 40, `inequality(cause) > inequality(control)`, `tension(cause) > tension(control)`, `wellbeing(cause) < wellbeing(control)`; and along the cause run **inequality is non-decreasing for the first 40 years**.
- **Must be able to fail:** `test_mutations_are_caught` re-runs the same assertions with the R2 gain `gI_LS` set to 0 and **requires them to fail** (inequality equal in both runs).

### B5 (tension, delayed policy response, lower inequality)
- **Named outputs:** `policy_response` and `inequality`.
- **Setup:** an input regime that drives tension above `Te_threshold` (labour share falling to 0.5, unemployment 0.2), run once with the B5 loop active (`kP = 2`) and once with it off (`kP = 0`).
- **Expected direction:** (a) `policy_response` **stays at 0 until tension exceeds the threshold** and is positive afterwards; (b) **the response lags tension**: the first year `policy_response` exceeds 0.05 is **later** than the first year `tension` exceeds `Te_threshold`; (c) at year 100, `inequality(B5 on) < inequality(B5 off)`.
- **Must be able to fail:** the mutation check sets `kP` to 0 in the "on" run and requires (a)'s positivity and (c) to fail.

### Other signs
- **S-1 warming:** warming 3 K against 0 K (all else equal) gives **higher tension and lower well-being** at year 40.
- **S-2 redistribution:** redistribution 0.5 against 0 gives **lower inequality** at year 40.
- **S-3 growth:** growth +0.03 against -0.03 gives **higher well-being** at year 40.
- **S-4 unemployment:** unemployment 0.2 against 0 gives **higher inequality and higher tension** at year 40.

## Interface and labelling tests
- **I-1** the module declares units for every input and output (strings) and the coupling core accepts it (`Model` builds with `ReplaySector` inputs of matching units).
- **I-2** `S7Social.validation_status` exists and contains the words "illustrative" and "not validated against history" and the D-029 sentence about S3's unvalidated output.
- **I-3** the parameter table in `docs/m5-s7-parameters.md` and the module's `PARAMETERS` dict **agree**: same names, same values, and every parameter is marked illustrative unless the document names a source (the test parses the document).
- **I-4** the module imports nothing from S3, S1 or S6 (it reads them only through the loop's named inputs).

## What is not tested here (stated so it is not read as covered)
No comparison with any observed series (deferred, D-049); no calibration; no coupling to S2; no test of magnitudes. The sign tests show only that the loops point the intended way under illustrative gains.
