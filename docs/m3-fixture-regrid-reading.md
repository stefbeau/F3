# Fixture correction: re-export the S1 and World3 recorded inputs on the 1/64-year grid (reading, written before any export or run)

**Date:** 2026-10-21. **Authority:** editor's instruction of 2026-10-21 ("small labelled follow-up: fixture correction, no criterion change"), following D-044 (the Earth4All fixtures were re-exported on a 1/64-year grid after a result was seen). **This is a fixture correction, not a change to any criterion, tolerance or rule.**

## 1. What is re-exported

- `tests/fixtures/s1_inputs_world3_1974.csv` and `s1_inputs_world3_2004.csv` (S1's four recorded inputs: `dr₊fpc`, `br₊sopc`, `dr₊iopc`, `dr₊ppolx`), and
- `tests/fixtures/w3_signals_world3_1974.csv` and `w3_signals_world3_2004.csv` (the 17 recorded inputs of the four M3 sectors),

from the same pinned Julia environment (`audit/env`, D-017), the same default-option solve, **with `saveat = 1/64` instead of `1/16`**, at 12 significant digits (as D-044). The **reference files** (`s1_reference_*`, `w3_reference_*`, on the 0.5-year grid, default and tight) are **not** re-exported and are not changed. The old files are replaced in place; the old values stay recoverable from git history.

**Limit that must be stated:** WorldDynamics.jl's default solver is adaptive, so values saved at 1/64-year points are the solver's **dense-output interpolation**, not new solver steps. The finer grid removes the extra error of linearly interpolating a 1/16-year sample inside F3; it adds no information the solver did not have. (Earth4All.jl, by contrast, is a fixed-step Euler solver whose steps are 1/64 year, which is why the D-044 case differed.)

## 2. Which criteria can be affected, and which cannot (by construction)

| criterion | uses recorded inputs? | expected effect |
|---|---|---|
| A3.2 (full coupled run, 29 states, both sets) | **No**: the full model computes its own partner values | **cannot change**; re-run to confirm identical figures |
| A3.3 (twelve stocks against unmodified PyWorld3) | **No**: full model against PyWorld3 | **cannot change**; re-run to confirm identical figures |
| A3.4(b) (S1 inside the full run against S1 alone with recorded inputs) | **Yes**: the comparator "S1 alone" reads `s1_inputs_*` | **can change** |
| A3.1 (each of four sectors alone with recorded inputs, both sets) | **Yes** (`w3_signals_*`) | **can change** |
| S1 port criterion of step 1.4 (S1 alone with recorded inputs within 2% of WorldDynamics.jl; step 1.4 worst gaps 0.25% (2004 set) and 1.57% (1974 set), `audit/s1-port-report.md`) | **Yes** | **can change** |
| A0.1 (S1 in the loop equals stand-alone S1, same inputs both sides, 1e-9) | Yes, on both sides | expected unchanged (0.0) |
| M3 diagnostics that use signals (1970 restart; step-halving diagnostics) | partly | reported, not criteria |

## 3. What counts as a result, and the written prediction

- **Procedure.** (1) Capture the current figures by running the affected tests once with output (baseline). (2) Export the four files; replace the fixtures. (3) Re-run the whole suite once; collect the same figures. (4) Compare figure by figure.
- **Outcome categories (fixed now):**
  - **(i) No change:** every pass/fail status is as before and every compared figure moves by less than 0.05 percentage points.
  - **(ii) Figures move, statuses as before:** record the sizes.
  - **(iii) A previously failed criterion now passes** (only A3.4(b) can plausibly): record "failed on the 1/16 grid, passed on the 1/64 grid" and the sizes; it does not erase the earlier record.
  - **(iv) A previously met criterion now fails:** **stop and report**; nothing is adjusted.
- **Prediction (written before any run):** category (i) or (ii) with moves well under 0.1 percentage points; **A3.4(b) still fails** (its gap, 1.019% and 0.931%, comes from the other four sectors' differences from the reference, which the input grid does not touch); A3.2 and A3.3 identical to the digit; no previously met criterion fails.
- **No criterion, tolerance or rule is changed.** If nothing changes, that is recorded as the result.

## 4. Record

Dated note appended to D-044 and a new Provisional (delegated) decision (D-045) with the outcome; the figures go into `audit/m3-world3-port-report.md` as a new section and into `docs/tracks/track-b.md`.
