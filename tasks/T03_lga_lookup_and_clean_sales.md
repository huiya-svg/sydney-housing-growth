# T03 — LGA lookup table + clean core sales into long format + measure revisions

**Phase:** 2 · **Implementer:** Codex · **Reviewer:** Claude · **Owner:** Kang
**Read first:** `AGENTS.md`, `docs/decisions.md` (D04, D05, D06), `tasks/reviews/T01_review.md`,
`tasks/reviews/T02_review.md` (note 4), notebook `01_explore.ipynb` Part A (how the workbooks are laid out).

## Context

We now know the DCJ workbooks well (T01) and have the ABS codes for each LGA (T02). This task turns the
29 workbooks into **one tidy table**, one row per geography × quarter × dwelling type, and builds the
lookup table that every later join will use. Decisions that apply:

- **D04:** Greater Sydney = DCJ's own 34 LGAs, with DCJ's Inner / Middle / Outer Ring as the region.
- **D05:** Wollondilly units have no 2019 baseline. Keep the rows (as missing). Exclusion happens in the analysis.
- **D06:** Use each quarter **as first published**. This task measures how large later revisions are.

## Outputs

### 1. `data/reference/lga_lookup.csv`: 34 rows, one per LGA

| Column | Meaning |
|---|---|
| `lga` | DCJ label, the canonical name used everywhere in this project (e.g. `Sutherland Shire`) |
| `region` | DCJ ring: `Inner Ring`, `Middle Ring` or `Outer Ring` |
| `lga_code_2025` | ABS LGA 2025 code (5 digits, stored as text) |
| `abs_name_2025` | ABS LGA 2025 label (e.g. `Sutherland`) |

Build it in the notebook from the raw files: DCJ labels and rings from the sales workbooks, and ABS codes and
names from the ERP workbook (`abs_erp/32180DS0004_2001-25.xlsx`, Table 1). Handle the six known name
differences with **one small, visible Python dict** (DCJ label → ABS 2025 label), not fuzzy matching.
Every later join to ABS data uses `lga_code_2025`, never the name.

### 2. `data/interim/sales_long.csv`: one row per geography × quarter × dwelling type

| Column | Type | Meaning |
|---|---|---|
| `quarter_date` | date | First day of the quarter (`2019-01-01` = March quarter 2019) |
| `geo_level` | text | `lga`, `ring` or `greater_sydney` |
| `geo_name` | text | LGA label (as in `lga_lookup`), ring name, or `Greater Sydney` |
| `region` | text | Ring for `lga` and `ring` rows. Empty for `greater_sydney`. |
| `dwelling_type` | text | `house` (DCJ `Non Strata`) or `unit` (DCJ `Strata`). Drop DCJ `Total`. |
| `median_price` | integer, nullable | Median sale price in **dollars** (DCJ's $'000 × 1,000). Empty if not published. |
| `sales_count` | integer, nullable | Number of sales. Empty if not published. |
| `price_status` | text | `published`, `suppressed` (DCJ `-`), or `not_in_source` (row absent from the workbook) |
| `count_status` | text | `published`, `suppressed_10_or_fewer` (`-`), `suppressed_30_or_fewer` (`s`), or `not_in_source` |
| `low_sales_flag` | boolean | True when `count_status` is not `published`, i.e. 30 or fewer sales or unknown |
| `source_file` | text | Workbook filename |
| `source_row` | integer, nullable | Excel row number in sheet `LGA` (empty for `not_in_source`) |

Expected size: LGA rows 34 × 29 × 2 = **1,972** (including 1 `not_in_source`), ring rows 3 × 29 × 2 = **174**,
Greater Sydney rows 1 × 29 × 2 = **58**, so **2,204** rows in total. If the numbers differ, explain why rather
than forcing them.

Keep the ring and Greater Sydney rows. They are DCJ's own published medians, and later steps use them as
the benchmark instead of averaging LGA medians (pitfall in the project plan).

## Steps (`notebooks/02_clean.ipynb`, plain pandas, no SQL in this task)

Each step gets a plain-English markdown cell (what and why).

1. **Read.** Load the `LGA` sheet of all 29 sales workbooks. You may move the reading logic from
   `01_explore.ipynb` into a small helper module `src/dcj_sales.py` (one or two functions with docstrings)
   and import it. **Do not edit `01_explore.ipynb`.**
2. **Select rows.** Keep the Greater Sydney block only: 34 LGA rows per quarter per type, the three ring
   totals and the Greater Sydney total. Show how each is identified (columns A–E values).
3. **Convert values.** Strip thousands separators, turn `-` and `s` into missing (never 0), set the
   status columns, multiply prices by 1,000, cast to nullable integers.
4. **Complete the grid.** Add explicit rows for any geography × quarter × type missing from the workbook
   (expected: Wollondilly unit, June 2019) with status `not_in_source`.
5. **Build `lga_lookup`.** As described above. Assert that each LGA sits in exactly one ring in all 29
   quarters, and that all 34 codes exist in both the ERP table and the T02 boundary GeoJSON.
6. **Measure revisions (D06).** Each workbook's `quarterly_median_change` (column K) is calculated against
   DCJ's *revised* previous-quarter median. For every LGA × type × quarter from 2019 Q2 onwards:
   `implied_revised_prev = median_t / (1 + change_t)`. Compare it with the first-published
   `median_{t-1}`: `revision_pct = implied_revised_prev / first_published_prev − 1`.
   - First work out the rounding tolerance. Medians are rounded to $'000 and the change to a fixed number
     of decimals, so state the largest revision that rounding alone could produce.
   - Summarise by dwelling type: count, median absolute revision, 90th percentile, max, and share within
     the rounding tolerance. Show the 5 largest revisions with their source cells.
   - Do the same for the Greater Sydney rows.
   - End with a 2–3 sentence plain-English conclusion that could go straight into the README limitations.
   - The revision analysis stays in the notebook and is **not** written to a CSV.
7. **Validate** (as `assert` statements that fail loudly, plus a printed summary):
   - row counts per `geo_level` as above; no duplicate (`quarter_date`, `geo_level`, `geo_name`, `dwelling_type`);
   - 29 distinct quarters from 2019-01-01 to 2026-01-01, with no gaps;
   - set of LGA `geo_name`s equals `lga_lookup.lga` (34);
   - exactly the expected `not_in_source` rows; every missing `median_price` has a non-`published` status, and
     no price or count is 0;
   - all published prices between $100,000 and $10,000,000 (sanity range);
   - reconcile the number of suppressed prices and counts with the T01 marker audit (notebook 01 section 6) and
     explain any difference (T01 also counted DCJ `Total` rows);
   - spot checks in dollars, March quarter 2026: Blacktown house median **1,250,000**; Sydney unit median
     **967,000**; Parramatta unit sales **835**; Greater Sydney house median **1,550,000**; Greater Sydney unit
     median **855,000**; Wollondilly unit, March 2019: price `suppressed`.
8. **Export** both CSVs (UTF-8, header, no index, dates as `YYYY-MM-DD`). End the notebook with a markdown
   cell listing each output column in one line (T06 turns this into the data dictionary).

Must pass: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb`.
Running it twice must produce byte-identical CSVs.

## Out of scope

- Factor tables (population, distance, etc.) and `dim_lga`. That's T04, after Kang decides D07.
- SQL, `dim_date`, year-on-year change, growth calculations. That's T05 and T07.
- Editing `01_explore.ipynb`, `docs/data_dictionary.md`, or anything in `data/raw/`.

## Allowed files

- `notebooks/02_clean.ipynb`
- `src/dcj_sales.py` (and an empty `src/__init__.py` if needed)
- `data/reference/lga_lookup.csv`
- `data/interim/sales_long.csv`
- `tasks/reports/T03_report.md`

## Questions to answer in the report

- **Q1.** Row counts per `geo_level`, `not_in_source` rows, and counts of each `price_status` / `count_status`
  value by dwelling type (LGA rows only).
- **Q2.** The six DCJ → ABS name mappings used, and confirmation that all 34 codes are found in ERP and GeoJSON.
- **Q3.** Ring membership: how many LGAs per ring, and whether any LGA changes ring across quarters.
- **Q4.** Revisions: rounding tolerance, the summary table, the 5 largest, and your plain-English conclusion.
  Does using first-published values plausibly change any LGA's growth ranking materially?
- **Q5.** Reconciliation with the T01 marker counts.
- **Q6.** Anything odd: medians that jump suspiciously quarter to quarter (e.g. > 25% in one quarter with
  > 30 sales), header or format quirks, values that needed special handling.

## Acceptance criteria

- [ ] A1 Both CSVs exist with exactly the columns above, in that order; row counts as expected or explained.
- [ ] A2 All validation asserts pass; notebook executes top to bottom with nbconvert; second run gives
      byte-identical CSVs.
- [ ] A3 No missing value is stored as 0. Suppressed and absent rows are distinguishable by status.
- [ ] A4 Revision analysis present with tolerance, summary, top 5 and conclusion.
- [ ] A5 Code is plain pandas with a markdown explanation per step; helper module (if any) is short and documented.
- [ ] A6 Report answers Q1–Q6; only allowed files changed; no git commands.

## Kang's part (after review)

1. Open `data/interim/sales_long.csv` in Excel. Filter to **your own choice of LGA** and `house`. Check the
   four 2019 medians against the raw workbooks (find the row via `source_file` and `source_row`).
2. Read the revisions section and be ready to say in one sentence why we use first-published values.
3. Be ready to explain why the table keeps ring and Greater Sydney rows (hint: pitfall #1 in the plan).
4. Commit after Claude's review says Accept.
