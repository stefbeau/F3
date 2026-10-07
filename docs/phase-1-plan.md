# F3 — Phase 1 Plan: Reproduce & Audit

**Status:** In progress (see `docs/STATUS.md` for the current state of each step) · **Depends on:** Phase 0 (complete) · **Governing decisions:** D-001, D-004, D-010, D-011, D-012 (and proposed D-013, D-014)

---

## 1. Goal

Before F3 builds anything of its own, establish **which existing components can be trusted** and get the first one running in Python.

Phase 1 delivers two things:

1. **An audit verdict on Earth4All** (tests T1–T4 from D-010), stating which components F3 may reuse.
2. **World3's population sector running in Python**, matching its reference within ±2% (D-004). This becomes F3 sector S1.

## 2. Principles for this phase

- **Audit before translating.** Earth4All is tested in Julia exactly as published (D-011). Nothing is ported until it passes.
- **Never trust a single source.** Every result is checked against a second, independent reference where one exists.
- **Pin everything.** Each external model is fixed to an exact version or commit, recorded in `audit/REFERENCES.md`, so anyone can rerun the audit and get the same numbers.
- **Human checkpoints.** The editor-in-chief approves the outcome of each step marked ✋ before the next one starts.

## 3. Steps

### Step 1.0 — Reference environment

| Item | Detail |
|---|---|
| Tools | Julia (installed with `juliaup`), Python 3.11+, Git |
| References | Earth4All.jl (commit hash recorded), WorldDynamics.jl v1.0.0, PyWorld3 (unmodified, latest PyPI release) |
| Repo additions | `audit/` folder with its own Julia project files (`Project.toml`, `Manifest.toml`) and `audit/REFERENCES.md` |
| Excluded | The `vensim_source` folder shipped inside Earth4All.jl is never copied into F3 (D-011) |

**Done when:** All three references install and run their default scenario on the editor-in-chief's machine or in CI.

### Step 1.1 — T0: sanity check of the references

Before auditing Earth4All, confirm the Julia implementation behaves as published.

- Run Earth4All.jl's "Too Little Too Late" and "Giant Leap" scenarios and regenerate its comparison figures against Vensim.
- Run WorldDynamics.jl's World3 standard run and regenerate its comparison with the original book figure.

**Pass:** Visual and numerical agreement with the published figures. Any mismatch is logged before going further. For Earth4All.jl the numeric check is the package's own `all_mre` against the Vensim output in its repository (D-014). For WorldDynamics.jl the numeric check is the cross-check against PyWorld3 (D-013).
✋ **Checkpoint:** Editor-in-chief reviews the T0 figures.

### Step 1.2 — Earth4All audit (T1–T4)

Run on Earth4All.jl as published, for both scenarios, 1980–2100 unless stated.

| Test | Question | Method | Pass criterion |
|---|---|---|---|
| **T1** Population | Does every cohort have mortality, and do stocks stay non-negative? | Inspect population equations for death flows per cohort; record the minimum value of each cohort stock | Mortality in every cohort and no negative stock before 2100 |
| **T2** Labor | Can more people be employed than are of working age? | Compare employed population with working-age population every year | Employed ≤ working-age population in every year |
| **T3** Forcing audit | Which outcomes are driven by time-based inputs rather than feedback? | List every variable that depends directly on time, on a time-keyed lookup table, or on a step/ramp between fixed dates; classify each as *policy input* (acceptable if documented) or *behavior forcing* (red flag) | No unreplaceable behavior forcing in the sectors F3 might reuse (output, demand, inventory, finance, public, energy) |
| **T4** Horizon stability | What breaks if the model runs past 2100? | Run to 2200; record the first variable to leave a plausible range, and when | Informational only (F3 stops at 2100) |

**Deliverable:** `audit/earth4all-audit.md`: method, raw results, figures and a per-test verdict. The audit report states facts and evidence, not opinions about the model's authors or its critics.

### Step 1.3 — Audit verdict

Turn the audit into a decision: a new entry in `DECISIONS.md` (D-016) listing, sector by sector, whether F3 **reuses**, **reuses with changes**, or **replaces** each Earth4All component. MODEL_SPEC is updated to match.
✋ **Checkpoint:** Editor-in-chief approves D-016.

### Step 1.4 — World3 population sector in Python (S1)

Per D-012: port from WorldDynamics.jl with MIT attribution.

1. **Port** the World3 population sector to `f3/sectors/s1_population.py`, with an attribution header and a `NOTICE` entry.
2. **Test it in isolation.** The population sector depends on inputs from other World3 sectors (food, industrial output, services, pollution). For the test, these inputs are fed in as time series recorded from a full WorldDynamics.jl run, so the test isolates the population equations alone.
3. **Compare** against WorldDynamics.jl (pass/fail, ±2% on every reported year) and against PyWorld3 (second check; any gap must be explained).
4. **Document** each equation with its source page in *Dynamics of Growth in a Finite World* where available.

**Known issue to resolve here:** World3 starts in 1900, while F3 is specified to start in 1970. Reproduction tests use 1900. How F3 initializes its stocks in 1970 gets its own decision entry during this step.
✋ **Checkpoint:** Editor-in-chief reviews the comparison report.

### Step 1.5 — Phase 1 review

Update `MODEL_SPEC.md`, `README.md` and the roadmap; list open issues carried into Phase 2.

## 4. Agent assignments

| Step | Lead agent | Support | Output |
|---|---|---|---|
| 1.0 | Validator | — | `audit/` environment, `REFERENCES.md` |
| 1.1 | Validator | Research | T0 figures and notes |
| 1.2 | Validator | Research (reads equations, links findings to the D-010 review) | `audit/earth4all-audit.md` |
| 1.3 | Research | Validator | D-016 draft |
| 1.4 | Modeler | Validator (tests), Research (equation sources) | `f3/sectors/s1_population.py`, `tests/test_s1_population.py`, comparison report |
| 1.5 | Publisher | All | Updated docs |

## 5. Exit criteria

Phase 1 is complete when:

- [ ] References pinned and T0 passed
- [ ] T1–T4 run and published in `audit/earth4all-audit.md`
- [ ] D-016 approved and MODEL_SPEC updated
- [ ] S1 population passes ±2% against WorldDynamics.jl, with PyWorld3 gaps explained
- [ ] 1970 initialization decision logged
- [ ] README roadmap updated
