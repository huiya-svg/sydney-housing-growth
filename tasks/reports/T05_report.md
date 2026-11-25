# T05 report — SQL transform and Power BI exports

## Summary

The DuckDB transformation builds four Power BI tables from the accepted sales grid, LGA lookup and factors. It keeps first-published medians as the main series and builds a separate D08 revised estimate. Wollondilly units are the only series without growth because all four 2019 medians are unavailable. The first-published preview puts Fairfield first for house growth and Hawkesbury first for unit growth.

## Files created or changed

- `sql/transform.sql` — typed input, quarter-grid check, fact, geography and date dimensions, and growth summary.
- `notebooks/02_clean.ipynb` — appended four steps to run, preview, validate and export the SQL tables.
- `data/processed/fact_sales.csv` — quarterly published prices and counts, YoY change and revised estimates.
- `data/processed/dim_lga.csv` — sorted geography labels and LGA factors.
- `data/processed/dim_date.csv` — calendar-quarter labels, indexes and analysis-window flags.
- `data/processed/lga_growth.csv` — four-quarter price windows and nominal growth measures by geography and dwelling type.
- `tasks/reports/T05_report.md` — submission and verification evidence.

## Commands run

| Command | Result |
|---|---|
| `cat`, `sed`, `rg` and `head` | Read AGENTS.md, the T05 spec, the relevant project plan, D02 and D04–D08, the T03 and T04 reviews, the path precedent and input headers. |
| `.venv/bin/python -` with nbformat and DuckDB | Recorded starting file hashes and all 35 original notebook cells. Appended and syntax-checked the notebook section. Tested CSV serialisation of a date, boolean, fraction and null. |
| `.venv/bin/python -` to run the SQL in memory | The first two smoke-test wrappers hit `AttributeError: Relations no longer have fetchone()` and `Resource In Use Error: connection has an unfinished result from execute()`. Fetching complete results with `fetchall()` resolved both. The SQL returned all four expected row counts. |
| `.venv/bin/python -` with a temporary input missing one quarter row | Pass. SQL raised `Expected 29 consecutive quarter starts for each of the 76 sales series` before building the fact table. |
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb` | Pass twice consecutively. All 20 code cells executed. Jupyter emitted its standard `Kernel is running over TCP without encryption` startup warning. |
| `shasum -a 256` and `test` | Pass. All four processed CSV hashes matched across runs. |
| `.venv/bin/python -` for independent CSV and workbook checks | Pass. Recomputed all YoY changes, revised estimates and growth rows, verified the factor join and checked three prices against the source workbook. Initial capture of the successful audit output failed with `SyntaxError: Unexpected token '<'` because a pandas `PerformanceWarning` preceded the JSON. Parsing the JSON line on the retry returned the full audit. |
| `.venv/bin/python -` with nbformat and the nbconvert HTML exporter | Pass. Verified the final executed cells and restored the original 35 cells' execution timestamps from the pre-task snapshot. The in-memory HTML showed the T05 evidence outputs. |
| `rg -n`, `nl -ba`, `wc -l` and the file hash comparison | Pass. Verified the SQL line references, CSV line counts and file scope. |

## Answers to the task questions

### Q1. Row counts and null growth

| Table | Data rows | Key |
|---|---:|---|
| `fact_sales` | 2,204 | `lga`, `quarter_date`, `dwelling_type` |
| `dim_lga` | 38 | `lga` |
| `dim_date` | 29 | `quarter_date` |
| `lga_growth` | 76 | `lga`, `dwelling_type` |

The only null `growth_pct` row is **Wollondilly, unit**, with the note `baseline: 0 of 4 quarters published`. It has four published latest-quarter medians. Its revised growth is also null. [Growth export](../../data/processed/lga_growth.csv)

### Q2. Growth cross-checks

Pandas independently averaged the four 2019 and four latest first-published medians in the input CSV. Growth values below are decimal fractions. The absolute difference was zero for all three pairs, below the required `1e-9` tolerance. [Sales input](../../data/interim/sales_long.csv), [Executed notebook](../../notebooks/02_clean.ipynb)

| Geography and type | 2019 average | Latest four-quarter average | SQL growth | pandas growth | Absolute difference |
|---|---:|---:|---:|---:|---:|
| Blacktown house | $716,000 | $1,236,250 | 0.726606145251 | 0.726606145251 | 0 |
| Sydney unit | $906,500 | $969,000 | 0.068946497518 | 0.068946497518 | 0 |
| Greater Sydney house | $923,750 | $1,547,000 | 0.674695534506 | 0.674695534506 | 0 |

The additional YoY checks compare the March 2026 quarter with March 2025. SQL and pandas matched for all three.

| Geography and type | SQL YoY | pandas YoY |
|---|---:|---:|
| Blacktown house | 0.069289991446 | 0.069289991446 |
| Sydney unit | -0.013265306122 | -0.013265306122 |
| Greater Sydney house | 0.083916083916 | 0.083916083916 |

The March 2026 first-published prices also match the original workbook. Blacktown houses are `LGA!G1865` ($1,250,000), Sydney units are `LGA!G1815` ($967,000) and Greater Sydney houses are `LGA!G1691` ($1,550,000). [DCJ March 2026 sales workbook](../../data/raw/dcj_sales/sales-tables-march-2026-quarter.xlsx)

### Q3. Annualisation interval

The date dimension numbers the quarter starts from earliest to latest. The 2019 indexes 1–4 have a midpoint of 2.5. The latest four indexes 26–29, June 2025 through March 2026, have a midpoint of 27.5. Their difference is 25 quarters, or **6.25 years**. SQL uses that date-derived interval as the denominator in the annualisation exponent. [Date export](../../data/processed/dim_date.csv), [Transformation SQL](../../sql/transform.sql)

### Q4. Revised-estimate counts and rank movement

| `revised_source` | Sales rows |
|---|---:|
| `annual` | 1,888 |
| `quarterly` | 232 |
| `first_published` | 78 |
| Null | 6 |
| **Total** | **2,204** |

All 76 rows in the latest quarter use `first_published`. **Four of 67 comparable LGA × dwelling type pairs** moved by more than three ranks, all houses. Ranks are descending within each dwelling type over the pairs with growth in both series. There were no ties. [Sales export](../../data/processed/fact_sales.csv), [Growth export](../../data/processed/lga_growth.csv)

### Q5. First-published growth preview

Figures are nominal growth from the 2019 average to the latest four-quarter average. The preview uses 34 house and 33 unit LGA rows with published growth. [Growth export](../../data/processed/lga_growth.csv)

#### Houses

| Position | Fastest | Growth | Slowest | Growth |
|---:|---|---:|---|---:|
| 1 | Fairfield | 82.98% | Woollahra | 43.02% |
| 2 | Cumberland | 81.43% | North Sydney | 48.89% |
| 3 | Burwood | 80.50% | Wollondilly | 50.07% |
| 4 | Canterbury-Bankstown | 80.43% | Sydney | 51.28% |
| 5 | Ryde | 79.60% | Randwick | 54.33% |

#### Units

| Position | Fastest | Growth | Slowest | Growth |
|---:|---|---:|---|---:|
| 1 | Hawkesbury | 58.79% | Hunters Hill | 0.72% |
| 2 | Campbelltown | 57.66% | Strathfield | 5.59% |
| 3 | Central Coast | 54.20% | Parramatta | 5.84% |
| 4 | Northern Beaches | 47.79% | Sydney | 6.89% |
| 5 | Penrith | 47.36% | Cumberland | 7.55% |

### Q6. SQL features and line numbers

| Feature | Lines in `sql/transform.sql` | Use |
|---|---:|---|
| Explicit CSV types | 8–14, 85–94 | Read dates, text codes, integer prices and counts, booleans and numeric factors with known types. |
| CTEs and grid assertion | 17–36, 40–70 | Validate consecutive quarters before splitting revision selection from price calculation. |
| `LAG`, `LEAD` and a named window | 43–49 | Fetch prior-year and future-quarter prices and change rates within each geography and dwelling type. |
| Join on ABS code and `UNION ALL` | 85–110 | Attach factors by code and include the four published benchmark geographies. |
| `ROW_NUMBER` | 84, 122–123 | Apply LGA display order and number dates in both directions to flag the latest four. |
| Conditional aggregation | 136–137, 143–154 | Derive the time gap, count valid medians and low-sales quarters, and average complete windows. |
| Fact-to-date and growth-to-geography joins | 155–156, 174–176 | Attach window flags, geography labels and the shared midpoint gap. |
| `POWER` | 168 | Annualise nominal growth using the date-derived interval. |

[Transformation SQL](../../sql/transform.sql)

## Acceptance checks

| Check | Pass/Fail | Evidence |
|---|---|---|
| A1. Four CSVs, exact columns and row counts | Pass | 2,204 fact rows, 38 geography rows, 29 date rows and 76 growth rows. Verified all four headers against the spec. |
| A2. SQL structure and required features | Pass | Commented table definitions and CTEs. The latest quarter is data-derived. Q6 identifies the joins, offsets, numbering and conditional aggregations. |
| A3. Validation and pandas cross-check | Pass | Unique keys and valid fact foreign keys, two four-quarter windows, three YoY and three growth comparisons, missing-growth note and revision-source checks. No zero prices and all non-null growth measures are within the sanity bounds. |
| A4. Notebook execution and deterministic output | Pass | Both final notebook runs completed. SHA-256 hashes matched for all four output files. |
| A5. Report, scope and no git operations | Pass | Q1–Q6 are answered above. Only the seven allowed project files were added or changed. The 35 earlier notebook cells, interim data, reference data and raw inputs are unchanged. No git commands were run. |

Both runs produced the following SHA-256 values.

| CSV | SHA-256 |
|---|---|
| `fact_sales.csv` | `9c5c66eba72c7e7cdc171ca3568698ec8b18a9654f9fab2ed1a56db5d1ae4b49` |
| `dim_lga.csv` | `abcaf3571943e759798205863feb837198d2340b57cb497302b91dbc8b1a0455` |
| `dim_date.csv` | `173ee3f6cf69f425a67b21c4d41613c0463c90f4373d7b9bf4bf36935c868edc` |
| `lga_growth.csv` | `1bcd3a7175bf63900a4d8fd21fe3ce1e8c5da036993a821e07b16e42c3a30c91` |

## Decisions needed (for Kang)

None.

## Issues and risks

- Ten rows have a revised estimate and a blank first-published median. The original median and status are preserved. Revised estimates use rounded inputs from later DCJ issues and are themselves rounded to the nearest $1,000.
- The revised series has less opportunity to incorporate later issues near the end of the data. Its latest quarter uses the same prices as the first-published series.

## Suggested commit message(s)

- `feat: build and export Sydney housing star schema in DuckDB`
