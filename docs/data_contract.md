# PricePulse MY Data Contract

**Verification date:** 12 September 2026 (Malaysia Time)  
**Status:** verified for schema, public availability, and official provenance; full historical quality profiling remains an ingestion-stage task.

## Approved sources

| Asset | Official URL | Verified facts |
| --- | --- | --- |
| Price transactions | `https://storage.data.gov.my/pricecatcher/pricecatcher_YYYY-MM.csv` | Monthly CSV endpoint. `pricecatcher_2026-09.csv` returned HTTP 200, had a 15,002,536-byte response, and was last modified 11 September 2026 12:00:28 GMT. |
| Item lookup | `https://storage.data.gov.my/pricecatcher/lookup_item.csv` | Returned HTTP 200, 56,042 bytes, last modified 9 September 2026 09:54:25 GMT. |
| Premise lookup | `https://storage.data.gov.my/pricecatcher/lookup_premise.csv` | Returned HTTP 200, 492,832 bytes, last modified 7 September 2026 12:00:31 GMT. |

The public [PriceCatcher catalogue](https://data.gov.my/data-catalogue/pricecatcher) identifies the sources as the Ministry of Domestic Trade and Department of Statistics Malaysia. It says prices are collected and verified daily by ground staff, and warns that PriceCatcher is suited to high-frequency, item-and-location price surveillance rather than inflation measurement.

## Live schema verification

The following headers were read directly from the live CSV responses on 12 September 2026.

### Transactions

```text
date,premise_code,item_code,price
```

| Field | Contract |
| --- | --- |
| `date` | Date in `YYYY-MM-DD` format. |
| `premise_code` | Identifier joined to the premise lookup. |
| `item_code` | Identifier joined to the item lookup. |
| `price` | Numeric observed price in RM. |

The first raw row observed in the September 2026 file was dated 2026-09-01; the last raw row read was dated 2026-09-11. Ingestion must independently calculate the actual range, continuity, duplicates, missingness, and valid-price counts. Do not infer these from file order.

### Item lookup

```text
item_code,item,unit,item_group,item_category
```

`item_code` defines the only permitted item-level analysis grain. `unit` must be present and displayed with all price results. The sample contains a sentinel `-1` row with blank item data; it must be reported as an invalid/missing lookup record rather than repaired silently.

### Premise lookup

```text
premise_code,premise,address,premise_type,state,district
```

`state` and `district` are the approved local geography filters. The sample contains a `-1.0` blank sentinel premise row; it must be reported, not silently mapped to a location.

## Relationship and aggregation contract

1. Join transactions to both lookups by their code fields and record unmatched rows.
2. Filter for exactly one official `item_code` and one selected geography before aggregation.
3. Verify the item's published unit; never combine codes or units.
4. Aggregate qualified transaction prices to a daily median in RM per verified unit.
5. Retain daily transaction count and distinct-premise count with each median.
6. Mark a day coverage-ineligible when it does not meet configured thresholds. It cannot receive a forecast, anomaly classification, or recommendation.

## Historical availability

The representative endpoints `pricecatcher_2026-08.csv`, `pricecatcher_2025-09.csv`, and `pricecatcher_2024-09.csv` each returned HTTP 200 on 12 September 2026. The loader may use a configurable sequence of monthly URLs, but must record unavailable files and never assume the pattern guarantees every month exists.

## Explicit limitations

- The data does not establish a representative inflation rate; official CPI is required for that purpose.
- The data contains prices, not evidence of their cause, a seller's intent, policy impact, stock availability, or misconduct.
- A detected residual anomaly means only that an observed qualified daily median differs from a historical expectation.
- No claim is permitted until data validation and chronological model evaluation are complete.
