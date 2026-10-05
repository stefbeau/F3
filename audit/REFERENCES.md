# F3 — Pinned references

Every external model F3 audits or ports from, pinned to an exact version. Updated only after an approved audit run.

| Reference | Role | License | Pinned version | Status |
|---|---|---|---|---|
| WorldDynamics.jl | World3 reference (D-012) | MIT | v1.0.0 | ⚠️ Default solve fails (`InitialFailure`) with current dependencies; works with `initializealg = NoInit()` (T0 run #4); under validation, see T0-FINDINGS.md |
| Earth4All.jl | Earth4All reference for audit (D-011) | MIT | Commit `16f37d013a2f68135f03e7815bf861dbf47311f2` (branch `master`), observed in T0 run #2 | 🟡 Runs; see T0-FINDINGS.md |
| PyWorld3 | Independent World3 second check, used unmodified (D-001, D-012) | CeCILL 2.1 | 1.1, observed in T0 run #2 | 🟡 Runs; see T0-FINDINGS.md |
| Julia | Runtime | MIT | 1.10 series; 1.10.12 in T0 run #2 | Pinned to 1.10 series |

## How a pin is updated

1. Run the audit workflow with the new version or commit.
2. Review the results.
3. Add a decision entry if results change, then update this table.
