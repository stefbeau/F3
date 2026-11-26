# Links 3, 4, 6 and 7 of the connections map: what it takes to build them

Written 2026-11-26 at the editor's request ("I want to complete the steps for connections 3, 4, 6 and 7"). **A plan. Nothing is built, no test is run, no label changes.** Numbering is that of the Explorer's connections page (`site_src/links.py`), not the data campaign's L3 to L7 (`docs/links/`), which differ; the matching note is named under each link.

## Where the four links stand

| Link | From, to | What exists | What blocks it |
|---|---|---|---|
| 3 | Warming to World3 health and yield | D-049 left the Earth4All channels out and labelled the gap. `docs/links/L3.md`: forms from the literature and four pass/fail tests, written before any code. | The papers that give the size of the yield response are not read (marked "from memory, unverified"). A coefficient has to be chosen. Heat mortality needs temperature distributions, which F3 does not have. |
| 4 | S3 output to World3 | `docs/s3-world3-reconciliation.md`: measured, three options, tests named. The reverse direction (World3 labour force into S3) is built as a switch. | Measured with the earlier composite, S3's uplift factor is 1.86 in 2030, 31 in 2040 and 2.2 million by 2100. Applied to World3 it is not a reconciliation. A bounded form needs a new coefficient. |
| 6 | Data-centre electricity to emissions | `docs/links/L6.md` (energy emissions to climate): forms, data and five tests. Emissions are prescribed (D-021). | (a) Data-centre electricity leaves any plausible range until step E1 of D-066 is built. (b) A carbon intensity of the electricity is needed. (c) FaIR must be re-run for every scenario: 22 minutes for 841 members, measured on 2026-11-25. |
| 7 | World3 to emissions | Same note and tests as link 6. GCB fossil CO2 for 2015 to 2024 is in the repository; CEDS 1750 to 2023 was retrieved. | World3 has no CO2. An emission factor per unit of industrial output, and its trend, must be fitted to history. One FaIR run per World3 scenario. |

## Order proposed

1. **Step E1 of the electricity module** (D-066, approved; the ranges of `g_max` and `outer_share` are still the editor's to set). Links 4 and 6 both read S3 quantities that are implausible without it.
2. **Link 6**, as an addition to the prescribed CO2 path, not a replacement of it.
3. **Link 7**, with the same emissions adapter.
4. **Link 3**, yield first.
5. **Link 4** last, and only if a new measurement supports it.

## Steps for each link

### Link 6: data-centre electricity to emissions
1. E1 built and its tests run (E-T1 to E-T7 of `docs/electricity-module-proposal.md`).
2. **Editor:** the source of the carbon intensity of data-centre electricity (g CO2 per kWh, by year). Candidates: the recorded Earth4All electricity intensity; a constant; an IEA mix. This is a new parameter.
3. Tests fixed before code, from `docs/links/L6.md`: join continuity in 2023 to 2025, the historical warming unchanged, mass conservation, switch-off invariance to the recorded tolerance, labels D-030 kept.
4. An emissions adapter: CO2 added = (data-centre electricity used minus the baseline already inside the prescribed path) x intensity. Non-CO2 stays prescribed and stays labelled.
5. **Editor:** the FaIR budget. Three AI settings x two supply cases = 6 runs, about 2.2 hours with all 841 members. A smaller ensemble would be a new decision.
6. Site: link 6 "built", with its effect in kelvin and its notice.

### Link 7: World3 to emissions
1. **Editor:** the method for the emission factor. Proposal: fossil CO2 = World3 industrial output x intensity(t), intensity fitted to 1970 to 2024 and extended at its fitted trend. Two parameters, both new.
2. Tests fixed first: the hindcast reproduces observed fossil CO2 for 1970 to 2024 within a tolerance set by the editor before the fit is seen; the five L6 tests.
3. Adapter as for link 6; the two additions are reported separately (no double counting when both are on).
4. FaIR runs: 27 World3 lever combinations, about 10 hours with 841 members, once.
5. Site: link 7 "built"; the warming panel then differs by scenario, which it never has.

### Link 3: warming to World3 yield (health not built)
1. Read the four papers listed in `audit/data/needs-user.json` (Zhao 2017, Schlenker and Roberts 2009, Burke 2015, Jagermeyr 2021).
2. **Editor:** the range of the yield response per kelvin (low, central, high, as for D-007), fixed from the papers.
3. Tests fixed first, from `docs/links/L3.md`: sign and size, switch-off invariance to 1e-9, the 1961 to 2024 bound, no double counting with the output damage.
4. A multiplier on World3's land yield from 2025, default off.
5. **Health stays not built** and stays labelled: a global mean temperature gives no defensible mortality function. The link's name on the site becomes "yield built, health not built".

### Link 4: S3 output to World3
1. After E1: run `audit/t0/s3_world3_measure.py` again with the default composite and the build-rate limit.
2. **Editor:** read the new uplift factor. If it still leaves plausible ranges, the link stays not built and the page says why. If not, choose between the plain multiplier and a bounded form (a new coefficient).
3. Tests as named in `docs/s3-world3-reconciliation.md`, option A, (i) to (v).
4. Build as a switch, default off.

## What cannot be promised
- That link 4 is buildable at all. The measurement decides.
- That links 6 and 7 change warming by an amount larger than FaIR's own spread. They may not; that would be reported as the result.
- Any effect of warming on health.

## Cost
Rough, in working sessions: E1 two; link 6 two, plus 2.2 hours of FaIR; link 7 three, plus 10 hours of FaIR; link 3 two, after the reading; link 4 one for the measurement, two more if it goes ahead.
