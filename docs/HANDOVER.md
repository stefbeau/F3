# Prompts for Claude Code

**Status (2026-10-08):** Prompts 0 to 4 and 6 are done (see `docs/phase-1-review.md`). Prompt 5 is open. The Phase 2 prompts are at the end of this file.

Paste these in order, one per session or task. Each ends with what "done" means and when to stop and ask. Before every task: read `CLAUDE.md` and `docs/STATUS.md`.

---

## Prompt 0 — onboarding and sync (do this first)
```
You are continuing the F3 project (Foundation for Earth). Do only this task.

1. If a file f3-handover.zip is in this folder, extract it over the repository, overwriting existing files (PowerShell: Expand-Archive -Path f3-handover.zip -DestinationPath . -Force), then delete the zip.
2. Read CLAUDE.md, docs/STATUS.md, DECISIONS.md, audit/T0-FINDINGS.md, audit/earth4all-audit.md and docs/phase-1-plan.md.
3. Check the tooling and fix what you can yourself: git push works to origin (if not, tell me the exact one-time sign-in step); Python 3.11+; Julia 1.10 via juliaup (winget install --id Julialang.juliaup -e, then juliaup add 1.10). Set PYTHONUTF8=1.
4. Remove the stale duplicate phase-1-plan.md in the repository root (docs/phase-1-plan.md is the real one).
5. Commit and push with the message "Sync: handover files, D-017 and D-018 approved, Earth4All audit started".
6. Report in at most 10 lines: what you found, the tooling status, and anything where the repository and the docs disagree.

Done when: the push succeeded and the report is written. Do not start other tasks.
```

## Prompt 1 — verify the World3 environment locally (closes T0)
```
Goal: test D-017 condition (a) on this machine and close T0 for World3. Follow CLAUDE.md.

1. Instantiate audit/env (Julia 1.10). Run audit/t0/world3_t0.jl, then audit/t0/pyworld3_t0.py and audit/t0/compare_world3.py, with F3_OUT pointing to a local results folder (git-ignored).
2. Check, and report as numbers: the default-option solve returns Success with at least 401 saved points; each of the twelve main stocks is within 2% of the fine-step PyWorld3 run that uses the diagnostic start-up (recorded earlier: worst 1.70%, pollution, 2100); the as-shipped PyWorld3 comparison is reported alongside (recorded earlier: pollution 373.70%).
3. Run the package's own tests in the pinned environment (Pkg.test("WorldDynamics")) and record the outcome. We do not know it yet.
4. Add a dated section "Local verification" to audit/T0-FINDINGS.md with the results, and update the condition-(a) line in D-017 (result only; do not change its status). If (a) fails, say so first, mark D-017 as "reopened" and stop for my decision.
5. Commit and push. Store only small report files (*.md), not result CSVs.

Done when: findings and D-017 are updated and pushed, and you have told me in at most 10 lines whether T0 for World3 is closed.
```

## Prompt 2 — Earth4All audit T1b, T2, T3, T4 and the verdict draft
```
Goal: finish the D-010 audit of Earth4All.jl at commit 16f37d013a2f68135f03e7815bf861dbf47311f2 and draft the verdict. Follow CLAUDE.md; respect D-011, D-014 and D-018. Do not use vensim_source/. Work on a clone outside this repository.

Tests (definitions are in audit/earth4all-audit.md; extend them if a term is ambiguous and say how you defined it):
- T1b: minimum value of each population cohort stock (A0020, A2040, A4060, A60PL) over 1980-2100, both scenarios.
- T2: employed versus working-age population every year, both scenarios. Find the right variables from their descriptions in the package; document the definitions; flag any ambiguity instead of guessing.
- T3: take the 40 equations in audit/earth4all-time-driven-equations.csv. Classify each as policy input (acceptable if documented) or behaviour forcing (red flag). For behaviour forcing, trace which outputs it drives. Confirm or correct the candidate classes in the CSV.
- T4: run to 2200; record the first variable that leaves a plausible range and when.

Write the results into audit/earth4all-audit.md (facts and evidence, no opinions about authors or critics). Draft D-016 in DECISIONS.md as Proposed: for each Earth4All component, reuse / reuse with changes / replace, with evidence. Do not mark it Approved.

Done when: the audit file is complete, D-016 is drafted, everything is pushed, and you have told me the headline findings in at most 15 lines.
Stop and ask me if a test needs a definition that changes its meaning.
```

## Prompt 3 — which World3 variant (draft D-015)
```
Goal: gather the evidence for D-015 (which World3 variant F3's population sector is based on) and draft it. Follow CLAUDE.md.

WorldDynamics.jl v1.0.0 contains World3 (1974), World3_91 and World3_03 (2004, the variant in The Limits to Growth: The 30-Year Update). PyWorld3 implements only the 1974 model. Using the pinned environment audit/env:
1. List the differences between World3 (1974) and World3_03 that matter for F3: parameters, tables, structure, initial values, scenarios available.
2. Run World3_03 with default options; compare its main stocks and population with the 1974 run; report the differences as numbers.
3. Find out which variant is used in recent comparisons of World3 with data (for example Herrington 2021) and what the 1970-2025 data say. Cite primary sources; mark anything unverified.
4. Draft D-015 as Proposed with a recommendation, trade-offs and what each choice means for step 1.4 and for backtesting from 1970.

Done when: D-015 is drafted and pushed and you have summarised it in at most 12 lines. Do not mark it Approved.
```

## Prompt 4 — Python port of the World3 population sector (S1)
```
Goal: step 1.4 of docs/phase-1-plan.md. Precondition: D-015 is Approved. If it is not, stop and tell me.

Port the population sector of the approved World3 variant from WorldDynamics.jl (MIT; src/World3/...) to Python in f3/sectors/s1_population.py. Follow CLAUDE.md:
- Attribution: add the MIT licence text under licenses/ and an entry in NOTICE; put an attribution header in each ported file. Do not use PyWorld3 code.
- Document each equation with its source (Appendix A line numbers where WorldDynamics.jl cites them).
- Test in isolation: feed the inputs the sector needs (food, health services, pollution, industrial output, ...) as time series exported from the pinned Julia run, matched by variable NAME. Start the port from the same initial state as the reference. Compare with the reference trajectory; D-004 requires within 2%; report the actual figures.
- Handle the switched and discontinuous inputs explicitly (for example the 1940 switch); say how.
- Add tests/test_s1_population.py and a GitHub Action that runs the Python tests.
- Start-up conventions (see CLAUDE.md, PyWorld3 delay start) are documented separately from equation differences.

Done when: tests pass locally and in CI, STATUS.md is updated, and you have summarised the comparison in at most 12 lines.
Stop and ask me before changing any equation.
```

## Prompt 5 — automate reports and CI
```
Goal: remove the manual copy-and-paste loop. Follow CLAUDE.md.

1. Change .github/workflows/audit-t0.yml so a finished run commits its small report files (the *_report.md files and the version report, not data CSVs) to audit/runs/<date>-<run number>/ on main, with permissions: contents: write and a commit message that names the run. Avoid triggering itself in a loop.
2. Delete the flawed .github/workflows/audit-world3-pins.yml (its result is recorded in audit/T0-FINDINGS.md). Keep audit-world3-snapshot.yml as a record.
3. Add a small local runner (for example tools/run_world3_audit.py) that does what Prompt 1 does in one command.
4. Add a Python test workflow once f3/ exists.
5. Update audit/README.md and docs/STATUS.md.

Done when: a workflow run has committed its reports by itself and you have told me in at most 8 lines how to start an audit and where the results appear.
```

## Prompt 6 — verify the source register and research the gaps
```
Goal: make research/SOURCES.md reliable. Follow CLAUDE.md.

1. For each row marked "web search", open the primary document, confirm or correct the figures, add the URL, the version or date, and the licence or terms. Do not paraphrase beyond what the document says; keep quotations short.
2. Research the missing rows: (a) water use of data centers and chip fabrication; (b) inequality and social-stability data for S7 (World Inequality Database, ILO labour share, candidate historical proxies for the social-tension index, which is the open decision D-008). For each, say what is available, since when, at what resolution, and under what licence.
3. Check whether UN World Population Prospects 2026 has been published, whether Global Carbon Budget 2026 is out, and whether GATE has a newer version or public code.
4. Update research/SOURCES.md and draft D-008 evidence. Mark anything unverified.

Done when: every row has a primary-source URL or an explicit "could not verify", the file is pushed, and you have summarised what changed in at most 12 lines.
```

---

# Phase 2 prompts

Written 2026-10-08 from `docs/phase-2-plan.md` (approved, order B). Each prompt is one session or task. They follow the plan's milestones; the acceptance tests (A-numbers) are in the plan and were stated before the work. Every prompt starts with `CLAUDE.md` and `docs/STATUS.md`. **Each stops at its checkpoint for the editor-in-chief. A prompt marked "needs" must not start before that decision is approved.** The plan's milestones M0 to M2 are written out here in detail; M3 to M6 are listed with a pointer and are turned into full prompts when their predecessors are finished, so that they use what was learned.

## Prompt P2-M0 — carry-over and interfaces (done as far as the checkpoint)
Done in the session of 2026-10-08: the sector interface and coupling loop with S1 inside (A0.1, A0.2: `f3/core/`, `docs/coupling-interface.md`), the time-convention evidence (`docs/time-convention-evidence.md`), decisions D-020 to D-025 drafted as Proposed, the damage-function sources note (`research/damage-functions.md`), and the repository-map check (A0.5). **Waiting for the editor's checkpoint**: read the interface and D-020 to D-025. Remaining in M0 once approved: write the chosen time convention into `MODEL_SPEC.md` (A0.3), then close M0 in `docs/STATUS.md`.

## Prompt P2-M1 — S3 AI sector, GATE-like, standalone
```
Needs: D-005 amended with numeric criteria (plan A1.2) and approved; D-020 (start years) approved; D-022 (interface and time convention) approved.
Goal: milestone M1 of docs/phase-2-plan.md. Follow CLAUDE.md. Stop and ask before changing anything in a ported sector.

1. A1.1 first, before any code: extract GATE's equations and default parameters from the paper (arXiv:2503.04941 v2; the appendix tables give the defaults) into research/gate-equations.md, with the section of each. Establish what the sandbox at epoch.ai/gate can export (named presets? downloadable results?). If nothing can be exported, say so and propose the fallback A1.6 for the editor; do not start the comparison.
2. Write f3/sectors/s3_ai.py as a Sector of the coupling loop, with the behavioural investment rule of D-005. Carry the paper's defaults.
3. Run the plan's tests A1.3 to A1.6 and write the comparison report (as audit/s1-port-report.md was written: real runs, the reference's own error beside each figure).
4. Commit after each of the three steps.

Done when: the report is pushed and you have told me, in at most 10 lines, which of A1.3 to A1.6 passed, failed or were not run. Then STOP at the M1 checkpoint.
```

## Prompt P2-M2 — slice: AI, electricity, climate, and Demo 0
```
Needs: M1 checkpoint passed; D-007 (damage function) approved; D-021 (FaIR coupling and non-CO2 emissions) approved; D-022 approved.
Goal: milestone M2. Follow CLAUDE.md.

1. Add FaIR to the project environment (pin it). Run it alone first (A2.1): historical emissions from the sources D-021 fixes; observed-warming dataset added to research/SOURCES.md and verified before the test; uncertainty read from the dataset.
2. Data-centre electricity module (A2.2) against the IEA estimates for 2024 and 2025; the IEA 2030 figure is compared and reported, never a target.
3. S6 climate (FaIR as a sector with its period), the damage function with the three options of D-007, and the coupled slice. Tests A2.3 to A2.6.
4. Demo 0: a static page of precomputed runs, labelled "conditional scenarios, not forecasts", with the caveats listed in plan section 10. Do not publish; show the content to the editor (A2.7).

Done when: tests are run and reported, Demo 0 content is ready for review, and you have told me in at most 12 lines what passed and what did not. STOP at the M2 checkpoint.
```

## Prompts for M3 to M6 (to be written when each is next)
- **M3** complete World3 in Python: agriculture, capital, non-renewable resources, pollution. One sector per commit; the method of `audit/s1-port-report.md`; tests A3.1 to A3.5. No decision needed.
- **M4** the reused Earth4All sectors. Needs D-023 (inputs from replaced sectors) and, for the materials link, D-006. Tests A4.1 to A4.6; the step mismatch (Earth4All.jl solves at 1/64 year) is measured first.
- **M5** new modules: S7 social, S5 minerals and water, and any warming channels in replaced sectors. Needs D-006, D-008, D-024; the documentation-first rule (A5.1) applies. No dataset is committed before its licence is read from its own page (A5.6).
- **M6** integration and the Phase 2 review. Needs D-025 if it is to be used.

## Other open prompts (carried from Phase 1)
- **Prompt 5** (automation of audit reports and CI) in the section above can run at any time in parallel; note the audit-t0 workflow now installs two pinned environments.
- **Reading tasks the editor may be able to do faster than automated access can** (publisher sites refused): the full text of Herrington (2021)'s Supporting Information; the damage-function sections of Nordhaus (2017) or Barrage and Nordhaus (2024), Howard and Sterner (2017) and Burke et al. (2015); the LBNL data-centre report and TSMC sustainability report; the licence terms of WID and ILOSTAT.
