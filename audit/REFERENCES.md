# F3 — Pinned references

Every external model F3 audits or ports from, pinned to an exact version. Updated only after an approved audit run.

| Reference | Role | License | Pinned version | Status |
|---|---|---|---|---|
| WorldDynamics.jl | World3 reference (D-012) | MIT | v1.0.0 | Pinned |
| Earth4All.jl | Earth4All reference for audit (D-011) | MIT | Commit hash to record from the first T0 run | ⏳ Pending first run |
| PyWorld3 | Independent World3 second check, used unmodified (D-001, D-012) | CeCILL 2.1 | Version to record from the first T0 run | ⏳ Pending first run |
| Julia | Runtime | MIT | 1.10 (LTS); exact patch version recorded per run | Pinned to 1.10 series |

## How a pin is updated

1. Run the audit workflow with the new version or commit.
2. Review the results.
3. Add a decision entry if results change, then update this table.
