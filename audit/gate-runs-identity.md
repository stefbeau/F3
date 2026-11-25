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

## Field-by-field check against the bundle now on GitHub Pages (2026-11-25)

**Why.** On 2026-11-25 the live page https://epoch.ai/gate no longer loads the playground; it links to https://epoch-research.github.io/gate-playground/, which loads `gate.js` from the same folder. That file is **not** the D-026 bundle: 3,202,707 bytes, sha256 `24bae00ebfe0a59d62fab3fff2245657b414bfc0a423a706248301915a3c293e`, Last-Modified 2026-11-06 (a Wayback capture of 2026-11-10 has the same bytes). It was downloaded to a scratch folder outside the repository and is not committed. The D-026 pin is unchanged.

**How.** `audit/t0/gate_playground_probe.py` **fails on this file as it stands**: its `main()` looks for the marker `// legacy/one-offs/gate/…`, which in this bundle reads `// src/gate/…`. The probe was not edited. Its own reader `balanced()` was called from a scratch script (not committed) with the marker `// src/gate/backend/cache.json`, as `tests/gate_reference.py` does for the old marker. The stored runs were then compared with the files in `.gate_cache/runs` (the D-063 hashes above, checked).

**Result.**
- **The bundle contains stored runs: 3 entries, 80 states each.**
- **Matching.** Each entry's `modelParams` equals exactly one preset's `world_params` on all 42 parameters the two have in common (0 differences), and differs from the other two presets in 3. Entry 0 matches `default`, entry 1 matches `conservative` and entry 2 matches `aggressive`.
- **Fields.** 28 fields are in both. `time`, `compute_allocation` and `chip_fabrication_scale_up` are only in the bundle; `epistemic_state` and `objective` are only in the files Epoch sent. Neither group was compared.
- **Largest relative difference per field, over the three presets and all 80 states** (|bundle − sent| / |sent|; zero where both are zero):

| Field | Largest | Field | Largest |
|---|---|---|---|
| `ai_value` | 4.0e-16 | `oom_compute` | 2.2e-16 |
| `best_training_run` | 4.5e-16 | `physical_best_training_run` | 5.5e-16 |
| `capital` | 4.1e-16 | `q_capital` | 4.1e-16 |
| `capital_share` | 1.6e-16 | `q_compute` | 4.3e-16 |
| `cognitive_ces_term` | 4.4e-16 | `q_consumption` | 0 (identical) |
| `compute` | 4.4e-16 | `q_hardware_rnd` | 4.1e-16 |
| `compute_investment` | 4.2e-16 | `q_runtime_compute` | 4.1e-16 |
| `consumption` | 5.1e-16 | `q_software_rnd` | 5.1e-16 |
| `effective_compute_investment` | 5.1e-16 | `q_training_compute` | 4.2e-16 |
| `frac_automated` | 1.7e-16 | `runtime_compute` | 4.1e-16 |
| `gwp` | 4.3e-16 | `runtime_compute_share` | 4.0e-16 |
| `hardware` | 4.1e-16 | `software` | 3.7e-16 |
| `labor` | 1.3e-16 | `tobin_q_compute` | 4.3e-16 |
| `labor_share` | 4.1e-16 | `training_compute` | 5.0e-16 |

- **Overall largest: 5.5e-16** (`physical_best_training_run`), about two to three units in the last place of a double. One field (`q_consumption`) is bit-identical; the others differ only at that level.

**What this supports, and what it does not.**
- **Supports, measured:** for the 28 common fields, the three presets Epoch sent equal the runs stored in the GitHub bundle to rounding precision. This is consistent with Epoch's statement of about 1e-16; that statement was about the shipped bundle, which this is not.
- **Does not show** that the GitHub bundle's runs are the D-026 bundle's runs. That bundle cannot be read any more. The link between Epoch's files and it is still only the 67 figures above (largest difference 2.0e-11).
- **Not compared:** the five fields present on one side only, and the two stress settings (they are not in the bundle).
- **No pin, test or reference was changed.** The GitHub bundle is not used by any test: `tests/gate_reference.py` would only accept a file matching the D-026 pin.
