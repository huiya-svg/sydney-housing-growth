# T08 report — Factor tests for Greater Sydney price growth

## Summary

Part B tests five pre-specified factors separately for houses and units, using first-published nominal growth as the main outcome. Seven of the ten fastest-growing house LGAs were in the Middle Ring, and eight of the ten fastest-growing unit LGAs were in the Outer Ring. Four house tests found associations at the specified threshold, while all five unit tests returned “no clear relationship”. Under the revised house series, population and rent moved to “no clear relationship”, and the baseline-price association weakened to weak negative.

## Files created or changed

- `notebooks/03_analysis.ipynb` — Part B with the tests, overlap matrices, visuals and findings, plus the Part A house chart title.
- `data/processed/factor_tests.csv` — ten rows with nominal and revised Spearman results.
- `docs/figures/factor_scatter_house.png` and `docs/figures/factor_scatter_unit.png` — five labelled factor panels per dwelling type.
- `docs/figures/factor_correlation.png` — house and unit correlation matrices on a shared scale.
- `docs/figures/growth_by_lga_house.png` — updated title supported by the ring counts.
- `tasks/reports/T08_report.md` — submission and verification evidence.

## Commands run

| Command | Result |
|---|---|
| `cat`, `sed`, `rg` and `.venv/bin/python -` with nbformat | Read the task, AGENTS.md, Phase 3B–3C, D05/D07/D08, C1–C5, the T07 review and Part A. Captured file and cell hashes and appended 22 Part B cells. |
| `.venv/bin/python -` with pandas, SciPy and matplotlib | Checked sample sizes, preliminary tests, ring counts and the space needed for the exact house title. Wrapped and fitted the house title within its existing chart. |
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb` then the same command for `notebooks/03_analysis.ipynb` | Both rounds passed in order. Before the second round, refined the scatter labels so unit sale-price ticks display quarter-million increments precisely. The Jupyter kernel emitted its standard startup TCP warning. |
| `.venv/bin/python -` for an independent rank and Holm comparison | Pass. Recomputed rho as Pearson correlation on average ranks and two-sided p using the t transformation. Independently applied the four Holm multipliers to each version, then matched every test and verdict. |
| `.venv/bin/python -` with nbformat and Pillow, `shasum -a 256` and visual inspection | Pass. Checked the four PNGs at 150 dpi, the house title's pixel difference, execution counts, the ten-row export, and file scope. Preserved the saved outputs and execution metadata of the unchanged notebook cells after validation runs. |

## Answers to the task questions

### Q1. Test sample sizes and exclusions

| Factor | Family | Houses n | Units n |
|---|---|---:|---:|
| CBD distance | main | 34 | 33 |
| 2016–19 population growth | main | 34 | 33 |
| 2019 price | main | 34 | 33 |
| 2016 household income | exploratory | 33 | 32 |
| 2019 rent | exploratory | 34 | 33 |

The sample contains LGA rows only. Wollondilly is excluded from all unit tests because it has no 2019 strata price baseline (D05). Bayside is excluded from the two income tests because the 2016 Census medians are for its predecessor councils. Bayside is present in the other eight tests. The rent factor stored as `rent_2019_weekly` uses the source column for that row's dwelling type. Sample sizes are the same for the first-published and revised tests. [Decision log](../../docs/decisions.md), [Factor export](../../data/processed/factor_tests.csv)

### Q2. Top ten LGAs by ring

| DCJ ring | All LGAs | House top ten | Unit top ten |
|---|---:|---:|---:|
| Inner Ring | 8 | 0 | 2 |
| Middle Ring | 12 | 7 | 0 |
| Outer Ring | 14 | 3 | 8 |
| **Total** | **34** | **10** | **10** |

The Outer Ring's total includes Wollondilly, leaving 13 eligible unit LGAs in that ring. Five of the top six house LGAs are Middle Ring. Cumberland, Burwood, Canterbury-Bankstown, Ryde and Canada Bay grew between 79.31% and 81.43%. Fairfield ranked first at 82.98% and is in the Outer Ring. These counts support the requested title, “Middle-ring houses grew fastest: 5 of the top 6 LGAs rose about 80% since 2019”. [Growth export](../../data/processed/lga_growth.csv), [House growth chart](../../docs/figures/growth_by_lga_house.png)

### Q3. Spearman results and revision sensitivity

P-values are two-sided. Nominal verdicts use raw p for the main tests and Holm-adjusted p for the four exploratory tests. Revised verdicts use the same rule and a separate Holm calculation over the four revised exploratory tests. [Factor export](../../data/processed/factor_tests.csv), [Analysis notebook](../../notebooks/03_analysis.ipynb)

| Dwelling | Factor | Family | n | ρ | p | Holm p | Verdict | Revised ρ | Revised p | Revised Holm p | Revised verdict |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| house | CBD distance | main | 34 | 0.3262 | 0.0597 | — | no clear relationship | 0.2565 | 0.1431 | — | no clear relationship |
| house | 2016–19 population growth | main | 34 | 0.4289 | 0.0114 | — | moderate positive | 0.3268 | 0.0592 | — | no clear relationship |
| house | 2019 price | main | 34 | −0.4405 | 0.0091 | — | moderate negative | −0.3687 | 0.0319 | — | weak negative |
| house | 2016 household income | exploratory | 33 | −0.5137 | 0.0022 | 0.0089 | moderate negative | −0.4382 | 0.0108 | 0.0430 | moderate negative |
| house | 2019 rent | exploratory | 34 | −0.4162 | 0.0144 | 0.0431 | moderate negative | −0.3317 | 0.0553 | 0.1660 | no clear relationship |
| unit | CBD distance | main | 33 | 0.3075 | 0.0817 | — | no clear relationship | 0.3098 | 0.0793 | — | no clear relationship |
| unit | 2016–19 population growth | main | 33 | −0.3212 | 0.0684 | — | no clear relationship | −0.3135 | 0.0756 | — | no clear relationship |
| unit | 2019 price | main | 33 | −0.1297 | 0.4720 | — | no clear relationship | −0.1180 | 0.5132 | — | no clear relationship |
| unit | 2016 household income | exploratory | 32 | −0.0403 | 0.8266 | 0.8266 | no clear relationship | −0.0022 | 0.9905 | 0.9905 | no clear relationship |
| unit | 2019 rent | exploratory | 33 | −0.1534 | 0.3940 | 0.7880 | no clear relationship | −0.1531 | 0.3951 | 0.7901 | no clear relationship |

Three verdicts changed, all for houses. Population growth and 2019 rent moved to “no clear relationship”. The 2019 price association changed from moderate negative to weak negative. The one real-growth check, house CBD distance, returned the same ρ (0.326203) and p (0.059728) as the nominal test. The common positive CPI ratio preserves the growth ranks.

### Q4. Revised baseline price check

Correlating `price_2019_rev` with `growth_pct_rev` uses the revised estimates for both price windows. The house result survives as a **weak negative** association (ρ = −0.3705, p = 0.0310). The unit comparison shows no clear relationship. [Analysis notebook](../../notebooks/03_analysis.ipynb)

| Dwelling | n | Revised 2019 price vs revised growth ρ | Two-sided p | Verdict |
|---|---:|---:|---:|---|
| house | 34 | −0.3705 | 0.0310 | weak negative |
| unit | 33 | −0.1285 | 0.4760 | no clear relationship |

The 2019 price is also the denominator of growth. Sampling noise that lowers the baseline median can inflate measured growth, contributing mechanically to a negative association. This caveat applies to the revised check too.

### Q5. Factor pairs with absolute ρ of at least 0.7

| Pair | Houses n | House ρ | Units n | Unit ρ |
|---|---:|---:|---:|---:|
| CBD distance and 2019 price | 34 | −0.883 | 33 | −0.815 |
| CBD distance and 2019 rent | 34 | −0.838 | 33 | −0.854 |
| 2019 price and 2016 household income | 33 | 0.780 | 32 | 0.853 |
| 2019 price and 2019 rent | 34 | 0.953 | 33 | 0.898 |
| 2016 household income and 2019 rent | 33 | 0.826 | 32 | 0.722 |

Higher prices, incomes and rents tend to rank together in both dwelling types. Distance ranks run in the opposite direction to price and rent. The pairwise results cannot isolate their individual associations with growth, so the findings describe the overlap and avoid attributing the result to a single factor. [Correlation chart](../../docs/figures/factor_correlation.png)

### Q6. Findings

7 of the ten fastest-growing house LGAs were in the Middle Ring (12 LGAs total), and 8 of the ten fastest-growing unit LGAs were in the Outer Ring (14 total). First-published house growth had a moderate positive association with population growth (ρ = 0.43, p = 0.011) and a moderate negative association with 2019 price (ρ = -0.44, p = 0.009), which is also the growth denominator. Exploratory household income and house rent both had moderate negative associations with house growth (Holm p = 0.009 and 0.043), and 2019 house price and rent ranked similarly (ρ = 0.95). We tested CBD distance and found no clear relationship for houses or units (p = 0.060 and 0.082), and all five unit tests had that verdict. With revised house growth, population and rent had no clear relationship (p = 0.059 and Holm p = 0.166), and the 2019 price association was weak negative (ρ = -0.37, p = 0.032).

[House factor chart](../../docs/figures/factor_scatter_house.png), [Unit factor chart](../../docs/figures/factor_scatter_unit.png)

### Q7. Part A outputs and existing CSV hashes

Fifteen of the original 16 Part A cells, including saved outputs, match their original cell hashes. Only the title code and the house image in cell 12 differ. The unit image in that cell matches its original saved output. The house plot's pixel difference is bounded by `(45, 17, 773, 78)` from the image's upper-left origin, entirely in the title area. [Analysis notebook](../../notebooks/03_analysis.ipynb)

| Part A PNG | SHA-256 before | SHA-256 after |
|---|---|---|
| `growth_by_lga_house.png` | `6e84572d63ccd24b263b85141ad2583555c255648dad25d0033f793a05558927` | `6a230bfc13472e1740b1100de627273084392450676eb987d595cad32b69dbda` |
| `growth_by_lga_unit.png` | `791d8903ad1dad7d9bf0fde91675ed3c95b4a197e1d4ab8483d1229640ad5257` | `791d8903ad1dad7d9bf0fde91675ed3c95b4a197e1d4ab8483d1229640ad5257` |
| `price_index_rings.png` | `14c28c32dd8fbf5f377f846c307d06c7f649de73191847268aa4e54a863e3213` | `14c28c32dd8fbf5f377f846c307d06c7f649de73191847268aa4e54a863e3213` |

Each existing CSV had the same SHA-256 before and after the two ordered executions.

| Existing CSV | SHA-256 before and after |
|---|---|
| `data/interim/cpi_sydney.csv` | `de486ee17bbfaf395c6018214229808bd54d9d5a1d660a7274391dad2c8ad8ce` |
| `data/interim/lga_factors.csv` | `aba5c04ae360cb001da41c71a384b3c9d4badcd466268a75ae8e0eb65cbd95e2` |
| `data/interim/sales_long.csv` | `129403ad50c2be6a1c345f43239f2c38a0667d78c295cd8732dfed36abfe2800` |
| `data/processed/dim_date.csv` | `21a969110f7a1eda3910811452101e2908825ca1477b5ec7194cb8ba0ba9d1a7` |
| `data/processed/dim_lga.csv` | `abcaf3571943e759798205863feb837198d2340b57cb497302b91dbc8b1a0455` |
| `data/processed/fact_sales.csv` | `9c5c66eba72c7e7cdc171ca3568698ec8b18a9654f9fab2ed1a56db5d1ae4b49` |
| `data/processed/lga_growth.csv` | `482a5bc5cf1d6dcbb55b3f6b36e201f9f662fa7bbc713272e45aee5b8419ae39` |
| `data/raw/MANIFEST.csv` | `55d5a39fbe71d70d5292c4d469929cb3718aabc6d676274948fadec06a1d1612` |
| `data/raw/abs_asgs/CG_2022_LGA_2023_LGA.csv` | `ddaf727a330bcfa8e2bf3bc02b97711997b75617e01a4ffed79ae8b089949a7a` |
| `data/raw/abs_asgs/CG_LGA_2016_LGA_2021.csv` | `7849f286e0dad2c3782ad2403e72e5e2f3199481c47fbee46ed4d50bcf6c97f8` |
| `data/raw/abs_asgs/CG_LGA_2020_LGA_2021.csv` | `fb1ba47536e1ee6423d25f1af4ec97be3c8e5dbef83996e8298de17fec71f4d9` |
| `data/raw/abs_asgs/CG_LGA_2021_LGA_2022.csv` | `be6722c14903be34886e1c77477f34e1b45257fa0cb07a277643e860196251d2` |
| `data/raw/abs_asgs/CG_LGA_2023_LGA_2024.csv` | `e115acc5a6e8702ec5cd331542a7c3c2b6cf369c218ee61e2be76d91ce498813` |
| `data/raw/abs_asgs/CG_LGA_2024_LGA_2025.csv` | `92697d6d02e2c4926f7bc2e81704ae6beb92e9aae6198f9ef67a7e893948579f` |
| `data/raw/abs_census/2016Census_G02_NSW_LGA.csv` | `1415ed6aebe4726921be823ff8ef910cff01151ed3a0cc438326de477b1a7df7` |
| `data/raw/abs_census/2016Census_G32_NSW_LGA.csv` | `01c826250bbd2e6b1a78289ea7688b6795ff378b5fdfc3ef40469c92aa864907` |
| `data/raw/abs_census/2021Census_G02_NSW_LGA.csv` | `d06edc06faa829bdcadc99bcb2cafa1a7e7e56246519b266368b65c5890a7275` |
| `data/reference/lga_lookup.csv` | `448fd4bcf746775f82846d8896f0e61b05306eccdcd16b3571dc3d3414db562c` |

Both runs produced the new `factor_tests.csv` SHA-256 `33ab5cacdf2f5b19065b57acf28ea83bf5ac0601346e7adcac11ae7f8f64663a`.

## Acceptance checks

| Check | Pass/Fail | Evidence |
|---|---|---|
| A1. Ten Spearman tests and four exploratory Holm p-values | Pass | Independent rank and p-value calculation matched the ten nominal and ten revised tests. Only the four exploratory rows were adjusted in each series. |
| A2. Deterministic export | Pass | Exactly 11 columns in the specified order and ten unique dwelling type × factor rows. SHA-256 matched between runs. |
| A3. Notebook execution and four figures | Pass | Both notebooks executed twice in order. The four PNGs passed 150 dpi and metadata checks. Visual checks covered panel subtitles, axes, extreme-LGA labels, a zero-centred correlation scale and the house title. |
| A4. Findings and sensitivity | Pass | The five sentences cover both dwelling types, use association language and report a no-clear result and all three D08 verdict changes. |
| A5. Report and scope | Pass | Q1–Q7 are answered. Only the seven allowed paths have content changes. No git commands were run. |

## Decisions needed (for Kang)

None.

## Issues and risks

- These are pairwise tests across 32–34 LGAs. The p-values use the specified main and exploratory rules, and the results describe associations for this period.
- The 2019 price denominator and the correlations among price, income, rent and distance limit interpretation of the house associations. Population and rent also depend on the version of the growth series.

## Suggested commit message(s)

- `feat: test Sydney growth factors and revision sensitivity`
