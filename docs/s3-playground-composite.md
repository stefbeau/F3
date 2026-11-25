# S3 variant P: the playground's production block (D-062)

**Status:** reading and tests written on 2026-11-25 **before** variant P was added to `f3/sectors/s3_ai.py` and before any closed-loop run. Results go to `audit/s3-playground-composite.md`. Nothing here changes a criterion, a tolerance or a label.

## What was already seen when this was written (stated so that it is not mistaken for a blind test)
On 2026-11-25 a stand-alone re-implementation of the composite step, fed each run's **own stored states** period by period, reproduced the stored `cognitive_ces_term` of the five runs Epoch sent to a largest relative difference of 1.1e-12 (80 periods each). That was **the composite step alone**. It is the reason the variant is worth building. **Not seen when this was written:** any run of S3 itself with variant P, in which S3's own states feed the composite and errors can compound.

## Source
Reply of Anson Ho (Epoch AI) to the editor's email of 2026-10-17: a description of the playground's implementation with code excerpts, and five runs produced with Epoch's solver (the three presets regenerated, plus T = 1e41 eFLOP with lambda = 0.25 and T = 1e33 eFLOP with lambda = 1). **Neither the excerpts nor the runs are in this repository** (D-026). Variant P is F3's own code written from the description.

## How the playground differs from the paper's equations (and from variants A, B and C101)
1. **The inverse f^-1 is tabulated, and rounded down.** f is evaluated on 300 equally spaced points from log10 C_T(0) - 5 to log10 T + 5; points where f does not increase are dropped; a task's training requirement is the grid point **below** the exact value. Tasks above the frontier therefore get a smaller runtime requirement than eq. 15 with the exact eq. 16.
2. **The planner searches a grid of cutoffs.** It tries cutoffs i/200 not above f, takes a geometric interpolation of the two neighbouring cutoffs at f itself, and keeps the largest composite. It does not automate every task that can be automated.
3. **No joint allocation.** Below the cutoff only AI works, with compute shared by the CES first-order condition; above it only humans work, spread evenly. Humans are never placed on automated tasks. (Variants A, B and C101 solve the joint allocation of footnote 39.)
4. **Integral.** A left Riemann sum on 1000 points. The playground uses 200 and 1000 where the paper's footnote 38 says 20 and 100.
5. **Timing.** Production in a period uses labour, software and the best training run **at the start of the period**, and the runtime compute **chosen in the previous period** multiplied by the start-of-period software level. The automated fraction is the current period's (as already in S3).

Confirmed by the reply, and already how S3 reads it: the stored `compute` field is the raw stock Q before the cap g.

## What variant P is in F3
`GateParams(composite="P")`. Constants `PG_INVERSE_POINTS = 300`, `PG_SEARCH = 200`, `PG_INTEGRAL = 1000`. **The default stays "A".** Nothing that uses S3 today changes. Variant P is not used by R3, the slice, the integrated loop or the site.

## Tests and readings, fixed now
**T1 (needs the pinned bundle, D-026; the A1.3 criterion, unchanged).** S3 with `composite="P"`, driven by each shipped run's own investment shares: every quantity that counts in A1.3 within 2% at every period end, indices 0 to 75, for the three settings of D-005 amendment B. Same helper, same list of quantities and same tolerance as `test_a13_criterion`. Written as a plain assertion: if it fails, that is recorded as a failure, with the first index and quantity.

**T2 (the runs Epoch sent; local, never committed).** `audit/t0/s3_playground_check.py` with `F3_GATE_RUNS` pointing at the unzipped runs: the same comparison and the same 2% for all five runs. Reported per run: pass or fail; the largest relative difference per quantity and its index; the composite and the two shares (reported, not in the criterion, as in A1.3). Only these figures are stored (`audit/data/s3-playground-composite.json`).
- T2 is **not** A1.3: Epoch's note says the three regenerated presets equal the shipped series to about 1e-16, which **has not been checked here**. A1.3 is T1.
- The two extra settings have no pre-set criterion in D-005 (they are "report-only stress runs"); the 2% reading is applied and reported, and decides nothing.

**T3 (no reference data).** (a) With f = f_init and negligible compute the composite equals labour. (b) The tabulated inverse never exceeds the exact one. (c) The composite does not fall when compute rises, other inputs fixed. (d) The default composite is still "A".

## What a pass would and would not mean
- A pass of T1 would mean: **given GATE's own investment path, S3 with variant P is within 2% of the playground's shipped runs for the quantities of A1.3.** It would not mean that F3 "reproduces GATE": the investment path is supplied, not solved.
- It would not change the default, remove the D-029 label, or validate R3. Each of those is a separate decision for the editor.
- It says nothing about the size of S3's compute and electricity under R3 (`docs/STATUS.md`, "To revisit after the Epoch reply", item 4).

## Later on 2026-11-25
D-063 changed the reference of T1, D-064 the compute row that counts, and D-065 made variant P the default (so T3(d) now checks that the default is "P"). The text above is left as written.
