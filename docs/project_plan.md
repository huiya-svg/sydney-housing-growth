# Sydney Housing Price Growth Project — Outline

Kang Liang · 24 Nov 2026 · Source of truth for scope. Agents: read this for context; the current task file
in `tasks/` decides what to do now.

## Overview

The project answers one question with public data: **which Greater Sydney LGAs have had the fastest median
house and unit price growth since 2019, and what do the fastest-growing areas have in common?**
Python and SQL do the data work; Power BI in the browser does the model and the report.

Pipeline: raw files → Python (pandas) + DuckDB SQL to clean, join and test → clean CSV tables →
Power BI (data model, DAX measures, report) → GitHub (README, code, screenshots, PDF).

| Layer | Tool | Skill it proves |
|---|---|---|
| Data collection | Python (requests or manual download) | Finding and judging public data |
| Cleaning and joining | Python (pandas) + DuckDB (SQL) | SQL and Python |
| Analysis | pandas, SciPy, Matplotlib/Seaborn | Statistics and honest interpretation |
| Model and report | Power BI service in the browser | Dashboards and DAX |
| Publishing | Git + GitHub | Communication and reproducible work |

Final deliverables: a public GitHub repo, a 4-page Power BI report (screenshots + PDF export), a README with
3–5 numbered findings, and a LinkedIn post linking to it.

## Phase 0 — Setup

- Power BI account (work/school email; UNSW or WSU login, else Microsoft 365 trial "onmicrosoft" account).
- Python 3 environment: pandas, duckdb, scipy, matplotlib, seaborn, openpyxl.
- GitHub account (professional username, e.g. `kangliang-data`), public repo `sydney-housing-growth`.
- LinkedIn custom URL.

## Phase 1 — Data acquisition and screening

Start with one core dataset that answers the question by itself, then add a few candidate "why" factors and
keep only those that pass screening.

| Role | Dataset | Level and time | Source |
|---|---|---|---|
| Core | Median sales price and number of sales, strata and non-strata | LGA, quarterly, 2011 onwards | NSW Rent and Sales Report (DCJ) |
| Candidate | Median weekly rent | LGA, quarterly | Same report |
| Candidate | Population and population growth | LGA, yearly | ABS Regional Population |
| Candidate | Median household income | LGA, 2021 Census | ABS Census DataPacks |
| Candidate | Distance from the Sydney CBD | LGA (calculated) | LGA centre coordinates |
| Candidate | New dwelling supply | LGA | NSW Housing Evidence Centre |
| Context only | RBA cash rate, CPI | Australia, monthly/quarterly | RBA, ABS |
| Optional stretch | Individual property sales | One row per sale, weekly | NSW Valuer General bulk sales |

Screening checks for every candidate (record results in `docs/data_sources.md`, including rejects):

1. Same geography and time? By LGA, covering 2019 onwards. Suburb/postcode data needs a mapping table first.
2. Does it vary between LGAs? The cash rate is identical everywhere → timeline overlay only.
3. Measured before or at the start of the period? A factor measured after the fact may be a result of growth.
4. Licence and privacy. Aggregated LGA tables are fine to share; never commit address-level sales.

Note: starting in 2019 is after the 2016 council mergers, so LGA names should be stable. Going back before
2016 needs an old-to-new council mapping.

## Phase 2 — Cleaning and joining in Python + SQL

Goal: four tidy CSVs, one row per thing, that Power BI loads with no further cleaning.

1. Explore each raw file (`01_explore.ipynb`): row counts, columns, types, missing values, quarters covered.
2. Reshape to long format: one row per LGA × quarter × dwelling type (melt quarters out of columns).
3. Fix types and labels: prices to numbers, quarters to a real date (first day of quarter), consistent LGA names.
4. Small samples: blank/suppressed stays blank, never zero. Flag LGA-quarters with few sales.
5. Filter to Greater Sydney LGAs and add a region column (inner / middle / outer ring).
6. Join in SQL (`sql/transform.sql`, run with DuckDB from the notebook): factors onto the LGA list; window
   functions for year-on-year change.
7. Validate: every Greater Sydney LGA present, no duplicate LGA × quarter × type rows, spot check 3 values
   against the original report.
8. Export to `data/processed/`:

| File | One row per | Key columns |
|---|---|---|
| fact_sales.csv | LGA × quarter × dwelling type | lga, quarter_date, dwelling_type, median_price, sales_count |
| dim_lga.csv | LGA | lga, region, distance_km, pop_growth_pct, median_income |
| dim_date.csv | quarter | quarter_date, year, quarter_label, q_index, is_baseline_2019, is_latest_4q |
| lga_growth.csv | LGA × dwelling type | lga, dwelling_type, price_2019, price_latest, growth_pct |

Example SQL step:

```sql
SELECT lga, dwelling_type, quarter_date, median_price,
       median_price / LAG(median_price, 4) OVER (
           PARTITION BY lga, dwelling_type ORDER BY quarter_date) - 1 AS yoy_change
FROM fact_sales
ORDER BY lga, dwelling_type, quarter_date;
```

## Phase 3 — Analysis in Python

**A. Measure growth.** Baseline = average of the four 2019 quarterly medians; end = average of the latest
four quarters. Separately for houses (non-strata) and units (strata). Growth = Price_latest4Q / Price_2019 − 1.
Rank LGAs; convert to an annual rate. Optional: real growth using ABS CPI.

**B. Test candidate factors.** Scatter of growth vs each factor (one point per LGA); Spearman correlation with
coefficient and p-value (~33 LGAs, weak = "no clear relationship"); correlation matrix to check proxies
(distance vs 2019 price); stretch: linear regression on 2–3 factors, reported as association, not cause.

**C. Findings** as sentences with numbers; 3–5, including at least one "we tested X and found no clear link".

## Phase 4 — Power BI (owner-led)

Star schema: `dim_lga` → `fact_sales` (lga), `dim_date` → `fact_sales` (quarter_date), one-to-many.
Hide technical columns. DAX measures written by Kang:

```DAX
Median Price = MAX ( fact_sales[median_price] )
Price 2019 = CALCULATE ( AVERAGE ( fact_sales[median_price] ), dim_date[is_baseline_2019] = TRUE () )
Price Latest 4Q = CALCULATE ( AVERAGE ( fact_sales[median_price] ), dim_date[is_latest_4q] = TRUE () )
Growth Since 2019 = DIVIDE ( [Price Latest 4Q] - [Price 2019], [Price 2019] )
YoY Change =
VAR cur = [Median Price]
VAR qi = MAX ( dim_date[q_index] )
VAR prev = CALCULATE ( [Median Price], FILTER ( ALL ( dim_date ), dim_date[q_index] = qi - 4 ) )
RETURN DIVIDE ( cur - prev, prev )
Price Index (2019 = 100) = DIVIDE ( [Median Price], [Price 2019] ) * 100
```

Cross-check: Growth Since 2019 must match Python `growth_pct` for 3 LGAs.

| Page | Main visual | Supporting | Answers |
|---|---|---|---|
| 1 The answer | Sorted bar: growth since 2019 by LGA | Houses/units slicer; cards: Greater Sydney growth, fastest, slowest | Which LGAs grew fastest |
| 2 Trends | Line: price index (2019 = 100) | LGA slicer vs Sydney line | When growth happened |
| 3 Why? | Scatter: growth vs distance (and vs 2019 price) | Size = sales; tooltip LGA | What fast growers share |
| 4 Notes | Text | Sources, method, limitations, as-of date | Trust |

Design: one question per page, finding-stating titles, ≤2 colours + grey, same slicer position on every page.

## Phase 5 — Write-up and GitHub

README order: title + one-sentence answer with number → page 1 screenshot → 3–5 numbered findings →
sources with links, licences, as-of dates → method (5–6 bullets) → limitations → how to reproduce →
tools used (including AI assistance, stated plainly).

## Final checklist

- Public repo with clean commit history (commit as you go)
- Notebooks run top to bottom without errors
- `sql/transform.sql` with at least one join, one CTE and one window function
- 4 page screenshots in `powerbi/` + PDF export
- README with findings, limitations and sources; `docs/data_dictionary.md` for every column
- No address-level data, passwords or keys in the repo
- LinkedIn post: 3 findings, one screenshot, repo link
- Kang can explain every DAX measure and chart choice out loud in 2 minutes

## Pitfalls

- Averaging medians across LGAs (meaningless) — show each LGA or use the published Greater Sydney figure.
- Mixing houses and units in one growth number.
- Reading too much into a correlation from ~33 points.
- Adding every dataset found; 2–3 tested factors beat 10 untested ones.
- Letting AI write code the owner cannot explain.
