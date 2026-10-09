# UNSENT DRAFT, saved 2026-10-08. The editor chose not to send it yet. Check the contact address on the playground page (research/gate-equations.md names info@epoch.ai) before sending.

Subject: GATE playground: permission to use shipped results as test references, and a few questions

Hello,

I'm Stéphane Beau, working on F3, an open-source model (github.com/stefbeau/F3) that couples AI-transition economics with planetary-limits models. I am re-implementing GATE's AI-development module from the paper (arXiv:2503.04941, CC BY 4.0) and want to test it against GATE itself.

While checking what the playground can export, I saw that the page includes three precomputed runs (default, conservative, aggressive), and that it exports parameters as JSON and charts as PNG. I have a few questions:

1. May I use the numerical results of those three runs as test references in a public repository, with attribution to Epoch AI? If you would rather I did not redistribute them, I will keep them out of the repository and publish only comparison figures.

2. Could you share result series (CSV or similar: investment shares, effective compute, automation fraction and output, 2025 to 2100) for two parameter settings I would like to test? Setting 1: T = 1e41 eFLOP with lambda_H = lambda_S = 0.25. Setting 2: T = 1e33 eFLOP with lambda_H = lambda_S = 1. All other parameters at their defaults.

3. So that I compare like with like: is stored period k the end of year 2025+k, with automation lagging the training run by one period? And for runs where compute approaches the heat limit C_L, what is the law of motion for effective compute (the paper says "plus appropriate product-rule terms")?

4. Is a newer version of the paper or the model, or published source code, planned?

Thank you; the paper and the playground are very useful. I am happy to share the comparison results once they are done.

Best regards,
Stéphane Beau
