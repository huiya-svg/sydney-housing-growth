# T03 review — LGA lookup + clean sales + revisions

**Verdict: Accept** · Reviewer: Claude · 2026-11-25

## What I re-ran myself

| Check | Result |
|---|---|
| A1 Outputs | Pass. `lga_lookup.csv` 34 rows, 4 columns; `sales_long.csv` 2,204 rows (lga 1,972 / ring 174 / greater_sydney 58), columns in spec order. |
| A2 Rerun | Pass. Re-executed `02_clean.ipynb`: 25 cells, 0 errors, 36 asserts; both CSVs byte-identical (sha1 unchanged). |
| A3 Missing ≠ 0 | Pass. 0 zero prices, 0 zero counts, 0 missing prices with `published` status. Wollondilly unit 2019: 3 × `suppressed` + 1 × `not_in_source`. |
| A4 Revisions | Pass. Tolerance, summary, top 5 and README wording present. |
| A5 Code | Pass. Plain pandas + openpyxl, markdown per step (346 code lines). No `src/` helper was created, which is fine. |
| A6 Scope | Pass. Only the 4 allowed files are new; `docs/` edits are mine (D07). |

## Independent spot checks

8 random rows from `sales_long.csv` traced by `source_file` + `source_row` back to the raw workbook:
labels (ring, LGA, dwelling type), median ($'000 × 1,000) and count all match. This includes
Blue Mountains unit Mar 2019 with count `s` → empty + `suppressed_30_or_fewer`.

## Extra check: are the "revisions" real?

Codex inferred revisions from the **quarterly** change column (K). I cross-checked with the **annual**
change column (L), which gives a second, independent back-calculation of the same quarter a year later.

| Scope | Revision after 1 quarter (median) | Revision after 4 quarters (median) | K-based vs L-based estimate agree to (median abs.) |
|---|---|---|---|
| LGA houses | +0.52% | +0.65% | 0.13% |
| LGA units | +0.11% | +0.69% | 0.29% |
| Greater Sydney houses | +1.85% | +1.83% | 0.16% |
| Greater Sydney units | +0.45% | +0.61% | 0.20% |

**Conclusion:** the two methods agree, so the revisions are real DCJ revisions, not a calculation
artefact. First-published medians are **systematically a little low** (late-notified sales). For most
LGAs it's < 1%, but **Woollahra houses** are revised up 7–45% in recent quarters (few, very expensive
sales arrive late).

**Effect on D06:** because *both* ends of the growth calculation (2019 and the latest 4 quarters) use
first-published values, the systematic part mostly cancels in the growth ratio. D06 (a) stays as the
main method. But Woollahra-type noise doesn't cancel, so:
- T04 adds the raw change columns K and L to `sales_long.csv`.
- T05 builds a **revised-estimate** series in SQL with window functions (`LEAD(..., 4)`).
- T07 reports growth on both series and lists any LGA whose rank moves by more than 3 places
  (sensitivity check). This goes in the README as a rigour point.

## Notes carried forward

1. Large one-quarter jumps (Willoughby units +47%, Woollahra houses ±38%) are composition effects. The
   4-quarter averaging in the growth definition is the right protection; mention it in Limitations.
2. `low_sales_flag` is true for 146 LGA rows, mostly units. T07 should report how many of the
   8 baseline + latest quarters per LGA are flagged.
