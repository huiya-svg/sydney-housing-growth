# T06 — Data dictionary for every processed column

**Phase:** 2 (deferred to after T08) · **Implementer:** Codex · **Reviewer:** Claude · **Owner:** Kang
**Read first:** `AGENTS.md`, `docs/data_dictionary.md` (stub), `sql/transform.sql`, `notebooks/02_clean.ipynb`
(steps 1–15), `notebooks/03_analysis.ipynb` (Part B), `docs/decisions.md`, `docs/data_sources.md`,
`data/raw/MANIFEST.csv`.

## Context

Every column now exists in its final form. A recruiter (or Kang in an interview) must be able to open one file and
learn, for any column in `data/processed/`, what it means, its unit, where it comes from and when it's blank.
This is documentation only: **no code, data or notebook changes.**

## Scope

Rewrite `docs/data_dictionary.md` with these sections:

1. **Intro (3–5 lines).** What the five tables are, how they join (star schema: `dim_lga`, `dim_date` and the Power BI
   table `dim_dwelling` → `fact_sales` and `lga_growth`), and the conventions: `quarter_date` = first day of the
   quarter, prices in AUD (not $'000), growth as a decimal fraction (0.67 = 67%), blank = missing, never 0.
2. **One section per CSV**, in this order: `fact_sales`, `lga_growth`, `dim_lga`, `dim_date`, `factor_tests`. Each
   starts with its grain (one row per …), its row count and its key columns, then a table:

   | Column | Type | Unit | Meaning | Source / derivation | Blank when |
   |---|---|---|---|---|---|

   - **Type**: text / date / integer / decimal / boolean, as written in the CSV.
   - **Meaning**: one plain-English sentence.
   - **Source / derivation**: the raw source (DCJ sheet `LGA`, ABS ERP table, Census G02, CPI A2325806K, …, matching
     `data_sources.md` names), or the formula/rule, with the SQL step or notebook step it comes from. Cite decisions
     where relevant (e.g. "D06 first-published", "D08 revised estimate", "D05").
   - **Blank when**: the actual rule (e.g. "DCJ suppressed (≤ 10 sales)", "not all 4 baseline quarters published",
     "non-LGA rows"). Write "never" if the column is never blank, and **verify this against the CSV**.
3. **`dim_dwelling`** (Power BI only, entered by hand): 2 rows, 2 columns.
4. **Glossary (short):** median, strata/non-strata, DCJ rings, first-published vs revised estimate, real growth,
   Spearman ρ, Holm p.

## Rules

- Every column in every `data/processed/*.csv` appears **exactly once** under its table, in the CSV's column order.
- Definitions must match the code. Read the SQL/notebook rather than guessing; if the code and an earlier spec
  disagree, document the **code** and mention the difference in the report.
- Plain English, short sentences. No marketing words.

## Out of scope

Any change outside `docs/data_dictionary.md`. README (T11). Interim and raw files: list them only in one closing line
pointing to `data/raw/MANIFEST.csv`.

## Allowed files

- `docs/data_dictionary.md`
- `tasks/reports/T06_report.md`

## Questions to answer in the report

- **Q1.** A coverage check: a short script output listing, per CSV, the columns found in the CSV vs documented
  (they must match exactly, in order).
- **Q2.** The "Blank when" verification: for each column with blanks, the blank count in the CSV and the rule that
  explains every one of them.
- **Q3.** Any place where code and earlier specs disagree.

## Acceptance criteria

- [ ] A1 All columns of all 5 CSVs documented once, in CSV order (Claude re-runs the coverage check).
- [ ] A2 Spot-checked definitions match `sql/transform.sql` and the notebooks; blank rules match actual blank counts.
- [ ] A3 Only allowed files changed; no git commands.

## Kang's part (after review)

Pick any 5 columns at random and explain each one out loud without looking. If you can't, that's the column to study.
