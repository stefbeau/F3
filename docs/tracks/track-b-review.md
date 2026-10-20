# Track B review (M3, complete World3 in Python), for the editor's batch review

Branch `track-b`, 2026-10-20. Full figures: `audit/m3-world3-port-report.md`; log and paste-ready Provisional blocks: `docs/tracks/track-b.md`. Nothing merged; shared files untouched.

## Failures (size and first year; criteria not relaxed)
| test | result |
|---|---|
| A3.2 full run, 1974 | FAILED: worst `lufd` 6.90%; 15 of 29 states above 2%; first failure 2023.5 (`fcfpc1`) |
| A3.2 full run, 2004 | FAILED: worst `lufd` 7.96%; 16 of 29 above 2%; first failure 2023.0 (`fcfpc1`) |
| A3.3 PyWorld3, 1974, start-up matched | FAILED: `ic` 3.39%, `sc` 2.42% (2100); the other ten within 1.6% |
| A3.4(b) S1 in full run vs alone (0.25%) | FAILED, predicted in advance: 4.36% (1974, `aiopc`), 3.69% (2004, `fcfpc1`); above 0.25% from 1900.5 |

Met: A3.1 (all 14 states of the four sectors within 0.124%), A3.4(a) (existing tests pass), A3.5 (measured: 0.59 s per run at step 0.25). A3.3 for 2004 is diagnostic (all twelve within 2.4%).

Cause: not the reference's solver (its own default-vs-tight difference is at most 1.61% / 0.26%) and not the equations (each sector alone within 0.13%). It is first-order explicit coupling at step 0.25 (D-022). A post-hoc scan shows the worst state falling 6.9 -> 3.2 -> 1.6% (1974) and 8.0 -> 3.9 -> 1.9 -> 0.9% (2004) as the loop step goes 0.25 -> 0.125 -> 0.0625 -> 0.03125, with no state above 2% from 0.0625. This is a measurement, not a changed criterion.

## Labels
- 2004 PyWorld3 comparison: diagnostic, not independent (parameters overridden on an instance).
- PyWorld3 pollution start-up match: labelled runtime diagnostic; the as-shipped `ppol` gap (373%) is shown beside it.
- D-029 and D-030 labels: this track shows no S3 or climate output; none added or removed.

## Provisional decisions drafted (paste-ready text in `docs/tracks/track-b.md`)
P1 module names and structure; P2 the A3.2 failure is recorded and nothing repaired; P3 initial outputs of the coupled sectors.

## What I recommend the editor decide
1. The A3.2 failure (I applied none of these): (a) run the full World3 at loop step 0.0625 (A3.2 would pass both sets, 2.3 s per run), which amends D-003 for this model; (b) predictor-corrector coupling (the D-022 alternative); (c) accept the failure and restate A3.2 and A3.4(b) as a labelled post-hoc proposal. Recommendation: (a) or (b) before M4 builds on the loop. D-022 said the error with live partners was unknown; it is now measured at up to 8%.
2. A3.4(b)'s 0.25% was not tested below step 0.0625 for S1 inside the full run; at 0.0625 the S1 gap has not been separately measured.
3. Approve P1 to P3, or reverse (cost small).
4. The plan's run-time guess (5-10 s) was too high; at 0.59 s per run a thousand-run Monte Carlo is about 10 minutes on one core (World3 only, no FaIR, S3 or Earth4All).

Unverified: the 21 skipped tests are pre-existing, not from this track; CI was not run.
