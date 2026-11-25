# Data dictionary

Every column in `data/processed/`: meaning, unit, source. Filled in during T06.

## fact_sales.csv — one row per LGA × quarter × dwelling type

| Column | Type | Unit | Meaning | Source |
|---|---|---|---|---|
| lga | text | | | |
| quarter_date | date | | | |
| dwelling_type | text | | | |
| median_price | number | AUD | | |
| sales_count | integer | sales | | |

## dim_lga.csv — one row per LGA

_TBD_

## dim_date.csv — one row per quarter

_TBD_

## lga_growth.csv — one row per LGA × dwelling type

_TBD_
