# Data dictionary

The five processed CSVs contain quarterly sales, growth summaries, geography and quarter lookups, and factor-test results.

In the Power BI star schema, `dim_lga` and the manually entered `dim_dwelling` filter both `fact_sales` and `lga_growth` on `lga` and `dwelling_type`. `dim_date` filters `fact_sales` on `quarter_date`. `lga_growth` summarises fixed windows, and `factor_tests` is a separate results table. [Power BI model guide](../tasks/T09_powerbi_model_guide.md#22-create-the-five-relationships)

`quarter_date` is the first day of the calendar quarter. The March 2019 quarter is `2019-01-01`.

Prices are in Australian dollars (AUD). Growth values are decimal fractions, so `0.67` means 67%. Blank means missing or inapplicable, and zero is a measured or calculated value.

## fact_sales.csv

One row per geography, quarter and dwelling type. **2,204 rows.** The key is `lga`, `quarter_date`, `dwelling_type`. [CSV](../data/processed/fact_sales.csv)

The cleaning notebook builds the complete quarterly grid in steps 1–4. The `fact_sales` statement adds year-on-year growth and revised estimates. [Cleaning notebook](../notebooks/02_clean.ipynb), [SQL transform](../sql/transform.sql)

| Column | Type | Unit | Meaning | Source / derivation | Blank when |
|---|---|---|---|---|---|
| `lga` | text | — | Names the LGA, DCJ ring or Greater Sydney series. | NSW DCJ Rent and Sales Report, sales sheet `LGA`. Cleaning step 2 keeps the three published rings and Greater Sydney aggregate (D04). SQL renames the geography key. | never |
| `quarter_date` | date | quarter start | Identifies the calendar quarter covered by the sales report. | Cleaning steps 1 and 4 convert the workbook reporting quarter to an ISO quarter-start date and complete the grid. | never |
| `dwelling_type` | text | — | Identifies the house or unit series. | DCJ sales sheet `LGA`, column E. Cleaning step 2 maps `Non Strata` to `house` and `Strata` to `unit` (D01). | never |
| `median_price` | integer | AUD | Gives the median sale price as first published for that quarter. | DCJ sales sheet `LGA`, column G. Cleaning step 3 multiplies the published thousands by 1,000 (D06). | The source median is suppressed at 10 sales or fewer, or the workbook has no row for the series. |
| `sales_count` | integer | sales | Gives the published number of sales for the quarter. | DCJ sales sheet `LGA`, column J. Cleaning steps 3–4 preserve missing counts and keep the reason. | DCJ uses `-` for 10 sales or fewer, uses `s` for 30 sales or fewer, or omits the row. |
| `price_status` | text | — | Records whether the original median was published, suppressed or absent from the source. | Cleaning steps 3–4 set `published` for a reported price, `suppressed` for a dash in column G and `not_in_source` for a missing workbook row. | never |
| `low_sales_flag` | boolean | — | Flags a row whose sale count is unavailable. | Cleaning step 4 sets `true` when the count is suppressed or the source row is absent, and `false` when DCJ publishes the count. | never |
| `yoy_change` | decimal | fraction | Measures the change in first-published price from the same quarter one year earlier. | SQL `quarter_neighbours` and `fact_sales` divide the current median by the median four quarters earlier in the same geography and dwelling series, then subtract 1. | One year of history is unavailable or either first-published median is missing. |
| `median_price_revised_est` | integer | AUD | Gives the rounded price estimate used in the revision sensitivity check. | SQL `revision_choices` and `revision_values` divide the later median by `1 + reported change` (D08). Use the row four quarters later with sales sheet `LGA` column L, then the row one quarter later with column K. The current first-published median is the fallback. Round to the nearest AUD 1,000. | Neither later price-and-change pair is usable and the original median is missing. |
| `revised_source` | text | — | Identifies the input used for the revised price estimate. | SQL `revision_choices` sets `annual`, `quarterly` or `first_published` in that priority order (D08). | No revised estimate can be produced. |

## lga_growth.csv

One row per geography and dwelling type. **76 rows.** The key is `lga`, `dwelling_type`. [CSV](../data/processed/lga_growth.csv)

The baseline is the four quarters of 2019. The latest window is the four most recent sales quarters, currently June 2025 through March 2026. Each growth figure uses that geography's own medians, including DCJ's published ring and Greater Sydney medians (D02, D04). [SQL transform](../sql/transform.sql)

| Column | Type | Unit | Meaning | Source / derivation | Blank when |
|---|---|---|---|---|---|
| `lga` | text | — | Names the LGA, DCJ ring or Greater Sydney series summarised in this row. | SQL `window_prices` groups the sales fact by geography and dwelling type (D04). | never |
| `geo_level` | text | — | Identifies the geography as an LGA, a ring or Greater Sydney. | SQL joins `dim_lga`, which assigns `lga`, `ring` or `greater_sydney`. | never |
| `region` | text | — | Gives the LGA's DCJ ring or the ring benchmark's own name. | SQL joins `dim_lga` for `Inner Ring`, `Middle Ring` or `Outer Ring` (D04). | The row is for Greater Sydney. |
| `dwelling_type` | text | — | Identifies the house or unit series used for the growth comparison. | SQL `window_prices` carries `fact_sales.dwelling_type` into each summary (D01). | never |
| `baseline_quarters` | integer | quarters | Counts the 2019 quarters with a first-published median. | SQL `window_prices` counts present `median_price` values for quarters flagged `is_baseline_2019`. | never |
| `latest_quarters` | integer | quarters | Counts the latest four quarters with a first-published median. | SQL `window_prices` counts present `median_price` values for quarters flagged `is_latest_4q`. | never |
| `baseline_low_sales_quarters` | integer | quarters | Counts 2019 quarters with both a first-published median and a low-sales flag. | SQL `window_prices` counts present medians in the baseline window where `low_sales_flag` is true. | never |
| `latest_low_sales_quarters` | integer | quarters | Counts the latest quarters with both a first-published median and a low-sales flag. | SQL `window_prices` counts present medians in the latest window where `low_sales_flag` is true. | never |
| `price_2019` | decimal | AUD | Gives the average of the four first-published 2019 medians. | SQL `window_prices` takes the simple average when all four baseline medians are present (D02, D06). | Fewer than four first-published 2019 medians are available, as for Wollondilly units (D05). |
| `price_latest` | decimal | AUD | Gives the average of the four latest first-published medians. | SQL `window_prices` averages the latest window when all four medians are present (D02, D06). All rows satisfy that rule in this export. | never |
| `growth_pct` | decimal | fraction | Measures nominal price growth between the two windows. | SQL `window_growth` computes `price_latest / price_2019 - 1` (D02, D06). | Either first-published window average is missing. |
| `growth_annualised` | decimal | fraction per year | Gives the equivalent compounded annual rate of nominal growth. | SQL computes `POWER(1 + growth_pct, 1 / years) - 1`. `window_parameters` divides the difference between the mean quarter indexes by four to give the midpoint gap in years, currently 6.25. | Nominal growth is missing. |
| `price_2019_rev` | decimal | AUD | Gives the average of the four 2019 medians used in the revised series. | SQL `window_prices` averages `median_price_revised_est` when all four baseline values are present (D08). | Fewer than four revised-series baseline medians are available. |
| `price_latest_rev` | decimal | AUD | Gives the average of the four latest medians used in the revised series. | SQL `window_prices` averages `median_price_revised_est` when all four latest values are present (D08). All rows satisfy that rule in this export. | never |
| `growth_pct_rev` | decimal | fraction | Measures nominal price growth using the revised series for both windows. | SQL `window_growth` computes `price_latest_rev / price_2019_rev - 1` (D08). | Either revised-series window average is missing. |
| `growth_note` | text | — | Explains which window lacks enough first-published medians for nominal growth. | The final SQL selection reports the number of published quarters for each incomplete window, such as `baseline: 0 of 4 quarters published` for Wollondilly units (D05). | Both first-published windows have four medians. |
| `cpi_ratio` | decimal | ratio | Gives the common ratio of the latest-window CPI to the baseline-window CPI. | SQL `window_parameters` divides the average Sydney All groups CPI in the latest window by the average in 2019. | never |
| `growth_pct_real` | decimal | fraction | Measures price growth after adjusting for Sydney inflation. | The final SQL selection computes `(1 + growth_pct) / cpi_ratio - 1` using ABS Sydney All groups CPI. | Nominal growth is missing. |
| `growth_rank` | integer | rank | Ranks LGAs within each dwelling type by nominal growth, with 1 highest. | SQL `nominal_ranks` applies descending `RANK()` to `growth_pct` for eligible LGA rows. Ties share a rank. | The row is a ring or Greater Sydney, or the LGA's nominal growth is missing. |
| `growth_rank_rev` | integer | rank | Ranks LGAs within each dwelling type by revised growth, with 1 highest. | SQL `revised_ranks` applies the same ranking rule to `growth_pct_rev` (D08). | The row is a ring or Greater Sydney, or the LGA's revised growth is missing. |
| `rank_change_rev` | integer | rank places | Measures the rank change under revisions, with a positive number indicating a drop. | The final SQL selection subtracts `growth_rank` from `growth_rank_rev` (D08). | Either rank is missing. |

## dim_lga.csv

One row per geography, covering 34 LGAs, three DCJ rings and Greater Sydney. **38 rows.** The key is `lga`. [CSV](../data/processed/dim_lga.csv)

The `dim_lga` statement joins the LGA lookup and factors on the ABS code, then adds the benchmark rows. [Cleaning notebook](../notebooks/02_clean.ipynb), [SQL transform](../sql/transform.sql)

| Column | Type | Unit | Meaning | Source / derivation | Blank when |
|---|---|---|---|---|---|
| `lga` | text | — | Gives the canonical DCJ geography name used to join the model. | Cleaning steps 2 and 5 take the LGA names from the DCJ sales sheet `LGA`. SQL `benchmark_rows` adds the published ring and Greater Sydney names (D04). | never |
| `geo_level` | text | — | Identifies the kind of geography. | SQL sets `lga` for an LGA, `ring` for a DCJ ring and `greater_sydney` for Greater Sydney. | never |
| `region` | text | — | Assigns an LGA or ring benchmark to the Inner, Middle or Outer Ring. | DCJ sales sheet `LGA`, column C, for the LGA assignments in cleaning step 5. SQL uses each ring's own name for its benchmark. | The row is for Greater Sydney. |
| `lga_code_2025` | text | — | Identifies the LGA by its five-digit ABS 2025 code. | Cleaning step 5 takes the code from ABS Regional Population 2024–25, ERP Table 1, and checks it against the ABS LGA 2025 polygons. SQL uses the code to attach the factors. | The row is for a ring or Greater Sydney. |
| `distance_km` | decimal | km | Gives the straight-line distance from the LGA's geometric centre to the Sydney GPO. | ABS LGA 2025 polygons and the Heritage NSW GPO point (C5, D07). Cleaning step 9 runs `distance.sql`, which finds the centroid in Australian Albers, measures distance along the WGS84 ellipsoid and rounds to two decimals. | The row is for a ring or Greater Sydney. |
| `pop_growth_2016_19` | decimal | fraction | Measures change in the LGA's estimated resident population between June 2016 and June 2019. | ABS Regional Population 2024–25, ERP Table 1, on LGA 2025 boundaries (C3, D07). Cleaning step 10 divides the 2019 count by the 2016 count and subtracts 1. Step 13 writes four decimal places before the SQL import. | The row is for a ring or Greater Sydney. |
| `income_2016_weekly` | integer | AUD/week | Gives the LGA's median total weekly household income in the 2016 Census. | ABS Census DataPacks, NSW LGA General Community Profile G02, field `Median_tot_hhd_inc_weekly` (C4, D07). Cleaning step 11 matches the 2016 and 2025 LGA codes. | The row is for a ring or Greater Sydney, or it is Bayside, which has two separate predecessor medians. |
| `rent_2019_house_weekly` | decimal | AUD/week | Gives the LGA's average of the available 2019 quarterly house rent medians. | DCJ Rent and Sales Report, rent sheet `LGA`, Table 1, column H for new bonds, `House` and all bedrooms. Cleaning step 12 averages the 2019 medians (C2, D07). | The row is for a ring or Greater Sydney. All LGAs have four published quarterly rent medians in this export. |
| `rent_2019_unit_weekly` | decimal | AUD/week | Gives the LGA's average of the available 2019 quarterly flat and unit rent medians. | DCJ Rent and Sales Report, rent sheet `LGA`, Table 1, column H for new bonds, `Flat/Unit` and all bedrooms. Cleaning step 12 averages the 2019 medians (C2, D07). | The row is for a ring or Greater Sydney. All LGAs have four published quarterly rent medians in this export. |
| `sort_order` | integer | position | Sets the order in which geographies are displayed. | SQL `benchmark_rows` gives Greater Sydney 1 and the Inner, Middle and Outer Rings 2–4. SQL `lga_rows` assigns 5–38 in alphabetical LGA order. | never |

## dim_date.csv

One row per sales quarter. **29 rows.** The key is `quarter_date`. [CSV](../data/processed/dim_date.csv)

The `dim_date` statement takes distinct sales quarters and adds the window flags and Sydney CPI. [Cleaning notebook](../notebooks/02_clean.ipynb), [SQL transform](../sql/transform.sql)

| Column | Type | Unit | Meaning | Source / derivation | Blank when |
|---|---|---|---|---|---|
| `quarter_date` | date | quarter start | Identifies the sales quarter by its first calendar day. | SQL `quarters` takes distinct dates from the cleaned sales grid prepared in steps 1–4. | never |
| `year` | integer | calendar year | Gives the calendar year of the quarter. | SQL `numbered_quarters` extracts `YEAR(quarter_date)`. | never |
| `quarter_label` | text | — | Gives the display label in the form `2019 Q1`. | SQL combines the year and the quarter number from `quarter_date`. | never |
| `q_index` | integer | quarter position | Numbers the quarters in time order from 1. | SQL `numbered_quarters` applies `ROW_NUMBER()` from oldest to newest. | never |
| `is_baseline_2019` | boolean | — | Marks the four quarters in the 2019 baseline. | The final SQL selection sets `true` when `year = 2019` (D02). | never |
| `is_latest_4q` | boolean | — | Marks the four most recent quarters in the sales data. | SQL `numbered_quarters` also numbers dates from newest to oldest. The final selection sets `true` for the first four in that order (D02). | never |
| `cpi_sydney` | decimal | index points | Gives Sydney's quarterly All groups consumer price index. | ABS Consumer Price Index, Table 17, series A2325806K (C7), workbook sheet `Data1`. Cleaning step 14 moves the quarter's last-month label to the quarter start and checks coverage. SQL joins on `quarter_date`. | never |

## factor_tests.csv

One row per dwelling type and D07 factor. **10 rows.** The key is `dwelling_type`, `factor`. [CSV](../data/processed/factor_tests.csv)

Part B tests associations across eligible LGAs. It excludes Wollondilly from unit tests (D05) and Bayside from income tests. The revised comparison uses the same factors with revised growth (D08). [Analysis notebook](../notebooks/03_analysis.ipynb)

| Column | Type | Unit | Meaning | Source / derivation | Blank when |
|---|---|---|---|---|---|
| `dwelling_type` | text | — | Identifies the house or unit outcome tested. | Part B, “Test the five factors with Spearman correlation”, groups the eligible `lga_growth` rows by `dwelling_type` (D01). | never |
| `factor` | text | — | Identifies the factor compared with growth. | Part B uses `distance_km`, `pop_growth_2016_19`, `price_2019`, `income_2016_weekly` and `rent_2019_weekly` (D07). The rent code picks the matching house or unit rent from `dim_lga`. | never |
| `family` | text | — | Identifies whether the test is main or exploratory. | Part B assigns `main` to distance, population growth and price, and `exploratory` to income and rent (D07). | never |
| `n` | integer | LGAs | Counts the LGAs with both a factor and a growth value for the test. | Part B drops rows missing either member of the pair and checks that sample sizes match across both growth versions. | never |
| `rho` | decimal | coefficient | Measures the direction and strength of the rank association with first-published growth. | Part B uses `scipy.stats.spearmanr` on the factor and `growth_pct` within each dwelling type (D07). | never |
| `p` | decimal | probability | Gives the raw two-sided p-value for the first-published growth test. | Returned with `rho` by `spearmanr` in Part B. | never |
| `p_holm` | decimal | probability | Gives the first-published exploratory test's p-value after Holm correction. | Part B sorts the four exploratory p-values across both dwelling types, multiplies by 4, 3, 2 and 1 in order, then takes the running maximum capped at 1 (D07). | The test is in the main family. |
| `verdict` | text | — | Summarises the direction and strength of the first-published result under the chosen thresholds. | Part B uses raw p for main tests and Holm p for exploratory tests. A p-value of at least 0.05 gives `no clear relationship`. Below 0.05, absolute rho below 0.4 is weak, 0.4 to below 0.6 is moderate, and 0.6 or higher is strong. The sign supplies the direction. | never |
| `rho_rev` | decimal | coefficient | Measures the rank association with revised growth. | Part B, “Check sensitivity to revised-estimate growth”, repeats Spearman using the original factor and `growth_pct_rev` (D08). | never |
| `p_rev` | decimal | probability | Gives the raw two-sided p-value for the revised growth test. | Returned with `rho_rev` by `spearmanr` in the Part B sensitivity step (D08). | never |
| `verdict_rev` | text | — | Summarises the revised result under the same thresholds. | Part B uses `p_rev` for main tests and reruns Holm across the four revised exploratory tests for the exploratory verdicts. The revised Holm values are shown in the notebook. | never |

## dim_dwelling

One row per dwelling type. **2 rows, 2 text columns.** Enter this table by hand in Power BI. The key `dwelling_type` filters both fact tables, and `dwelling_label` supplies the slicer labels. [Power BI model guide](../tasks/T09_powerbi_model_guide.md#16-add-the-dwelling-type-table)

| dwelling_type | dwelling_label |
|---|---|
| house | Houses |
| unit | Units |

## Glossary

- **Median** — the middle value after prices are ordered, using the average of the two middle values for an even count.
- **Strata and non-strata** — DCJ title categories used as the project's unit and house series, respectively.
- **DCJ rings** — the Inner, Middle and Outer Ring groupings DCJ publishes for Greater Sydney.
- **First-published and revised estimate** — the first issue supplies the original median. The revised series estimates an earlier median from a later issue when its price and change rate are available, with the original median as fallback (D06, D08).
- **Real growth** — price growth after adjusting the gross price change by Sydney CPI.
- **Spearman ρ** — rank correlation from −1 to +1, describing the direction and strength of a monotonic association.
- **Holm p** — a p-value adjusted across a group of tests to control the chance of at least one false positive.

For interim and raw inputs, see the cleaning steps, the [data source notes](data_sources.md) and [data/raw/MANIFEST.csv](../data/raw/MANIFEST.csv).
