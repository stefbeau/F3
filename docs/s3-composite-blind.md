# Brief: blind re-derivation of S3's task-allocation composite (the A1.3 gap) (D-053 B; written 2026-10-21; NOT RUN)

**Status:** a brief only. Nothing here has been run, and no agent has been started. It exists so that the editor can approve the exact information boundary before any run. S3's current composite stays as it is and stays recorded as failed (A1.3, D-027 outcome ii).

## 1. The gap, in one paragraph

S3 reproduces GATE's laws of motion for compute, hardware, software, capital and automation to 1e-15 to 1.5e-3 when Epoch's stored composite task input `T` (field `cognitive_ces_term`) is supplied (`audit/s3-gate-comparison.md` section 3). With S3's own composite the output is 5.7% low in 2027 and the gap compounds to 100% by 2051. So the whole A1.3 failure is the step that turns labour `L`, the automated fraction `f`, the runtime compute `C_I` and the largest training run `C_T` into `T`: the task allocation of eqs. 14 to 16 and footnotes 38 and 39 of the paper. Two variants of the discretisation (20,000 midpoints; the paper's 20/100-point grids; a 101-point case) failed in the same years (`research/gate-equations.md` section 10). The cause is unresolved.

## 2. What a blind agent may see, and may not

**May see (the only inputs):**
- The paper, arXiv:2503.04941 **v2** (CC BY 4.0), the full text including Appendix C (solving the model) and Appendix D (inputs). The agent fetches it itself.
- The **parameter values** of the playground default and of the two other shipped settings **as a table of the model's inputs** (`T_oom`, `r_H`, `r_S`, `lambda`, `gamma_0`, `gamma_1`, `m`, `iota_max`, `rho`, `alpha`, `L0`, `K0`, `Y0`, `C_L`, `C_T0`, `delta_f`, `f_init`, `runtime_compute_init`), which are the paper's own Appendix D numbers and the three settings of D-005 amendment B. No output value.
- The **starting values at 2025** (the paper's Table of initial values): labour, capital, GWP, largest training run, initial runtime compute.
- The task: "Implement, from the paper alone, the function that returns the composite task input `T` given `L`, `f`, `C_I`, `C_T` and the parameters. Document every reading of an ambiguity."

**May NOT see:**
- **Any S3 code or F3 file** (`f3/sectors/s3_ai.py`, the composite variants A, B, C101), `research/gate-equations.md`, `audit/s3-gate-comparison.md`, or any F3 document describing what was tried.
- **Any Epoch value**: no stored series (`cognitive_ces_term`, the stored per-task allocation, `runtime_compute`, `compute`, `gwp`), nothing from the playground bundle, no screenshot or number from the playground page.
- Epoch's posts and any third-party reproduction or code of GATE.
- Any statement of how large the A1.3 gap is, or in which direction.

**Mechanism.** The agent is started fresh with a brief that contains only the lists above, in a working folder outside the repository that holds no F3 file. It returns one file (the function and a text of its readings) plus, for a set of **inputs specified by the editor in advance** (see section 3), the values it computes. It never learns the comparison result.

## 3. What is compared afterwards (fixed before the run)

By a **separate** step, after the agent has returned and its output is frozen (hash recorded):
1. **Input points.** The period-0 and period-1 inputs of the default run (where `T` matches S3's to 0.1% to 0.3%, and the stored allocation is known to reproduce `T` to 3e-4), and the inputs at periods 2, 5, 11 and 20 of each of the three settings, taken from the stored runs by the comparing step (the blind agent is given only the numbers `L, f, C_I, C_T` at those points, not their source or any `T`).
2. **Criterion.** The blind `T` equals the stored `cognitive_ces_term` within **0.1%** at every point (the first two periods already agree to 0.3% for S3's own composite, so 0.1% separates a real fix from the present state), **and** S3 with the blind composite substituted for its own passes A1.3 (2% at every period, three settings). Both are required; neither tolerance is changed after the result.
3. **Comparison with S3's own composite**: at the same points, the blind `T` against S3's `T`, to see whether they differ and where, **before** any reading of why.
4. **Outcomes, pre-registered:** (i) the blind `T` matches the stored one: the cause is identified by diffing the blind readings against S3's (a labelled, post-hoc proposal to the editor, not applied automatically); (ii) the blind `T` matches S3's and not the stored one: two independent readings agree and differ from Epoch's, so the paper alone does not determine Epoch's composite, and the case for pressing Epoch (the email was sent on 2026-10-17, no reply as of 2026-10-22) is strengthened; (iii) the blind `T` matches neither: reported as such.
5. **What the result cannot say:** that the stored `T` is correct, or that the paper is complete. A match shows the paper is sufficient; a mismatch shows only that this reader could not reproduce Epoch's solver from it.

## 4. Cost

- **Agent run:** one fresh agent, a long task (Appendix C is dense): roughly 150,000 to 400,000 tokens of model work, and a few hours of wall-clock; a second independent agent doubles it and is recommended only if the first is inconclusive.
- **Comparison step:** small (a script, about 20,000 tokens, seconds of compute).
- **Compute:** the composite solver at 20,000 midpoints is the slow part; one full-grid evaluation takes seconds, so the whole comparison is minutes.
- **Total:** about half a working session of tokens; no external cost; no data leaves the machine except the fetch of the public paper.
- **Risks:** the blind agent may reproduce the same ambiguity choices S3 made (outcome ii); the 101-entry stored grid versus the paper's 20/100-point footnote may make an exact match impossible by design; the agent may use search to find third-party GATE code, so the brief forbids it and the output is checked for citations of anything but the paper.

## 5. What this does not do

It does not change S3, the A1.3 record, or any label. It does not ask Epoch (the editor already wrote to Epoch on 2026-10-17 through epoch.ai/contact; no reply as of 2026-10-22). **Editor decision 2026-10-22 (D-054): this brief is NOT run now and is kept as a brief; A1.3 stays failed and labelled.**
