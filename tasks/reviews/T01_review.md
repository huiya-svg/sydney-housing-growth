# T01 review — Python environment + core DCJ sales data

**Verdict: Accept** · Reviewer: Claude · 2026-11-25

## What I re-ran myself

| Check | Result |
|---|---|
| A1 Python + imports | Pass. Python 3.12.14; pandas 3.1.1, duckdb 2.0.1 and the rest import; 10 `==` pins. |
| A2 Raw files vs manifest | Pass. 29 files, 29 manifest rows, 0 hash mismatches, no unlisted files. |
| A3 Download script rerun | Pass. "29/29 present", `MANIFEST.csv` byte-identical after rerun. |
| A4 Notebook executes | Pass. Re-executed to a scratch copy with nbconvert: 18 cells, 8 code, 0 errors, ~15 s. Reads only `data/raw/`; no writes. |
| A5 Plain-English steps | Pass. Each code cell has a markdown explanation. |
| A6 Docs | Pass. Core row in `docs/data_sources.md`, `data/raw/README.md` with attribution. |
| A7 Report | Pass. Template followed; Q1–Q8 answered with cell-level evidence. |
| A8 Scope | Pass. `git status` shows only allowed paths; no git commands. |

## Independent spot checks (openpyxl, straight from the workbooks)

| Workbook | Cell | Value | Row labels | Matches report |
|---|---|---|---|---|
| Mar 2026 | G1865 | 1250 | Outer Ring / Blacktown / Non Strata | ✅ |
| Mar 2026 | G1815 | 967 | Inner Ring / Sydney / Strata | ✅ |
| Mar 2026 | J1851 | 835 | Middle Ring / Parramatta / Strata | ✅ |
| Mar 2026 | G1691 / G1692 | 1550 / 855 | Greater Sydney Total, Non Strata / Strata | ✅ |
| Mar 2026 | G1884, J1884 | 808, `s` | Hawkesbury / Strata (price published, count suppressed) | ✅ |
| Mar 2019 / Dec 2019 | G1863 / G1885 | `-` / `-` | Wollondilly / Strata | ✅ |
| Dec 2025 | J1823 | `1,265` | Sydney / Strata (revision example) | ✅ |

## Notes carried forward (not blocking)

1. **Numbers are stored as text** in newer workbooks (`'1250'`, `'1,265'`) and prices are in **$'000**.
   T03 must strip commas, convert to numbers and multiply prices by 1,000.
2. **Revisions.** Each workbook gives one quarter as first published; later issues revise the
   previous quarter (Sydney strata Dec 2025 count: 1,265 first published vs ~1,301 implied later).
   T03 should measure how big revisions are for *medians* using the quarterly-change column,
   so the README can state it. Proposed default: use first-published values (decision D06).
3. **`download_data.py` recomputes hashes of existing files instead of verifying them.** If a raw file
   were ever changed, the manifest would silently update. Fixed in T02 (verify and warn).
4. **Notebook density.** Sections 2 (regex for quarter captions) and 7 (MultiIndex for missing keys)
   are the hardest to explain. Kang should read these two closely and ask about anything unclear.

## Decisions raised for Kang (see `docs/decisions.md`)

- **D04** Greater Sydney boundary — recommendation: DCJ's 34 LGAs.
- **D05** Wollondilly units have no 2019 baseline — recommendation: exclude from unit rankings only.
- **D06** First-published vs revised values — recommendation: first-published, revision size reported.
