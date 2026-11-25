# T04 review — Factor table, distance SQL, change columns

**Verdict: Accept** · Reviewer: Claude · 2026-11-25

## What I re-ran myself

| Check | Result |
|---|---|
| A1 `sales_long.csv` | Pass. 14 columns. Stripping the two new columns gives a file **byte-identical to the committed T03 version** (280,126 bytes, checked against `git show HEAD:`). |
| A2 `lga_factors.csv` | Pass. 34 rows, 11 columns; only Bayside income is empty; all rents use 4/4 quarters. |
| A3 `sql/distance.sql` | Pass. One query, three commented CTEs, parameterised paths. I ran it standalone in DuckDB: Blacktown 34.79, Blue Mountains 76.16, Camden 47.36, Sydney 2.45 km. |
| A4 Notebook | Pass. Re-executed: 0 errors; all three CSV hashes equal the ones in the report. |
| A5 Scope | Pass. Only allowed files changed (`docs/decisions.md` edit is mine: D08). |

## Independent spot checks (read straight from the raw files)

| Value | Raw source | Result |
|---|---|---|
| Blacktown 2016 income $1,711; Woollahra $2,687 | Census 2016 G02 CSV | ✅ |
| Bayside predecessors: Botany Bay $1,626, Rockdale $1,575 | same | ✅ (Bayside correctly left empty) |
| Camden ERP 80,268 → 104,706 | ERP Table 1, row 27 | ✅ |
| Wollondilly unit rent Dec 2019 $298 | Rent issue 130, `LGA` row 22105 | ✅ |

## Camden: +30.4% population growth

This is real. Camden's new estates (Oran Park, Gregory Hills) grew fast, and the ABS counts confirm it.
The ±30% range was my own arbitrary sanity limit, not a data rule. **Keep it as a documented
exception, with no change to the data.** It matters for analysis: Camden will be an outlier on the
population factor. That's one reason the plan uses **Spearman** (rank-based) correlation, which an extreme
value can't dominate.

## Notes carried forward

1. Four LGAs lost population 2016–19 (Randwick, Hunters Hill, Woollahra, Mosman). They're all inner,
   expensive areas, which hints that population growth and distance/price overlap. T08's correlation matrix
   will show it.
2. README "How to reproduce" must say DuckDB's `spatial` extension downloads on first run.
3. `.DS_Store` files appeared; they're gitignored, so no action is needed.
