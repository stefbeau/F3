# F3 — Foundation for Earth

**An open global model of how the AI race interacts with the planet's limits and society's stability.**

> **Status:** Phase 0 complete · Phase 1 (Reproduce & audit) planned · v0.1 specification in draft
> F3 is under construction. No results are published yet.

---

## Why F3?

For fifty years, models like **World3** (*The Limits to Growth*, 1972) and its successor **Earth4All** have explored how population, economy, resources, pollution and climate interact. Separately, newer models such as **GATE** (Epoch AI, 2025) explore how AI compute and automation could accelerate economic growth.

These two families rarely meet. Yet the AI race already depends on electricity, minerals and water, and automation is already reshaping who earns what. F3 brings both families into one set of feedback loops, so we can explore questions such as:

- Can energy and materials supply keep up with a fast AI build-out?
- What happens to inequality and social stability if automation gains are not shared?
- Which combinations of policies lead to a stable, prosperous transition, and which lead to overshoot?

## What F3 is not

**F3 does not predict the future.** It produces **conditional scenarios**: *if* these assumptions hold, *then* these trajectories follow, within these uncertainty ranges. Its purpose is to show which levers matter most, not to forecast a date.

## The model at a glance

Seven coupled sectors, running yearly from 1970 to 2100:

| Sector | Based on |
|---|---|
| S1 Population | World3 |
| S2 Economy & capital | Earth4All (after audit), GATE |
| S3 AI development & automation | GATE |
| S4 Energy (incl. data centers) | Earth4All, extended with material limits |
| S5 Materials & water | World3, extended |
| S6 Climate | FaIR |
| S7 Social stability & well-being | New F3 module (informed by Earth4All, structural-demographic theory) |

Full details: [MODEL_SPEC.md](MODEL_SPEC.md)

## How F3 is built

1. **Reproduce and audit** existing models before changing anything.
2. **Couple** the AI sector to energy, materials, water and society.
3. **Calibrate** against observed data from 1970 to today, and quantify uncertainty.
4. **Publish** an online dashboard where anyone can run scenarios.

Every assumption is recorded and approved in [DECISIONS.md](DECISIONS.md).

## Roadmap

| Phase | Goal | Status |
|---|---|---|
| 0 — Setup | Repository, specification, decision log | ✅ Done |
| 1 — Reproduce & audit | World3 sectors in Python; Earth4All audited | 🟡 Planned ([plan](docs/phase-1-plan.md)) |
| 2 — Couple | AI sector linked to energy, materials, society | ⚪ Not started |
| 3 — Calibrate | Backtest and uncertainty analysis | ⚪ Not started |
| 4 — Publish | Public scenario dashboard | ⚪ Not started |

## Repository structure

```
research/     Source-model notes and citations
data/         Raw and processed datasets, with one data card each
f3/           Model code (sectors, coupling, scenarios)
tests/        Reproduction tests and backtests
notebooks/    Exploratory analysis
docs/         Methodology documentation
dashboard/    Public scenario dashboard (Phase 4)
```

## Standing on the shoulders of

- Meadows, D. H., Meadows, D. L., Randers, J., & Behrens, W. W. (1972). *The Limits to Growth*.
- Dixson-Declève, S., Gaffney, O., Ghosh, J., Randers, J., Rockström, J., & Stoknes, P. E. (2022). *Earth for All: A Survival Guide for Humanity*.
- Epoch AI (2025). *GATE: An Integrated Assessment Model for AI Automation*. arXiv:2503.04941.
- Leach, N. J., et al. — FaIR climate emulator.
- Vanwynsberghe, C. — PyWorld3, a Python implementation of World3.

## License

- Code: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- Documentation and processed data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Third-party data keeps its original license, recorded in each data card.

See D-001 in [DECISIONS.md](DECISIONS.md).

## Maintainer

Stéphane Beau · [github.com/stefbeau](https://github.com/stefbeau)
