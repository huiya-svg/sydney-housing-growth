# T07 report — Growth, inflation adjustment, rankings and sensitivity

## Summary

The pipeline adds Sydney CPI, real growth and two LGA rankings while preserving every T05 output column byte-for-byte. Greater Sydney house prices grew 67.5% in nominal terms and 34.9% after inflation, while unit prices grew 18.1% nominally and fell 4.8% after inflation. Fairfield led first-published house growth and Hawkesbury led unit growth. Woollahra houses moved from 34th to 17th in the revised-estimate ranking, the largest movement.

## Files created or changed

- `notebooks/02_clean.ipynb` — appended the CPI preparation and validation steps.
- `notebooks/03_analysis.ipynb` — Part A with benchmarks, rankings, sensitivity, caveats, figures and draft findings.
- `sql/transform.sql` — added the CPI join, real growth calculation and first-published and revised ranks.
- `data/interim/cpi_sydney.csv` — 29 quarter-start CPI values from the ABS workbook.
- `data/processed/dim_date.csv` — re-exported with one appended CPI column.
- `data/processed/lga_growth.csv` — re-exported with five appended CPI, real growth and ranking columns.
- `data/processed/fact_sales.csv` and `data/processed/dim_lga.csv` — re-exported byte-for-byte.
- `docs/figures/growth_by_lga_house.png` and `docs/figures/growth_by_lga_unit.png` — ranked nominal LGA growth, the Greater Sydney benchmarks and caveat hatching.
- `docs/figures/price_index_rings.png` — two panels for the published Greater Sydney and ring price indexes.
- `tasks/reports/T07_report.md` — submission and verification evidence.

## Commands run

| Command | Result |
|---|---|
| `cat`, `sed`, `rg`, `shasum -a 256` and `.venv/bin/python -` with nbformat and openpyxl | Read AGENTS.md, T07, Phase 3A, the decisions, T05 review, the T05 SQL and the workbook. Recorded starting file and cell hashes. The initial directory check returned `ls: docs/figures: No such file or directory`. The analysis notebook created it. |
| `.venv/bin/python -` to prepare both notebooks and seed the CPI input | Wrote 29 CPI rows using the cleaning notebook step and T05 date dimension. The initial compile of the ranking table emitted `SyntaxWarning: invalid escape sequence '\$'`. Removed the escapes and recompiled successfully. |
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb`, then the same command for `notebooks/03_analysis.ipynb` | Pass in that order for both rounds. The kernel emitted its startup warning, `Kernel is running over TCP without encryption`. |
| `shasum -a 256` and `test` | Pass. The CPI input and all four processed CSVs have identical hashes across runs. |
| `.venv/bin/python -` for the independent workbook, CSV and SciPy checks | Pass. All 29 CPI observations matched the workbook, real growth and ranks recomputed, and all four T05 projections matched their starting hashes. |
| `.venv/bin/python -` with a temporary copy containing a stale CPI value | Pass. The appended section corrected that value from the workbook and re-exported all four expected tables. |
| `.venv/bin/python -` with nbformat and Pillow, then visual inspection of the PNGs | Pass. Verified executed notebook cells, restored the pre-task records for the original 43 cells, checked all three PNG dimensions and resolution, and read each figure at its saved width. |

## Answers to the task questions

### Q1. Sydney CPI and the two price windows

The Sydney All groups CPI series is **A2325806K** in `Data1!B10`. The date/value range used is `Data1!A293:B321`, covering all 29 matched quarters from March 2019 to March 2026. The quarter-end observation label is mapped to that quarter's first date. [ABS CPI workbook](../../data/raw/abs_cpi/6401017.xlsx), [CPI input](../../data/interim/cpi_sydney.csv)

| Window | Source cells | CPI observations | Average |
|---|---|---|---:|
| 2019 | `Data1!A293:B296` | 79.97, 80.48, 80.91, 81.34 | 80.6750 |
| June 2025 to March 2026 | `Data1!A318:B321` | 98.47, 99.91, 100.38, 101.81 | 100.1425 |

The ratio is **1.241307716145**, or a **24.13%** CPI rise between the two windows. Real growth is `(1 + growth_pct) / cpi_ratio − 1`. The same positive ratio applies to all geographies and both dwelling types, preserving the nominal rankings.

### Q2. Published benchmarks

Each row uses DCJ's own Greater Sydney or ring median series separately for houses and units. Nominal and real growth cover the full comparison period. Annualised growth is nominal and uses the 6.25-year midpoint gap from T05. [Growth CSV](../../data/processed/lga_growth.csv)

| Geography | Dwelling | Nominal | Annualised | Real |
|---|---|---:|---:|---:|
| Greater Sydney | house | 67.47% | 8.60% | 34.91% |
| Greater Sydney | unit | 18.14% | 2.70% | −4.82% |
| Inner Ring | house | 51.85% | 6.91% | 22.33% |
| Inner Ring | unit | 22.72% | 3.33% | −1.14% |
| Middle Ring | house | 71.80% | 9.04% | 38.40% |
| Middle Ring | unit | 14.53% | 2.19% | −7.73% |
| Outer Ring | house | 67.46% | 8.60% | 34.91% |
| Outer Ring | unit | 30.33% | 4.33% | 4.99% |

### Q3. Top and bottom five with caveat flags

Low-sales columns count flagged published medians out of four in each window. A positive revision change means the LGA dropped in rank. A revision caveat applies above three places in either direction. [Analysis notebook](../../notebooks/03_analysis.ipynb), [Growth CSV](../../data/processed/lga_growth.csv)

#### Houses

| Group | Nominal rank | LGA | Nominal | Real | Low sales in 2019 | Low sales in latest four | Revision rank change | Caveat |
|---|---:|---|---:|---:|---:|---:|---:|---|
| Top five | 1 | Fairfield | 82.98% | 47.41% | 0 | 0 | 0 | None |
| Top five | 2 | Cumberland | 81.43% | 46.16% | 0 | 0 | 0 | None |
| Top five | 3 | Burwood | 80.50% | 45.41% | 3 | 0 | 0 | Low sales |
| Top five | 4 | Canterbury-Bankstown | 80.43% | 45.35% | 0 | 0 | 0 | None |
| Top five | 5 | Ryde | 79.60% | 44.68% | 0 | 0 | +1 | None |
| Bottom five | 34 | Woollahra | 43.02% | 15.22% | 0 | 0 | −17 | Revision |
| Bottom five | 33 | North Sydney | 48.89% | 19.95% | 0 | 0 | +1 | None |
| Bottom five | 32 | Wollondilly | 50.07% | 20.90% | 0 | 0 | 0 | None |
| Bottom five | 31 | Sydney | 51.28% | 21.87% | 0 | 0 | +2 | None |
| Bottom five | 30 | Randwick | 54.33% | 24.33% | 0 | 0 | −3 | None |

#### Units

| Group | Nominal rank | LGA | Nominal | Real | Low sales in 2019 | Low sales in latest four | Revision rank change | Caveat |
|---|---:|---|---:|---:|---:|---:|---:|---|
| Top five | 1 | Hawkesbury | 58.79% | 27.92% | 3 | 1 | 0 | Low sales |
| Top five | 2 | Campbelltown | 57.66% | 27.01% | 0 | 0 | 0 | None |
| Top five | 3 | Central Coast | 54.20% | 24.22% | 0 | 0 | 0 | None |
| Top five | 4 | Northern Beaches | 47.79% | 19.06% | 0 | 0 | +1 | None |
| Top five | 5 | Penrith | 47.36% | 18.71% | 0 | 0 | +1 | None |
| Bottom five | 33 | Hunters Hill | 0.72% | −18.86% | 4 | 3 | 0 | Low sales |
| Bottom five | 32 | Strathfield | 5.59% | −14.94% | 0 | 0 | −1 | None |
| Bottom five | 31 | Parramatta | 5.84% | −14.73% | 0 | 0 | +1 | None |
| Bottom five | 30 | Sydney | 6.89% | −13.89% | 0 | 0 | −2 | None |
| Bottom five | 29 | Cumberland | 7.55% | −13.35% | 0 | 0 | 0 | None |

**Wollondilly units** — no 2019 baseline (D05). [Decision log](../../docs/decisions.md)

### Q4. D08 sensitivity

Spearman rank agreement between the first-published and revised-estimate growth measures was **0.934 for houses** (34 LGAs) and **0.992 for units** (33 LGAs). All four movements greater than three places were in house growth. [Analysis notebook](../../notebooks/03_analysis.ipynb), [T05 review](../reviews/T05_review.md)

| LGA | Dwelling | First-published growth | Revised growth | First to revised rank | Rank change |
|---|---|---:|---:|---:|---:|
| Woollahra | house | 43.02% | 64.78% | 34 → 17 | −17 |
| Willoughby | house | 60.62% | 56.68% | 22 → 28 | +6 |
| Hawkesbury | house | 57.20% | 53.00% | 26 → 31 | +5 |
| Mosman | house | 55.32% | 59.99% | 28 → 23 | −5 |

Agreement is high overall, especially for units. Woollahra's house growth estimate rises from 43.0% to 64.8% with revisions, moving it from last in the first-published series to 17th. Its bottom ranking is sensitive to which series is used.

### Q5. Draft findings

From the 2019 average to the four quarters through March 2026, Greater Sydney's median house price rose 67.5% and its unit median rose 18.1%. Fairfield led houses at 83.0% nominal growth and 47.4% after inflation. Hawkesbury led units in the first-published series at 58.8%, with 4 low-sales quarters across the two windows. After inflation, Greater Sydney house prices rose 34.9% and unit prices fell 4.8%.

[House growth chart](../../docs/figures/growth_by_lga_house.png), [Unit growth chart](../../docs/figures/growth_by_lga_unit.png), [Ring price index](../../docs/figures/price_index_rings.png)

### Q6. Byte-identical T05 columns

I captured the accepted T05 workspace file hashes before editing and matched them against the hashes in the T05 report. For the two extended tables I stripped the appended fields from each raw line, including the header, and preserved the original column order, row order and line endings. For both unchanged exports I hashed the full file. [T05 submission hashes](T05_report.md)

| Processed CSV | Appended fields | SHA-256 of the T05 file and the T07 projection |
|---|---|---|
| `dim_lga.csv` | None | `abcaf3571943e759798205863feb837198d2340b57cb497302b91dbc8b1a0455` |
| `fact_sales.csv` | None | `9c5c66eba72c7e7cdc171ca3568698ec8b18a9654f9fab2ed1a56db5d1ae4b49` |
| `dim_date.csv` | `cpi_sydney` | `173ee3f6cf69f425a67b21c4d41613c0463c90f4373d7b9bf4bf36935c868edc` |
| `lga_growth.csv` | `cpi_ratio`, `growth_pct_real`, `growth_rank`, `growth_rank_rev`, `rank_change_rev` | `1bcd3a7175bf63900a4d8fd21fe3ce1e8c5da036993a821e07b16e42c3a30c91` |

## Acceptance checks

| Check | Pass/Fail | Evidence |
|---|---|---|
| A1. Append-only and byte-identical existing fields | Pass | The four projections match T05, and both re-exports match the full T05 files where no columns were added. |
| A2. Real growth and correct rank eligibility | Pass | All real growth values recompute from the exported CPI ratio. The nominal, revised and real LGA order checks passed. All eight benchmark rows have blank ranks. |
| A3. Both notebooks execute and figures meet the specification | Pass | Both notebook rounds completed in order. All five CSV hashes matched. Visual QA confirmed the three 1,080 px-wide PNGs at 150 dpi, including sorted bars, top-five highlighting, caveat hatching, benchmark lines and the two ring-index panels. |
| A4. Report, scope and no git | Pass | Q1–Q6 are answered. Only allowed files have content changes. The original 43 cells of `02_clean.ipynb` are identical to the starting version. No git commands were run. |

## Decisions needed (for Kang)

None.

## Issues and risks

- Burwood houses, Hawkesbury units and Hunters Hill units have low-sales quarters at the ranking extremes. Woollahra houses have a 17-place revision shift. These are the four extreme rows flagged for the README.
- The unchanged T05 SQL step runs using the included CPI CSV. The appended step regenerates that file from the workbook and refreshes all four exports if the CPI values change.
- Sydney CPI is the common inflation measure for all areas. It adjusts purchasing power at the city level and leaves the relative ordering within each dwelling type unchanged.

## Suggested commit message(s)

- `feat: add real housing growth, rank sensitivity and charts`

## Revision 1

Step 14 prepares Sydney CPI from the 29 distinct quarter dates in the cleaned sales table. It checks that every quarter has a CPI value and writes `data/interim/cpi_sydney.csv` before step 15 runs SQL. The final real-growth and rank checks still run after export. SQL now runs once per notebook execution.

| Verification | Result |
|---|---|
| Clean rebuild in a temporary copy | Pass. Excluded `.venv`, `.git` and `data/raw/_archives`, then deleted the copy's `cpi_sydney.csv`. Ran `02_clean.ipynb` followed by `03_analysis.ipynb` with `.venv/bin/jupyter nbconvert --to notebook --execute --inplace`, using the workspace virtual environment. Both passed with 22 and 8 executed code cells respectively. The CPI file was regenerated with 29 quarters before SQL ran. |
| Two workspace runs in the same order | Pass. Both notebooks completed in each run. Each of the seven interim and processed CSVs matched its starting bytes in both workspace runs and in the clean copy. |
| Scope | Pass. Only the cleaning notebook and this report changed. SQL, `03_analysis.ipynb` and the figures matched their starting bytes. No git commands were run. |

| CSV | SHA-256 before and after both workspace runs |
|---|---|
| `data/interim/cpi_sydney.csv` | `de486ee17bbfaf395c6018214229808bd54d9d5a1d660a7274391dad2c8ad8ce` |
| `data/interim/lga_factors.csv` | `aba5c04ae360cb001da41c71a384b3c9d4badcd466268a75ae8e0eb65cbd95e2` |
| `data/interim/sales_long.csv` | `129403ad50c2be6a1c345f43239f2c38a0667d78c295cd8732dfed36abfe2800` |
| `data/processed/dim_date.csv` | `21a969110f7a1eda3910811452101e2908825ca1477b5ec7194cb8ba0ba9d1a7` |
| `data/processed/dim_lga.csv` | `abcaf3571943e759798205863feb837198d2340b57cb497302b91dbc8b1a0455` |
| `data/processed/fact_sales.csv` | `9c5c66eba72c7e7cdc171ca3568698ec8b18a9654f9fab2ed1a56db5d1ae4b49` |
| `data/processed/lga_growth.csv` | `482a5bc5cf1d6dcbb55b3f6b36e201f9f662fa7bbc713272e45aee5b8419ae39` |
