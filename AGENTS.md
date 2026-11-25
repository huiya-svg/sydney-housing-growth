# AGENTS.md — instructions for Codex (and any coding agent)

Read this file in full before every task. The full project plan is in `docs/project_plan.md`.

## The project in one line

Which Greater Sydney LGAs have had the fastest median **house** and **unit** price growth since 2019,
and what do the fastest-growing areas have in common? Public data only. Python (pandas) + DuckDB SQL
do the data work; Power BI (browser) does the model and report; GitHub publishes it.

## Roles

| Who | Role |
|---|---|
| **Kang Liang** (owner) | Makes every decision, reviews every step, writes the DAX, makes every git commit. This is Kang's portfolio project. |
| **Claude** (commander / reviewer) | Writes one task spec at a time in `tasks/TNN_*.md`, reviews each submission, writes verdicts in `tasks/reviews/`. |
| **Codex** (implementer) | Carries out exactly one task spec, then writes a submission report in `tasks/reports/TNN_report.md`. |

## Hard rules

1. **One task at a time.** Do only what the current task file asks. Do not start the next phase, add
   datasets, or "improve" files outside the task's allowed-files list. If something outside scope
   looks wrong, mention it in the report instead of fixing it.
2. **No git operations.** Never run `git commit`, `git push`, `git add`, `git config`, branch or reset.
   Kang commits after review. Suggest commit messages in the report instead.
3. **No address-level data in the repo.** Individual property sales (one row per sale) may only live in
   `data/raw/private/` (gitignored) and only if a task asks for it. No passwords, keys or tokens anywhere.
4. **Raw data is read-only.** Files in `data/raw/` are saved exactly as downloaded, with their original
   filenames, and never edited. Record each in `data/raw/MANIFEST.csv`
   (`filename, source_url, downloaded_on, sha256, bytes, licence`).
   Archives or files over 25 MB go in `data/raw/_archives/` (gitignored, still in the manifest); the
   specific member files we use are extracted byte-for-byte next to them under `data/raw/<source>/`.
5. **Missing stays missing.** Blank or suppressed values become `NaN`/`NULL`, never `0`.
6. **Never mix houses and units.** Every price figure is per dwelling type
   (`house` = non-strata, `unit` = strata).
7. **Never average medians across LGAs.** For Greater Sydney, use the published aggregate row.
8. **Code the owner can explain.** Plain pandas and SQL, small functions, descriptive names, comments
   that explain *why*. No clever one-liners, no unnecessary libraries. Kang will be asked about this
   code in interviews.
9. **Notebooks run top to bottom** with
   `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/<name>.ipynb`.
   Each step gets a short markdown cell in plain English: what we do and why.
10. **SQL lives in `sql/*.sql`** and is executed from notebooks with DuckDB. Only trivial one-line
    queries may be inline.
11. **Relative paths only** (`pathlib.Path`, from the repo root). No absolute paths, no user names.
12. **Don't guess on data or method choices.** If a choice changes results (which LGAs, which quarter,
    how to treat a gap), pick nothing: list it under *Decisions needed* in the report.
13. **Report honestly.** If a command fails or a check was skipped, say so with the error text.

## Conventions

- Column names: `snake_case`. Dates: `quarter_date` = first day of the quarter (e.g. `2019-01-01` for Mar Q 2019).
- `dwelling_type` values: `house`, `unit`. LGA names: one canonical spelling, held in `data/reference/`.
- CSV output: UTF-8, comma-separated, header row, no index column.
- Python 3.12 virtual environment in `.venv/`, created with `uv`. Install with
  `uv pip install -r requirements.txt`. If `uv` cannot write its cache in the sandbox, use
  `UV_CACHE_DIR=.uv-cache` (gitignored).

## Folder map

```
data/raw/          original downloads (read-only) + MANIFEST.csv
data/reference/    small hand-made lookup tables (LGA list, regions, name mappings)
data/processed/    clean CSVs that feed Power BI
notebooks/         01_explore, 02_clean, 03_analysis
sql/               transform.sql and other DuckDB queries
scripts/           download_data.py and other runnable scripts
src/               small helper modules imported by notebooks (optional)
powerbi/           screenshots + PDF export of the report
docs/              project_plan, data_sources (screening), data_dictionary, decisions, workflow
tasks/             task specs (TNN_*.md), reports/ (Codex), reviews/ (Claude)
```

## Submission report template (`tasks/reports/TNN_report.md`)

```markdown
# TNN report — <task title>

## Summary
3–5 sentences: what was done and the most important finding.

## Files created or changed
- path — one line on what it is

## Commands run
Each command and its result (pass/fail, key output lines).

## Answers to the task questions
Q1 … QN, each answered directly with evidence (sheet/cell, row counts, URLs).

## Acceptance checks
| Check | Pass/Fail | Evidence |

## Decisions needed (for Kang)
Numbered, each with the options and the trade-off. Write "None" if none.

## Issues and risks
Anything odd in the data, anything skipped, anything out of scope you noticed.

## Suggested commit message(s)
One or more conventional, imperative messages Kang can use.
```
