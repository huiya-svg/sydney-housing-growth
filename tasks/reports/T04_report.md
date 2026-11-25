# T04 report — LGA factors and sales change columns

## Summary

The notebook exports distance to the Sydney GPO, June 2016 to June 2019 population growth, 2016 Census household income and 2019 rents for all 34 Greater Sydney LGAs. Bayside income is the sole blank factor cell, and each LGA uses four quarterly rents for houses and four for units. The two DCJ change fields extend the 2,204-row sales table, and removing them reproduces the accepted T03 file's SHA-256 hash. Camden's published ERP values imply 30.4455% growth, the only result outside the specified population range.

## Files created or changed

- `notebooks/02_clean.ipynb` — appends DCJ columns K and L and adds the factor sections, checks and export.
- `sql/distance.sql` — calculates geometric centroids and straight-line distances to the GPO in one query.
- `data/interim/sales_long.csv` — the 2,204 sales rows with two appended change columns.
- `data/interim/lga_factors.csv` — 34 factor rows keyed by canonical DCJ LGA and ABS code.
- `tasks/reports/T04_report.md` — submission and verification evidence.

## Commands run

| Command | Result |
|---|---|
| `cat`, `rg` and `.venv/bin/python -` using `nbformat` | Read AGENTS.md, the T04 spec, D07–D08, the T02 and T03 reviews and both notebooks. Recorded the starting file hashes. |
| `shasum -a 256 data/interim/sales_long.csv data/reference/lga_lookup.csv` | Captured the pre-T04 sales and lookup SHA-256 hashes. |
| `.venv/bin/python -` with `nbformat` to run the T02 distance reference | The first partial replay stopped with `NameError: name 'layout' is not defined`. Reran the two original Part B cells with the accepted DCJ lookup labels and recovered all 34 reference distances. |
| `.venv/bin/python -` with DuckDB to run `sql/distance.sql` | Pass. Returned 43 boundary features, with the three requested spot distances matching before the full 34-code comparison. |
| `.venv/bin/python -` with pandas, openpyxl and `nbformat` | Read ERP headers and source rows, checked the rent layout and the Census predecessors, and updated and syntax-checked the notebook. |
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb` | Two preliminary failures in the final cell. The first was `SyntaxError: unterminated string literal (detected at line 54)` from the CSV line terminator. The next was an `AssertionError` because the key comparison treated pandas string dtypes as unequal. Both were corrected. The final notebook executed twice consecutively with 16 code cells, zero cell errors and the same kernel startup TCP warning on both runs. |
| `shasum -a 256 data/interim/sales_long.csv data/reference/lga_lookup.csv data/interim/lga_factors.csv` after each final execution, followed by `test` | Pass. All three hashes matched between runs. |
| `.venv/bin/python -` with the nbconvert HTML exporter | Pass. Rendered the executed notebook in memory and verified the five factor audit outputs are present. |
| `.venv/bin/python -` for CSV, raw-source and scope audits | Pass. Checked the sales byte projection, both source change cells for every sales row, all 272 quarterly rent inputs, the Census joins and ERP values. The scope comparison identified the five allowed paths and three new ignored macOS metadata files. |

## Answers to the task questions

### Q1. Sales byte comparison and empty changes

The final file has 2,204 data rows and 14 columns. Removing the last two fields from every line, including the header, and preserving the original bytes gives the same SHA-256 hash as the accepted T03 file present in the workspace at the start of T04. Both hashes are `28f660880cef6cff01b50acec8d9621d5077765b7e89341418c27e1f610aa01d`. The comparison used that working copy of the T03 output under the repository's no-git rule. [T03 review](../reviews/T03_review.md)

| Field | Published | Source dash | Blank source cell | Source row absent | Total empty |
|---|---:|---:|---:|---:|---:|
| `quarterly_change` | 2,188 | 15 | 0 | 1 | 16 |
| `annual_change` | 2,188 | 15 | 0 | 1 | 16 |

The 15 dashes in each field come from DCJ-suppressed rows. The other empty row is Wollondilly units in June 2019, which has no source row. Every sourced value was checked through `source_file` and `source_row`. For example, the September 2025 Woollahra house row in `sales_tables_september_2025_quarter.xlsx`, `LGA!K1824:L1824`, exports `-0.2391` and `0.1194`. [Sales CSV](../../data/interim/sales_long.csv)

### Q2. Full 34-row factor table

Population is estimated at 30 June. Growth is a decimal fraction. Income and rents are in Australian dollars per week. The last two columns give the number of quarterly medians used for each rent figure. [Factor CSV](../../data/interim/lga_factors.csv)

| LGA | 2025 code | Distance (km) | Pop. 2016 | Pop. 2019 | Pop. growth | 2016 income | 2019 house rent | 2019 unit rent | House quarters | Unit quarters |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Bayside | 10500 | 9.81 | 164534 | 173913 | 0.0570 |  | 647.00 | 570.00 | 4 | 4 |
| Blacktown | 10750 | 34.79 | 348030 | 380186 | 0.0924 | 1711 | 460.00 | 370.00 | 4 | 4 |
| Blue Mountains | 10900 | 76.16 | 78835 | 79077 | 0.0031 | 1468 | 442.50 | 305.00 | 4 | 4 |
| Burwood | 11300 | 9.83 | 38536 | 40333 | 0.0466 | 1569 | 667.50 | 548.75 | 4 | 4 |
| Camden | 11450 | 47.36 | 80268 | 104706 | 0.3045 | 2047 | 500.75 | 344.50 | 4 | 4 |
| Campbelltown | 11500 | 41.11 | 161562 | 172286 | 0.0664 | 1459 | 422.50 | 353.25 | 4 | 4 |
| Canada Bay | 11520 | 8.74 | 92534 | 92609 | 0.0008 | 2061 | 745.00 | 585.00 | 4 | 4 |
| Canterbury-Bankstown | 11570 | 16.93 | 361862 | 375333 | 0.0372 | 1298 | 550.00 | 411.25 | 4 | 4 |
| Central Coast | 11650 | 62.52 | 336611 | 345695 | 0.0270 | 1258 | 442.50 | 351.25 | 4 | 4 |
| Cumberland | 12380 | 20.67 | 225691 | 240090 | 0.0638 | 1379 | 497.50 | 427.50 | 4 | 4 |
| Fairfield | 12850 | 28.90 | 205675 | 212825 | 0.0348 | 1222 | 470.00 | 338.75 | 4 | 4 |
| Georges River | 12930 | 16.03 | 153161 | 156510 | 0.0219 | 1654 | 588.75 | 486.25 | 4 | 4 |
| Hawkesbury | 13800 | 71.57 | 66346 | 67244 | 0.0135 | 1668 | 450.00 | 322.50 | 4 | 4 |
| Hornsby | 14000 | 33.35 | 147385 | 153216 | 0.0396 | 2121 | 667.50 | 471.25 | 4 | 4 |
| Hunters Hill | 14100 | 6.94 | 14656 | 14427 | -0.0156 | 2467 | 990.00 | 511.25 | 4 | 4 |
| Inner West | 14170 | 5.54 | 191194 | 191965 | 0.0040 | 2048 | 768.75 | 492.50 | 4 | 4 |
| Ku-Ring-Gai | 14500 | 15.68 | 122472 | 126364 | 0.0318 | 2640 | 977.00 | 590.00 | 4 | 4 |
| Lane Cove | 14700 | 6.51 | 37694 | 39790 | 0.0556 | 2376 | 897.00 | 550.00 | 4 | 4 |
| Liverpool | 14900 | 36.18 | 211983 | 227187 | 0.0717 | 1550 | 500.00 | 377.50 | 4 | 4 |
| Mosman | 15350 | 5.49 | 30260 | 30020 | -0.0079 | 2522 | 1543.75 | 572.00 | 4 | 4 |
| North Sydney | 15950 | 3.88 | 71809 | 72155 | 0.0048 | 2360 | 917.50 | 602.50 | 4 | 4 |
| Northern Beaches | 15990 | 20.08 | 265468 | 268935 | 0.0131 | 2178 | 964.25 | 597.50 | 4 | 4 |
| Parramatta | 16260 | 18.17 | 234444 | 257472 | 0.0982 | 1759 | 540.00 | 483.75 | 4 | 4 |
| Penrith | 16350 | 46.73 | 201597 | 213534 | 0.0592 | 1658 | 432.50 | 356.25 | 4 | 4 |
| Randwick | 16550 | 8.89 | 148922 | 145287 | -0.0244 | 1916 | 928.75 | 595.00 | 4 | 4 |
| Ryde | 16700 | 11.78 | 121270 | 129738 | 0.0698 | 1786 | 645.00 | 480.00 | 4 | 4 |
| Strathfield | 17100 | 12.23 | 42415 | 45895 | 0.0820 | 1781 | 667.50 | 501.25 | 4 | 4 |
| Sutherland Shire | 17150 | 27.18 | 226461 | 229213 | 0.0122 | 1979 | 679.50 | 468.75 | 4 | 4 |
| Sydney | 17200 | 2.45 | 222717 | 229596 | 0.0309 | 1926 | 785.75 | 647.50 | 4 | 4 |
| The Hills Shire | 17420 | 38.48 | 162975 | 180102 | 0.1051 | 2363 | 633.75 | 496.25 | 4 | 4 |
| Waverley | 18050 | 6.00 | 72013 | 72485 | 0.0066 | 2308 | 1180.75 | 686.25 | 4 | 4 |
| Willoughby | 18250 | 7.47 | 77888 | 78830 | 0.0121 | 2271 | 951.25 | 591.25 | 4 | 4 |
| Wollondilly | 18400 | 75.22 | 49854 | 52826 | 0.0596 | 1871 | 463.75 | 318.25 | 4 | 4 |
| Woollahra | 18500 | 4.62 | 57744 | 56892 | -0.0148 | 2687 | 1289.50 | 680.00 | 4 | 4 |

Blacktown's counts are 348,030 and 380,186 with growth of 0.0924. Sydney's counts are 222,717 and 229,596. The counts come from `Table 1!R16` and `U16` for Blacktown and `R112` and `U112` for Sydney. [ABS ERP workbook](../../data/raw/abs_erp/32180DS0004_2001-25.xlsx)

### Q3. Census code matches and Bayside

For each of these 33 LGAs, the five-digit ABS 2025 code equals the five digits in the Census 2016 G02 key. The Census labels and numeric codes come from the `2016_ASGS_Non-ABS_Structures` sheet. [2016 Census descriptors](../../data/raw/abs_census/2016Census_geog_desc_1st_and_2nd_release.xlsx), [2016 Census G02](../../data/raw/abs_census/2016Census_G02_NSW_LGA.csv)

| Code (2016 = 2025) | DCJ label | 2016 Census label |
| --- | --- | --- |
| 10750 | Blacktown | Blacktown (C) |
| 10900 | Blue Mountains | Blue Mountains (C) |
| 11300 | Burwood | Burwood (A) |
| 11450 | Camden | Camden (A) |
| 11500 | Campbelltown | Campbelltown (C) (NSW) |
| 11520 | Canada Bay | Canada Bay (A) |
| 11570 | Canterbury-Bankstown | Canterbury-Bankstown (A) |
| 11650 | Central Coast | Central Coast (C) (NSW) |
| 12380 | Cumberland | Cumberland (A) |
| 12850 | Fairfield | Fairfield (C) |
| 12930 | Georges River | Georges River (A) |
| 13800 | Hawkesbury | Hawkesbury (C) |
| 14000 | Hornsby | Hornsby (A) |
| 14100 | Hunters Hill | Hunters Hill (A) |
| 14170 | Inner West | Inner West (A) |
| 14500 | Ku-Ring-Gai | Ku-ring-gai (A) |
| 14700 | Lane Cove | Lane Cove (A) |
| 14900 | Liverpool | Liverpool (C) |
| 15350 | Mosman | Mosman (A) |
| 15950 | North Sydney | North Sydney (A) |
| 15990 | Northern Beaches | Northern Beaches (A) |
| 16260 | Parramatta | Parramatta (C) |
| 16350 | Penrith | Penrith (C) |
| 16550 | Randwick | Randwick (C) |
| 16700 | Ryde | Ryde (C) |
| 17100 | Strathfield | Strathfield (A) |
| 17150 | Sutherland Shire | Sutherland Shire (A) |
| 17200 | Sydney | Sydney (C) |
| 17420 | The Hills Shire | The Hills Shire (A) |
| 18050 | Waverley | Waverley (A) |
| 18250 | Willoughby | Willoughby (C) |
| 18400 | Wollondilly | Wollondilly (A) |
| 18500 | Woollahra | Woollahra (A) |

Bayside's 2025 code `10500` has no 2016 Census G02 record. Botany Bay (C), `LGA11100`, has a median of **$1,626/week**. Rockdale (C), `LGA16650`, has a median of **$1,575/week**. Bayside remains blank because the two published medians cannot reconstruct the merged area's median. [2016 Census G02](../../data/raw/abs_census/2016Census_G02_NSW_LGA.csv)

### Q4. Rent quarters and coverage

Each of the 34 LGAs used four house medians and four flat/unit medians, as shown in Q2. All 272 eligible medians were published, and neither dwelling type has a zero-quarter case. Six published medians had suppressed new-bond counts in column J marked `s` (30 or fewer bonds lodged). All six published medians from H are included. They were all four Wollondilly unit quarters and the September and December Hunters Hill house quarters.

| Source series | March | June | September | December | Average |
|---|---:|---:|---:|---:|---:|
| Blacktown houses | $470 (`LGA!H21629`) | $450 (`LGA!H21646`) | $460 (`LGA!H21629`) | $460 (`LGA!H21633`) | $460.00 |
| Sydney units | $650 (`LGA!H21062`) | $650 (`LGA!H21079`) | $650 (`LGA!H21062`) | $640 (`LGA!H21065`) | $647.50 |
| Wollondilly units | $320 (`LGA!H22099`) | $320 (`LGA!H22117`) | $335 (`LGA!H22101`) | $298 (`LGA!H22105`) | $318.25 |

For issue 129, the September filename, cover and `LGA!F1` identify the correct quarter. `LGA!A1` repeats the June heading. The calculation maps issue 129 to `2019-07-01`, the September quarter's start. [Issue 127](../../data/raw/dcj_rent/issue-127-rent-tables-march-2019.xlsx), [Issue 128](../../data/raw/dcj_rent/issue-128-rent-tables-june-2019.xlsx), [Issue 129](../../data/raw/dcj_rent/issue-129-rent-tables-september-2019.xlsx), [Issue 130](../../data/raw/dcj_rent/issue-130-rent-tables-december-2019.xlsx)

### Q5. SQL distances against T02

The SQL matches the T02 results to two decimal places for all 34 codes. The maximum absolute difference is **0.00 km**, within the 0.01 km tolerance. Notebook section 9 prints the SQL value, T02 value and difference for each LGA. It includes Blacktown at 34.79 km, Blue Mountains at 76.16 km and Sydney at 2.45 km. [SQL query](../../sql/distance.sql), [Executed notebook](../../notebooks/02_clean.ipynb), [T02 exploration](../../notebooks/01_explore.ipynb)

### Q6. Surprising values

- Camden rose from 80,268 to 104,706 people, or **30.4455%**. The next-highest growth was **10.51%** in The Hills Shire. Camden's values come from `Table 1!R27` and `U27`. [ABS ERP workbook](../../data/raw/abs_erp/32180DS0004_2001-25.xlsx)
- Four LGAs had negative population growth. Randwick fell **2.44%**, Hunters Hill **1.56%**, Woollahra **1.48%** and Mosman **0.79%**, using the exported growth precision. [Factor CSV](../../data/interim/lga_factors.csv)
- Mosman had the highest house rent at **$1,543.75/week**, followed by Woollahra at **$1,289.50/week**. Waverley had the highest unit rent at **$686.25/week**. [Factor CSV](../../data/interim/lga_factors.csv)

## Acceptance checks

| Check | Pass/Fail | Evidence |
|---|---|---|
| A1. 14 sales columns and byte-identical original fields | Pass | 2,204 rows. Removing the two appended fields reproduces the pre-T04 SHA-256 in Q1. |
| A2. Factor schema, geography and missingness | Pass | 34 rows, 11 columns in the specified order, and 34 unique canonical labels and codes matching the lookup in order. Only Bayside income is empty. |
| A3. One SQL query and distance agreement | Pass | One query with three commented CTEs. Maximum difference from T02 is 0.00 km over 34 LGAs. |
| A4. Assertions, notebook execution and deterministic CSVs | Pass with documented exception | Two final nbconvert runs passed. All spot checks and notebook assertions passed. The literal population range check flagged Camden, confirmed against the source and retained by the notebook's explicit exception check. The three CSV hashes match across runs. |
| Strict population range (−10% to +30%) | Fail | 33 of 34 are in range. Camden is 30.4455% based on the source counts. |
| A5. Q1–Q6, scope and no git | Pass | All six answers are above. Only the five listed project files were added or changed. The audit also found the ignored macOS metadata noted below. No git commands were run. |

Final SHA-256 hashes from both executions

| CSV | SHA-256 |
|---|---|
| `data/interim/sales_long.csv` | `129403ad50c2be6a1c345f43239f2c38a0667d78c295cd8732dfed36abfe2800` |
| `data/reference/lga_lookup.csv` | `448fd4bcf746775f82846d8896f0e61b05306eccdcd16b3571dc3d3414db562c` |
| `data/interim/lga_factors.csv` | `aba5c04ae360cb001da41c71a384b3c9d4badcd466268a75ae8e0eb65cbd95e2` |

## Decisions needed (for Kang)

1. Camden exceeds the +30% population sanity limit. Keep +30% as a review threshold and accept Camden as a documented exception, or raise the upper limit so the check passes without an exception. Either choice can preserve the published counts. The current notebook keeps the stated threshold visible and checks Camden's counts explicitly.

## Issues and risks

- Distances use the land-area geometric centroid of the LGA. Large rural or bushland areas can move it away from population centres. DuckDB may need network access the first time it installs the spatial extension.
- The Census code comparison checks code continuity. Minor boundary changes can occur within the same code.
- The rent averages apply to newly lodged bonds, using DCJ's physical dwelling types. Sales classify houses and units by non-strata and strata title.
- Three macOS metadata files appeared during the task at `.DS_Store`, `data/.DS_Store` and `data/raw/.DS_Store`. The repository ignores them. Every raw source file and the manifest retained its starting hash.

## Suggested commit message(s)

- `feat: build Sydney LGA factors and retain DCJ sales changes`
