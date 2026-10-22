# DRAFT (finalised 2026-10-12). CORRECTION 2026-10-22: the editor sent an email to Epoch on 2026-10-17 through epoch.ai/contact (no reply as of 2026-10-22). The text actually sent is not in the repository; this file is the prepared version.
#
# Traceability of every number below: audit/s3-gate-comparison.md (sections 2, 3, 7), audit/data/s3-gate-comparison.json, research/gate-equations.md (sections 9.1, 9.2, 10), DECISIONS.md D-026 and D-027.

Subject: GATE playground: how is the task-level allocation of labour and runtime compute computed? (and a permission question)

Hello,

I'm Stéphane Beau, working on F3, an open-source model (github.com/stefbeau/F3) that couples AI-transition economics with planetary-limits models. I re-implemented GATE's laws of motion, automation and production from the paper (arXiv:2503.04941 v2) and tested the result against the three runs the playground ships (default, conservative, aggressive), feeding in each run's own investment shares. Most of it matches closely. One step does not, and I would be grateful for your help with it.

1. The per-task allocation. Everything matches the three shipped runs (output, capital, hardware, software, compute stock, automation; each within about 0.15%) when I feed in the playground's own cognitive_ces_term period by period. With my own computation of that term, output drifts from the shipped runs from 2026 to 2027 (for example 5.7% low in 2027 in the default run) and the gap compounds. So the difference is entirely in how the composite of tasks is computed. I implement eqs. 15, 16, 26 to 28 and footnote 39 as: runtime requirement R_i = max(1, f^-1(i)/C_T)^m x 10^(gamma_0 + gamma_1 i), with C_T the largest training run at the start of the period; labour and runtime compute are then allocated across tasks to maximise the CES composite. Could you tell me where this differs from what the playground does (the definition of R_i, which C_T it uses, the objective or constraints of the allocation)? I have ruled out the discretisation: the paper's footnote-38 grids (20 points for digital workers, 100 for humans and the integral), a single 101-point grid (the size of each stored compute_allocation) and a fine grid of 20,000 points all give the same failures.

2. Is the stored "compute" field the raw compute stock Q, before the cap g(Q)? That is what I measured (Q[k] = Q[k-1] exp(-delta_Q) + I_q[k] H[k-1] holds to 1e-15 in all three runs), and I want to be sure I read it correctly.

3. Permission: may I use the numerical results of the three shipped runs as test references? I would read them at test time from a local copy of the public script (checked against its sha256), store only comparison figures (differences and first-year indices), and not redistribute the series or commit any part of the file. If you would rather I did not, I will keep to that. Separately, could you share result series for two settings I would like to test, T = 1e41 eFLOP with lambda_H = lambda_S = 0.25, and T = 1e33 eFLOP with lambda_H = lambda_S = 1, all other parameters at their defaults?

4. Is a newer version of the paper or the model, or published source code, planned?

Thank you; the paper and the playground are very useful. I am happy to share the comparison results and the F3 code once they are in better shape.

Best regards,
Stéphane Beau
