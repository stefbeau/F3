# S3 variant P against the runs Epoch AI sent (D-062; test T2)

**Date:** 2026-11-25. Readings fixed beforehand in `docs/s3-playground-composite.md`. Script: `audit/t0/s3_playground_check.py`. Figures: `audit/data/s3-playground-composite.json`. Reference values: five runs produced by Epoch AI with its own solver and sent to the editor in reply to his email of 2026-10-17 (held locally, not in this repository).

## Result, by the criterion as written
**T2 FAILED on all five runs, on one quantity only: "effective compute against stored `compute`", from index 0.** That row compares `g(Q)·S` with a field that Epoch's reply confirms is the raw stock `Q` before the cap, so it is not like for like and no model can pass it (`audit/s3-gate-comparison.md` already says so; which pairing counts is an open call of the editor's, D-005 outcome note). The criterion was not changed.

**Every other quantity in the criterion is within 2% at every index 0 to 75, in all five runs.** Largest relative differences (S3 with `composite="P"`, each run's own investment shares supplied):

| Run | output (`gwp`) | capital | hardware | software | compute stock `Q` | composite (reported) | labour share (reported) |
|---|---|---|---|---|---|---|---|
| default | 0.073% | 0.062% | 0.018% | 0.087% | 0.083% | 0.087% | 7.8e-13 |
| conservative | 0.101% | 0.023% | 0.0014% | 0.146% | 0.046% | 0.146% | 5.1e-13 |
| aggressive | 0.0042% | 0.0041% | 0.018% | 0.0043% | 0.018% | 0.0043% | 1.5e-13 |
| T = 1e41, lambda 0.25 | 0.023% | 0.022% | 1.1e-10% | 0.025% | 0.023% | 0.025% | 1.1e-12 |
| T = 1e33, lambda 1 | 7.8e-12% | 2.2e-12% | 0 | 0 | 3.1e-12% | 1.2e-11% | 9.8e-15 |

Labour and the automated fraction agree to 1e-14 or better in all runs.

For contrast, the same script with the default variant A (`--composite A`, not stored): output leaves 2% at index 1 or 2 in every run and the difference reaches 100%.

## What this shows and what it does not
- **Shown:** with GATE's own investment path supplied, S3 with variant P stays within about 0.15% of the five runs Epoch sent for output, capital, hardware, software, the compute stock and the automated fraction, over 76 years.
- **Not shown: A1.3.** Test T1 (`tests/test_s3_playground.py::test_t1_a13_criterion_variant_p`) needs the pinned playground bundle and was **not run** (the bundle could not be fetched where this was run). Epoch's note says the regenerated presets equal the shipped series to about 1e-16; that was not checked. T1 will fail on the same not-like-for-like row unless the editor rules on the pairing.
- **Not shown:** that F3 "reproduces GATE". The investment path is supplied, not solved. R3 is untouched.
- **Inferred, not tested:** the remaining differences of up to 0.15% are the same size as those recorded earlier with Epoch's stored composite supplied (`audit/s3-gate-comparison.md`), which suggests they come from S3's laws of motion and not from the composite.

## Correction of my own work (made after a result was seen)
The first version of variant P reported the runtime-compute share as the elasticity of the composite at the **start-of-period** states. It differed from the stored share by large factors (up to about 700). The stored share is reproduced (to 1e-12) by evaluating the composite on the **period-end** states with the period's automated fraction, and the code was changed to that after seeing the stored values. The shares are reported quantities, not in the criterion; no criterion quantity changed with this correction (the output figures above were identical before and after).

## Labels
Unchanged. The default composite is still "A"; the D-029 notice on S3 stays; nothing on the site changes.

## T1 (added 2026-11-25, after D-063)
T1 was run against the reference of D-063 (the three preset runs Epoch sent, hash-pinned; the playground bundle is no longer available, and identity with it is supported by `audit/gate-runs-identity.md`, not proven).

**T1 FAILED in all three settings, on one row only: "effective compute against stored `compute`", from index 0.** Every other quantity of the criterion is within 2% at every index 0 to 75 (the figures are those of the table above, which used the same three files). The test is now a strict xfail with this reason, as the repository does for recorded failures; the assertion is unchanged.

A **post-hoc** test, labelled as such and not a substitute for the criterion, was added after this result was seen: it asserts that the failing rows are exactly that one row (`test_posthoc_like_for_like_quantities_variant_p`).

With the same reference, the nine recorded A1.3 failures of variants A, B and C101 fail again as recorded.

The earlier statement in this file that T1 "was not run" is true of the first run and is superseded by this section.

## After the editor's ruling D-064 (2026-11-25)
The editor ruled that the compute row that counts in A1.3 is the raw stock; "effective compute against stored `compute`" is reported and no longer in the criterion. The ruling was made after the results above were known and is recorded as a change of criterion (D-064).

- **T1 now passes in all three settings** (reference of D-063). Its assertion is unchanged; the strict xfail added earlier today is removed.
- **T2 now reads PASS for all five runs**; `audit/data/s3-playground-composite.json` was regenerated (the differences are the same figures as in the table above; only the criterion flag of one row changed).
- The nine recorded A1.3 failures of variants A, B and C101 still fail and stay strict xfails.
- The post-hoc test added earlier today (`test_posthoc_like_for_like_quantities_variant_p`) is replaced by `test_effective_compute_row_is_reported_and_not_like_for_like`, which checks that the effective-compute row is reported, outside 2% from index 0, and not in the criterion.

**What this is:** with GATE's own investment path supplied, S3 with variant P is within 2% (in fact about 0.15%) of the reference runs for the quantities of A1.3 as amended by D-064. **What it is not:** F3 reproducing GATE; a comparison with the shipped bundle (D-063); a statement about R3. The default composite is still "A" and the D-029 label is unchanged.
