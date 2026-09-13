# Reliability Audit

**Audit date:** 13 September 2026  
**Scope:** PricePulse MVP backend, deterministic workflow, and frontend production build.

| Check | Result | Evidence |
| --- | --- | --- |
| Official-source provenance | Pass | Loader has only official PriceCatcher URLs; live smoke check retrieved all three source files. |
| Fabricated / hard-coded data | Pass | UI begins empty and receives results only from API payloads; fixture values live only in tests. |
| Unit and item safety | Pass | Scope requires one `item_code`; series requires a verified unit and records exclusions. |
| Future-data leakage | Pass | Baselines, lag features, and rolling features consume only preceding qualified values; test covers future-price invariance. |
| Random temporal split | Pass | Forecast partitions are chronological and tested for non-overlap. |
| Baseline fairness | Pass | Ridge is selected only when it improves validation MAE and does not worsen validation RMSE; final test is not used for selection. |
| Anomaly evidence | Pass | Modified z-score/MAD runs only on coverage-qualified, held-out residuals. |
| Claim boundary | Pass | Critic rejects prohibited causal, inflation, recommended-price, and wrongdoing language; reporter requires critic approval. |
| Secret exposure | Pass | No secret or external-model configuration is included in the browser bundle. |
| Error handling | Pass | API returns bounded validation/source errors and UI exposes retry/error states. |
| Backend tests | Pass | 19 fixture and workflow tests passed. |
| Frontend build | Pass with non-blocking warning | Production build passed. Recharts produces a 593 kB uncompressed main bundle; code-splitting is a future performance optimisation, not an MVP correctness failure. |

## Live-source smoke checks

- Current official September 2026 transaction file: 620,488 loaded rows, 1–12 September 2026 date range.
- Data quality result: `PASS_WITH_LIMITATIONS`; unmatched/missing-unit lookup rows were surfaced as limitations, not repaired.
- Bounded real workflow for item code 1, national scope, 1 August–12 September 2026: 41 daily points, baseline selected, zero qualified anomalies, critic `PASS_WITH_LIMITATIONS`.

## Remaining declared limitation

The workspace sandbox prevents package managers from writing build artifacts into the repository itself. Tests and production compilation were therefore executed in isolated temporary environments using the repository source unchanged. A normal local checkout can use the commands in `README.md` to install dependencies in place.
