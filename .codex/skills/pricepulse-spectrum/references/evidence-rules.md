# Evidence and modelling rules

## Official sources

- Transactions: `https://storage.data.gov.my/pricecatcher/`
- Item lookup: `https://storage.data.gov.my/pricecatcher/lookup_item.csv`
- Premise lookup: `https://storage.data.gov.my/pricecatcher/lookup_premise.csv`

Inspect the actual files and metadata before fixing filenames, date coverage, or field names in code. Preserve verified source URLs and dates in application outputs.

## Required boundaries

- PriceCatcher is local, high-frequency price-surveillance data. It is not a representative consumer-price index; do not label a result inflation.
- A high price, large residual, or an outlier is not evidence of a cause or merchant wrongdoing.
- Never silently repair, impute, or discard source data. Record exclusions and their reasons.
- Every displayed claim needs a source field or deterministic calculation behind it.

## Leakage-safe time series

- Process one official `item_code` and its documented unit at a time.
- Aggregate price observations to a daily median only after applying the explicit selected geography filter.
- Include transaction and distinct-premise counts with every daily estimate.
- Do not create a prediction or anomaly for a date that fails configurable coverage gates.
- A baseline and features for date `t` may use only observations before `t`.
- Split training, validation, and final test periods chronologically. Never randomize rows or tune on the final test period.
- Calculate MAE and RMSE deterministically. Retain the baseline when the eligible ML model does not outperform it on validation.
- Detect anomalies from out-of-sample residuals using a documented robust threshold such as MAD. Return the score, threshold, method, coverage, and limitations.

## Approved language

Approved: "Observed price is materially above the historical expectation and qualified coverage meets the configured threshold; conduct a human price-surveillance review."

Rejected: statements declaring inflation, a cause, a supply shortage, a recommended price, or misconduct.
