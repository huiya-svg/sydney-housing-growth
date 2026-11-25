# T02 review — Candidate factors

**Verdict: Accept** · Reviewer: Claude · 2026-11-25

## What I re-ran myself

| Check | Result |
|---|---|
| A1 Manifest | Pass. 55 rows, 0 hash mismatches, no unlisted files. Largest committed file 17.6 MB (`supply/14100DO0003_2011-25.xlsx`); archives > 25 MB are in gitignored `_archives/`. Total committed raw ≈ 65 MB, which is fine for GitHub. |
| A2 Downloader | Pass. Rerun: "55/55 listed files on disk", manifest byte-identical. Hash-verify logic replaces the T01 recompute issue. |
| A3 Notebook | Pass. Re-executed to a scratch copy: 37 cells, 0 errors. Part A code cells are identical to the committed T01 version. Part B adds 19 cells / ~260 code lines. |
| A4 Screening table | Pass. C1–C9 all filled with source, licence, four checks, verdict. |
| A5 Report | Pass. Q1–Q8 answered with evidence; D07 left open. |
| A6 Scope | Pass. Only allowed paths changed (`decisions.md` / `workflow.md` edits were mine). Only new package: `xlrd==2.0.2` (needed for two old ABS `.xls` files). |

## Independent spot checks

| Value | Source read directly | Result |
|---|---|---|
| ERP Blacktown, June 2016 → June 2019 | `abs_erp/32180DS0004_2001-25.xlsx`, Table 1 | 348,030 → 380,186 (+9.2%) ✅ |
| ERP Sydney, June 2016 → June 2019 | same | 222,717 → 229,596 (+3.1%) ✅ |
| ERP Bayside code | same | 10500 `Bayside (NSW)`, all years present ✅ |
| Blue Mountains distance | Haversine from the reported centroid to the reported GPO point | 76.02 km vs 76.16 km reported (spheroid vs sphere, so the difference is expected) ✅ |
| Blacktown / Sydney distance | Notebook output | 34.79 km / 2.45 km, plausible ✅ |

## Notes carried forward

1. **Distance code is hard to explain.** It uses DuckDB's Python relational API (`.project(...)` chains).
   In T04 it should become one plain SQL query in `sql/`. That's better interview material and better SQL
   evidence.
2. **DuckDB `spatial` extension is installed at runtime** (`INSTALL spatial`), so the first run needs
   network access. Add this to "How to reproduce" in the README.
3. **Geometric centroids** put the four large outer LGAs 62–76 km out. Spearman correlation uses ranks,
   and these LGAs are the farthest by any measure, so ranks barely change. State it as a limitation and
   don't build population weighting.
4. **ABS labels differ from DCJ for 6 LGAs** (e.g. `Sutherland` vs `Sutherland Shire`). Join on the
   **ABS code**, never on the name. T03 builds the lookup table that holds both.

## D07 — my recommendation (Kang decides)

Test **three** factors, all measured at or before the start of the period, all available for all 34 LGAs:

| Factor | Why keep it |
|---|---|
| C5 Distance to CBD (km) | Static, clean, and the classic location story. |
| C3 Population growth June 2016 → June 2019 (%) | Pre-period demand. Before the outcome window, so it can't be a *result* of 2019–26 price growth. |
| C1 2019 price level (avg of the four 2019 medians) | The "catch-up" question: did cheaper areas grow faster? It comes free from the core data and the plan names it. The 4-quarter average reduces the noise that Codex warns about. Report it as an association. |

Reject or defer, with the reason kept in `docs/data_sources.md`:
- **C4 income 2016**: no single 2016 Bayside median, and likely a proxy for 2019 price. 2021 income is concurrent.
- **C2 rent / gross yield**: rent types (house, flat/unit) don't match sale types (non-strata, strata), and yield contains the price.
- **C6 supply**: the 2016 council mergers break the pre-period approval series for 8 of the 34 LGAs.
- **C7 CPI**: keep as the deflator for real growth. **C8 cash rate**: timeline overlay only. **C9**: not pursued (address-level).

Codex recommended C3 + C5 with income as an optional third. My difference: I'd use 2019 price instead of
income, because it has no data gap, and the plan's correlation-matrix step exists to check exactly the
distance ↔ price overlap.
