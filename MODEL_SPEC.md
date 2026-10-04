# F3 — Foundation for Earth
## Global Model Specification · v0.1 (draft)

**Status:** v0.1 draft, updated after decisions D-001 to D-004, D-010 and D-011 · **Owner:** Stéphane Beau (editor-in-chief) · **Repo:** github.com/stefbeau/f3
**Last updated:** 2026-10-04

---

## 1. Purpose

F3 is an open, global system dynamics model that couples two families of models that have so far evolved separately:

- **Planetary-limits models** (World3, Earth4All, climate integrated assessment models), which track population, economy, resources, pollution, climate and social well-being.
- **AI-transition models** (GATE, compute-centric takeoff models), which track compute, algorithmic progress, task automation and AI-driven growth.

F3 asks one central question: **how does a fast AI race interact with energy, materials, water, climate and social stability, and which policy levers change the outcome?**

### What F3 is not

F3 does not predict the future. Every output is a **conditional scenario**: *if* these assumptions hold, *then* these trajectories follow, within these uncertainty bands. F3's value lies in revealing which levers and feedback loops matter most, not in naming a date.

---

## 2. Design principles

1. **Reproduce before inventing.** Every borrowed sector must first reproduce its source model's published runs before being modified or coupled.
2. **Every assumption is logged.** Each parameter value and equation choice gets an entry in `DECISIONS.md` with its source and rationale, and is approved by the editor-in-chief.
3. **Uncertainty first.** Key parameters are defined as distributions, not single values. Headline results are always shown as ranges.
4. **Modular sectors.** Each sector is a self-contained module with explicit inputs and outputs, so it can be tested, replaced or upgraded independently.
5. **Backtested.** The model runs from 1970 so that its behavior up to 2025 can be compared with observed history before any projection is trusted.
6. **Simple before complex.** v0.1 is global and aggregate. Regional disaggregation (e.g. US / China / EU / rest of world) is a v0.3+ goal.

---

## 3. Architecture overview

| Item | v0.1 choice |
|---|---|
| Method | System dynamics (stocks, flows, feedback loops) |
| Time horizon | 1970–2100 |
| Time step | 1 year for output; 0.25 year internal integration (to be confirmed, see D-003) |
| Spatial resolution | One global region |
| Language | Python 3.11+ |
| Core libraries | PyWorld3 (unmodified, for reproduction tests only — see D-001), FaIR (climate emulator), NumPy, pandas, SALib (sensitivity analysis) |
| Reference implementations | Earth4All.jl (MIT), run in Julia for the D-010 audit tests T1–T4; passing components ported to Python (D-011) |
| Uncertainty | Monte Carlo (≥1,000 runs per scenario) with Latin hypercube sampling |

### Sector map

| # | Sector | Primary source model | New in F3? |
|---|---|---|---|
| S1 | Population | World3 population sector (re-implemented from published equations) | Adapted |
| S2 | Economy & capital | Earth4All output/demand structure, conditional on audit (D-010); GATE task-based production | Adapted, conditional |
| S3 | AI development & automation | GATE | Adapted, newly coupled |
| S4 | Energy | Earth4All capacity structure + new data-center module, coupled to material limits | Extended |
| S5 | Materials & water | World3 resources + new critical-minerals and water modules; WORLD7 as reference | Extended |
| S6 | Climate | FaIR emulator | Adopted |
| S7 | Social stability & well-being | New F3 module with explicit stocks, informed by Earth4All and Turchin | New |

**Role of Earth4All (D-010):** Earth4All is a *reference model and component library*, not F3's baseline. Its components are reused only after passing the audit tests T1–T4 listed in `DECISIONS.md`.

---

## 4. Sector specifications

Notation is indicative. Final equations are fixed in v0.2 after the reproduction phase.

### S1 — Population

- **Origin:** World3 population sector (age cohorts, fertility, mortality in every cohort), re-implemented from the published equations rather than copied from PyWorld3 (D-001). Well-being moves to S7.
- **Key stocks:** Population by age group (0–14, 15–44, 45–64, 65+).
- **Key flows:** Births, deaths, aging.
- **Drivers:** Income per person, food per person (World3 agriculture sector in v0.1), health services, temperature stress (from S6), well-being (from S7).
- **Outputs to other sectors:** Labor force (S2, S3), consumption demand (S2, S4).
- **Calibration data:** UN World Population Prospects.

### S2 — Economy & capital

- **Origin:** Earth4All output, demand and public sectors, **reused only if they pass audit tests T2 and T3** (D-010). The labor module is built by F3 if T2 fails.
- **Key stocks:** Physical capital (K), public capital, debt.
- **Production (indicative):** task-based production in which output Y combines human labor on non-automated tasks and AI/capital on automated tasks:
  `Y = A · F(K, L · (1 − f), K_AI · f)`
  where `f` is the fraction of tasks automated (from S3).
- **Key outputs:** GDP, investment, labor share of income (to S7), investment available for AI (to S3) and energy (to S4).
- **Damages:** Output reduced by a climate damage function of temperature (from S6). The choice of damage function is a major uncertainty (see D-007).
- **Calibration data:** World Bank WDI, Penn World Table, Maddison Project (pre-1990 history).

### S3 — AI development & automation (core novelty)

- **Origin:** GATE (Epoch AI, 2025): compute-based AI development, automation framework, semi-endogenous growth.
- **Key stocks:** Installed hardware compute (`C_hw`), algorithmic efficiency (`A_alg`), fraction of tasks automated (`f`).
- **Indicative equations:**
  - Effective compute: `C_eff = C_hw · A_alg`
  - Hardware growth driven by AI investment share of output and the cost of compute (price per FLOP falls over time).
  - Automation: `f = G(log C_eff)`, a cumulative distribution over the compute required to automate each task (GATE's approach).
  - **Hard constraints new to F3:** compute growth is capped by available electricity (S4), chip-critical minerals (S5) and cooling water (S5).
- **Outputs:** Automation fraction (to S2, S7), electricity demand of compute (to S4), mineral and water demand (to S5), optional AI-driven boost to R&D productivity (to S4 energy efficiency and S2 productivity).
- **Calibration data:** Epoch AI datasets on training compute, hardware price-performance and data-center capacity.

### S4 — Energy

- **Origin:** Earth4All energy capacity structure, extended. Renewable build-out is constrained by S5 material availability, which Earth4All lacks (D-010).
- **Key stocks:** Fossil generating capacity, renewable capacity, nuclear capacity, data-center electricity load.
- **New module — data-center demand:**
  `E_dc = C_hw_operating / η_hw · PUE`
  where `η_hw` is hardware energy efficiency (FLOP per joule, improving over time) and PUE is power usage effectiveness of data centers.
- **Outputs:** Emissions (to S6), energy cost and supply gap (to S2, S3), mineral demand for renewables and grids (to S5).
- **Calibration data:** IEA World Energy Balances, IEA *Energy and AI* reporting, Energy Institute Statistical Review of World Energy.

### S5 — Materials & water

- **Origin:** World3 nonrenewable resources sector, extended with specific modules. WORLD7 (Sverdrup et al.) is a reference for metals supply, subject to availability and license.
- **Key stocks:**
  - Aggregate nonrenewable resources (World3 style).
  - Critical minerals for chips and the energy transition (v0.1: aggregate index; candidates for tracking separately in v0.2: copper, lithium, gallium, rare earths).
  - Freshwater availability index.
- **Water module:** `W_dc = E_dc · WUE` (water usage effectiveness), plus water used in chip fabrication and power generation.
- **Outputs:** Extraction costs and supply limits (to S2, S3, S4).
- **Calibration data:** USGS Mineral Commodity Summaries, FAO AQUASTAT, company and IEA reporting on data-center water use.

### S6 — Climate

- **Origin:** FaIR (Finite-amplitude Impulse Response) open-source climate emulator.
- **Inputs:** CO₂ and other emissions from S4 and S2 (land use, industry).
- **Outputs:** Global mean temperature anomaly (to S1, S2, S7), optional food-yield stress (to S1).
- **Calibration data:** Global Carbon Budget, HadCRUT / NOAA temperature records.

### S7 — Social stability & well-being

- **Origin:** New F3 module (D-010). Draws on the concepts of Earth4All's Social Tension and Average Wellbeing indices and on structural-demographic theory (Turchin), but uses explicit stocks rather than smoothed indices.
- **Key stocks:** Inequality (e.g. income share of top 10%), social trust, social tension, well-being.
- **Drivers:** Change in well-being, labor share of income (falls as `f` rises unless redistributed), unemployment or underemployment from automation, temperature stress.
- **Feedback to the system:** High tension reduces governance capacity and investment efficiency (S2) and triggers delayed policy responses (redistribution, AI regulation) defined as scenario levers.
- **Calibration data:** World Inequality Database, ILO labour-share data. A historical proxy for social tension is still to be chosen (see D-008).

---

## 5. Key feedback loops

| ID | Type | Loop |
|---|---|---|
| R1 | Reinforcing | Output → AI investment → compute → automation → output (the AI growth engine) |
| R2 | Reinforcing | Automation → falling labor share → rising inequality → rising social tension → lower well-being |
| R3 | Reinforcing (optional) | AI → faster R&D → cheaper clean energy and better hardware efficiency → more compute per unit of energy |
| B1 | Balancing | Compute → electricity demand → supply gap and higher energy cost → slower compute growth |
| B2 | Balancing | Output and compute → emissions → temperature → climate damages → lower output |
| B3 | Balancing | Chips and renewables → mineral demand → depletion and higher cost → slower build-out |
| B4 | Balancing | Data centers → water demand → local scarcity → constraint on capacity |
| B5 | Balancing (delayed) | Social tension → policy response (redistribution, regulation) → lower inequality, possibly slower AI |
| B6 | Balancing | Well-being and income → lower fertility → slower population growth |

The scientific core of F3 is the race between **R1/R3** (AI-driven acceleration) and **B1–B5** (physical and social limits).

---

## 6. Scenario levers (dashboard controls)

| Lever | Range (indicative) |
|---|---|
| AI investment share of GDP | Low / central / race |
| Algorithmic progress rate | Distribution from Epoch data |
| Hardware energy-efficiency improvement | Slow / historical / fast |
| Clean-energy build-out speed | Earth4All "Too Little Too Late" to "Giant Leap" |
| Redistribution of AI income (taxation, dividends) | 0–100% of automation gains |
| AI regulation / compute caps | None / moderate / strict |
| Climate damage function | Low / central / high |
| Critical-mineral recycling rate | Current / doubled / circular |

### Reference scenarios for v0.1

1. **Baseline reproduction:** F3 with the AI sector switched off. Population, resources and agriculture must reproduce the World3 standard run within ±2% (D-004); behavior is compared with Earth4All "Too Little Too Late" for information, not as a pass/fail test.
2. **AI Race:** High AI investment, weak redistribution, current clean-energy pace.
3. **AI Race + Giant Leap:** High AI investment combined with Earth4All's five turnarounds.
4. **Managed Transition:** Moderate AI growth, strong redistribution, fast clean energy.

---

## 7. Validation plan

1. **Reproduction tests:** F3's World3-based sectors match the published World3 standard run (checked against unmodified PyWorld3) within ±2% (D-004). Earth4All components are audited with tests T1–T4 (D-010) before any reuse.
2. **Backtest 1970–2025:** Key outputs (population, GDP, energy, CO₂, temperature) compared with observed data, with error metrics reported.
3. **AI-sector check:** With F3 constraints switched off, S3 approximately reproduces GATE sandbox presets.
4. **Sensitivity analysis:** Sobol indices (SALib) identify which parameters drive outcome uncertainty.
5. **Extreme-condition tests:** Zero compute growth, infinite energy and similar limits must produce plausible behavior.
6. **External review:** Before public launch, invite review from system dynamics and AI-economics researchers.

---

## 8. Agent responsibilities

| Agent | Owns | Key outputs |
|---|---|---|
| Research | Literature and source-model documentation | `research/` notes, citation register |
| Data | Fetching, cleaning and versioning datasets | `data/raw/`, `data/processed/`, data cards |
| Modeler | Sector code and equations | `f3/sectors/*.py` |
| Validator | Tests, backtests, sensitivity analysis | `tests/`, validation reports |
| Publisher | Documentation and dashboard | `docs/`, `dashboard/` |
| **Editor-in-chief (Stéphane)** | Approves every entry in `DECISIONS.md` | Final say on assumptions |

---

## 9. Open decisions (for approval)

| ID | Decision | Proposed default |
|---|---|---|
| D-001 | Licensing | **Approved:** Apache 2.0 for code, CC BY 4.0 for docs and data; no PyWorld3 code copied |
| D-002 | Earth4All integration route | Superseded by D-011 |
| D-011 | Earth4All reference implementation | **Approved:** Earth4All.jl only; audit in Julia, port only what passes |
| D-003 | Internal time step | **Approved:** 0.25 year |
| D-004 | Reproduction tolerance | **Approved:** ±2% on key variables |
| D-005 | AI sector integration | Re-implement GATE's three modules in simplified form (GATE's optimization-based investment is replaced by a behavioral rule) |
| D-006 | Critical minerals in v0.1 | Single aggregate index; split into named minerals in v0.2 |
| D-007 | Climate damage function | Provide three options (low / central / high) rather than choose one |
| D-008 | Social tension historical proxy | To research (candidates: political instability indices, protest-event data) |
| D-009 | Dashboard stack | Decide in phase 4 (candidates: Streamlit; static site with precomputed scenario runs) |
| D-010 | Role of Earth4All | **Approved:** reference model and component library, audited by tests T1–T4 |

---

## 10. Roadmap

| Phase | Goal | Done when |
|---|---|---|
| 0 — Setup | Repo, structure, `DECISIONS.md`, agent workflow | Repo live, D-001 to D-004 and D-010 approved ✅ |
| 1 — Reproduce & audit | World3 sectors re-implemented; Earth4All audited | Reproduction tests and T1–T4 complete |
| 2 — Couple | S3 AI sector added and linked to S4, S5, S7 | All loops in section 5 active |
| 3 — Calibrate & quantify uncertainty | Backtest and Monte Carlo | Validation report published |
| 4 — Publish | Public dashboard with scenario levers | Dashboard live, methodology documented |

---

## 11. Proposed repository structure

```
f3/
├── README.md
├── MODEL_SPEC.md          ← this document
├── DECISIONS.md           ← decision log (D-xxx)
├── research/              ← source-model notes, citations
├── data/
│   ├── raw/
│   ├── processed/
│   └── cards/             ← one data card per dataset
├── f3/
│   ├── sectors/           ← s1_population.py … s7_social.py
│   ├── coupling.py
│   └── scenarios/
├── tests/                 ← reproduction and backtest tests
├── notebooks/
├── docs/
└── dashboard/
```
