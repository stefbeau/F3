# Links 3 and 4: results

Date: 2026-11-26. Readings and tests were committed (5f05e36) before the code: `docs/link3-link4-tests.md`. Both links are switches of `World3Group`, off by default. Figures: `audit/data/link3-link4.json`. World3 2004 parameter set, standard levers; warming is the recorded FaIR ensemble mean (1.35 K in 2025, 1.92 K in 2050, 2.86 K in 2100).

## Link 3: warming to land yield (health not built)
Source: Zhao et al. (2017), PNAS 114, 9326, **abstract only** (PubMed Central): per kelvin of global mean warming, yields fall by 6.0% (wheat), 3.2% (rice), 7.4% (maize), 3.1% (soybean), without CO2 fertilisation, adaptation or genetic improvement. Options: low 3.1%, central 4.925% (plain mean, my arithmetic), high 7.4% per K above the 2025 level.

All six readings met (L3-T1 to L3-T6, including the control).

| Option | Land yield 2050 | Land yield 2100 | Population 2050 | Population 2100 |
|---|---|---|---|---|
| low | -1.8% | -4.7% | -0.3% | -2.3% |
| central | -2.8% | -7.4% | -0.4% | -3.6% |
| high | -4.2% | -11.1% | -0.6% | -5.5% |

(Change against the same run with the link off.) Not validated: there is no hindcast, because the link is inactive before 2025 by construction. Upper reading for the four crops, since fertilisation and adaptation are left out; other crops, regions and extremes are not represented. **Health is not built**: a global mean temperature gives no defensible mortality function. Link 3 is therefore half built and must keep saying so.

## Link 4: S3 output to World3 industrial output, bounded
S3's uplift, re-measured with steps E1 and E2 on, is still unbounded (about 1.9 in 2030, 9 to 14 in 2040, 160 to 310 in 2050). The link applies it limited to a growth of `cap` a year; the cap has no default.

All readings met (L4-T1 to L4-T5, the control, and the no-default check).

| Cap | Cap binds | Bounded uplift 2050 / 2099 | Industrial output 2030 / 2050 / 2100 | Population 2050 / 2100 |
|---|---|---|---|---|
| 1% a year | 2027 to 2099, every year | 1.27 / 2.07 | +2.9% / +24% / +114% | +3.4% / +17% |
| 2% a year | 2027 to 2099, every year | 1.61 / 4.25 | +5.8% / +51% / +247% | +6.3% / +31% |
| 5% a year | 2027 to 2099, every year | 3.23 / 35.2 | +14.8% / +108% / +50% | +11.6% / +19% |

**Plain statement.** The cap binds in every year from 2027. S3 contributes nothing to these results except the first year; the table is the answer to "what if AI added 1%, 2% or 5% a year to World3's industrial output", and nothing more. The link runs and is tested, but it carries no information from S3 until S3's level is bounded by something measured. With a 5% cap World3 overshoots harder: output is higher in 2050 and the gain shrinks by 2100. One-way; the two economies are not reconciled.
