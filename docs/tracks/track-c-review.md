# Track C review: M4, reused Earth4All sectors (for the editor's batch review)

Branch `track-c` (not merged). Report: `audit/m4-earth4all-port-report.md`. Log and paste-ready drafts: `docs/tracks/track-c.md`. Suite: 217 passed, 21 skipped (pre-existing), 32 strict xfail.

## Provisional decisions (drafted as text in `docs/tracks/track-c.md`, not recorded)
1. **N4** follows D-023 option C (recorded series for sector tests, adapters later; none built beyond A4.5). Recommend approving.
2. **Euler with a 1/64-year internal sub-step** for the reused Earth4All sectors, by the rule written before the run (D-031 pattern; D-003 and D-022 untouched). Recommend approving: it is the only rung that reproduces the reference; it did not carry over to the coupled group (failure 1).

## Failures (nothing adjusted)
1. **A4.5 coupled economy fails, both scenarios** (strict xfail): GDP 2.227% (TLTL, first above 2% 2090.5) and 2.514% (GL, 2088.5); GDP per person the same; `GS` 2.149% / 2.877%, `PSP` 2.153% / 2.859%; `INEQ`/`INEQI` 3.234% in GL (first 2076.5; TLTL 1.12% passes); energy mix exact. Earth4All.jl's own error against Vensim for these: GDP p95 about 1.0%, `INEQ` p95 1.7%, maximum 1.96% / 2.00%. Members are exact alone; reading (inferred, untested): coupling lag among members; finer sub-steps are worse. Options: (a) a new decision for an ordered or iterated coupling inside the group (not in the plan, not tried; recommended, group-interface change only); (b) restate A4.5 as a labelled proposal (a relaxation, needs the editor); (c) accept as recorded. The gap is in the last decades (first above 2% from 2076.5 at the earliest); before that every economy variable is inside 2% in both scenarios.
2. **RK4 at the loop step exceeds 2% in 7 of 8 sectors** (recorded strict xfails S1/S2): the reference's own Euler error, not an F3 coupling effect; handled by the rule above. Output `OGR` 70% / 15%, inventory `IR` 7% / 11%, finance `ISR` 38%, labour market near-zero variables, public `RTFPUA` 2.5%, demand `CFWB` 11.8%, energy GL `FEP` 23%.

## Corrections of my own work (in the log)
- The first fixture had recorded inputs on a 1/16-year grid; the first S0 run failed in four sectors for that reason alone. I amended the export to the 1/64 grid after seeing the result; criteria, tolerance and rule were not changed. Labelled post-hoc in `docs/tracks/track-c.md`.

## Labels
- D-029 and D-030: this track shows no S3 or climate output; none added or removed. The warming channels are shown only with the recorded Earth4All.jl warming path; the D-023 baseline caveat (constant 1.35, F3's own baseline unchecked) is in the report and module headers. The channel sizes are not a damage estimate and do not use D-007.
- D-018: every comparison carries Earth4All.jl's own error against Vensim; the report says the port is measured against Earth4All.jl and does not reproduce Vensim where Earth4All.jl does not.

## Findings to record
- **"other"** (D-016: not assessed): only `CTA` is read by another sector (public: TFP loss from unprofitable activity; demand: extra taxes). The rest are indicators. Ported; exact. Its input `COFO` comes from the replaced foodland sector (no World3 equivalent: open for M6).
- A4.2 limit: Earth4All.jl has no off-run, so "off still passes A4.1" is established up to 2022 only.
- A4.4: T2 met on the port with Earth4All's own population (maximum WF/WAP 0.8144 / 0.8251); World3-cohort re-test and S3 effect belong to M6.
- `IC2022` ramp end `2020 + IPP` copied as in Earth4All.jl; Vensim not checked. Active in GL only.
- Demand: 16 (TLTL) and 13 (GL) variables deviate from Vensim above 2% (p95 or maximum) in Earth4All.jl itself; D-004 not relaxed.

## Recommendation
Approve the two Provisional decisions; decide option (a) for A4.5 before M6 builds on the economy; merge track-c if the suite is green apart from the documented strict xfails.

## Not done
Adapters beyond A4.5, M5, water, minerals, S3 coupling, Phase 3. The Gauss-Seidel or iterated coupling was not tried (not in the plan).
