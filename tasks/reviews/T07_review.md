# T07 review — CPI real growth, rankings, sensitivity, first charts

**Verdict: Accept (after Revision 1)** · Reviewer: Claude · 2026-11-26

> **Revision 1 check.** The CPI section is now step 14, before the SQL step (now 15). Apart from that one
> renumbered heading, every original cell is unchanged. The refresh workaround is gone. I copied the repo,
> deleted `cpi_sydney.csv` and ran both notebooks: both **pass**, and all 7 CSVs are **byte-identical** to the
> repo's. Accepted.
>
> **Chart title (Kang's question).** Canterbury-Bankstown is **not** inner west: it's south-western Sydney,
> and Ryde (5th) and Ku-ring-gai (10th) are on the north side. So my earlier suggestion "west and inner west"
> was wrong. What the top really shares is DCJ's **Middle Ring**: 5 of the top 6 house LGAs are Middle Ring
> (Fairfield is Outer Ring), and no Inner Ring LGA is in the top 14. Suggested title: *"Middle-ring houses
> grew fastest: 5 of the top 6 LGAs rose about 80% since 2019"*. Kang to confirm; it gets applied in T08.

---

*Original review (before Revision 1):*

All numbers, ranks and charts are correct. The one problem is the **order of steps in
`02_clean.ipynb`**. The SQL step (step 14) reads `data/interim/cpi_sydney.csv`, but that file is only
written by the new section at the **end** of the notebook (step 15). It works today only because the file
already exists from an earlier run. On a clean rebuild without that file, the notebook crashes. My
"append only" wording in the spec caused this, so the fix below changes that rule for this task.

## What I re-ran myself

| Check | Result |
|---|---|
| A1 Append-only | Pass. In all four processed CSVs the old columns come first, in the same order. Dropping the new columns gives files **byte-identical to the committed T05 versions** (checked against `git show HEAD:`). `fact_sales` and `dim_lga` are unchanged. |
| A2 Real growth and ranks | Pass. The CPI CSV matches the raw workbook (read independently with openpyxl, `Data1` B10 = A2325806K) with max diff 0.0. `cpi_ratio` = 100.1425 / 80.675 = **1.241308**. `growth_pct_real` recomputes with max diff 0.0. Ranks are correct for 34 house and 33 unit LGAs, and null for the rings, Greater Sydney and Wollondilly units. Spearman 0.934 / 0.992 reproduced. |
| A3 Notebooks and charts | Pass on rerun: both notebooks ran in order with 0 errors, and all CSVs were byte-identical. `03_analysis.ipynb` reads only `data/processed/`, has 8 plain-English markdown cells and saves PNGs with `Software` metadata removed. **Fail on a clean rebuild:** with `cpi_sydney.csv` deleted, `02_clean.ipynb` stops at the SQL cell with a DuckDB `IOException` (file not found). |
| A4 Scope | Pass. Only allowed files changed; the original 43 cells' code is unchanged; no git commands. |

## The charts

Good work overall. Each chart sticks to 2 colours plus grey, has % axes, hatches the caveat LGAs, draws the
Greater Sydney line, and has a title that states the finding.

- **Houses:** the title "Fairfield led house price growth at 83%" is true, but the top 5 are within 3.4
  points of each other (79.6–83.0%). A title about the **group** would say more. Kang decides (see below).
- **Units:** Penrith (5th, 47.36%) and Randwick (6th, 47.34%) are almost tied, so the top-5 cut-off here is
  arbitrary. That's fine for a chart, but don't build a sentence on "Penrith is top 5".
- **Rings:** "House prices grew faster than unit prices in every ring" is a strong, true headline.

## Key findings now confirmed

- Sydney CPI rose **24.1%** between the two windows.
- **Houses:** Greater Sydney +67.5% nominal, **+34.9% real**.
- **Units:** Greater Sydney +18.1% nominal, **−4.8% real**. After inflation, Greater Sydney units lost
  value; only the Outer Ring (+5.0%) beat inflation. This may be the project's most quotable finding.
- Caveat rows for the README: Burwood houses (3 low-sales quarters in 2019), Hawkesbury units (3 + 1),
  Hunters Hill units (4 + 3, bottom), and Woollahra houses (revision, 34 → 17).

## Fix prompt for Codex (paste as is)

```text
Read AGENTS.md and tasks/reviews/T07_review.md, then make this one fix to T07. Update tasks/reports/T07_report.md (add a "Revision 1" section).

Problem: in notebooks/02_clean.ipynb, step 14 (SQL transform) reads data/interim/cpi_sydney.csv, but that file is written later, in step 15. With the CSV deleted, the notebook fails at step 14 with an IOException.

Fix (this overrides the "append only" rule for this one change):
1. Move the CPI preparation (the markdown cell and the code cell that write cpi_sydney.csv) so it runs BEFORE the SQL step. Make it "## 14. Prepare Sydney CPI for real growth" and renumber the SQL step heading to "## 15. SQL transform and export". Renumbering these two headings is the only change allowed to existing cells.
2. The CPI cell can no longer use date_dim (it doesn't exist yet). Take the 29 quarters from the distinct quarter_date values of the cleaned sales table already in memory, and assert there are 29 and that none lacks a CPI value.
3. Keep the "Verify real growth and LGA ranks" cell at the end, but delete the "refresh the exports if the CPI input changed" block. It's no longer needed, and it is harder to explain than a simple top-to-bottom order. Update its markdown so it no longer says the SQL step reads a checked-in CSV.
4. Do not change any other cell, SQL, CSV values or 03_analysis.ipynb.

Prove it in the report:
- Copy the repo (without .venv, .git and data/raw/_archives) to a temp folder, delete data/interim/cpi_sydney.csv there, and run 02_clean.ipynb then 03_analysis.ipynb with nbconvert. Both must pass.
- In the real repo, run both notebooks twice. All CSVs in data/processed/ and data/interim/ must be byte-identical to the current files (list the SHA-256 hashes).
- No git commands.
```

## Kang's part (after the fix is accepted)

1. **Chart titles.** Look at the three PNGs in `docs/figures/`. For houses, pick one:
   (a) keep "Fairfield led house price growth at 83%", or
   (b) a group title such as "Houses in Sydney's west and inner west grew fastest, about 80% since 2019".
   Tell me your choice or your own wording; it'll go into T08's chart pass.
2. **Your CV sentences.** Pick the 2 findings you'd lead with and rewrite them in your own words. My
   suggestion is the real-terms contrast: houses beat inflation by about a third, while units fell behind it.
3. **Power BI.** After you commit T07, pull it on Windows and click **Refresh**. You'll see the new columns
   (`cpi_sydney`, `growth_pct_real`, `growth_rank`, …).
