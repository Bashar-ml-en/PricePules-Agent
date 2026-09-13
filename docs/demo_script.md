# PricePulse MY — 90-second demo script

## 0–15 seconds: Problem

“PricePulse MY is an evidence-first price-surveillance prototype. Its purpose is not to accuse a seller or calculate inflation. It helps a human reviewer identify where an observed local essential-goods price movement is unusually different from a historical expectation.”

## 15–30 seconds: Source and scope

“The source is official Malaysian PriceCatcher data. I choose one verified item and its unit, one geography, and a date window. The system refuses to combine different item codes or units.”

Show the source status and item/geography controls.

## 30–50 seconds: Deterministic ML

“Python validates the schema, lookup matches, dates, prices, duplicates, and daily coverage. It aggregates to a daily median, establishes a historical baseline, and only tests Ridge regression using chronological validation. If Ridge does not beat the baseline, the baseline remains selected.”

Show the observed-versus-expected chart and model comparison.

## 50–65 seconds: Anomaly evidence

“An anomaly is not simply a high price. It is an out-of-sample residual that exceeds an explicit robust MAD threshold, and only on a date with enough transactions and premises. The table exposes the observed price, expected price, residual, score, and coverage.”

Show the anomaly table or its empty state.

## 65–82 seconds: Agent governance

“Four deterministic specialist agents then inspect the same typed evidence: data quality, price signal, market scope, and a reliability critic. The critic can reject weak coverage, leakage, missing baselines, unsupported claims, and any attempt to label inflation or wrongdoing.”

Show the agent timeline and critic verdict.

## 82–90 seconds: Decision boundary

“The only approved recommendation is to conduct a human price-surveillance review when the evidence qualifies. PricePulse never claims the cause, inflation, or price gouging from PriceCatcher alone.”

Show the limitation statement and methodology drawer.
