# T06 review — Data dictionary

**Verdict: Accept** · Reviewer: Claude · 2026-11-26

## What I re-ran myself

| Check | Result |
|---|---|
| A1 Coverage | Pass. My own script parsed every dictionary table and compared it with the CSV header. All 5 tables match exactly and in order: `fact_sales` 10, `lga_growth` 21, `dim_lga` 10, `dim_date` 7, `factor_tests` 11 (59 columns). Row counts in the headings (2,204 / 76 / 38 / 29 / 10) are correct. |
| A2 Blank rules | Pass. Every column marked "never" has 0 blanks. Every blank count matches the report, and I traced each one to its rule: the 16 blank medians = 15 `suppressed` + 1 `not_in_source`; the 146 blank counts are exactly the `low_sales_flag = true` rows; `yoy_change` = 304 first-year rows + 18 rows missing a median at either end; the 6 blank revised estimates all have a blank original median; the 9 blank ranks = 8 benchmark rows + Wollondilly units; the 5 blank incomes = 4 benchmarks + Bayside. |
| A2 Definitions | Pass. Recomputed from the CSVs: `yoy_change`, `price_2019` (all-four-quarters rule; no partial baselines exist), the four quarter-count columns, `growth_annualised` (6.25 years), `growth_pct_real`, `cpi_ratio` (1.241308), `rank_change_rev` (rev − rank, 67 of 67), `sort_order`, `q_index` and the latest-4 flags. All give a difference of 0. Checked against code: the revision priority annual → quarterly → first-published (`transform.sql` lines 55–67), the `-`/`s` count markers (`02_clean` step 3), the distance method (`distance.sql`: Albers centroid, spheroid distance) and the `dim_dwelling` column names (T09 guide). |
| A3 Scope | Pass. Only `docs/data_dictionary.md` and `tasks/reports/T06_report.md` changed; no git commands. |

## Notes (not blocking)

1. **`low_sales_flag` in plain words.** The dictionary says it "flags a row whose sale count is unavailable", which matches
   the code. For interviews, the useful translation is: *true means DCJ hid the sales count because there were 30 or
   fewer sales*, so that median rests on few sales.
2. **Stale text found by Codex (Q3), for T11 to tidy:** `docs/data_sources.md` (C1) still calls baseline averaging
   "future work", and `docs/project_plan.md` still uses the placeholder names `pop_growth_pct` and `median_income`.
   The dictionary correctly documents the code.
3. **My T08 spec shorthand.** It said real growth = nominal ÷ CPI ratio. The exact formula is
   `(1 + growth_pct) / cpi_ratio − 1`, as the dictionary says. The T08 conclusion still holds: the formula keeps the
   order of the LGAs, so every Spearman result is the same for real growth.

## Kang's part

Pick any 5 columns at random and explain each one out loud without looking. Good ones to practise:
`median_price_revised_est`, `growth_annualised`, `rank_change_rev` (positive = dropped places), `low_sales_flag`,
`p_holm`.
