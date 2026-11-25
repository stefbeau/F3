# What changes when S3's default composite goes from variant A to variant P (D-065)

**Date:** 2026-11-25. Script: `audit/t0/s3_default_composite.py`. Figures: `audit/data/s3-default-composite.json`. S3 under F3's own investment rule R3 (central levers), no climate damage, with and without the data-centre electricity limit (TLTL supply, `DCParams` defaults). These are **conditional model outputs, not forecasts**, and S3's absolute output under R3 is unvalidated.

## Output (trillion USD per year; about 110 at the start)

| Year | No electricity limit, A | No electricity limit, P | Electricity limit, A | Electricity limit, P |
|---|---|---|---|---|
| 2027 | 148 | 156 | 148 | 156 |
| 2030 | 274 | 339 | 206 | 258 |
| 2035 | 758 | 1,640 | 295 | 446 |
| 2040 | 4,490 | 391,000 | 439 | 856 |
| 2060 | 2.2e7 | 5.5e12 | 1,700 | 17,600 |
| 2099 | 5.7e7 | 1.1e13 | 6,200 | 8.7e6 |

Largest growth of output in one year: 109% (A, 2051) and 546% (P, 2046) without the limit; 18% and 29% (both 2028) with it.

## Against the default GATE run (ratio of F3's output without the limit to GATE's; ratios only)

| Year | A / GATE | P / GATE |
|---|---|---|
| 2027 | 0.94 | 1.00 |
| 2030 | 0.82 | 1.01 |
| 2035 | 0.30 | 0.65 |
| 2040 | 0.0031 | 0.27 |
| 2060 | 3.3e-6 | 0.85 |
| 2099 | 5.4e-6 | 1.04 |

Here GATE's run uses its optimised investment path and F3 uses R3, so the ratio mixes the composite with the investment rule.

## Automation and electricity

- Half of all tasks automated by 2029 in all four runs. All tasks automated in 2036 (both variants, no limit), 2049 (A) and 2048 (P) with the limit.
- Data-centre electricity demanded, with the limit on: 36,900 TWh (A) and 39,200 TWh (P) in 2030; 442,000 and 624,000 TWh in 2040. Electricity actually available to data centres under the 5% cap: 1,750 TWh in 2030 and 2,090 TWh in 2040 in both, so the supply ratio is below 5% from 2030 and below 0.5% in 2040.

## Reading
- **Measured:** variant A falls behind the default GATE run by a factor of about 300 by 2040 and of hundreds of thousands by 2060; variant P stays within a factor of 4 over the whole century. Output growth of several hundred percent a year appears with P and not with A.
- **Measured:** the implausible electricity demand is there with both variants (it was first recorded with A, `docs/STATUS.md`, Track A).
- **Inferred, not tested:** the very large output and compute paths are a property of the GATE equations at their default parameters, which have no energy constraint, and not of the composite; the electricity limit, not the composite, is what keeps F3's output in a describable range.
- **Not done:** any run with climate damage, with the World3 link, with other R3 levers or other GATE settings; the published site was not regenerated.

## Also changed by the default (measured in the test suite, 2026-11-25)
The pre-registered "reading 4" of D-054 (the effect of a halved labour index on output fades once automation saturates) **failed with variant A and holds with variant P** (`tests/test_s3_labor_index.py`). Documents and labels that say the effect "persists" describe variant A and have not been revised.
