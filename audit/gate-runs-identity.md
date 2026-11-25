# Are the preset runs Epoch sent the same series as the shipped playground runs?

**Date:** 2026-11-25. Script: `audit/t0/gate_runs_identity_check.py`. Figures: `audit/data/gate-runs-identity.json`.

## Why this check
The pinned playground bundle can no longer be fetched (D-026 outcome note, 2026-11-25: the URL returns 404, the Wayback Machine holds no capture, no copy was found on the editor's PC). A1.3 and test T1 of D-062 are defined against that bundle. Epoch AI's reply includes the three presets "regenerated" with its solver and says they equal the shipped series to about 1e-16. That statement cannot be checked directly any more.

## What was done
In October 2026, comparison figures computed from the shipped bundle (sha256 `3afe8e4d…c55bf`) were stored in `audit/data/s3-gate-comparison.json`: for S3 variant A and for the stored-composite diagnostic, the largest and mean relative difference per quantity and the index of the largest, for the three settings. The same figures were recomputed from the runs Epoch sent and compared with the stored ones.

## Result
- **67 figures compared; all 67 agree to better than 1e-9; the largest relative difference is 2.0e-11.** The index of the largest difference is the same for every quantity (0 mismatches).
- Figures that are themselves rounding noise (stored value below 1e-12, for example labour's 4e-15) are only checked to be below 1e-12 again: all are.

## What this supports, and what it does not
- **Supports:** the three presets Epoch sent are the same series as the shipped runs **for the fields these figures depend on**: output, capital, labour, hardware, software, the automated fraction, the compute stock, the two shares, the composite, and the six investment shares used as inputs.
- **Does not prove** equality field by field: a maximum and a mean could in principle stay the same while single values differ. Fields that no stored figure uses are not covered.
- **Assumes** S3's variant A and its helpers compute the same thing now as in October. If they had changed, the figures would differ, so the agreement also speaks against that; it is not shown separately.

## sha256 of the files compared (the files themselves are not in the repository)
| File | sha256 |
|---|---|
| `default_run.json` | `bff0cbadf5f9fd8c0725cb4015d724a81aeccc547e9f252000a444d0ffb3e863` |
| `conservative_run.json` | `a36a022c68f9f444f91a785cc6ecae907d5360c5be771667f117f184a731f0f3` |
| `aggressive_run.json` | `968f48d2e8b525038bfd2d9a9c6559ffd85f2efdc1059fd07cc3e449cfe084be` |
| `T41_lam025_run.json` | `ed70eedc47d48cae545b06a65d8180d169377ce94d5bcb626511211f0a4fb705` |
| `T33_lam1_run.json` | `8728fd9bacffdfa9a68337f20ccf928b48257c3217c77fb4b2e0cdd81af27a42` |
