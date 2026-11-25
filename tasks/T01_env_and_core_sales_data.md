# T01 — Python environment + core DCJ sales data: download and first look

**Phase:** 0–1 · **Implementer:** Codex · **Reviewer:** Claude · **Owner:** Kang
**Read first:** `AGENTS.md` (hard rules + report template), `docs/project_plan.md` (Phase 1 and 2.1).

## Context

The whole project rests on one core dataset: the **NSW Department of Communities and Justice (DCJ)
Rent and Sales Report** — median sales price and number of sales by LGA, quarterly, split into
strata (units) and non-strata (houses). Before we clean anything, we need the environment working,
the right raw files on disk with a clear record of where they came from, and an honest first look at
their structure. This task produces no clean data — only facts about the raw data.

## Scope

1. Create the Python environment.
2. Find and download the DCJ sales tables covering **Mar quarter 2019 → the latest published quarter**,
   by LGA, strata and non-strata.
3. Record provenance (manifest + data sources row) and make the download reproducible.
4. Build `notebooks/01_explore.ipynb` for the core sales data only.
5. Answer the questions below in the report.

## Out of scope (do not do)

- Rent data, population, income, distance, supply, CPI or any other dataset (that is T02).
- Reshaping, cleaning, or writing anything to `data/processed/` (that is T03).
- Building the Greater Sydney LGA list or regions in `data/reference/` (T03 — after Kang decides D04).
- Any git operation.

## Allowed files (create or edit only these)

- `.venv/`, `.uv-cache/`
- `requirements.txt`
- `data/raw/dcj_sales/**` (downloads, unchanged), `data/raw/MANIFEST.csv`, `data/raw/README.md`
- `scripts/download_data.py`
- `notebooks/01_explore.ipynb`
- `src/*.py` (only if a helper genuinely makes the notebook clearer)
- `docs/data_sources.md` — the **Core** row only
- `tasks/reports/T01_report.md`

## Steps

### 1. Environment
- `uv venv --python 3.12 .venv`, then `uv pip install -r requirements.txt` (use `UV_CACHE_DIR=.uv-cache` if needed).
- Replace `requirements.txt` with pinned versions (`package==x.y.z`) of the **top-level** packages only
  (the ten listed now, plus any you genuinely needed, e.g. `xlrd` for old `.xls` files — say why in the report).
- Check: `.venv/bin/python -c "import pandas, duckdb, scipy, matplotlib, seaborn, openpyxl, requests"`.

### 2. Find the right files
- Start from the official DCJ site (`dcj.nsw.gov.au`; older issues may sit on `facs.nsw.gov.au`).
  Use only official NSW Government domains.
- Work out how the sales data is published: one workbook per quarterly issue (each holding only that
  quarter), or a back-series / historical file holding many quarters. **Prefer a single official
  back-series file if one exists.** Otherwise download every issue needed to cover Mar Q 2019 → latest.
- Note the licence stated on the page (name only, e.g. "CC BY 4.0") and the release date of the latest issue.

### 3. Download reproducibly
- Save files under `data/raw/dcj_sales/` with their **original filenames**, unchanged.
- Write `scripts/download_data.py` (requests + pathlib, plain and readable): a list of
  `(url, filename)` pairs, download any missing file, compute sha256, and (re)write the DCJ rows of
  `data/raw/MANIFEST.csv` with columns `filename, source_url, downloaded_on, sha256, bytes, licence`.
  Running it twice must not re-download existing files.
- If a file cannot be fetched by script (blocked, needs a click-through), do not work around it:
  write the exact page URL and manual steps in `data/raw/README.md`, list it under *Decisions needed*,
  and continue with what you have.
- `data/raw/README.md`: 5–10 lines — what is in `data/raw/`, how to re-download, that raw files are never edited.

### 4. `notebooks/01_explore.ipynb` (core sales only)
Plain-English markdown cell before each step. Read only from `data/raw/`. Sections:
1. **Files** — list of raw files with size and sheet names.
2. **Layout** — for one representative workbook: header row position, column names, wide vs long,
   where dwelling type (strata / non-strata / total) is encoded, what measures exist
   (median, count, mean?, quarterly / annual change?).
3. **Load** — load the LGA-level sales table(s) into a raw DataFrame (no cleaning beyond what is
   needed to read it); show `shape`, `dtypes`, `head()`.
4. **Coverage** — quarters covered (first, last, any gaps) and number of distinct geography rows.
5. **Geography labels** — every distinct geography label; which are LGAs vs aggregates
   (e.g. Greater Sydney, Inner / Middle / Outer Ring, Rest of NSW); any spelling variants across issues.
6. **Missing and suppressed values** — every non-numeric marker in price and count columns
   (e.g. `-`, `s`, `n.a.`, blank) with counts, overall and for rows in DCJ's Sydney grouping.
7. **Small samples** — distribution of sales counts per LGA-quarter for the Sydney grouping;
   how many LGA-quarter-type cells have < 30 sales.
8. **Spot-check candidates** — 3 specific values (LGA, quarter, dwelling type, value) with their
   exact location in the raw file (file, sheet, cell), for Kang to verify by hand.

Must pass: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_explore.ipynb`
with outputs saved in the notebook.

### 5. Data sources row
Fill the **Core** row in `docs/data_sources.md`: source URL, licence, geography/time actually found,
checks 1 and 4, notes (issue numbers, latest quarter).

## Questions to answer in the report

- **Q1.** Source page URL(s), file URL(s), issue number(s), latest quarter covered, release date of
  the latest issue, licence.
- **Q2.** One back-series file or one file per quarter? How many files cover Mar Q 2019 → latest, and
  were all downloaded? Any quarters missing?
- **Q3.** Layout: sheets, header rows, wide or long, how dwelling type is encoded, which measures exist.
- **Q4.** Missing / suppressed markers, their meaning per DCJ's notes (quote the note's wording
  briefly or paraphrase), and how often they occur in the Sydney grouping.
- **Q5.** Geography: number of distinct LGAs; which aggregate rows exist; does DCJ group Sydney LGAs
  into Inner / Middle / Outer Ring; any LGA name variants across issues.
- **Q6.** By DCJ's own grouping, how many LGAs are in Greater Sydney, and are Central Coast,
  Blue Mountains, Hawkesbury and Wollondilly included? (Input for Kang's decision D04.)
- **Q7.** The 3 spot-check values with file / sheet / cell.
- **Q8.** Anything surprising or risky: breaks in series, revised figures between issues, methodology
  changes, units of the price (dollars vs $'000).

## Acceptance criteria (Claude will check each)

- [ ] A1 `.venv` on Python 3.12; import check passes; `requirements.txt` pinned with `==`.
- [ ] A2 Raw files in `data/raw/dcj_sales/` with original names; every file has a `MANIFEST.csv` row whose
      sha256 matches the file on disk.
- [ ] A3 `scripts/download_data.py` runs a second time without re-downloading and leaves the manifest unchanged
      (except `downloaded_on` must **not** change for existing files).
- [ ] A4 `01_explore.ipynb` executes top to bottom via nbconvert with no errors; outputs saved; reads only
      `data/raw/`; writes nothing to `data/processed/`.
- [ ] A5 Every notebook step has a plain-English markdown cell; code is simple enough to explain in an interview.
- [ ] A6 Core row in `docs/data_sources.md` filled; `data/raw/README.md` written.
- [ ] A7 `tasks/reports/T01_report.md` follows the AGENTS.md template and answers Q1–Q8 with evidence.
- [ ] A8 No files changed outside the allowed list; no git commands run.

## Kang's part (after Codex, before commit)

1. Open the latest raw workbook in Excel and confirm the 3 spot-check values from Q7 yourself.
2. Read `01_explore.ipynb` top to bottom; note anything you could not explain and ask Claude.
3. Decide **D04** (which LGAs count as Greater Sydney) using Q5–Q6, and record it in `docs/decisions.md`.
4. Commit using the message suggested in the report (after Claude's review says Accept).
