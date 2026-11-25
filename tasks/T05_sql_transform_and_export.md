# T05 — `sql/transform.sql`: star schema tables, revised-estimate series, growth, validation, export

**Phase:** 2 (steps 6–8) · **Implementer:** Codex · **Reviewer:** Claude · **Owner:** Kang
**Read first:** `AGENTS.md`, `docs/project_plan.md` (Phase 2 step 6–8, Phase 3A, Phase 4.1–4.2),
`docs/decisions.md` (D02, D04–D08), `tasks/reviews/T03_review.md`, `tasks/reviews/T04_review.md`.

## Context

All inputs are now clean: `data/interim/sales_long.csv` (2,204 rows, 14 columns),
`data/interim/lga_factors.csv` (34 rows) and `data/reference/lga_lookup.csv` (34 rows). This task is the
project's **SQL showcase**. One SQL file builds the four tables Power BI will load, as a star schema.
Recruiters will read `sql/transform.sql`, so it must be **clean, commented and easy to follow**: CTEs with
meaningful names, one short comment per step, no clever tricks.

## Design (already decided, so follow it)

**Geographies in one dimension.** `dim_lga` holds the 34 LGAs **plus** the 3 rings and Greater Sydney
(38 rows), with a `geo_level` column. `fact_sales` holds all 2,204 rows. Power BI then filters
`geo_level = "lga"` for LGA visuals and uses `greater_sydney` for the benchmark. This way we never average
LGA medians (pitfall #1). The key column is called `lga` everywhere (for ring and Greater Sydney rows it holds
the ring name or `Greater Sydney`).

### Output 1: `data/processed/fact_sales.csv` (one row per `lga` × `quarter_date` × `dwelling_type`, 2,204 rows)

| Column | Definition |
|---|---|
| `lga`, `quarter_date`, `dwelling_type` | Keys (from `geo_name`, `quarter_date`, `dwelling_type`) |
| `median_price`, `sales_count` | First-published values (D06), nullable |
| `price_status`, `low_sales_flag` | As in `sales_long` |
| `yoy_change` | `median_price / LAG(median_price, 4) − 1` over (`lga`, `dwelling_type`) ordered by quarter. Null if either value is null. |
| `median_price_revised_est` | D08 revised estimate, see below. Rounded to the nearest $1,000. |
| `revised_source` | `annual` / `quarterly` / `first_published` / null: which rule produced the estimate |

**Revised-estimate rule (D08), using window functions over (`lga`, `dwelling_type`) ordered by quarter:**
1. If the row 4 quarters later has a price and an `annual_change`: `LEAD(median_price, 4) / (1 + LEAD(annual_change, 4))` → `annual`.
2. Else, if the next row has a price and a `quarterly_change`: `LEAD(median_price, 1) / (1 + LEAD(quarterly_change, 1))` → `quarterly`.
3. Else, if this row has a price: `median_price` → `first_published` (e.g. the latest quarter).
4. Else null.

The grid is complete (T03 added the missing Wollondilly row), so `LEAD`/`LAG` by row are correct. Assert this
before relying on it: 29 consecutive quarters per `lga` × `dwelling_type`.

### Output 2: `data/processed/dim_lga.csv` (38 rows)

`lga, geo_level, region, lga_code_2025, distance_km, pop_growth_2016_19, income_2016_weekly,
rent_2019_house_weekly, rent_2019_unit_weekly, sort_order`

LGA rows: join `lga_lookup` to `lga_factors` on `lga_code_2025`. Ring rows: `region` = ring name, factors null.
Greater Sydney row: region and factors null. `sort_order`: Greater Sydney 1, rings 2–4 (Inner, Middle, Outer),
LGAs 5–38 alphabetically.

### Output 3: `data/processed/dim_date.csv` (29 rows)

`quarter_date, year, quarter_label (e.g. "2019 Q1"), q_index (1…29), is_baseline_2019, is_latest_4q`

Derive the quarters from the data (`DISTINCT quarter_date`), not a hard-coded list. `is_latest_4q` = the four
most recent quarters in the data (currently Jun 2025 – Mar 2026), computed with a window function or
`MAX(...)`, never hard-coded.

### Output 4: `data/processed/lga_growth.csv` (one row per `lga` × `dwelling_type`, 76 rows)

| Column | Definition |
|---|---|
| `lga`, `geo_level`, `region`, `dwelling_type` | Keys and labels |
| `baseline_quarters`, `latest_quarters` | Number of published medians (0–4) in each window |
| `baseline_low_sales_quarters`, `latest_low_sales_quarters` | How many of those had `low_sales_flag` |
| `price_2019` | Average of the four 2019 medians, **only if all 4 are published**, else null |
| `price_latest` | Average of the latest four medians, **only if all 4 are published**, else null |
| `growth_pct` | `price_latest / price_2019 − 1` (decimal fraction), null if either is null |
| `growth_annualised` | `(1 + growth_pct) ^ (1 / years) − 1`, with `years` = gap between the two window midpoints in years (currently 6.25). Compute it from the dates; don't hard-code. |
| `price_2019_rev`, `price_latest_rev`, `growth_pct_rev` | Same three using `median_price_revised_est` (D08 sensitivity) |
| `growth_note` | Null, or a short reason when growth is null (e.g. `baseline: 0 of 4 quarters published`) |

Rankings, real growth and the sensitivity comparison are **T07**, not here.

## `sql/transform.sql` structure

- Plain DuckDB SQL. Read the three input CSVs with `read_csv(..., columns = {...})` or explicit casts
  (`quarter_date` as DATE, codes as VARCHAR, prices as BIGINT/DOUBLE). Don't rely on type sniffing.
- A sequence of `CREATE OR REPLACE TABLE <name> AS ...` statements, one per output (plus a staging table if
  needed), each with a 1–3 line header comment saying what it builds and why.
- Must include at least: one **join** (dim_lga), one **CTE** (several is fine), **window functions** (`LAG`,
  `LEAD`, plus one for `q_index` such as `ROW_NUMBER()`), and **conditional aggregation** for the growth windows
  (`AVG(...) FILTER (WHERE ...)` or `CASE`).
- File paths: use relative paths that work when DuckDB runs from the repo root, or parameters, whichever
  `distance.sql` set as the precedent. Document the choice in the file's header.
- The SQL builds tables only. The notebook does the export (`COPY ... TO ... (HEADER, DELIMITER ',')`, or pandas)
  so the export step is visible.

## Notebook: new final section in `notebooks/02_clean.ipynb`

"Step 10 — SQL transform and export" (or the next number), with a markdown cell per step:
1. Run `sql/transform.sql` in a fresh in-memory DuckDB connection.
2. Show the first rows of each table and its row count.
3. **Validation** (asserts + printed summary):
   - row counts: fact 2,204; dim_lga 38; dim_date 29; lga_growth 76;
   - no duplicate keys in any table; every `fact_sales.lga` in `dim_lga`; every `fact_sales.quarter_date` in `dim_date`;
   - exactly 4 rows with `is_baseline_2019` and exactly 4 with `is_latest_4q`;
   - `yoy_change` spot check: recompute 3 values in pandas from `sales_long` and compare;
   - **growth cross-check:** recompute `growth_pct` in pandas for Blacktown house, Sydney unit and Greater Sydney
     house, and compare to SQL (abs diff < 1e-9). Print the numbers;
   - Wollondilly unit `growth_pct` is null, with a note (D05). List **every** null-growth row and its note;
   - `revised_source` counts by type; the latest quarter's rows are all `first_published`;
   - no zero prices; all growth values between −50% and +200% (sanity).
4. Export the four CSVs to `data/processed/` (UTF-8, header, no index, dates `YYYY-MM-DD`, booleans
   `true`/`false`, decimals with full precision). A second run must give byte-identical files.

Must pass: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb`.

## Out of scope

- Real (CPI-adjusted) growth, rankings, charts, correlations (T07, T08). Data dictionary (T06).
- Changing earlier notebook sections or any interim/reference CSV.

## Allowed files

- `sql/transform.sql`
- `notebooks/02_clean.ipynb` (append the new section only)
- `data/processed/fact_sales.csv`, `dim_lga.csv`, `dim_date.csv`, `lga_growth.csv`
- `tasks/reports/T05_report.md`

## Questions to answer in the report

- **Q1.** Row counts for all four tables, and the full list of null-growth rows with their notes.
- **Q2.** The growth cross-check numbers (SQL vs pandas) for the three named rows.
- **Q3.** `years` used for annualising and how it was derived.
- **Q4.** `revised_source` counts; how many LGA × type pairs have a different growth rank (first-published vs
  revised) — just the count of rank changes > 3 places; T07 does the full analysis.
- **Q5.** Top 5 and bottom 5 LGAs by `growth_pct` for houses and for units (LGA rows only). This is the first
  preview of the project's answer.
- **Q6.** Which SQL features are used and where (line numbers), for Kang's CV notes.

## Acceptance criteria

- [ ] A1 Four CSVs with exactly the specified columns and row counts.
- [ ] A2 `sql/transform.sql` is readable: header comment, one comment per table/CTE, no hard-coded quarter dates,
      contains a join, CTEs, `LAG`, `LEAD`, a ranking/numbering window, and conditional aggregation.
- [ ] A3 All validation asserts pass, including the pandas growth cross-check.
- [ ] A4 Notebook executes clean; second run gives byte-identical CSVs.
- [ ] A5 Report answers Q1–Q6; only allowed files changed; no git commands.

## Kang's part (after review)

1. Read `sql/transform.sql` top to bottom. For each table, say in one sentence what it does. Mark any line you
   can't explain and ask Claude. This file is your main SQL interview material.
2. In Excel, take one LGA you know from `fact_sales.csv` and recompute its `growth_pct` by hand from the 8
   quarterly medians. It must match `lga_growth.csv`. (In T09 you'll repeat this check in Power BI with DAX.)
3. Commit after Claude's review says Accept.
