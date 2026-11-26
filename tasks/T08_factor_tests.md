# T08 — Factor tests: what do the fastest-growing LGAs have in common?

**Phase:** 3B–3C · **Implementer:** Codex · **Reviewer:** Claude · **Owner:** Kang
**Read first:** `AGENTS.md`, `docs/project_plan.md` (Phase 3B–3C), `docs/decisions.md` (D05, D07, D08),
`docs/data_sources.md` (C1–C5 verdicts), `tasks/reviews/T07_review.md`, `notebooks/03_analysis.ipynb`.

## Context

T07 answered "how much did prices grow, and where?". This task answers the second half of the project question:
**what do the fastest-growing LGAs have in common?** We test the five factors Kang chose in D07, one dwelling type
at a time, with Spearman rank correlation. With only 33–34 LGAs, the honest result for several factors may be "no
clear relationship". That's a valid finding and must be reported as one.

## Inputs (read only from `data/processed/`)

- **Outcome:** `lga_growth.growth_pct` (first-published, nominal), LGA rows only (`geo_level = 'lga'`).
  Units exclude Wollondilly (no 2019 baseline, D05).
- **Main factors (D07):** `dim_lga.distance_km`, `dim_lga.pop_growth_2016_19`, `lga_growth.price_2019` (the same
  dwelling type as the outcome).
- **Exploratory factors (D07):** `dim_lga.income_2016_weekly` (Bayside is missing; leave it out of that test only),
  and 2019 rent for the **same** dwelling type: `rent_2019_house_weekly` for houses and `rent_2019_unit_weekly` for
  units.

## Part B: append to `notebooks/03_analysis.ipynb`

Add a section "Part B — What do the fastest-growing LGAs have in common?". Use plain pandas, `scipy.stats.spearmanr`
and matplotlib. Put a plain-English markdown cell before each step.

1. **Analysis table.** One row per LGA × dwelling type with the outcome and the five factors. Print `n` per test
   (expected: houses 34, units 33; income tests one fewer because of Bayside).
2. **Where the top 10 are.** For each dwelling type, count how many of the top-10 LGAs by `growth_rank` are in each
   ring (Inner / Middle / Outer), next to how many LGAs each ring has in total. This tests the draft chart title
   claim about the Middle Ring (T07 review).
3. **Spearman tests.** For each dwelling type × factor (10 tests), report `n`, `rho` and the two-sided `p`.
   - **Holm correction** applies to the **exploratory family only**: income and rent × 2 dwelling types = 4 tests,
     corrected together. Main-factor p-values stay unadjusted (pre-specified in D07). Implement Holm in a few
     commented lines of pandas, not a new library, so Kang can explain it.
   - **Wording rule** for the `verdict` column (use it in the findings too):
     - p (Holm p for exploratory) ≥ 0.05 → "no clear relationship";
     - otherwise |rho| < 0.4 → "weak", 0.4–0.6 → "moderate", ≥ 0.6 → "strong", plus "positive" or "negative".
4. **Real growth note.** Real growth = nominal growth ÷ the same CPI ratio for every LGA, so all Spearman results
   are identical for real growth. Assert this for one factor, and state it in one sentence. Don't run it 10 times.
5. **Sensitivity (D08).** Repeat the 10 tests with `growth_pct_rev`. Report `rho_rev`, `p_rev` and whether the verdict
   changes. Any change must be mentioned in the findings.
6. **Price-level caveat.** `price_2019` is also the denominator of growth. A low 2019 median caused by sampling noise
   inflates growth, so a negative rho is partly mechanical. Say this in markdown next to the result, and repeat the
   price test using the **revised** 2019 price (`price_2019_rev`) with the revised growth as a check.
7. **Overlap between factors.** Spearman correlation matrix of the five factors (and growth), one per dwelling type.
   Comment on any |rho| ≥ 0.7 pair (e.g. distance vs price). This means two factors can't be separated with this
   data, so the findings must not credit one over the other.
8. **Results table export.** Write `data/processed/factor_tests.csv`: `dwelling_type, factor, family
   (main/exploratory), n, rho, p, p_holm (null for main), verdict, rho_rev, p_rev, verdict_rev`. Exactly 10 rows, one per test (the
   step-6 price check stays in the notebook only). For the exploratory rows, `verdict_rev` uses Holm p on the
   revised tests too. The file must be deterministic.
9. **Charts** → `docs/figures/`, 150 dpi, `metadata={"Software": None}`, the same style as T07 (2 colours plus grey,
   titles that state the finding, labelled axes with units):
   - `factor_scatter_house.png` and `factor_scatter_unit.png`: 5 small panels (growth % on y, factor on x), one
     dot per LGA. Each panel subtitle shows `rho` and `p` (or Holm p). Label the top-3 and bottom-3 LGAs by name.
     Distance on a linear km axis; price and income on $ axes.
   - `factor_correlation.png`: the two factor-overlap matrices side by side. Use a diverging grey-to-colour scale
     centred at 0, numbers printed in cells. This is the only chart allowed a colour scale.
   - Update the title of `growth_by_lga_house.png` to: **"Middle-ring houses grew fastest: 5 of the top 6 LGAs rose
     about 80% since 2019"**, but only if step 2 supports it. If step 2 doesn't, keep the current title and say why
     in the report.
10. **Findings (Phase 3C).** 3–5 sentences with numbers, covering both dwelling types. At least one must be a "we
    tested X and found no clear relationship" sentence. Use "is associated with", never "causes" or "drives".
    Mention any D08 verdict change.

Must pass, in this order: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb`,
then the same for `03_analysis.ipynb`. A second run gives byte-identical CSVs.

## Out of scope

- Regression or any multi-factor model. With ~33 LGAs and overlapping factors it would be over-fitted. Kang decides
  later (possible D09) after seeing the correlation matrix.
- Factors not in D07 (2021 income, post-2019 population, approvals, yield).
- Changing Part A, earlier notebooks, SQL or existing CSV columns. Data dictionary (T06). README (T11).

## Allowed files

- `notebooks/03_analysis.ipynb` (append Part B; plus the one title string in Part A's house chart, step 9)
- `data/processed/factor_tests.csv` (new)
- `docs/figures/factor_scatter_house.png`, `factor_scatter_unit.png`, `factor_correlation.png` (new),
  `growth_by_lga_house.png` (title only)
- `tasks/reports/T08_report.md`

## Questions to answer in the report

- **Q1.** `n` per test and which LGAs are excluded from which test, and why.
- **Q2.** The top-10 by ring table, and whether the Middle Ring title is supported.
- **Q3.** The 10-row results table (rho, p, Holm p, verdict), plus the D08 columns.
- **Q4.** The price-level caveat check: does the price result survive using revised prices at both ends?
- **Q5.** Factor pairs with |rho| ≥ 0.7, and what that means for the findings.
- **Q6.** The findings sentences.
- **Q7.** Proof that the Part A outputs and all existing CSVs are unchanged (hashes before and after).

## Acceptance criteria

- [ ] A1 10 Spearman tests correct (Claude recomputes them); Holm applied to exactly the 4 exploratory tests.
- [ ] A2 `factor_tests.csv` has exactly the specified columns and 10 rows, and is deterministic.
- [ ] A3 Both notebooks run clean in order; the 4 new or changed PNGs follow the design rules.
- [ ] A4 Findings use association language, include a "no clear relationship" result if any, and mention D08 changes.
- [ ] A5 Report answers Q1–Q7; only allowed files changed; no git commands.

## Kang's part (after review)

1. For each factor, say in one sentence what Spearman's rho means here, and why we use ranks, not Pearson.
   (Hint: Camden's +30% population growth.)
2. Explain Holm in your own words: why 4 tests need a stricter bar than 1.
3. Pick your final 3 findings for the README and the LinkedIn post.
4. Decide D09: is a regression worth adding, given the correlation matrix?
