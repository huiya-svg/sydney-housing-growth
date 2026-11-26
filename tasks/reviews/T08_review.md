# T08 review — Factor tests

**Verdict: Accept** · Reviewer: Claude · 2026-11-26

## What I re-ran myself

| Check | Result |
|---|---|
| A1 Spearman and Holm | Pass. I recomputed all **20** tests (10 first-published + 10 revised) from `lga_growth.csv` and `dim_lga.csv` with my own code. Every n, rho and p matches the report to 4 dp. Holm over the 4 exploratory tests matches (0.0089, 0.0431, 0.788, 0.8266; revised 0.0430, 0.1660, 0.7901, 0.9905). |
| A2 `factor_tests.csv` | Pass. 11 columns as specified, 10 rows, deterministic. |
| A3 Notebooks and charts | Pass. Both notebooks re-ran in order with 0 errors, and all CSVs are byte-identical. The 4 PNGs follow the design rules: 2 colours plus grey, ρ and p shown on each panel, extremes labelled, a diverging scale centred on 0 for the matrix only. |
| A4 Findings | Pass. They use association language, include "no clear relationship" results (distance for both types; all five unit tests) and report all three D08 verdict changes. |
| A5 Scope | Pass. Only allowed files changed; Part A changed only in the house chart title; no git commands. (My rerun touched `02_clean.ipynb` timestamps; I restored it.) |
| Ring counts | Confirmed: house top 10 = **7 Middle + 3 Outer**; unit top 10 = **8 Outer + 2 Inner**. The new house chart title is supported. |

## What the results say (my reading, for Kang)

1. **Houses: one cluster, not five separate factors.** 2019 price, 2016 income and 2019 rent overlap almost
   completely (ρ = 0.78–0.95), and all three run opposite to distance (−0.58 to −0.88). The honest summary is:
   *"house prices grew faster in LGAs that were cheaper, lower-income and lower-rent in 2019"*. We can't say which
   of the three matters.
2. **That cluster weakens under revisions.** With revised estimates, rent drops to "no clear relationship" and
   price to "weak". Part of the house result comes from Woollahra, whose first-published growth is understated
   (43% vs 64.8% revised). It sits in the bottom-right corner of every house panel.
3. **Distance: no straight-line link, but a middle-distance pattern.** Spearman tests a one-direction (monotonic)
   relationship, and finds none. The scatter and the ring counts show that the fastest houses sit **10–30 km** out
   (the Middle Ring), with slower growth both closer in and far out. That's a **descriptive** observation found
   after looking at the data, so present it as a pattern, not as a tested result.
4. **Units: nothing explains the ranking.** All five tests show no clear relationship. The fastest units are
   8 of 10 in the Outer Ring (Hawkesbury, Campbelltown, Central Coast…), yet distance alone isn't significant
   (p = 0.08). That's a valid, interesting "we tested it and found no clear link".

## Small suggestions (not blocking; apply in T10/T11 chart polish)

- **House scatter title.** "Lower 2019 house prices were associated with faster growth" credits **price**
  alone, but the report itself (Q5) says price, income and rent can't be separated. A better title would be:
  *"Houses grew faster in LGAs that were cheaper in 2019 (price, rent and income move together)"*. Kang decides.
- **Woollahra in the house scatters** is labelled "bottom 3" with no caveat. Add a footnote: "Woollahra's
  first-published growth is understated; revised estimate 64.8%."

## Decision for Kang: D09 (regression or not)

My recommendation is **(a) no regression**. With 34 LGAs and price/rent/income/distance correlated at 0.78–0.95,
a regression couldn't separate their effects (multicollinearity), and the coefficients would be unstable. The
pairwise tests plus the overlap matrix tell the honest story. Option (b), a single 2-factor model (distance +
population growth, the least overlapping pair at ρ = 0.50), is possible but adds little. Record your choice in
`docs/decisions.md`.

## Kang's part

1. Say in one sentence each: what ρ = −0.51 for income means here, and why we use Spearman (ranks) and not Pearson.
   (Camden's +30% population growth would dominate Pearson.)
2. Explain Holm: with 4 exploratory tests at 0.05, the chance of at least one fluke is about 19%, so the smallest
   p is multiplied by 4, the next by 3, and so on.
3. Decide D09 and the house scatter title.
4. Pick your final 3 findings (README + LinkedIn). My suggested three:
   - **Houses vs units, real terms:** Greater Sydney houses +67.5% (+34.9% after inflation) vs units +18.1%
     (−4.8% after inflation).
   - **Where:** 7 of the 10 fastest-growing house LGAs are Middle Ring (10–30 km), led by Fairfield, Cumberland,
     Burwood and Canterbury-Bankstown (about 80–83%).
   - **What they share:** fast-growing house LGAs were the cheaper, lower-income ones in 2019; for units, none of the
     five factors showed a clear link.
