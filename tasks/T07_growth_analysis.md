# T07 — Growth analysis: real growth (CPI), rankings, sensitivity, first charts

**Phase:** 3A · **Implementer:** Codex · **Reviewer:** Claude · **Owner:** Kang
**Read first:** `AGENTS.md`, `docs/project_plan.md` (Phase 3A), `docs/decisions.md` (D02, D05, D06, D08),
`tasks/reviews/T05_review.md` (sensitivity section), `sql/transform.sql`.

> Order note: the dictionary task (T06) moves to after T08, so it documents the final columns once.

## Context

T05 produced nominal growth for every LGA × dwelling type. This task turns it into the **answer to the
project question**: rankings, inflation-adjusted (real) growth, the D08 sensitivity check, and the first
charts. Kang is building the Power BI model from the same CSVs in parallel, so **keep all existing columns
and their meaning unchanged**. Only add columns.

## Part 1: CPI and real growth (SQL)

1. **CPI input.** In `02_clean.ipynb`, add a short section that writes `data/interim/cpi_sydney.csv` with
   columns `quarter_date, cpi_sydney`. Use ABS series **A2325806K** (Sydney, All groups) from
   `data/raw/abs_cpi/6401017.xlsx`, sheet `Data1`. ABS dates the quarter by its **last month** (e.g. Mar-2019).
   Convert each to the **first day of the quarter** (`2019-01-01`) to match our `quarter_date`. Keep only the
   quarters in `dim_date`, and assert that none are missing.
2. **`sql/transform.sql`** (extend; keep the existing statements and style):
   - `dim_date`: add `cpi_sydney` (join on `quarter_date`).
   - `lga_growth`: add
     - `cpi_ratio` = average CPI of the latest four quarters ÷ average CPI of the four 2019 quarters (the same
       for every row);
     - `growth_pct_real` = `(1 + growth_pct) / cpi_ratio − 1`;
     - `growth_rank` = `RANK() OVER (PARTITION BY dwelling_type ORDER BY growth_pct DESC)` over **LGA rows with
       non-null growth only** (rings and Greater Sydney get null);
     - `growth_rank_rev` = the same on `growth_pct_rev`;
     - `rank_change_rev` = `growth_rank_rev − growth_rank`.
   - Add the new columns **at the end** of each table. The existing columns stay byte-identical (prove it as in
     T04, by dropping the new columns and comparing hashes with the committed files).
3. Re-export all four processed CSVs. Keep everything deterministic.

Real growth uses the same CPI ratio for every LGA, so it doesn't change any ranking. It changes the headline
numbers. State this in the notebook.

## Part 2: `notebooks/03_analysis.ipynb`, Part A "How much did prices grow?"

Read only from `data/processed/`. Plain pandas and matplotlib/seaborn. Plain-English markdown before each step.

1. **Benchmarks.** Table: Greater Sydney and the three rings, nominal growth, annualised, real, for houses and
   units.
2. **Rankings.** One table per dwelling type: rank, LGA, region, `price_2019`, `price_latest`, nominal growth,
   annualised, real growth, low-sales quarters (baseline + latest), and `rank_change_rev`. Wollondilly unit is
   listed separately as "no 2019 baseline (D05)".
3. **Sensitivity (D08).** Spearman correlation between `growth_pct` and `growth_pct_rev` per dwelling type, and
   every LGA with |`rank_change_rev`| > 3. Write a 2–3 sentence conclusion (Woollahra houses are the key case).
4. **Robustness flags.** For each LGA × type in the top 5 or bottom 5, say whether it has low-sales quarters
   in either window or a |rank change| > 3. These need a caveat in the README.
5. **Charts** → save as PNG (150 dpi) in `docs/figures/`:
   - `growth_by_lga_house.png` and `growth_by_lga_unit.png`: horizontal bars, LGAs sorted by growth, with a vertical
     line for Greater Sydney's growth. Highlight the top 5 in one colour, everyone else in grey, and give
     LGAs with caveats a hatch or marker plus a legend note.
   - `price_index_rings.png`: price index (2019 average = 100) by quarter for Greater Sydney and the three rings,
     with houses and units as two panels.
   - Design rules: at most 2 colours plus grey, titles that **state the finding** (e.g. "Houses in Sydney's
     south-west grew fastest since 2019"), axis labels with units, percent axes formatted as %, readable at
     README size (about 1,000 px wide). No 3D, no pie charts.
6. **Draft findings (houses and units).** 3–4 sentences with numbers, in the plan's style: "Houses in [LGA] grew
   X% from 2019 to [latest quarter], against Y% for Greater Sydney." Avoid claims the sensitivity check doesn't
   support. Factor findings come in T08.

Must pass: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace` for **both** `02_clean.ipynb` and
`03_analysis.ipynb` (in that order). A second run gives byte-identical CSVs. PNGs can differ in metadata, but
set `metadata={"Software": None}` or similar if that's easy.

## Out of scope

- Factor correlations and regression (T08). Data dictionary (T06). README (T11). Power BI.
- Changing any existing column, row or earlier notebook section.

## Allowed files

- `notebooks/02_clean.ipynb` (append the CPI section only), `notebooks/03_analysis.ipynb` (new)
- `sql/transform.sql` (extend)
- `data/interim/cpi_sydney.csv`, `data/processed/*.csv` (re-export with appended columns)
- `docs/figures/*.png`
- `tasks/reports/T07_report.md`

## Questions to answer in the report

- **Q1.** CPI: 2019 average, latest-4Q average, `cpi_ratio`; the source cell range used.
- **Q2.** Benchmark table (nominal, annualised, real) for Greater Sydney and the rings.
- **Q3.** Top 5 and bottom 5 per dwelling type with nominal and real growth, and caveat flags.
- **Q4.** Sensitivity: Spearman values, LGAs moving > 3 ranks, your conclusion.
- **Q5.** The draft findings sentences.
- **Q6.** Proof that the existing columns in all four processed CSVs are unchanged.

## Acceptance criteria

- [ ] A1 New columns only appended; existing columns byte-identical to the committed T05 files.
- [ ] A2 `growth_pct_real` recomputable from `growth_pct` and `cpi_ratio`; ranks correct and null for non-LGA rows.
- [ ] A3 `03_analysis.ipynb` runs clean after `02_clean.ipynb`; three PNGs saved and follow the design rules.
- [ ] A4 Report answers Q1–Q6; only allowed files changed; no git commands.

## Kang's part (after review)

1. Look at the three charts. Is each title true and the most important message? Suggest changes.
2. Pick the 2 sentences from the draft findings you'd put first on your CV, and rewrite them in your own words.
3. In Power BI Desktop: pull the new CSVs (GitHub Desktop → Fetch/Pull) and click **Refresh**. The new
   columns appear and your existing work stays.
4. Commit after Claude's review says Accept.
