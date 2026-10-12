# S3 investment rule: candidates and a recommendation (M1 step 4; for the editor's choice)

**Status:** written 2026-10-12. **No rule is implemented.** S3 takes six shares per year as input (`q_consumption`, `q_compute`, `q_capital`, `q_hardware_rnd`, `q_software_rnd`, and the training share of usable compute). D-005 replaces GATE's planner with a behavioural rule; this note lays out what the rule has to produce and three ways to build it. The choice is the editor's.

## 1. What the shipped investment shares show (the A1.4 evidence)

Read from the three shipped runs at test time (D-026; only summary figures are written here). These are the outputs of a solver that stopped at tolerance 0.02 after at most 40 iterations, so small features, such as the conservative run's late software R&D share of about 5%, may be solver noise and not economics. This is **evidence about what a rule must reproduce, not an A1.4 comparison**: A1.4 compares a rule with GATE's path and needs a rule to exist.

| | default | conservative | aggressive |
|---|---|---|---|
| AI share of output in 2025 (compute + hardware R&D + software R&D) | 24.0% (its peak) | 24.9% (peak 27.7% in 2098) | 21.8% (its peak) |
| compute share of output, 2025 / peak | 9.6% / about 15% (2030 to 2033) | 9.2% / 17.6% (2037) | 9.7% / about 12% |
| hardware + software R&D share, 2025 → 2035 | 14.4% → 2.4% | 15.7% → 3.5% | 12.2% → 2.5% |
| capital share | about 0.1% until 2030, then 9% to 33% | 0.3% until 2029, then 10% to 28% | 0.1% until 2029, then 8% to 30% |
| year automation reaches 100% | 2034 | 2040 | 2028 |
| training share of usable compute | 90% (2025), about 68% to 2033, below 20% from 2039, 1.3% by 2041 | 89%, about 69%, below 20% from 2048, 3% later | 66%, below 20% from 2030, 1.1% by 2033 |
| consumption share | 57% to 86% | 55% to 83% | 64% to 87% |

What this suggests (inference from the shipped shares, not a tested claim):
1. **The front-loaded AI push is large and short.** Roughly a fifth to a quarter of output goes to AI inputs in the first year, with R&D shares falling about six-fold within ten years. The planner pays for R&D while automation is incomplete and stops once `f` is near 1.
2. **Compute spending tracks automation, with a lag.** The compute share rises from about 9% to 15% as `f` goes from 0.1 to 0.7 and then falls to about 0.1% once the compute stock nears its usable limit (`g(Q)` flattening against `C_L`) and the marginal return collapses.
3. **Capital investment is switched on late.** It is near zero until automation is high, then jumps to 20% to 30% of output. A rule that gives capital a fixed share from 2025 would be wrong in the first decade.
4. **The training share is a regime switch.** About two-thirds of compute goes to training while tasks remain to automate; once `f = 1` nearly everything goes to runtime.

## 2. Candidate rules

All three keep S3's equations unchanged and only generate the six shares. None uses GATE's optimiser.

**R1: automation-indexed schedule.** Each share is a function of the current automated fraction `f` (and, for the training share, of `f` only), taken from a small table or a piecewise-linear curve fitted to the three shipped runs. *For:* simplest, reproduces the shape above, reacts to the model's own state so it moves under different parameters, easy to explain on a dashboard. *Against:* it hard-wires GATE's planner behaviour as a table; it has no economic lever, so policy or race-dynamics scenarios cannot move it except by editing the table; extrapolation outside the three fitted runs is untested.

**R2: return-driven allocation.** Spend on each AI input in proportion to an estimate of its marginal return (the shipped runs store a Tobin-q-like `tobin_q_compute`; marginal returns to hardware and software R&D follow from eq. 4 and 6), with an overall AI budget cap and a smoothing delay. *For:* closest in spirit to the planner, so it should generalise across parameter settings and stops spending when returns collapse; *Against:* needs marginal-return formulas that I have not verified against what the solver uses, the stored Tobin's q is a single series and one of its definitions is unknown to me, and it is the hardest to calibrate and explain. It risks reintroducing a mini-optimiser through the back door.

**R3: AI-race budget.** A policy-style rule with named levers: an overall AI share of output `s_AI(t)`, a split into compute, hardware R&D and software R&D, a capital share that rises with `f`, and a training share that falls with `f`. `s_AI` starts near the initial 20% to 25% and decays as `f` approaches 1 or as `g(Q)` nears `C_L`. The levers (initial `s_AI`, decay speed, split) are exposed as scenario parameters, calibrated once to the shipped runs. *For:* gives the dashboard the levers the project wants ("how a fast AI race interacts with energy, materials, water..."); *Against:* more parameters than R1; calibrating to three non-converged runs risks overfitting; the lever values are judgement.

## 3. Recommendation

**R3 with R1's fitted curves as its default calibration.** The project's purpose is conditional scenarios in which the pace of the AI race is a lever; R1 alone has no lever and R2 is too uncertain to build on now. Concretely: fit the six shares as functions of `f` and of `g(Q)/C_L` to the three shipped runs (R1), then expose the overall AI share, its decay and the split as scenario parameters (R3). Test it the way A1.4 says: report only, with the largest and mean relative difference of shares, effective compute and output against each shipped run and the first year each exceeds 5% and 10%.

Two caveats the editor should weigh before choosing:
- **A1.3 failed (`audit/s3-gate-comparison.md`).** Any rule is run on top of S3's production composite, which currently differs from the shipped runs by a lot after 2027. A1.4 differences will therefore mix the rule's error with that open difference. Settling the composite first, or reading A1.4 only on quantities that do not depend on it (compute stock, hardware, software, automation, given the stored `T`), keeps the two apart.
- **The shipped paths are solver outputs, not converged optima**, and only three exist. Calibrating a rule to them calibrates to Epoch's playground, not to a truth about investment behaviour.

## 4. Decision needed

Which rule (R1, R2, R3 as recommended, or something else), and whether to settle the A1.3 composite question first. Nothing here has been implemented.
