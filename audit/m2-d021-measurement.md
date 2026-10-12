# D-021 measurement: carrying state (b) and restarting every 10 years (c) against re-running from the start (a)

Numbers only. Readings fixed before any run: `docs/m2-d021-measurement.md` (commit `b92dc57`). Generated from `audit/data/m2-d021-measurement.json` by `audit/t0/m2_d021_measure.py`, run 2026-10-12. FaIR 2.2.4, the published fair-calibrate v1.4.1 ensemble, 841 members, scenario `medium-extension`, time bounds to 2100. **No accept or reject threshold is set and none of (a), (b), (c) is chosen here: that is the editor's decision (D-021).** Errors are (b) or (c) minus (a), absolute K, surface temperature on time bounds.

## 1. Reading 1: stochastic, noise matched to the exact run (primary reading)

Chains started at 1980, errors over 1980 to 2100:

| chain | max abs ensemble-mean error (K) | ensemble-mean error at 2100 (K) | max abs error of any member (K) | median over members of their max abs error (K) | 95th percentile over members of abs error at 2100 (K) | abs ensemble-mean error at 2100 as share of warming since 1850 | max of that share over 2000-2100 |
|---|---|---|---|---|---|---|---|
| (b) carry state from 1980 | 0.0249 | 0.0012 | 0.2697 | 0.0201 | 0.0307 | 0.041% | 0.70% |
| (c) restart every 10 years from 1980 | 0.0250 | 0.0004 | 0.2536 | 0.0203 | 0.0304 | 0.014% | 0.64% |

Chains started at 2025 (the realistic coupling window, emissions before 2025 are prescribed history), errors over 2025 to 2100:

| chain | max abs ensemble-mean error (K) | ensemble-mean error at 2100 (K) | max abs error of any member (K) | median over members of their max abs error (K) | 95th percentile over members of abs error at 2100 (K) | abs ensemble-mean error at 2100 as share of warming since 1850 | max of that share over 2000-2100 |
|---|---|---|---|---|---|---|---|
| (b) carry state from 2025 (realistic coupling window) | 0.0021 | 0.0008 | 0.2655 | 0.0152 | 0.0302 | 0.029% | 0.10% |
| (c) restart every 10 years from 2025 (realistic coupling window) | 0.0018 | 0.0005 | 0.2228 | 0.0150 | 0.0301 | 0.017% | 0.10% |

The same 2025 to 2100 window for the chains started at 1980:

| chain | max abs ensemble-mean error (K) | ensemble-mean error at 2100 (K) | max abs error of any member (K) | median over members of their max abs error (K) | 95th percentile over members of abs error at 2100 (K) | abs ensemble-mean error at 2100 as share of warming since 1850 | max of that share over 2000-2100 |
|---|---|---|---|---|---|---|---|
| (b) carry state from 1980 | 0.0047 | 0.0012 | 0.2697 | 0.0155 | 0.0307 | 0.041% | 0.35% |
| (c) restart every 10 years from 1980 | 0.0026 | 0.0004 | 0.2536 | 0.0152 | 0.0304 | 0.014% | 0.19% |

## 2. Reading 2: deterministic (internal variability off for all runs)

Chains started at 1980, errors over 1980 to 2100:

| chain | max abs ensemble-mean error (K) | ensemble-mean error at 2100 (K) | max abs error of any member (K) | median over members of their max abs error (K) | 95th percentile over members of abs error at 2100 (K) | abs ensemble-mean error at 2100 as share of warming since 1850 | max of that share over 2000-2100 |
|---|---|---|---|---|---|---|---|
| (b) carry state from 1980 | 0.0254 | 0.0009 | 0.1837 | 0.0153 | 0.0039 | 0.030% | 0.66% |
| (c) restart every 10 years from 1980 | 0.0254 | 0.0003 | 0.1882 | 0.0150 | 0.0016 | 0.010% | 0.70% |

Chains started at 2025, errors over 2025 to 2100:

| chain | max abs ensemble-mean error (K) | ensemble-mean error at 2100 (K) | max abs error of any member (K) | median over members of their max abs error (K) | 95th percentile over members of abs error at 2100 (K) | abs ensemble-mean error at 2100 as share of warming since 1850 | max of that share over 2000-2100 |
|---|---|---|---|---|---|---|---|
| (b) carry state from 2025 (realistic coupling window) | 0.0010 | 0.0005 | 0.0363 | 0.0004 | 0.0027 | 0.018% | 0.07% |
| (c) restart every 10 years from 2025 (realistic coupling window) | 0.0010 | 0.0002 | 0.0225 | 0.0004 | 0.0009 | 0.006% | 0.07% |

## 3. What the numbers show (measured; no recommendation)

- **Ensemble mean.** For chains started at 2025 the largest ensemble-mean error is 0.0021 K for (b) and 0.0018 K for (c) with noise matched, and 0.0010 K and 0.0010 K without internal variability. Chains started at 1980 reach about 0.025 K in the ensemble mean over 1980 to 2100, of which the 2025 to 2100 part is under 0.005 K: the largest errors occur before 2025.
- **Individual members** are much less accurate than the mean. With noise matched, the largest error of any member is 0.265 K for (b) and 0.223 K for (c) from 2025; without internal variability it is 0.036 K and 0.023 K. So most of the per-member error disappears when internal variability is switched off. This is consistent with the limitation fixed in the readings (the autocorrelated stochastic-forcing component cannot be carried by unmodified FaIR), but **this measurement does not isolate that cause**: it is an inference.
- **Per-member spread** (median over members of their maximum error, 2025 to 2100): 0.0152 K (b) and 0.0150 K (c) with noise matched; 0.00042 K and 0.00042 K without.
- **As a share of the warming since 1850** at 2100 the ensemble-mean error is at most 0.041%; the maximum over 2000 to 2100 is at most 0.70% (reached in 1980-start chains early in the window).

## 4. Time cost (this machine, single core, 841 members)

| item | seconds |
|---|---|
| exact re-run from 1750, ending 1981 / 2040 / 2099 / 2100 | 14.7, 15.2, 17.1, 16.3 |
| exact re-run, 20 members, same end years | 0.96, 0.93, 0.83, 0.83 |
| one carried one-year segment ((b) or (c)), range over the eight chains | 10.8 to 12.2 |
| one exact run 1750-2100 in one call | 18.0 (stochastic), 21.2 (deterministic) |

- **Correction of an earlier statement (2026-10-12).** `audit/m2-fair-report.md` section 6 carried a dated clarification saying the 39-minute projection was "slightly low, roughly 4% more". **That was wrong.** The earlier timings (19.4 s with 841 members) were taken for re-runs ending 2025 to 2030; the re-runs measured here are between 14.7 s and 17.1 s, so a 120-year loop of exact re-runs (a) costs roughly 29 to 34 minutes with 841 members, not more than 39. The timing varies by about 20% between measurements on this machine; the cause was not investigated.
- **A carried segment costs about as much as an exact re-run** (10.8 to 12.2 s against 14.7 to 17.1 s) because each segment is a separate FaIR run that sets up all 841 members. That setup cost is **inferred** as dominant (a one-year segment should be about 350 times cheaper than a 350-year run if the simulation itself dominated). So with unmodified FaIR, (b) and (c) save little time; the saving would have to come from avoiding the per-run setup, which this measurement did not test.

## 5. Is a 20-member subset representative of the 841? (rule fixed before the run: every 42nd member, rows 0, 42, ..., 798)

Same scenario, years 2025 to 2100, subset minus full, absolute K (the 20 members' trajectories are identical to their trajectories inside the full ensemble):

| statistic across members | max abs difference over 2025-2100 (K) | difference at 2100 (K) | subset at 2100 (K) | full at 2100 (K) |
|---|---|---|---|---|
| ensemble mean | 0.054 | -0.010 | 2.848 | 2.858 |
| 5th percentile | 0.176 | 0.108 | 2.147 | 2.038 |
| 95th percentile | 0.321 | -0.321 | 3.531 | 3.852 |

- The 20-member **mean** is within 0.054 K of the 841-member mean at every year; the **5th to 95th percentile band is much less well represented** (up to 0.176 K at the 5th and 0.321 K at the 95th percentile; at 2100 the 95th percentile is 0.321 K low). With 20 members a percentile is an interpolation between very few points, so band edges are noisier.
- For 2015 to 2024 the 20-member mean is 1.207 K against the 841-member 1.196 K (A2.1) and the HadCRUT5 interval [1.234, 1.305] K: **outside the interval**, as the full ensemble is (D-030).
- One subset rule was tried, as fixed; no other rule was searched. The result says nothing about other scenarios or other subsets.

## 6. Not done

No choice among (a), (b), (c) and no threshold. The cause of the per-member error was not isolated. The time saving available from avoiding per-run setup was not tested. 20-member carried-segment timings were not measured.
