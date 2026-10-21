# M5 plan: S7 social, S5 minerals and water, and the warming channels in replaced sectors

**Status:** plan only, written 2026-10-21. **No implementation, no data downloaded, no source opened for this plan.** Every "read" statement below is taken from the repository's own records (`research/SOURCES.md`, `docs/phase-2-plan.md` M5, `MODEL_SPEC.md`, D-006, D-008, `research/damage-functions-verified.md`, the Earth4All.jl source at the pinned commit). Anything those records do not show as read is marked **unverified**. Under the standing delegation (`CLAUDE.md`) any licence or third-party-data use not already covered by D-001, D-014 or D-026 is a **STOP-and-ask item**; they are marked **STOP** and collected in section 6.

**Authority.** D-006 (one aggregate critical-minerals index in v0.1; named minerals in v0.2) and D-008 option 3 (no backtest of tension against event data; S7 calibrated on its drivers; tension labelled "not validated against history"; UCDP only as a labelled plausibility overlay; tension excluded from the D-024 framework) are approved. M5's tests are those of `docs/phase-2-plan.md` A5.1 to A5.6.

## 1. Inventory: inputs, sources, whether read, licence, what is unverified

Legend: **Read** = a record in the repo says the primary page or document was opened and what was seen. **Unverified** = not opened, or opened and refused (HTTP 403), or known only from search summaries. **STOP** = needs the editor before any use.

### 1.1 S7 social (inequality, labour share, tension, well-being)

| Input | Source | Read? | Licence | Unverified / issues | STOP |
|---|---|---|---|---|---|
| Income share of the top 10% (and other shares) for 1970 to 2024, world and about 130 countries | World Inequality Database (WID), wid.world | **Partly**: the data page and home page were opened; they show world and country series and a "Download full dataset" option. **Not read**: any licence, reuse or citation text (none found on any WID page opened; guessed terms URLs returned 404); the coverage start year; the definition used (pre-tax national income, top 10%) beyond the page labels | **Not stated** on any page opened. A suggested citation (Alvaredo, Atkinson, Piketty, Saez, WID.world) was seen in search results only | The **terms are unknown**. The start year of the world series is unknown, so a 1970 hindcast is not established. Whether redistribution of derived series is allowed is unknown | **STOP (WID terms)** |
| Labour share of income, 2004 onward | ILOSTAT, SDG indicator 10.4.1 (labour income share as a percentage of GDP); UN SDG metadata | **No**: ILOSTAT's copyright pages returned HTTP 403; the UN metadata PDF was **not opened**. The "93 countries, from 2004" figure comes from a search-result summary | **Unverified.** ILO publications are generally CC BY 4.0: indirect evidence only, not a reading of the terms | Coverage and definition unverified; the series starts in 2004 (too short for a 1970 backtest, and D-008 notes this) | **STOP (ILOSTAT terms)** |
| A long labour-share series (1970 to 2004) | **Not identified.** A national-accounts source (Penn World Table, which `MODEL_SPEC.md` names for S2 calibration, or the Maddison Project) is a candidate | **No**: neither was opened for this purpose; their terms are in no repo record | **Unverified** | The A5.4 hindcast of the labour share over 1970 to 2024 **cannot be defined** until a long series is chosen and its terms read | **STOP (choice and terms)** |
| Armed-conflict plausibility overlay (not a calibration target) | UCDP/PRIO Armed Conflict v26.1, 1946 to 2025 | **Read**: the UCDP downloads page was opened (coverage and version verified) | **CC BY 4.0** (verified on the UCDP downloads page, per D-008's evidence note) | State-based armed conflict only; it is not "social tension"; one-sided violence and non-state conflict start only in 1989 | none (already approved use) |
| Earth4All Social Tension and Average Wellbeing indices as a comparison output | Earth4All.jl wellbeing sector, pinned run | **Read** (audited; D-016); the indices deviate from Vensim by 4.37% (TLTL) and 2.77% (GL) at worst, reported per D-018 | MIT (the package); the Vensim output is not stored (D-014) | Earth4All's indices are smoothed, not stocks; a comparison output only | none |
| Structural parameters of the S7 stocks (trust, tension, well-being dynamics: time constants, gains) | **No source.** Turchin's structural-demographic theory is a concept cited in the spec, not a parameter source | **No** | n/a | **Every S7 dynamic parameter is currently unsourced.** Plan A5.1 requires a one-page document stating the source of every parameter, and a decision for each parameter with no source | A parameter with no source is a decision for the editor (A5.1, M5 deliverables) |
| Policy-response lag and size (loop B5) | **No source** | **No** | n/a | scenario levers; illustrative | decision per parameter |

### 1.2 S5 minerals and water

| Input | Source | Read? | Licence | Unverified / issues | STOP |
|---|---|---|---|---|---|
| Critical-minerals data for the aggregate index (production, reserves, 2021 to 2025) | USGS Mineral Commodity Summaries 2026, https://doi.org/10.3133/mcs2026; data release https://doi.org/10.5066/P1WKQ63T | **Partly**: the **data-release metadata** were read (dated 6 Feb 2026, coverage 2021 to 2025). **The report PDF has not been read** (too large for the fetch tool), so **no figure from it has been checked**; the cited report version (1.3, May 2026) comes from a search result and the earlier register said 1.1 | **Public domain** (US government; the catalogue page links the USA.gov public-domain label; verified) | Every number taken from the report is **[unverified]** (D-006 outcome note). The data release can be read directly if a machine-readable file is offered: not checked. Which minerals the "critical" aggregate includes and how they are weighted is **not decided** | none for the licence; **the content must be read before any figure is used** |
| Global mineral demand of chips and of the energy transition | Not identified | **No** | n/a | The B3 loop (chips and renewables to mineral demand) needs demand per unit of compute and per unit of capacity. **No source found.** WORLD7 (Sverdrup et al.) is named in the spec as a reference "subject to availability and licence" | **STOP (source and licence not found)** |
| Data-centre water use, direct and indirect | LBNL, *2024 United States Data Center Energy Usage Report* (Shehabi et al., Dec 2024), escholarship | **No**: every attempt returned empty content or HTTP 403. Figures (about 21.2 billion litres in 2014, about 66 billion in 2023 direct; about 800 billion indirect) are from **search summaries and unverified** | **Not checked** | **US only**; no global series found; the primary document must be read | **STOP (primary document unread, terms unchecked)** |
| Chip-fabrication water use | TSMC, *2024 Sustainability Report* (water section about pp. 96 to 101) | **No**: HTTP 403. The figures (101 million m3 in 2023; 19.65 million m3 reclaimed at Tainan by end 2024) are from search summaries, **unverified** | **Not checked** | One company, not the sector; no per-wafer or sector series; a secondary source says the absolute figures are not consistently normalised | **STOP (primary document unread, terms unchecked)** |
| Freshwater availability index, water supply for the constraint of B4 | FAO AQUASTAT (named in `MODEL_SPEC.md` S5) | **No**: not opened for any repo record | **Unverified** | No data seen at all | **STOP (not opened, terms unknown)** |
| Water usage effectiveness (WUE) for `W_dc = E_dc x WUE`, and PUE | IEA reports give PUE ranges (1.1 to 1.2 and 1.5 to 1.7, read in M2 step 1); **no WUE source** | PUE: **read** in Key Questions; WUE: **no** | IEA: CC BY 4.0 | WUE has no source | decision for the editor if illustrative |
| Data-centre electricity `E_dc` (the driver of `W_dc`) | The M2 module (D-033, Provisional) driven by S3's compute | **Read** (IEA 415, 485 and 950 TWh) | CC BY 4.0 | **Inherits S3's unvalidated output (D-029): the modelled `E_dc` leaves any plausible range after about 2027** (the Explorer withholds it). Any water or mineral demand computed from it is unvalidated on the same basis | label per D-029; **no S5 output may be shown from S3's compute until S3 is validated** |

### 1.3 Warming channels in replaced sectors (traced here; the plan says it was not traced)

Read from Earth4All.jl at commit `16f37d0` (`src/*/subsystems.jl`, `parameters.jl`). All four have the form `1 + coefficient x (OW / OW2022 - 1)` (or the CO2 version) for `t > 2022`, and 1 before. The three channels in reused sectors (OWECC, OWELC, OWTFP) are already ported and switchable (M4). The four in replaced sectors are:

| Channel | Where Earth4All uses it (read) | What replaces that sector in F3 | Coefficient (read) | Does F3 need its own version? |
|---|---|---|---|---|
| `OWLCO2` | climate sector: `LECO2A = LECO2A1980 x OWLCO2` (warming shortens the CO2 lifetime in the atmosphere) | FaIR (S6) has its own carbon cycle and its own temperature feedback on carbon uptake | `SOWLCO2` = 1; baseline `OBWA2022` = 1.35 | **No (inferred, not tested):** FaIR replaces the whole climate sector, so this channel has no counterpart to attach to. Whether FaIR's own feedback is comparable was **not checked** |
| `WELE` | population sector: life expectancy `LE = (...) x WELE x LEM` | **S1 (World3 population)**, which has no warming term | `OWELE` = -0.02 | **Decision needed.** World3's life expectancy has no warming effect; adding one is new, unreferenced modelling of a size Earth4All sets at -2% of life expectancy per unit of `OW/OW2022 - 1`. Default: **omit and label** "no health effect of warming" |
| `WELY` | foodland: yield `ACY` and the land-yield term `GLY80` multiplied by `CO2ELY x WELY` | **World3 agriculture** (S1 food), which has no warming term | `OWEACY` = -0.3 | **Decision needed.** Same question for land yield, a larger coefficient (-30% per unit). Default: **omit and label** "no yield effect of warming" |
| `CO2ELY` | foodland: `1 + CO2CEACY x (CO2CA / CO2C2022 - 1)` (CO2 fertilisation of yield) | World3 agriculture | `CO2CEACY` = 0.3; baseline `CO2C2022` = 420 (ppm) | **Decision needed**, and it needs FaIR's CO2 concentration (the S6 sector already outputs it). Default: **omit and label** |

**What this means.** Without WELE, WELY and CO2ELY the model has **no warming effect on population or food**, so loop B2 acts only through output (the damage function) and, from M4, through the three channels in the reused sectors. This is a labelled limitation, not an error. Adding them is a scientific choice with large coefficients and **no F3 reference to test against**, so it is a delegated decision to be recorded **Provisional** with its reversal cost, and each added channel needs a sign test (A5.5 style) and a label. The baseline question of D-023 (FaIR's anomaly against Earth4All's constant `OW2022` = 1.35) applies to all of them and is **unresolved**.

## 2. Proposed order

Each step starts with its written documentation and tests (A5.1, A5.2 to A5.5), committed before any code. Steps 1 and 2 need no new data and no STOP item; the rest wait for the STOP items in section 6.

1. **Warming-channel decision and wiring (no new data).** Document the four replaced-sector channels (section 1.3); record the default "omit and label" as a Provisional decision; if the editor wants them, build `WELE`/`WELY`/`CO2ELY` as switchable multipliers that default to 1, with sign tests. Also resolve the `OW` baseline for the three reused channels (D-023). *Cost: small.*
2. **S7 skeleton with documented illustrative parameters (no new data).** Equations, units, bounds and every parameter written down with its source or marked illustrative; stocks: inequality (top-10% income share), trust, tension, well-being; drivers: labour share, unemployment from automation, temperature stress. Tests A5.2 (bounds, no NaN), A5.3 (no automation: constant labour share) and the sign test for R2 (automation, falling labour share, rising inequality, rising tension) on documented illustrative parameters. **No calibration, no hindcast, no claim of fit.** *Cost: medium.*
3. **S5 minerals: aggregate index.** After the USGS report is **read** (STOP): documentation, stock-and-flow with the index, tests A5.2 (stocks never negative) and A5.3 (zero compute: demand falls to baseline; infinite supply: B3 inactive), sign test for B3. *Cost: medium.*
4. **S5 water.** Only after the water sources are read (STOP). If they cannot be read, start with parameters **clearly labelled illustrative** and say so in every output; tests A5.2, A5.3 (zero compute: water falls to baseline; infinite supply: B4 inactive), sign test for B4. *Cost: medium to large (least verified data).*
5. **Labour share and inequality hindcast (A5.4).** Only after (a) a long labour-share series is chosen, (b) WID and ILOSTAT terms are read, and (c) **the editor sets the pass thresholds on the day the series are loaded, before the first run**, with the D-024 requirement that each criterion states what a failure triggers. Tension is excluded (D-008). *Cost: medium; may not happen in M5.*
6. **Data cards** (`data/`, D-001) for every dataset used, written as each dataset enters; no dataset is committed or redistributed until its licence has been read from its own page (A5.6).

## 3. Tests to write first (before any result)

Written and committed before the code and before any data is loaded; failures recorded with size and first year, nothing adjusted, as for M1 to M4.

| Test | What it fixes in advance | Needs data? |
|---|---|---|
| A5.1 documentation | for each module a one-page document: equations, units, source of every parameter or "illustrative", bounds; the editor has seen it before the code merges | no |
| A5.2 balance and bounds | mineral stocks never negative; water use never above the declared supply; social stocks inside declared bounds; no NaN, in every scenario of the grid | no (declared bounds) |
| A5.3 extreme conditions | zero compute: data-centre water and mineral demand fall to baseline; infinite supply: B3 and B4 inactive; no automation: labour share constant | no |
| A5.5 sign tests | B3, B4, B5 and R2, each with its output named **before** the test, and a check that the test can fail (as done for the R1 sentence) | no |
| Channel tests | each added warming channel is 1 at warming equal to `OW2022`, and moves in the sign Earth4All gives (negative for `WELE` and `WELY`, positive for `CO2ELY`) | no |
| Invariance | a coupling switched off returns the stand-alone sector result (A6.3 style) | no |
| A5.4 hindcast | metrics fixed now (labour share and top-10% share against observed series, 1970 to 2024); **thresholds fixed by the editor when the series are loaded, before the first run**, each with what a failure triggers; the age-structure numbers of D-024 were seen before approval, and any threshold touching them must say so | **yes** (series not in hand) |
| A5.6 open terms | a test or checklist that fails if a dataset file is committed whose licence note is missing | no |
| Labelling | every S5 or S7 output shown anywhere carries its labels: "illustrative parameters" where unsourced, "not validated against history" for tension (D-008), D-029 where S3 compute feeds it | no |

## 4. Token-cost estimates

These are estimates for planning, **not measurements**. Basis: the actual M1 to M4 tracks in this project, where one sector-sized port with tests and report cost on the order of 150 to 300 thousand subagent tokens per track (Track A about 216 thousand, Track B 268 thousand, Track C 308 thousand) and the document-and-decision work around each added roughly 30 to 100 thousand in the orchestrating session. M5 has **no reference model to port**, so the work is more writing and decisions and less mechanical porting, but more reading of sources. A line of uncertainty is stated for each.

| Step | Estimate (subagent + orchestration) | Main uncertainty |
|---|---|---|
| 1 Warming channels | 50 to 120 thousand | whether the editor wants them built; the `OW` baseline question |
| 2 S7 skeleton | 150 to 300 thousand | every parameter is unsourced, so many Provisional decisions |
| 3 S5 minerals | 150 to 300 thousand (+ 30 to 80 thousand to read the USGS report) | the report is large; which minerals; demand per unit has no source |
| 4 S5 water | 200 to 400 thousand | sources may stay unreadable (HTTP 403) |
| 5 Hindcast | 100 to 250 thousand | long labour-share series not identified; terms |
| 6 Data cards, reports, review file | 60 to 150 thousand | |
| **Total M5** | **about 0.7 to 1.5 million tokens** | the plan's own estimate is 6 to 10 sessions; it says nothing in tokens |

Reading the unread sources is part of the cost: the plan's token figures assume each source is reachable. Where a primary document stays blocked, the cost shifts to the editor (supplying the PDF) and the step waits.

## 5. M6 addition: S3 as-is, flagged unvalidated, so integration is not blocked

The following is **proposed text for the M6 plan** (`docs/phase-2-plan.md` M6 is not edited by this file; the editor or a dated amendment section applies it).

**M6 proceeds with S3 as it is.** S3 failed A1.3 (D-029); its absolute output (`gwp`, capital, effective compute) is unvalidated against GATE after about 2027, and the Epoch AI reply is not awaited (editor, 2026-10-21). Integration does **not** wait for it. Rules:

1. **S3 is wired in as built**, driven by R3 (D-028), a scenario-lever rule and not a GATE replica; its `validation_status` (D-029 text) is carried into every coupled run's metadata and every output that uses it.
2. **Every M6 test that involves S3 is a structural test**: loop signs (R1, B1, B3, B4, B5), invariance (coupling off returns the stand-alone S3 result to 1e-9, A6.3), extreme conditions (A6.4), bounds and finiteness. **No M6 criterion compares S3's absolute output with GATE or with observed data.** The four reference scenarios report S3 quantities **only as shapes and shares**, never as levels, until S3 is validated.
3. **The known S3 failures travel with it**: A1.3 (composite), A1.4 (R3 poor), A2.6 (step 0.565% against 0.1%), the B1 and R1 sign failures of the slice, and the implausible electricity demand. **The B1 sign failure matters for M6:** the loop B1 (compute to electricity demand to slower compute) does not hold in the slice as written, and the M6 test A6.2 for B1 must be written against an output and a window **fixed before the test**, with a note that the slice test failed. If B1 fails again it is recorded, not adjusted.
4. **Mineral and water demand driven by S3's compute (B3, B4) are shown as shapes only**, labelled per D-029, and the withheld-output rule of the Explorer (D-047) extends to them: **no absolute S5 demand from S3's compute path is displayed.**
5. **The Epoch reply, if it comes,** can change S3 (a new composite) without changing the M6 structure: the integration tests are written against S3's interface, and the A1.3 re-run would be a separate, dated update.
6. **What this does not do:** it does not make S3 validated, does not remove any label, and does not change any acceptance criterion; A6.1 (baseline scenario with the AI sector switched off reproduces full World3 within 2%) is **independent of S3** and unaffected.

## 6. STOP items collected (nothing below may be used until the editor decides)

1. **WID terms** (income-share series): read from its own page first; none found so far.
2. **ILOSTAT terms** (labour share): copyright pages returned 403; terms and coverage unread.
3. **A long labour-share series** (1970 to 2004): source and terms not chosen (Penn World Table or Maddison are candidates, neither read for this).
4. **USGS report content**: licence is fine (public domain); **the report PDF must be read before any figure is used**.
5. **Mineral demand per unit of compute and per unit of capacity**: no source found; WORLD7 availability and licence unknown.
6. **LBNL data-centre water report**: primary document unread (403); terms unchecked.
7. **TSMC sustainability report**: primary document unread (403); terms unchecked.
8. **FAO AQUASTAT**: not opened; terms unknown.
9. **WUE source**: none; illustrative only unless the editor decides.
10. **Every unsourced S7 and S5 parameter** is a decision for the editor, one by one (M5 deliverable), or is labelled illustrative.
11. **The three replaced-sector warming channels** (`WELE`, `WELY`, `CO2ELY`): a scientific choice with large coefficients and no reference; default is to omit and label.
12. **The `OW` baseline** (FaIR's 1850-1900 anomaly against Earth4All's constant 1.35, D-023): open.

Items 1 to 3 and 5 to 8 may need the editor to open or supply documents (publisher sites refused automated access, as in `research/SOURCES.md` open question 5).

## 7. What this plan does not do

It does not read any source, download any data, write any module, change any criterion or label, or start M5. It does not choose thresholds for A5.4. It does not edit `docs/phase-2-plan.md`, `DECISIONS.md` or `MODEL_SPEC.md`.
