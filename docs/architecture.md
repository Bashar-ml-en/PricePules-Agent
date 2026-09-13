# PricePulse MY Architecture

```text
Official PriceCatcher CSVs
        |
        v
Loader + validation -----------------------------------+
        |                                              |
        v                                              v
Unit-safe daily price series                  Data Quality Agent
        |
        v
Chronological baseline -> optional Ridge -> residual anomaly scoring
        |                                              |
        +-------------------+--------------------------+
                            v
               Price Signal + Market Scope Agents
                            |
                            v
                    Reliability Critic
                            |
                            v
               FastAPI structured response / SQLite
                            |
                            v
             React evidence dashboard (no direct secrets)
```

## Responsibilities

| Layer | Responsibility |
| --- | --- |
| Loader and validation | Download/cache official files, validate contract, and record exclusions. |
| Analysis | Build one-item, one-unit daily series; run leakage-safe chronological evaluation and robust residual scoring. |
| Agents | Interpret typed tool outputs, gate claims, and expose limitations. |
| API | Orchestrate analysis, return structured evidence, and persist concise completed run data. |
| Dashboard | Let the user select scope and inspect provenance, evidence, models, anomalies, critic verdict, and limitations. |

## Storage and secrets

SQLite is sufficient for the MVP's analysis metadata, metrics, anomalies, and agent decisions. Source data is fetched server-side. The browser never receives a secret, and no external AI provider is required.
