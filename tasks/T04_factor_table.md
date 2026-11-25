# T04 — Factor table for the D07 factors (distance in SQL) + change columns on sales

**Phase:** 2 · **Implementer:** Codex · **Reviewer:** Claude · **Owner:** Kang
**Read first:** `AGENTS.md`, `docs/decisions.md` (D07, D08), `tasks/reviews/T02_review.md`,
`tasks/reviews/T03_review.md`, `notebooks/01_explore.ipynb` Part B (how each factor file is laid out),
`notebooks/02_clean.ipynb`.

## Context

Kang chose the factors in **D07**:
- **Main:** distance to CBD, population growth June 2016 → June 2019, 2019 price level.
- **Exploratory:** 2016 median household income, 2019 median weekly rent.

The 2019 price level comes from the sales data and is calculated later (T05 and T07), so it's **not** part of
this task. This task produces one clean row per LGA with the other four factors. It also adds two raw
change columns to `sales_long.csv`, so that T05 can build a revised-estimate series in SQL (D08).

## Part 1: add change columns to `sales_long.csv` (small edit to `02_clean.ipynb`)

Append two columns at the **end** of `sales_long.csv`:

| Column | Meaning |
|---|---|
| `quarterly_change` | DCJ column K for that row (quarterly change in median), as a decimal fraction (−0.2391 for −23.91%). Empty if `-`, blank or not in source. |
| `annual_change` | DCJ column L (annual change in median), same format |

Don't change any other column or row. Prove it: all existing 12 columns must be byte-identical to the
committed version (compare after dropping the two new columns). Update the column list in the notebook's
final markdown cell.

## Part 2: factor table `data/interim/lga_factors.csv` (34 rows)

Add new sections to `02_clean.ipynb` after the existing ones. One section per factor, each with a
plain-English markdown cell. Join every ABS source on **`lga_code_2025`** from `data/reference/lga_lookup.csv`,
never on names.

| Column | Type | Definition | Source |
|---|---|---|---|
| `lga` | text | Canonical DCJ label | `lga_lookup.csv` |
| `lga_code_2025` | text | ABS code | `lga_lookup.csv` |
| `distance_km` | number (2 dp) | Straight-line km from the LGA's geometric centroid to the Sydney GPO | Part 3 SQL |
| `pop_2016` | integer | ERP at 30 June 2016 | ABS ERP Table 1 |
| `pop_2019` | integer | ERP at 30 June 2019 | ABS ERP Table 1 |
| `pop_growth_2016_19` | number (decimal fraction, 4 dp) | `pop_2019 / pop_2016 − 1` | derived |
| `income_2016_weekly` | integer, nullable | 2016 Census median total household weekly income ($) | Census 2016 G02 `Median_tot_hhd_inc_weekly` |
| `rent_2019_house_weekly` | number, nullable | Average of the four 2019 quarterly median weekly rents, dwelling type `House`, all bedrooms (`Total`) | DCJ rent tables, issues 127–130 |
| `rent_2019_unit_weekly` | number, nullable | Same for `Flat/Unit` | same |

Rules:
- **Income 2016:** the 2016 Census uses LGA 2016 codes. For the 33 LGAs whose code is unchanged, take the
  value directly and **prove** the code is the same (show the 2016 label next to the DCJ label). **Bayside
  stays empty.** Its predecessors (Botany Bay, Rockdale) have separate medians, and medians can't be averaged.
  Print the two predecessor medians in the notebook for information only.
- **Rent 2019:** use the Sydney ring rows of DCJ's rent table (as in T02 Part B). Averaging the four
  quarterly medians *of the same LGA* is the same method as our price baseline. It is not averaging across
  LGAs. If a quarter is suppressed, average the available ones and add a column
  `rent_2019_quarters_used_house` / `_unit` (0–4). Watch the T02 note: issue 129's `LGA!A1` says June, but the
  file is September.
- **Population:** June 2016 and June 2019 values from the ERP 2001–2025 table (LGA 2025 boundaries,
  back-cast by ABS, so no merger adjustment is needed).

## Part 3: distance as one SQL file, `sql/distance.sql`

Rewrite T02's distance calculation (DuckDB relational API) as **one readable SQL query with CTEs**, run from
the notebook with `duckdb.sql(Path('sql/distance.sql').read_text())` or similar. Suggested shape:

```sql
-- Distance from each LGA's geometric centroid to the Sydney GPO.
INSTALL spatial; LOAD spatial; SET geometry_always_xy = true;

WITH boundaries AS (          -- 1. read the ABS LGA 2025 polygons
    SELECT lga_code_2025, lga_name_2025, geom
    FROM ST_Read('data/raw/abs_asgs/LGA_2025_Sydney_region.geojson')
),
centroids AS (                -- 2. centroid in an equal-area projection, then back to lon/lat
    SELECT lga_code_2025,
           ST_Transform(ST_Centroid(ST_Transform(geom, 'EPSG:4326', 'EPSG:9473')),
                        'EPSG:9473', 'EPSG:4326') AS centre
    FROM boundaries
),
gpo AS (                      -- 3. the GPO point from the NSW heritage register file
    SELECT geom AS gpo_point FROM ST_Read('data/raw/abs_asgs/Sydney_GPO_00763.geojson')
)
SELECT c.lga_code_2025,
       ROUND(ST_Y(c.centre), 6) AS centroid_lat,
       ROUND(ST_X(c.centre), 6) AS centroid_lon,
       ROUND(ST_Distance_Spheroid(c.centre, g.gpo_point) / 1000, 2) AS distance_km
FROM centroids c CROSS JOIN gpo g
ORDER BY c.lga_code_2025;
```

Adjust the details (file paths relative to where the query runs, function arguments) until it works.
Keep it this readable, with a one-line comment per CTE. The result must match the T02 notebook output
within 0.01 km for all 34 LGAs. Show that comparison in the notebook.

## Validation (asserts + printed summary)

- 34 rows; `lga` and `lga_code_2025` match `lga_lookup.csv` exactly; no duplicates.
- The only missing values allowed: Bayside `income_2016_weekly`, plus any rent cell with
  `quarters_used = 0` (report which).
- Sanity ranges: distance 0–100 km; population growth −10% to +30%; income $800–$5,000/week;
  rent $250–$2,000/week.
- Spot checks: Blacktown `pop_2016` 348,030, `pop_2019` 380,186 (growth 0.0924); Sydney 222,717 → 229,596;
  Blacktown distance 34.79 km; Blue Mountains 76.16 km; Sydney 2.45 km; Blacktown March 2019 house rent
  $470 and Sydney March 2019 unit rent $650 appear among the averaged inputs.
- Running the notebook twice gives byte-identical `sales_long.csv`, `lga_lookup.csv` and `lga_factors.csv`.

Must pass: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb`.

## Out of scope

- 2019 price level, growth, correlations, `dim_lga` / `dim_date` / `fact_sales` (T05 and T07).
- Any factor not chosen in D07. Population-weighted centroids. Editing `01_explore.ipynb` or `data/raw/`.

## Allowed files

- `notebooks/02_clean.ipynb`
- `sql/distance.sql`
- `data/interim/sales_long.csv` (two appended columns only), `data/interim/lga_factors.csv`
- `tasks/reports/T04_report.md`

## Questions to answer in the report

- **Q1.** Proof that the 12 original `sales_long.csv` columns are unchanged; how many rows have empty
  `quarterly_change` / `annual_change`, and why.
- **Q2.** The full 34-row factor table (as a markdown table in the report).
- **Q3.** Income: the 33 code matches (2016 label vs DCJ label) and the two Bayside predecessor medians.
- **Q4.** Rent: quarters used per LGA and type; any suppressed or missing values; how issue 129 was handled.
- **Q5.** Distance: the SQL-vs-T02 comparison (max absolute difference).
- **Q6.** Anything surprising in the factor values (e.g. negative population growth, very high rents).

## Acceptance criteria

- [ ] A1 `sales_long.csv` has 14 columns; the first 12 are byte-identical to the committed file.
- [ ] A2 `lga_factors.csv` has exactly the columns above (plus the two `quarters_used` columns), 34 rows,
      and only the allowed missing values.
- [ ] A3 `sql/distance.sql` is a single readable query with commented CTEs; results match T02 within 0.01 km.
- [ ] A4 All asserts pass; nbconvert runs clean; second run gives byte-identical CSVs.
- [ ] A5 Report answers Q1–Q6; only allowed files changed; no git commands.

## Kang's part (after review)

1. Read `sql/distance.sql` and explain each CTE out loud in one sentence. This is a likely interview question.
2. Check one LGA's population growth by hand in Excel from `data/raw/abs_erp/32180DS0004_2001-25.xlsx`, Table 1.
3. Confirm or change **D08** (revisions sensitivity check) in `docs/decisions.md`.
4. Commit after Claude's review says Accept.
