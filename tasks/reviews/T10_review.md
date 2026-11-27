# T10 review: Power BI report pages, screenshots, PDF

**Verdict: Revise (polish only)** · Reviewer: Claude · 2026-11-27

Every number on the four pages is correct, the PDF has the right pages, and the story holds. Only presentation
fixes remain: two typos, one cut-off table, default titles Power BI added, and one page title that claims more than the test shows.
Kang does the fixes in Power BI (no Codex prompt needed). After that, it's Accept.

## What I checked myself

| Check | Result |
|---|---|
| Files committed (`095f0fc`) | Pass. 4 PNGs, the PDF and the updated `.pbix`, all in `powerbi/`. |
| PDF | Pass. 4 pages, A4 landscape, in order Answer → Trends → Why → Notes. The hidden Cross-check page is **not** in the PDF. Note: the PDF is image-only (no text, no links), which is how Power BI Desktop exports. I corrected guide 5.4, which wrongly said links stay clickable. |
| Pages in the `.pbix` | Pass. The Answer, Cross-check (`HiddenInViewMode`), Trends, Why and Notes pages, all 1920×1080. |
| Page 1 numbers | Pass. GS houses 67.47% → "67%", real 34.91%; units 18.14% → "18%", real −4.82% ("went backwards"). The top 5 in blue (Fairfield, Cumberland, Burwood, Canterbury-Bankstown, Ryde) match `growth_rank` 1–5 exactly. 34 bars. Fairfield 83.0%. |
| Page 2 numbers | Pass. The Greater Sydney house index matches my own calculation from `fact_sales.csv`: 93.6 (2019 Q1), peak 151.6 (2021 Q4), low 135.3 (2023 Q1), new high 158.1 (2024 Q2), 167.8 (2026 Q1). The title is true for houses. For units it is also true but mild (peak 112.8, new high 114.9 in 2024 Q4). |
| Page 3 numbers | Pass. The table matches `factor_tests.csv` (ρ, p, Holm p, n, verdicts). The blue dots are Middle Ring LGAs, as `Ring Colour` intends. |
| Page 4 facts | Pass on every fact. 7 of the top 10 house LGAs are Middle Ring (Cumberland, Burwood, Canterbury-Bankstown, Ryde, Canada Bay, Parramatta, Ku-Ring-Gai). "Usually slightly upward": 1,463 rows revised up, 208 down, 517 unchanged, median +0.6%. Woollahra 43.0% / 64.8%. Wollondilly units have 0 of 4 baseline quarters. CPI 1.241. The GPO point is from Heritage NSW, CC BY 4.0 (MANIFEST row 39). Latest four = Jun 2025 to Mar 2026. |
| Privacy (`RepoPath`) | **Not checked.** The new `.pbix` format compresses the data model, so I can't read the parameter from the Mac. Kang to confirm (see fix 9). |

## Fixes (in order of importance)

**Must fix: visible errors**

1. **Notes page typos:**
   - "(DSJ)" → **(DCJ)**
   - "Australian Bureau of Statitics" → **Statistics**
   - Heading "Data Resources:" → **"Data sources:"**
   - "Questions:" → **"Question:"** (there is one question)
2. **Notes page, right text box:** it is 960 px wide and ends exactly at the page edge (x 960 + 960 = 1920). The
   screenshot cuts the line ends ("March 202", "The", "and"). Set General → Properties → Size **Width 900** and
   Position **H 990**. Then retake `page4_notes.png`.
3. **Why page, factor table:** it is only 536 px wide, so "verdict" is cut ("moderate negati") and a scroll bar shows.
   - Widen it to about **Width 1100** (it can run across to x ≈ 1450; there is empty space on the right).
   - Rename the headers with "Rename for this visual": Factor, Group, n, ρ (rho), p, Holm p, Verdict.
   - Turn on a title: "Spearman tests: growth vs each 2019 factor".
   - The "Filter (0)" button in the screenshot is the visual header showing on hover. Click empty canvas before you take the screenshot.
4. **Why page title, "mid-distance":** the distance test itself says *no clear relationship* (ρ 0.33, p 0.060).
   The evidence for "middle" is the ring count: 7 of the top 10 are Middle Ring, and Middle Ring houses grew 71.8%
   vs Inner 51.9% and Outer 67.5%. Spearman can't see a "middle" pattern, because it only tests one-direction trends. An interviewer will spot
   the clash between the title and the table. Suggested title:
   **"Fast-growing houses were mostly middle-ring and cheaper in 2019. For units, no factor showed a clear link."**
5. **Why page scatters:** blue means Middle Ring, but nothing on the page says so. Add the subtitle
   "Blue = Middle Ring LGA" to both scatters (Format → Title → Subtitle).

**Should fix: default text Power BI added**

6. **Answer page bar chart:** the title is the default "Growth Since 2019 / by lga". Change it to
   **"Growth since 2019 by LGA"**. Set the subtitle to **"Top 5 in blue · dashed line = Greater Sydney"**, or turn it off.
   The reference-line label is hidden behind the Fairfield bar (you can just see it in the PDF). Set its label position to
   **Below** / **Left**, or turn the label off, since the subtitle now explains the line.
7. **Trends chart:** turn **off** the subtitle. It reads "…, Median Price and YoY Change by quarter_label and lga"
   because the tooltip fields are listed. Fix the title spacing to "(2019 average = 100)".

**Nice to have**

8. **Layout:**
   - Answer page: about 470 px is empty under the cards. Moving the cards up beside the slicer, or making the bar
     chart wider, would balance it.
   - Why page: there is a large gap between the title and the visuals. Move the title box down, or the visuals up.
   - The Dwelling type slicer is top-right on page 1 but top-left on pages 2–3. Optional, but it's tidier if it sits in one place.
   - Title alignment: centred on page 1, left/offset on pages 2–3. Pick one.
9. **`RepoPath` privacy:** if it still holds `C:\Users\<your name>\…`, set it to `C:\repo\`, then save. Tell me which.

Then: Ctrl+S, retake the screenshots that changed (all four, if the titles changed), re-export the PDF, then
commit with `Polish Power BI report titles, table and notes (T10)`.

## Kang's part

- Do fixes 1–7 (about 20 minutes), and 8–9 if you like.
- Out loud, without notes: why "mid-distance" can't come from the Spearman distance test, and what the ring count
  shows instead. This is a likely interview question.

---

## Re-check after polish (commit `bb875d5`, 2026-11-27)

**Verdict: Accept**, on one condition: the saved `.pbix` is committed. `bb875d5` changed only the 4 PNGs and
the PDF. `powerbi/sydney_housing.pbix` is still the version from `095f0fc`, so the report file on GitHub doesn't
have these fixes yet.

| Fix | Result |
|---|---|
| 1 Notes typos | Done: DCJ, Statistics, Data Sources. "Questions:" is still plural (nit). |
| 2 Notes right text box | Done. Every line ends inside the page. |
| 3 Factor table | Done: wider, verdicts in full, headers renamed (Factor, Group, n, ρ, p, Holm p, Verdict), sorted by ρ. No table title (nit). A "Filter (0)" button still shows, and it appears in the PDF too, so it isn't hover-only (nit; turn it off under Format visual → General → Header icons). |
| 4 Why page title | Done. "Mostly middle-ring and cheaper in 2019" matches the evidence. |
| 5 Scatter subtitles | Done: "Blue = Middle Ring LGA" on both. |
| 6 Bar chart title and line label | Done. "Growth Since 2019 by LGA", the subtitle explains blue and the dashed line, and the "67.5%" label now sits at the bottom, clear of the bars. |
| 7 Trends subtitle | Done (off). The title still renders as "(2019 average =100)", with no space after "=" (nit). |
| PDF | 4 pages, the same content as the new PNGs, no Cross-check page. |
| 8 Layout | Not changed. Optional. |
| 9 `RepoPath` | Still waiting for Kang's answer. |

The nits are optional. If you fix them, do it in the same save as the `.pbix` commit below.

**To close T10:** on Windows, Ctrl+S in Power BI. Then in GitHub Desktop tick `powerbi/sydney_housing.pbix` and commit
`Save polished Power BI report file (T10)`, then push.
