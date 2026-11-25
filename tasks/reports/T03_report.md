# T03 report — LGA lookup and clean quarterly sales

## Summary

Built the 34-row canonical LGA lookup and a 2,204-row quarterly sales table from DCJ’s 29 workbooks. The sales table preserves DCJ’s first-published medians and its published ring and Greater Sydney aggregates. Wollondilly units in June 2019 are the only absent source combination, with an explicit row for that gap. Typical implied revisions were below 1% for both dwelling types at LGA level, though the September 2025 workbook implies a 39.16% revision to Woollahra’s June 2025 house median.

## Files created or changed

- `notebooks/02_clean.ipynb` — reads the raw tables, builds both outputs, measures revisions and validates the exports. The executed notebook includes source references and diagnostics.
- `data/reference/lga_lookup.csv` — DCJ LGA labels and rings with verified ABS LGA 2025 codes and names.
- `data/interim/sales_long.csv` — house and unit prices and counts by quarter and geography, with statuses and source pointers.
- `tasks/reports/T03_report.md` — this submission.

## Commands run

| Command or check | Result |
|---|---|
| Read `AGENTS.md`, the T03 spec, D04–D06, both reviews and Part A of `01_explore.ipynb` | Pass. Confirmed the canonical geography, source layout, first-published rule and earlier marker counts. Recorded pre-task file hashes. |
| `.venv/bin/python -` with openpyxl to inspect source cell types, precision and markers | Pass. All numeric source medians are whole thousands of dollars. Both numeric and text K values have precision of 0.01 percentage point or coarser. |
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb` | Pass. The two runs of the final notebook each wrote 34 lookup rows and 2,204 sales rows. Jupyter printed its unencrypted kernel TCP transport warning. |
| `.venv/bin/python -` to compare the CSV hashes and independently read the raw worksheets | Pass. Both CSVs are byte-identical across runs. All 2,203 sourced rows matched the worksheet values, statuses and pointers. All 34 code/name pairs matched ERP and GeoJSON. |
| `.venv/bin/python -` to cross-check revision rounding with decimal interval overlap | Pass. Independently reproduced counts of 257, 399, 2 and 8 rounding-compatible pairs for LGA houses, LGA units, Greater Sydney houses and Greater Sydney units respectively. |
| `.venv/bin/python -` for notebook and repository file audit | The initial hash comparison raised `AssertionError: ['docs/data_sources.md', 'docs/decisions.md']` on the concurrent D07 updates. The scoped comparison passed. The executed notebook contains all eight steps and the four deliverables are the only additions. |

## Answers to the task questions

### Q1. Row counts and statuses

| Geography level | Sourced rows | Added absent rows | Exported rows |
|---|---:|---:|---:|
| LGA | 1,971 | 1 | 1,972 |
| Ring | 174 | 0 | 174 |
| Greater Sydney | 58 | 0 | 58 |
| **Total** | **2,203** | **1** | **2,204** |

The absent row is Wollondilly unit, June quarter 2019 (`quarter_date=2019-04-01`). It points to `issue-129-sales-tables-june-2019.xlsx`. Both statuses are `not_in_source`. Price, count and Excel row are empty, and the low-sales flag is true. The other three 2019 Wollondilly unit medians are suppressed as published.

| LGA field and status | House | Unit |
|---|---:|---:|
| `price_status=published` | 986 | 970 |
| `price_status=suppressed` | 0 | 15 |
| `price_status=not_in_source` | 0 | 1 |
| `count_status=published` | 949 | 877 |
| `count_status=suppressed_10_or_fewer` | 0 | 15 |
| `count_status=suppressed_30_or_fewer` | 37 | 93 |
| `count_status=not_in_source` | 0 | 1 |

### Q2. DCJ-to-ABS name mappings

| DCJ name | ABS LGA 2025 name | Code |
|---|---|---|
| Bayside | Bayside (NSW) | `10500` |
| Campbelltown | Campbelltown (NSW) | `11500` |
| Central Coast | Central Coast (NSW) | `11650` |
| Ku-Ring-Gai | Ku-ring-gai | `14500` |
| Sutherland Shire | Sutherland | `17150` |
| The Hills Shire | The Hills | `17420` |

The other 28 labels matched exactly. The notebook determined the codes from Table 1 of `data/raw/abs_erp/32180DS0004_2001-25.xlsx`. An independent check confirmed that every exported five-character code and associated ABS label appears in that table and in `data/raw/abs_asgs/LGA_2025_Sydney_region.geojson`.

### Q3. Published ring membership

DCJ reports 8 Inner Ring, 12 Middle Ring and 14 Outer Ring LGAs. Each of the 34 has one consistent ring assignment across all 29 quarters. The notebook checked the assignment from the selected Greater Sydney rows in every issue.

### Q4. Implied median revisions

Column K is the reported quarterly median change. For each comparable pair, the current median divided by `1 + change` implies a revised prior-quarter median. The revision measures the percentage difference from the prior workbook’s first-published median.

Under nearest rounding, each reported price can differ from its underlying value by $500, and the change by 0.005 percentage point. Let `B` be the first-published prior median in dollars and `q` the reported quarterly ratio `1 + change`. If the underlying prior median were unchanged, the current displayed price could range from `(B−500)(q−0.00005)−500` to `(B+500)(q+0.00005)+500`. Dividing those endpoints by `q×B` and subtracting one gives the rounding-only bounds for that pair. The largest observed bound was **0.249% of the prior median**, for Fairfield units in March 2020, as compared in the June issue.

| Geography | Dwelling | Possible pairs | Compared | Median absolute | 90th percentile | Maximum absolute | Within rounding | Max. rounding bound |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LGA | House | 952 | 952 | 0.5747% | 3.9760% | 39.1635% | 26.9958% | 0.1805% |
| LGA | Unit | 952 | 932 | 0.2868% | 2.3344% | 18.7410% | 42.8112% | 0.2487% |
| Greater Sydney | House | 28 | 28 | 1.8480% | 2.8272% | 3.5991% | 7.1429% | 0.1199% |
| Greater Sydney | Unit | 28 | 28 | 0.4475% | 0.8399% | 1.2821% | 28.5714% | 0.1487% |

Twenty LGA unit pairs were unavailable because one or both adjacent medians were missing. All four groups use immediately adjacent quarters.

**Five largest LGA revisions by absolute magnitude**

| LGA and prior reference quarter | First-published | Implied revised | Revision | Prior workbook and `LGA` cell | Later workbook and `LGA` cells |
|---|---:|---:|---:|---|---|
| Woollahra house, Jun 2025 | $4,958,000 | $6,899,724 | +39.163% | `sales_tables_june_2025_quarter.xlsx` G1796 | `sales_tables_september_2025_quarter.xlsx` G1824, K1824 |
| Woollahra house, Dec 2022 | $4,175,000 | $5,300,036 | +26.947% | Issue 143 G1796 | Issue 144 G1800, K1800 |
| Woollahra house, Jun 2023 | $4,240,000 | $5,349,929 | +26.178% | Issue 145 G1808 | Issue 146 G1808, K1808 |
| Woollahra house, Dec 2021 | $4,250,000 | $5,299,685 | +24.698% | Issue 139 G1828 | Issue 140 G1808, K1808 |
| Mosman house, Jun 2023 | $4,300,000 | $5,312,532 | +23.547% | Issue 145 G1793 | Issue 146 G1793, K1793 |

The largest case uses a September 2025 house median of $5,250,000 and a published quarterly change of −23.91%. There were 90 sales in the first-published June quarter and 108 in September. The workbook references above identify both inputs.

**Five largest Greater Sydney revisions by absolute magnitude**

| Prior reference quarter and dwelling | First-published | Implied revised | Revision | Prior workbook and `LGA` cell | Later workbook and `LGA` cells |
|---|---:|---:|---:|---|---|
| Mar 2021 house | $1,110,000 | $1,149,950 | +3.599% | Issue 136 G1695 | Issue 137 G1695, K1695 |
| Dec 2024 house | $1,452,000 | $1,500,052 | +3.309% | Issue 151 G1679 | Issue 152 G1671, K1671 |
| Mar 2019 house | $865,000 | $890,032 | +2.894% | Issue 128 G1649 | Issue 129 G1647, K1647 |
| Mar 2025 house | $1,430,000 | $1,470,021 | +2.799% | Issue 152 G1671 | `sales_tables_june_2025_quarter.xlsx` G1667, K1667 |
| Jun 2024 house | $1,460,000 | $1,500,265 | +2.758% | Issue 149 G1675 | `Sales_tables_September_2024_quarter.xlsx` G1675, K1675 |

The estimates can plausibly affect close rankings and could materially affect an outlier such as Woollahra. The 2019 baseline window contains absolute revisions up to 13.287% for houses and 8.925% for units. Among the three revisable quarters in the latest four-quarter window, the maxima are 39.163% for houses and 11.001% for units. The March 2026 median has no subsequent sales workbook in this snapshot. The actual ranking effect remains unverified.

**README limitations wording.** DCJ can revise quarterly medians after release, so this project consistently uses first-published values. The median absolute implied revision was 0.57% for LGA houses and 0.29% for units, with a 39.16% house outlier in the latest four-quarter window. These revisions could move close rankings and affect LGAs with unusually large revised quarters.

### Q5. Reconciliation with T01

| Scope | Price dashes | Count dashes | Count `s` |
|---|---:|---:|---:|
| T01, entire LGA sheets | 8,016 | 8,016 | 12,992 |
| T01, DCJ Sydney LGA rows with all dwelling labels | 15 | 15 | 133 |
| Sydney LGA dwelling `Total` rows removed in T03 | 0 | 0 | 3 |
| Ring and Greater Sydney published rows added to the export scope | 0 | 0 | 0 |
| T03 export | 15 | 15 | 130 |

The full-sheet totals include the repeated geography levels and other parts of NSW. The separate absent Wollondilly row has no raw marker. Suppressed values and the absent observation have empty numeric fields and distinct status values.

### Q6. Large moves and source quirks

- Thirteen LGA-quarter moves exceeded 25% in absolute first-published median change with more than 30 reported sales in the current quarter. Eight are house rows and five are unit rows. Eleven still qualify with the count threshold applied to both quarters, with seven house and four unit rows.
- The largest move with more than 30 sales in both quarters is Willoughby units, from $1,100,000 to $1,620,000 (+47.27%), with 128 and 205 sales. See issue 140 `LGA!G1848` and issue 141 `LGA!G1856`. Woollahra houses rose from $4,900,000 to $6,750,000 (+37.76%) and then fell to $4,100,000 (−39.26%). See issues 146, 147 and 148 at `LGA!G1808`, `LGA!G1808` and `LGA!G1784`. These are screening flags. Quarterly medians can change with the mix of homes sold.
- Header rows are 5 in two workbooks, 6 in one, and 7 in the other 26. The reporting caption moves from A1 in the early layout to A2 in the later layout. Numeric counts with commas and K percentages stored as text needed explicit parsing.
- The published sales median range is $404,000–$6,750,000. All six prescribed checks passed, including `LGA!G1865`, `G1815`, `J1851`, `G1691` and `G1692` in March 2026 and `G1863` in March 2019.

## Acceptance checks

| Check | Pass/Fail | Evidence |
|---|---|---|
| A1 | Pass | Both CSV headers are in specified order. There are 34 lookup rows and 2,204 sales rows. |
| A2 | Pass | Both nbconvert executions succeeded. Both CSVs are byte-identical across runs. |
| A3 | Pass | Missing numeric fields are empty. The status columns distinguish suppression from the one absent source row. |
| A4 | Pass | Section 6 includes the pair-specific bounds, summaries by scope and dwelling type, top five per scope and limitations wording. |
| A5 | Pass | All eight steps have plain-English markdown and use pandas with openpyxl for Excel reads. |
| A6 | Pass | Q1–Q6 are answered with workbook evidence. T03 added only its four allowed deliverables. The workspace comparison also identified separate D07 updates to two existing documents. No git commands ran. |

## Decisions needed (for Kang)

None.

## Issues and risks

- The revision estimates come from published medians and reported quarterly changes. They inherit rounding and cannot recover exact revised prices.
- The decision log and sources register received separate D07 updates during T03. D04–D06 still govern both exports.
- Kang’s Excel check of the four 2019 medians for his chosen LGA is the owner review step. The independent programmatic comparison covered every sourced export row.

## Suggested commit message(s)

- `feat: build the Sydney LGA lookup and quarterly sales table`
