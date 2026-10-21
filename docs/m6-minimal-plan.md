# M6 minimal integration plan: World3 + FaIR + S3, with S7 as output-only

**Status:** plan only, written 2026-10-21. **No code, no test run, no data.** It applies `docs/phase-2-plan.md` section 15 (D-049: M6 proceeds with S3 as built, structural tests only, shapes not levels) and D-050 (S7 scope and display rules). Where this file and an approved decision differ, the decision governs. It lists coupling variables, which A6.x tests apply, what is deferred, one open design question for the editor, and token estimates (estimates, not measurements).

## 1. What "minimal" means here

Four sector groups in one coupling loop at the 0.25-year step (D-003, D-022), each already a `Sector`:

| Group | Module | Starts | Notes |
|---|---|---|---|
| World3 (S1 population, agriculture, capital, resources, pollution) | `f3/sectors/world3_group.py` (D-031: 0.0625-year sub-steps inside the loop step) | 1900 (reported from 1970, D-019/D-020) | already merged; 2004 parameter set is the provisional default (D-015) |
| FaIR climate (S6) | `f3/sectors/s6_climate.py` (D-021 option a: exact re-run from 1750 each year) | its own history | **841 members for published runs (editor, D-021 note); about 19 s per annual re-run, so one 1980-2100 loop is roughly 30 to 34 minutes** (measured, `audit/m2-d021-measurement.md`); tests use the documented 20-member subset |
| S3 AI sector under R3 | `f3/sectors/s3_ai.py` + `s3_rule_r3.py` (+ the data-centre module and damage function of the M2 slice) | 2025 | **flagged unvalidated (D-029); structural tests only** |
| S7 social | `f3/sectors/s7_social.py` (merged if the suite is green) | at the start of its input | **output-only in M6: nothing reads it** |

**Not in M6-minimal (deferred):** S5 minerals and water (M5 steps 3 and 4), the S2 feedback of tension (spec S7 "feedback to the system"), the ported Earth4All sectors (S2 economy, S4 energy; M4 built and merged them, but they are **not wired in here**), the data-centre electricity coupling of the M2 slice beyond what S3 already needs, A5.4 (hindcast, deferred until after M6 by D-049), and any calibration.

## 2. Coupling variables

Units are strings and must match exactly across a coupling (the core refuses a mismatch); a unit change is an explicit adapter.

### 2.1 World3 group ↔ others
| From | Variable (unit) | To | Why / status |
|---|---|---|---|
| World3 `pop` (persons, sum of `p1` to `p4`) | population | S3 (`L0`-based labour) | **Open (section 5): S3 has its own labour `L(t) = L0 exp(g_L t)`, independent of World3.** In M6-minimal the two economies are **not reconciled** (known from D-020 and plan 14.2 item 2: GATE's economy and a World3-based economy are two models of the same world) |
| FaIR `warming` (K) | warming | World3 | **No consumer in World3** (it has no warming term; D-049 omits `WELE`, `WELY`, `CO2ELY`, `OWLCO2`) |
| World3 outputs (`pop`, industrial output per capita `iopc`, food per capita `fpc`) | state | S7 (inputs below) | S7 reads only **changes**; see 2.3 |

### 2.2 FaIR ↔ S3
| From | Variable | To | Status |
|---|---|---|---|
| S6 `warming` (K) | warming | S3 damage function (`warming` input, D-007 level-of-output options, default central) | **already built in the M2 slice** (`slice_m2.py`) |
| S3 / World3 emissions | CO2 emissions | S6 | **not built: emissions are prescribed (D-021 option A)**, so S6 has no inputs. The replay of one recorded climate is exact only while that holds (D-035 review note: a test must fail if any sector feeds S6). **If emissions are ever coupled, the exactness of replay ends and the 30-minute-per-run cost applies to every run.** |

### 2.3 To S7 (output-only)
| Input of S7 | Source | Status |
|---|---|---|
| `labor_share` (1) | S3 `labor_share` | accepted as the main driver using only its relative fall from the first step (D-050); level unvalidated (D-029) |
| `unemployment` (1) | none today | **no source in S3 or World3 as built**: a given path or zero in M6-minimal (illustrative input, labelled) |
| `warming` (K) | S6 `warming` | available |
| `gdp_per_capita_growth` (1/year) | S3 `gwp` and population | S3 level unvalidated: the growth rate is computed from S3 `gwp` and the **S3 labour** (not World3 population) for consistency; labelled |
| `redistribution` (1) | scenario lever | default 0 |

S7's four outputs are **recorded and displayed only as changes relative to the start**, with the D-008, D-029 and D-049 labels. **Nothing consumes them in M6-minimal** (no feedback into S1, S2 or S3); that is a design choice discussed in section 5.

## 3. Acceptance tests A6.x that apply

Each is written before any result; failures are recorded with size and first year, nothing adjusted, as for M1 to M5. Tests that involve S3 are **structural only** (section 15.2 of the plan): no comparison of S3's absolute output with GATE or observed data.

| Test | Applies to M6-minimal? | How, and what is deliberately not claimed |
|---|---|---|
| **A6.1** baseline: AI sector off, population, resources, agriculture, capital and pollution reproduce full World3 within ±2% (D-004) | **Yes, independent of S3** | the World3 group alone against WorldDynamics.jl, already **met** by M3 (A3.2: worst 1.906%, 2004 set); M6 re-runs it **inside the integrated loop with S3 and FaIR present but not coupled to World3**, and checks the result is unchanged. If the coupled loop changes World3's states beyond 1e-9 (nothing should reach it), that is a wiring bug |
| **A6.2** every loop has a sign test, each with an output named before the test | **Partly**: R1, B1, B2, R2, B5 are testable; **B3, B4 (S5) and B6 (fertility, S1/World3-internal) are not** | R1 (more AI investment raises automation: the slice's R1 test **failed** because both runs saturate at 1.0 by 2065; the M6 version names a different output and window **before** the test, e.g. the year the fraction reaches 0.5, with a control that can fail); **B1: the slice test failed as written, so the M6 test fixes its output and window in advance and notes the failure; if B1 fails again it is recorded**; B2 (high damage option gives lower output by 2100 than low) passed in the slice; R2 and B5 are S7's own sign tests (tests/test_s7_social.py), **driven by given input paths in M5 and by S3's relative labour-share fall in M6**; B6 is World3-internal and covered by A3 |
| **A6.3** invariance: each coupling can be switched off and the sector returns its stand-alone result (1e-9 for S3 and S1, within each sector's own recorded tolerance otherwise) | **Yes** | for each wired coupling (S6→S3 damage, S3→S7, World3→S7, supply→data centre): switch off and compare with the stand-alone run |
| **A6.4** extreme conditions: zero compute growth, infinite energy, zero investment: plausible behaviour, no NaN, no negative stock | **Yes, structural** | properties only; "plausible" is checked as bounds and finiteness, not against any figure |
| **A6.5** run time measured and an upper bound for a thousand-run Monte Carlo derived | **Yes** | **one full run with 841 FaIR members is roughly 30 to 34 minutes, so a thousand runs would be about 500 to 570 hours on one core**: the derived bound will say that Monte Carlo is not feasible with exact FaIR re-runs unless emissions stay prescribed (replay) or the D-021 decision is revisited. The World3 group takes 2 to 3 seconds per run |
| **A6.6** initialisation follows D-019 Option C | **Yes** | World3 from its own state; FaIR from its history; S3 from GATE's initial values at 2025 (D-020); S7 from its documented illustrative start |
| **A6.7** the review states which tests passed, failed, were not run | **Yes** | `docs/phase-2-review.md` is the M6 deliverable; **this plan does not write it** |

**Tests that do not apply and why:** any comparison of S3's output with GATE (A1.3 failed, D-029); any hindcast (A5.4 deferred); B3 and B4 (S5 not built); any magnitude claim about S7.

## 4. What is deferred, and what that costs

| Deferred item | Consequence for M6-minimal |
|---|---|
| S5 minerals and water | loops B3 and B4 are untested; the model has no mineral or water constraint |
| S2 feedback of tension (and of damages on the World3 economy) | tension affects nothing; the **damage function acts on S3's output only**, not on World3 |
| Earth4All sectors (M4) in the loop | World3's own capital and industry stand in for "the economy" for World3's outputs; S3 has its separate economy |
| Reconciliation of S3's economy and World3's | **none**: two economies of the same world in one run; a known open item (plan 14.2 item 2), stated on every output |
| S7 calibration and hindcast | S7 shows illustrative structure only |
| Coupling emissions to FaIR | emissions stay prescribed (D-021 A) |

## 5. The open question: should S7 feed back into S2 / S1?

**Recommendation (the Validator's, separate from the question; the decision is the editor's): no feedback in M6-minimal; S7 stays output-only.** Reasons:
1. **Every S7 parameter is illustrative (24 of 24).** A feedback would make invented numbers change the outputs of validated sectors (World3 matches WorldDynamics.jl within 2%); that would break A6.1 for any run with S7 active and contaminate the one part of the model that has been checked.
2. **It is not needed to test the loops:** R2 and B5 are closed inside S7 plus its inputs; the "tension reduces governance capacity and investment efficiency" link (spec S7) is the only S7 loop that needs a feedback, and its target sector (S2, Earth4All economy) is **not in the M6-minimal loop**.
3. **There is nothing to calibrate the size against** (hindcast deferred, tension not validated by decision D-008), so the size of a feedback would be invented.

**The options for the editor:**
- **(a) Output-only (recommended).** S7 is recorded and displayed as changes relative to the start; feeds nothing. A6.1 stays clean.
- **(b) Feedback into S3's investment** (tension lowers the AI investment share through R3): small code, but S3 is unvalidated and R3 is a scenario-lever rule, so this would stack one illustrative module on another unvalidated one.
- **(c) Feedback into S1** (tension or well-being into World3's fertility or mortality terms): scientifically the most interesting (loop B6 in the spec) and the **riskiest**: it changes World3's validated population equations and would need a new decision and a new reference-free test plan.
- **(d) Feedback into S2** (the spec's own design): **not possible in M6-minimal** because S2 (Earth4All economy) is deferred; it belongs to a later milestone.

Weaker points of the recommendation: with output-only, the Explorer's third panel cannot show any consequence of social stability for the rest of the system, which is the project's stated question; that is the price of keeping the validated part clean until S7 has sourced parameters.

## 6. Order of work inside M6-minimal (proposed)

1. **Tests and readings first** (committed before code): A6.1 to A6.6 written as above, with each named output and window for the sign tests fixed in a document; the unit adapters listed.
2. **The wiring**: a builder (like `slice_m2.build`) that adds the World3 group, FaIR, S3 (+ the M2 slice's data-centre and damage), S7 to one `Model`; units checked by the core; S7's inputs from the sources in 2.3.
3. **Run A6.1 and A6.3 first** (they protect the validated parts), then A6.4 and A6.2, then A6.5 (the 841-member run once, in the background, output to a file).
4. **Report** `audit/m6-integration-report.md` and a track log; the Phase 2 review (`docs/phase-2-review.md`) is a separate, later step and the editor's checkpoint.

## 7. Token estimates (estimates, not measurements)

Basis: Tracks A, B and C of this project (about 216, 268 and 308 thousand subagent tokens each) and the documents and decisions around them. M6-minimal has **less porting and more wiring and testing**, and one long run.

| Step | Estimate | Main uncertainty |
|---|---|---|
| 1 Tests and readings | 60 to 120 thousand | how many sign tests need new named outputs after the B1 and R1 failures |
| 2 Wiring (builder, adapters, S7 inputs) | 100 to 200 thousand | the unreconciled two economies; unit adapters; S7's `unemployment` source |
| 3 Runs A6.1 to A6.5 | 80 to 200 thousand (+ about 30 to 34 minutes of wall-clock for the 841-member run, no tokens while it runs) | surprises in coupling stability; a failed A6.1 would need diagnosis |
| 4 Report and track log | 40 to 100 thousand | |
| **Total** | **about 0.3 to 0.6 million tokens** | |

## 8. What this plan does not do
It writes no code, runs nothing, changes no criterion or label, does not write `docs/phase-2-review.md`, and does not decide the feedback question. It does not touch `docs/phase-2-plan.md` (section 15 already carries the S3-as-built rules).
