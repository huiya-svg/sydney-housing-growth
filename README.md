# Sydney Housing Price Growth (2019 – latest)

> **Status: work in progress.** Sections marked _TBD_ are filled in as the project advances.

**Answer:** _TBD — one sentence with the headline number, e.g. "Houses in [LGA] grew X% since 2019, against Y% for Greater Sydney."_

_TBD — screenshot of Power BI report page 1 (`powerbi/page1.png`)._

## Question

Which Greater Sydney LGAs have had the fastest median house and unit price growth since 2019,
and what do the fastest-growing areas have in common?

## Key findings

1. _TBD_
2. _TBD_
3. _TBD_

## Data sources

| Dataset | Source | Licence | As of |
|---|---|---|---|
| Median sales price and number of sales by LGA (strata / non-strata) | NSW DCJ Rent and Sales Report | _TBD_ | _TBD_ |

Screening of every candidate dataset, including the rejects: [`docs/data_sources.md`](docs/data_sources.md).

## Method

_TBD — 5–6 bullets: cleaning, SQL, growth definition, correlation tests, Power BI star schema, cross-check._

## Limitations

_TBD — ~33 LGAs, medians not averaged across areas, nominal vs real prices, correlation ≠ cause, data lag._

## How to reproduce

```bash
uv venv --python 3.12 .venv
uv pip install -r requirements.txt
# then run notebooks/01_explore.ipynb → 02_clean.ipynb → 03_analysis.ipynb in order
```

## Repo structure

```
data/raw/          original downloads (+ MANIFEST.csv with source, date, sha256)
data/reference/    lookup tables (LGA list, regions)
data/processed/    clean CSVs that feed Power BI
notebooks/         01_explore, 02_clean, 03_analysis
sql/               DuckDB SQL used in cleaning
powerbi/           report screenshots + PDF export
docs/              data sources, data dictionary, decisions log
```

## Tools used

Python (pandas, DuckDB, SciPy, Matplotlib/Seaborn), SQL, Power BI service, Git/GitHub.
AI assistance: Claude (task planning and code review) and OpenAI Codex (implementation under review).
All decisions, DAX measures and findings are my own and checked by me.
