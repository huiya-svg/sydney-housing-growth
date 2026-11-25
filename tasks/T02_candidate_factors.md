# T02 — Candidate "why" factors: find, download, first look, screen

**Phase:** 1 · **Implementer:** Codex · **Reviewer:** Claude · **Owner:** Kang
**Read first:** `AGENTS.md`, `docs/project_plan.md` (Phase 1 and Phase 3B), `docs/data_sources.md`,
`tasks/reviews/T01_review.md` (note 3 is fixed in this task).

## Context

T01 gave us the core sales data (29 DCJ workbooks, Mar 2019 – Mar 2026, 34 DCJ Greater Sydney LGAs).
Now we look for factors that might explain *why* some LGAs grew faster. The plan says 2–3 well-tested
factors beat 10 untested ones, so this task **finds, documents and screens** candidates. Kang then picks
which factors go forward (decision D07). No cleaning or joining happens here.

The screening is the point of this task. For each candidate, answer the four checks in
`docs/data_sources.md`. Check 3 (timing) matters most: a factor measured **at or before 2019** can be a
plausible driver. A factor measured **during 2019–2026** may be a result of price growth, so flag it
as "concurrent".

## Candidates (in this order)

| # | Candidate | Where to look (official sources only) | Proposed factor definition(s) |
|---|---|---|---|
| C1 | 2019 price level | Already in our DCJ sales data, so no download | 2019 average median price per LGA and dwelling type (the "catch-up" hypothesis) |
| C2 | Median weekly rent | DCJ Rent and Sales Report **rent tables**, the same pages as T01 | 2019 median rent; **2019 gross rental yield** = rent × 52 / 2019 price |
| C3 | Population | ABS Regional Population, estimated resident population (ERP) by LGA | Pre-period growth 2016→2019 %; concurrent growth 2019→latest % (flag) |
| C4 | Median household income | ABS Census DataPacks, General Community Profile, table G02, LGA level | 2016 Census (pre-period) and 2021 Census (mid-period, flag). Get both if practical. |
| C5 | Distance to Sydney CBD | ABS ASGS LGA digital boundaries (the edition matching our LGA names) | Straight-line km from the LGA centroid to the Sydney GPO |
| C6 | New dwelling supply | NSW Housing Evidence Centre (dwelling completions by LGA) **or** ABS Building Approvals by LGA | Pre-period supply 2016–2019 per 1,000 existing dwellings; concurrent supply (flag) |
| C7 | CPI | ABS CPI, Sydney All groups, quarterly | Context and deflator for real growth only. Not a factor (same everywhere). |
| C8 | RBA cash rate | RBA statistical table (cash rate target) | Timeline overlay only. Not a factor. |
| C9 | Individual property sales | NSW Valuer General bulk sales | **Do not download.** Record as "not pursued" with the reason. |

## Scope

1. For C2–C8: find the official source, download the smallest set of original files that covers the
   factor definition, record provenance, and take a first look.
2. Extend `scripts/download_data.py` to cover the new files, and fix T01 review note 3: for files already
   on disk, **verify** the hash against the manifest and print a clear warning on mismatch (don't overwrite).
3. Add a "Part B — candidate factors" to `notebooks/01_explore.ipynb`, one section per candidate.
4. Fill every candidate row in `docs/data_sources.md`, including C1, C8 and C9.
5. Recommend which 2–3 factors to test, but **do not decide**. That's D07 for Kang.

## Out of scope

- Cleaning, reshaping or joining. Writing anything to `data/processed/` or `data/reference/`.
- Building an LGA name-mapping table. **Report** the mismatches here; T03 builds the table.
- Computing correlations or growth. Using any address-level data.
- Rent tables for all 29 quarters. 2019 (four quarters) is enough for the baseline factor. Add the latest
  four quarters only if it's cheap, and label them context.

## Allowed files

- `data/raw/<source>/**` for new sources (e.g. `dcj_rent/`, `abs_erp/`, `abs_census/`, `abs_asgs/`,
  `supply/`, `abs_cpi/`, `rba/`), `data/raw/_archives/**` (files > 25 MB, gitignored),
  `data/raw/MANIFEST.csv`, `data/raw/README.md`
- `scripts/download_data.py`
- `notebooks/01_explore.ipynb` (append Part B; **do not change Part A's logic**. Retitling the top
  cell to cover both parts is fine.)
- `docs/data_sources.md`
- `requirements.txt` (only if a new package is genuinely needed. Prefer DuckDB's `spatial` extension or
  plain pandas over adding geopandas, and justify any addition.)
- `tasks/reports/T02_report.md`

## Rules specific to this task

- **Large files:** keep archives over 25 MB in `data/raw/_archives/` with a manifest row. Extract only the
  member files we need, byte-for-byte, into `data/raw/<source>/` and give each extracted file its own
  manifest row. Note the archive it came from in `source_url` or `data/raw/README.md`.
- **Boundary editions:** ABS releases use ASGS LGA editions (2016, 2021, 2024/2025). Record which edition
  each file uses. Check whether any of the 34 DCJ Sydney LGAs changed boundary or name between the
  editions involved.
- **Name matching:** for each source, list which of the 34 DCJ Sydney LGA labels match exactly and which
  don't (e.g. "Sutherland Shire" vs "Sutherland"). Report the mismatches; don't fix them.
- **Distance:** use the official boundary file and compute the centroid. Record the GPO coordinates
  you used and their source. Large outer LGAs (Central Coast, Hawkesbury, Blue Mountains, Wollondilly)
  have geometric centroids far from where people live. Show their centroid coordinates and say whether
  a population-weighted alternative is feasible from official data. Don't build it.
- If a source blocks scripted download, write the manual steps in `data/raw/README.md` and continue.

## Notebook Part B: one section per candidate (C2–C8)

Each section has a markdown cell in plain English, then:
- files used, row count, the relevant columns and their units;
- years or quarters covered, and the geography level and edition;
- coverage of the 34 DCJ Sydney LGAs (matched, unmatched, missing values);
- a small preview of the proposed factor's raw values for 3 Sydney LGAs (e.g. Blacktown, Sydney,
  Wollondilly). These are just values, with no cleaning pipeline.

Must pass: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_explore.ipynb`.

## Questions to answer in the report

- **Q1.** For each candidate C2–C8: source page URL, file(s), licence, as-of / release date, geography
  level and edition, time coverage.
- **Q2.** The four screening checks for every candidate C1–C9, with a one-line reason each.
- **Q3.** Name matching. Per source, how many of the 34 DCJ Sydney LGAs match exactly, and the list of
  mismatches with the source's spelling.
- **Q4.** Boundary or name changes affecting the 34 LGAs across the editions used. "None found" needs
  the evidence you checked.
- **Q5.** Distance: centroid method, GPO coordinates and source, centroids for the four large outer LGAs,
  and whether a population-weighted centroid is feasible.
- **Q6.** Supply: which source you chose and why, what it measures (approvals vs completions), and the
  years available.
- **Q7.** Which pairs of candidates are likely proxies for each other (e.g. distance vs 2019 price,
  income vs 2019 price)? Reason only, with no correlation computed yet.
- **Q8.** Your recommended 2–3 factors for testing (plus 2019 price level, if you think it should be
  included), with reasons. Put this under *Decisions needed* as D07 with options.

## Acceptance criteria

- [ ] A1 Every new raw file has a manifest row; hashes match; nothing over 25 MB outside `data/raw/_archives/`.
- [ ] A2 `download_data.py` reruns without re-downloading, leaves the manifest byte-identical, and prints a
      warning (without changing the manifest) when a file's hash doesn't match. Demonstrate this on a
      **temporary copy**, never by editing a real raw file.
- [ ] A3 `01_explore.ipynb` executes top to bottom with no errors. Part A outputs are unchanged in substance.
- [ ] A4 Every candidate row C1–C9 in `docs/data_sources.md` is filled: source, licence, the 4 checks, verdict.
- [ ] A5 The report answers Q1–Q8 with evidence; D07 is listed with options and is **not** decided.
- [ ] A6 No files outside the allowed list; no git commands; no address-level data.

## Kang's part (after review)

1. Read the screening table in `docs/data_sources.md`. For one accepted and one rejected candidate, be
   ready to explain *why* in one sentence (interview practice).
2. Decide **D07**: which 2–3 factors go into the analysis. Record it in `docs/decisions.md`.
3. Commit after Claude's review says Accept.
