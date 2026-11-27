# T06 report — Data dictionary for the processed CSVs

## Summary

The dictionary now covers all 59 columns in the five processed CSVs in their exported order. It records each table's grain and key, every column's type and unit, and the source or calculation behind each value. The audit verified the rules for all 24 columns with blanks and confirmed the other 35 have none. The dictionary also records the two-row Power BI dwelling table and the five model relationships.

## Files created or changed

- `docs/data_dictionary.md` — completed the processed-column dictionary, Power BI relationships and glossary.
- `tasks/reports/T06_report.md` — recorded the coverage check, blank counts and differences in earlier descriptions.

## Commands run

| Command | Result |
|---|---|
| `cat`, `sed`, `rg`, `cut` and `.venv/bin/python -` with nbformat | Read AGENTS.md, the T06 spec, the dictionary stub, SQL, cleaning steps 1–15, analysis Part B, source notes, decisions and raw manifest. Checked the T09 grain and join definitions. |
| `.venv/bin/python -` with pandas and the standard library | Parsed the dictionary tables and read each CSV as text. Verified header order, row counts, key uniqueness, types, and the blank rules against the source rows, window counts and test families. |
| `.venv/bin/python -` with openpyxl, pandas and Decimal | Checked individual sale, revision, CPI, population, growth and Holm values against their source cells or formula inputs. |
| `.venv/bin/python -` with SHA-256 file comparison | Verified that only the dictionary and submission report changed. |

## Answers to the task questions

### Q1. Coverage and order

The coverage script compared the CSV headers with the separate column list parsed from each dictionary table. All five lists match exactly. [Data dictionary](../../docs/data_dictionary.md)

```text
fact_sales.csv  2204 rows  10 columns  match=True
  CSV lga, quarter_date, dwelling_type, median_price, sales_count, price_status, low_sales_flag, yoy_change, median_price_revised_est, revised_source
  DOC lga, quarter_date, dwelling_type, median_price, sales_count, price_status, low_sales_flag, yoy_change, median_price_revised_est, revised_source

lga_growth.csv  76 rows  21 columns  match=True
  CSV lga, geo_level, region, dwelling_type, baseline_quarters, latest_quarters, baseline_low_sales_quarters, latest_low_sales_quarters, price_2019, price_latest, growth_pct, growth_annualised, price_2019_rev, price_latest_rev, growth_pct_rev, growth_note, cpi_ratio, growth_pct_real, growth_rank, growth_rank_rev, rank_change_rev
  DOC lga, geo_level, region, dwelling_type, baseline_quarters, latest_quarters, baseline_low_sales_quarters, latest_low_sales_quarters, price_2019, price_latest, growth_pct, growth_annualised, price_2019_rev, price_latest_rev, growth_pct_rev, growth_note, cpi_ratio, growth_pct_real, growth_rank, growth_rank_rev, rank_change_rev

dim_lga.csv  38 rows  10 columns  match=True
  CSV lga, geo_level, region, lga_code_2025, distance_km, pop_growth_2016_19, income_2016_weekly, rent_2019_house_weekly, rent_2019_unit_weekly, sort_order
  DOC lga, geo_level, region, lga_code_2025, distance_km, pop_growth_2016_19, income_2016_weekly, rent_2019_house_weekly, rent_2019_unit_weekly, sort_order

dim_date.csv  29 rows  7 columns  match=True
  CSV quarter_date, year, quarter_label, q_index, is_baseline_2019, is_latest_4q, cpi_sydney
  DOC quarter_date, year, quarter_label, q_index, is_baseline_2019, is_latest_4q, cpi_sydney

factor_tests.csv  10 rows  11 columns  match=True
  CSV dwelling_type, factor, family, n, rho, p, p_holm, verdict, rho_rev, p_rev, verdict_rev
  DOC dwelling_type, factor, family, n, rho, p, p_holm, verdict, rho_rev, p_rev, verdict_rev
```

### Q2. Blank counts and rules

The audit counted empty CSV fields directly and checked each blank against its source or calculation rule. Every column marked `never` had zero blanks, including all seven columns in `dim_date.csv`. [SQL transform](../../sql/transform.sql), [Cleaning notebook](../../notebooks/02_clean.ipynb), [Analysis notebook](../../notebooks/03_analysis.ipynb)

| Column | Blanks | Rule and observed rows |
|---|---:|---|
| `fact_sales.median_price` | 16 | 15 source medians suppressed at 10 sales or fewer and one absent workbook row for Wollondilly units in June 2019. |
| `fact_sales.sales_count` | 146 | 15 DCJ dashes (10 sales or fewer), 130 DCJ `s` markers (30 sales or fewer), and the same absent Wollondilly row. |
| `fact_sales.yoy_change` | 322 | 304 rows in the first four quarters have no prior-year quarter. Another 18 rows lack the current median, the prior-year median, or both. |
| `fact_sales.median_price_revised_est` | 6 | Neither the four-quarter nor the one-quarter later row has a usable price-and-change pair, and the original median is blank. |
| `fact_sales.revised_source` | 6 | The same six rows have no revised estimate or first-published fallback. |
| `lga_growth.region` | 2 | The Greater Sydney house and unit rows have no ring. |
| `lga_growth.price_2019` | 1 | Wollondilly units have zero of four first-published 2019 medians. |
| `lga_growth.growth_pct` | 1 | The first-published baseline average is missing for Wollondilly units. |
| `lga_growth.growth_annualised` | 1 | Nominal growth is missing for Wollondilly units. |
| `lga_growth.price_2019_rev` | 1 | Wollondilly units lack a complete four-quarter baseline in the revised series. |
| `lga_growth.growth_pct_rev` | 1 | The revised baseline average is missing for Wollondilly units. |
| `lga_growth.growth_note` | 75 | Both first-published windows have four medians. The sole nonblank note is `baseline: 0 of 4 quarters published` for Wollondilly units. |
| `lga_growth.growth_pct_real` | 1 | Nominal growth is missing for Wollondilly units. CPI is available. |
| `lga_growth.growth_rank` | 9 | Eight benchmark rows plus Wollondilly units, which lack nominal growth. |
| `lga_growth.growth_rank_rev` | 9 | Eight benchmark rows plus Wollondilly units, which lack revised growth. |
| `lga_growth.rank_change_rev` | 9 | Either rank is missing. The same eight benchmark rows and Wollondilly units have no ranks. |
| `dim_lga.region` | 1 | Greater Sydney has no ring. |
| `dim_lga.lga_code_2025` | 4 | The three ring benchmarks and Greater Sydney have no LGA code. |
| `dim_lga.distance_km` | 4 | The three ring benchmarks and Greater Sydney have no LGA distance. |
| `dim_lga.pop_growth_2016_19` | 4 | Population growth is attached to LGA rows. The three rings and Greater Sydney are blank. |
| `dim_lga.income_2016_weekly` | 5 | Four benchmark rows plus Bayside, whose two predecessor medians do not give a combined median. |
| `dim_lga.rent_2019_house_weekly` | 4 | The three rings and Greater Sydney are blank. All 34 LGAs have published house rent medians. |
| `dim_lga.rent_2019_unit_weekly` | 4 | The three rings and Greater Sydney are blank. All 34 LGAs have published flat or unit rent medians. |
| `factor_tests.p_holm` | 6 | The six main tests use their unadjusted p-values. The four exploratory rows have Holm-adjusted p-values. |

The revision rule also explains why ten blank original medians have a nonblank revised estimate. A later price-and-change pair supplies an estimate in each of those cases. [Fact sales CSV](../../data/processed/fact_sales.csv)

### Q3. Differences from earlier descriptions

- The Phase 2 outline shows a four-file design, an LGA-only geography dimension, and placeholder names `pop_growth_pct` and `median_income`. The current exports include `factor_tests.csv`, the four geography benchmarks and the fields `pop_growth_2016_19` and `income_2016_weekly`. The dictionary uses the exported names and grains. [Project outline](../../docs/project_plan.md)
- The relationship shorthand in T06 groups the dimensions and fact tables together. The T09 guide links `dim_date` to `fact_sales` only. `lga_growth` has fixed windows and joins on geography and dwelling type. The dictionary follows the guide's five joins. [T06 spec](../T06_data_dictionary.md), [T09 model guide](../T09_powerbi_model_guide.md#22-create-the-five-relationships)
- The outline's illustrative DAX uses a simple average of the available quarter prices. SQL publishes each window average only when all four corresponding medians are present. The C1 source note still describes the baseline averaging as future work. The dictionary documents the existing SQL rule. [Project outline](../../docs/project_plan.md), [Data source notes](../../docs/data_sources.md), [SQL transform](../../sql/transform.sql)
- T08's real-growth note uses shorthand that divides nominal growth by the CPI ratio. SQL deflates the gross change with `(1 + growth_pct) / cpi_ratio - 1`. That is the formula in the dictionary. [T08 spec](../T08_factor_tests.md), [SQL transform](../../sql/transform.sql)
- The Phase 3 outline glosses weak associations as “no clear relationship”. The T08 code bases that verdict on p ≥ 0.05 and uses absolute rho to grade results below 0.05. The revised house baseline-price test accordingly has a `weak negative` verdict. [Project outline](../../docs/project_plan.md), [Factor tests CSV](../../data/processed/factor_tests.csv), [Analysis notebook](../../notebooks/03_analysis.ipynb)

## Acceptance checks

| Check | Pass/Fail | Evidence |
|---|---|---|
| A1. Every processed column appears once in CSV order | Pass | Five files, 59 columns, and identical header lists in Q1. |
| A2. Definitions and blank rules match the implementation | Pass | The 24 columns with blanks reconcile in Q2. Spot checks matched Blacktown houses at AUD 1,250,000 in March 2026 (DCJ sales sheet `LGA!G1865`), Bayside's annual-source revised house median at AUD 1,150,000 in March 2019, Camden's population change from 80,268 to 104,706 (ERP `Table 1!R27` and `U27`), the March 2019 CPI of 79.97 (`Data1!B293`), Greater Sydney house real growth of 0.3491381, and the house income Holm p of 0.0089211. |
| A3. Only allowed files changed | Pass | The hash comparison found content changes only in `docs/data_dictionary.md` and `tasks/reports/T06_report.md`. No git commands were run. |

## Decisions needed (for Kang)

None.

## Issues and risks

- Earlier wording that differs from the implemented schema or formulas is recorded in Q3. The dictionary describes the current exports and their intended Power BI relationships.

## Suggested commit message(s)

- `docs: document processed Sydney housing tables and fields`
