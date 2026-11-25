# T05 review — SQL transform, star schema, growth

**Verdict: Accept** · Reviewer: Claude · 2026-11-26

## What I re-ran myself

| Check | Result |
|---|---|
| A1 Outputs | Pass. fact_sales 2,204 · dim_lga 38 · dim_date 29 · lga_growth 76 rows; headers as specified. |
| A2 SQL quality | Pass. `sql/transform.sql` (176 lines) is clean: header comment, one comment per table and CTE, a named window (`WINDOW by_quarter`), `LAG`/`LEAD`, `ROW_NUMBER` both directions, `FILTER` conditional aggregation, joins, `UNION ALL`, and a grid check that **fails loudly** via `error()`. No hard-coded quarter dates. This is strong interview material. |
| A3 Growth correctness | Pass. I recomputed **all 76** `growth_pct` and `growth_annualised` values independently in pandas from `sales_long.csv`: max difference **0.0**, null pattern identical (only Wollondilly unit). |
| A4 Rerun | Pass. Re-executed `02_clean.ipynb` (43 cells, 0 errors); all 7 CSVs (processed, interim, reference) byte-identical. |
| A5 Scope | Pass. Only allowed files changed. |

## Sensitivity check (D08): this matters for the findings

Rank agreement between first-published and revised-estimate growth (Spearman, LGA rows):
**houses 0.934, units 0.992**. Units are rock-solid. Four house LGAs move more than 3 places:

| LGA (house) | Growth (first-published) | Growth (revised est.) | Rank → rank |
|---|---|---|---|
| **Woollahra** | 43.0% | 64.8% | **34 → 17** |
| Willoughby | 60.6% | 56.7% | 22 → 28 |
| Hawkesbury | 57.2% | 53.0% | 26 → 31 |
| Mosman | 55.3% | 60.0% | 28 → 23 |

**Consequence:** Woollahra must **not** be headlined as "slowest-growing houses". Its first-published
medians are heavily understated by late-reported sales (T03 review). The README should say so. This is
a good rigour point, not a problem.

## First look at the answer (nominal, first-published)

| Benchmark | Houses | Units |
|---|---|---|
| Greater Sydney | +67.5% (8.6% a year) | +18.1% (2.7% a year) |
| Inner Ring | +51.9% | +22.7% |
| Middle Ring | +71.8% | +14.5% |
| Outer Ring | +67.5% | +30.3% |

Fastest houses: Fairfield, Cumberland, Burwood, Canterbury-Bankstown, Ryde (≈ 80–83%). Fastest units:
Hawkesbury, Campbelltown, Central Coast (≈ 54–59%). Houses grew roughly 3–4× faster than units.

## Notes carried forward

1. Ten fact rows have a revised estimate but no first-published price (suppressed, later published).
   That's fine, and it's documented in the report.
2. **Power BI pitfall:** with 38 geographies in `dim_lga`, any measure that averages `median_price`
   without a `geo_level` filter averages medians across areas. Every LGA visual must filter
   `geo_level = "lga"`, and the Greater Sydney card must filter `geo_level = "greater_sydney"`. This is
   covered in the T09 guide.
