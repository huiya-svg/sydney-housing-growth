# T11 review: README write-up and final checks

**Verdict: Accept** · Reviewer: Claude · 2026-11-27

The README is accurate, complete and in the planned order. The figures, the stale-text fixes and the final checklist
all pass. One wording fix is recommended before publishing (decision 1 below). It traces back to my spec, not to
Codex's work.

## What I re-ran myself

| Check | Result |
|---|---|
| A1 Order and content | Pass. All 10 parts are in order: title, answer sentence, page 1 screenshot with links to the other pages and the PDF, question, findings, sources, method, limitations, reproduce, structure, tools. The three findings match the confirmed D10 text word for word. No TBD is left. "Power BI service" is now "Power BI Desktop". |
| A2 Numbers | Pass. I checked 12 numbers against the CSVs: GS houses 67.5 / 34.9, units 18.1 / −4.8, Fairfield 83.0, Hawkesbury 58.8, Woollahra 43.0 / 64.8, 7 of the top 10 Middle Ring, Middle Ring distances 6.9–20.7 km ("about 7–21"), and the low-sales counts (Burwood houses 3/0, Hawkesbury units 3/1, Hunters Hill units 4/3). The method text matches `transform.sql` (the CTE `lga_rows`, `ROW_NUMBER`, a `LEFT JOIN` on `lga_code_2025`, i.e. by ABS code). |
| A3 Links | Pass. 10 relative paths exist (I re-ran Codex's check). Codex reports the 8 external links return 200. I accept that, since the URLs are the ones already in `data_sources.md`. |
| A4 Figures | Pass. I re-ran `03_analysis` into a scratch copy: no errors, 13 s, and all 6 figures byte-identical to Codex's versions. The house scatter has the confirmed title. Both house figures have the Woollahra footnote, with numbers taken from `lga_growth.csv` in code. |
| A5 Stale text | Pass. Only data_sources C1 (last column) and project_plan line 77 changed. Line 77 now uses the real column names. |
| A6 Final checklist | Pass. `git status --short data/` is empty after my run too. The address and secret scans are thorough, and every hit is explained. |
| A7 Scope | Pass. Only allowed files changed. Codex used read-only git only. |

Codex's report is unusually careful. Q3 correctly says the downloader only verifies hashes of files that already
exist; it does not verify new downloads against the manifest. Q5 caught the income-year problem below.

## Decisions for Kang

1. **"lower-income areas in 2019" (recommend: fix).** The income factor is the **2016 Census**, not 2019 (D07). My T11
   spec wrote "in 2019" and Codex kept it word for word, as told. The same slip is on the Power BI Notes page ("lower
   household incomes in 2019"). Suggested finding 3:
   > Fast-growing house LGAs were the cheaper areas in 2019 and had lower household incomes at the 2016 Census. Price,
   > income and rent move together, so the tests can't say which one matters. For units, none of the five factors
   > showed a clear link.

   I can make the README edit. The Notes page fix is yours in Power BI (then retake `page4_notes.png` and re-export the PDF).
2. **Code licence (Codex decision 2).** MIT is the usual choice for a portfolio repo: anyone may reuse the code with
   credit, and the data keeps its own CC BY licences. Or no licence, which means all rights are reserved. Either is fine; your call.

## Optional wording nits

- Limitations → Distance reads as an instruction ("Measure straight-line distance…"). Better: "Distance is the
  straight-line distance from each LGA's geometric centroid (2025 boundaries) to the Sydney GPO. Centroids sit far
  from where people live in large semi-rural LGAs (Hawkesbury, Blue Mountains, Wollondilly)."
- Limitations → Low sales: worth saying that **Hawkesbury is the unit leader** and Burwood ranks 3rd for houses, so
  two headline names rest partly on thin quarters. Saying so is a strength in an interview.

## Kang's part

- Decide 1 and 2. If you say yes to 1 and the nits, I'll make the README edits.
- Read the README top to bottom as a recruiter would, and change anything that doesn't sound like you.
- Commit: `Write README and run final checks (T11)`.

## Follow-up (2026-11-27)

Kang approved decision 1 and both nits. Claude edited README finding 3 (2016 Census income) and the Distance and Low sales
limitations, and recorded the correction in D10 and the T11 spec. Still Kang's: the same income-year fix on the Power BI
Notes page (retake `page4_notes.png` and re-export the PDF), and the licence choice.
