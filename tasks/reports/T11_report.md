# T11 report — README write-up and final checks

## Summary

Rewrote the README in the requested order, preserving the three confirmed findings word for word. The leading LGAs were Fairfield for houses at 83.0% and Hawkesbury for units at 58.8%. All three notebooks completed in order, and the replay produced byte-identical copies of all 72 data files. Only the two house PNGs changed, and all 18 distinct README link targets resolved.

## Files created or changed

- `README.md` — portfolio introduction, four report pages, findings, sources, method, limitations and reproduction instructions.
- `notebooks/03_analysis.ipynb` — confirmed house scatter title and a shared Woollahra footnote in the two house plots. The notebook includes the refreshed outputs.
- `docs/figures/factor_scatter_house.png` — regenerated house scatter with the confirmed title and the footnote.
- `docs/figures/growth_by_lga_house.png` — regenerated house ranking with the footnote.
- `docs/data_sources.md` — C1 Notes cell now describes the four-quarter average used for `price_2019`.
- `docs/project_plan.md` — line 77 now names `pop_growth_2016_19` and `income_2016_weekly`.
- `tasks/reports/T11_report.md` — submission and check evidence.

## Commands run

### Notebook replay and data

I copied the notebook inputs and outputs into a temporary directory and used the repository virtual environment to run the commands below in order. This gave `--inplace` a writable copy of each notebook and left the repository versions of 01 and 02 intact. I copied back the executed 03 notebook and the two changed PNGs after verifying the data hashes.

| Command | Result | Elapsed |
|---|---|---:|
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_explore.ipynb` | Pass. 17 code cells executed, 0 error outputs. Wrote 231,416 bytes. | 57.84 s |
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_clean.ipynb` | Pass. 22 code cells executed, 0 error outputs. Wrote 206,871 bytes. | 29.08 s |
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/03_analysis.ipynb` | Pass. 19 code cells executed, 0 error outputs. Wrote 1,013,739 bytes. | 11.96 s |
| Python SHA-256 inventory keyed by path, before and after replay | Pass. `Data files compared by SHA-256: 72; changes: []`. The working copy's data hashes also matched the pre-run inventory. |
| `git --no-optional-locks status --short data/` | Pass. Empty output. |
| Python `nbformat.validate` and cell-source comparison | Pass. Only the plotting cells at zero-based indices 11 and 33 changed source. Both show their two plot outputs. |
| Visual inspection of both regenerated PNGs | Pass. The confirmed title fits on two lines and the computed footnote is legible in small grey text at the bottom of both figures. |

Jupyter issued its startup warning `Kernel is running over TCP without encryption` on the local executions. Each run exited successfully.

### SQL and Power BI files

- `nl -ba sql/transform.sql` confirmed the `lga_rows` CTE at line 79, `ROW_NUMBER() OVER (...)` at line 84 and the factor `LEFT JOIN` at lines 88–94. The final growth tables also use `RANK() OVER (...)` at lines 180 and 188.
- `ls -1 powerbi/` returned the following files. A PDF object check found four pages, zero link annotations and zero URI actions. The screenshots, PDF and PBIX are all tracked.

```text
crosscheck.png
model_view.png
page1_answer.png
page2_trends.png
page3_why.png
page4_notes.png
sydney_housing.pbix
sydney_housing_report.pdf
sydney_theme.json
```

### README links

I ran this with `python3 -c` from the repository root.

```python
import re
from pathlib import Path

readme = Path('README.md').read_text(encoding='utf-8')
paths = [p for p in re.findall(r'!?\[[^\]\n]*\]\(([^()\s]+)\)', readme)
         if not p.startswith(('https://', 'http://'))]
for p in paths:
    print(f'{p}: {"OK" if Path(p).is_file() else "MISSING"}')
assert all(Path(p).is_file() for p in paths)
print(f'{len(paths)} relative links and image paths verified')
```

```text
powerbi/page1_answer.png: OK
powerbi/page2_trends.png: OK
powerbi/page3_why.png: OK
powerbi/page4_notes.png: OK
powerbi/sydney_housing_report.pdf: OK
docs/data_sources.md: OK
sql/transform.sql: OK
powerbi/crosscheck.png: OK
scripts/download_data.py: OK
powerbi/sydney_housing.pbix: OK
10 relative links and image paths verified
```

For each unique external target extracted from the same Markdown, I ran the following GET with redirect following. All eight returned `200`, zero redirects and curl exit code 0.

```bash
curl --location --silent --show-error --connect-timeout 10 --max-time 30 \
  --output /dev/null --write-out '%{http_code} %{num_redirects} %{url_effective}' "$url"
```

| External URL tested | HTTP |
|---|---:|
| [DCJ Rent and Sales Report](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/rent-and-sales-report.html) | 200 |
| [DCJ issue archive](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/previous-rent-and-sales-reports.html) | 200 |
| [ABS Regional Population](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25) | 200 |
| [ABS Census DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks) | 200 |
| [ABS Consumer Price Index](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/sep-2026) | 200 |
| [ABS LGA 2025 polygons](https://geo.abs.gov.au/arcgis/rest/services/Hosted/LGA_Regional_Population_2025/FeatureServer/1) | 200 |
| [Heritage NSW State Heritage Register](https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/HMS/Heritage/MapServer/5) | 200 |
| [DCJ sales explanatory notes](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/explanatory-notes.html) | 200 |

### Address-level data check

I ran the following with `python3 -c`. It counts data rows, excluding the header, and checks case- and separator-normalised column names.

```python
import csv, re
from pathlib import Path

pattern = re.compile(r'street|address|propertyid|parcelid|lotnumber|dpnumber')
def normalise(column):
    return re.sub(r'[^a-z0-9]', '', column.lower())

root = Path('data')
excluded = {root / 'raw/_archives', root / 'raw/private'}
for path in sorted(root.rglob('*.csv')):
    if excluded.intersection(path.parents):
        continue
    with path.open(encoding='utf-8-sig', newline='') as file:
        rows = csv.reader(file)
        columns = next(rows)
        count = sum(1 for _ in rows)
    hits = [column for column in columns if pattern.search(normalise(column))]
    print(f'{path}: {count} rows, {len(columns)} columns, address-like columns={hits}')
    assert not hits, path
```

```text
data/interim/cpi_sydney.csv: 29 rows, 2 columns, address-like columns=[]
data/interim/lga_factors.csv: 34 rows, 11 columns, address-like columns=[]
data/interim/sales_long.csv: 2204 rows, 14 columns, address-like columns=[]
data/processed/dim_date.csv: 29 rows, 7 columns, address-like columns=[]
data/processed/dim_lga.csv: 38 rows, 10 columns, address-like columns=[]
data/processed/fact_sales.csv: 2204 rows, 10 columns, address-like columns=[]
data/processed/factor_tests.csv: 10 rows, 11 columns, address-like columns=[]
data/processed/lga_growth.csv: 76 rows, 21 columns, address-like columns=[]
data/raw/MANIFEST.csv: 55 rows, 6 columns, address-like columns=[]
data/raw/abs_asgs/CG_2022_LGA_2023_LGA.csv: 566 rows, 8 columns, address-like columns=[]
data/raw/abs_asgs/CG_LGA_2016_LGA_2021.csv: 585 rows, 8 columns, address-like columns=[]
data/raw/abs_asgs/CG_LGA_2020_LGA_2021.csv: 577 rows, 8 columns, address-like columns=[]
data/raw/abs_asgs/CG_LGA_2021_LGA_2022.csv: 567 rows, 8 columns, address-like columns=[]
data/raw/abs_asgs/CG_LGA_2023_LGA_2024.csv: 566 rows, 8 columns, address-like columns=[]
data/raw/abs_asgs/CG_LGA_2024_LGA_2025.csv: 567 rows, 8 columns, address-like columns=[]
data/raw/abs_census/2016Census_G02_NSW_LGA.csv: 132 rows, 9 columns, address-like columns=[]
data/raw/abs_census/2016Census_G32_NSW_LGA.csv: 132 rows, 37 columns, address-like columns=[]
data/raw/abs_census/2021Census_G02_NSW_LGA.csv: 131 rows, 9 columns, address-like columns=[]
data/reference/lga_lookup.csv: 34 rows, 4 columns, address-like columns=[]
```

All 19 audited CSVs passed. `source_file` and `source_row` in the interim sales data identify workbook rows containing published area aggregates. The raw sales inputs are DCJ aggregate workbooks. The raw GPO GeoJSON is one public landmark used as the distance reference.

### Secret and path checks

```bash
git --no-optional-locks grep -n -I -o -i -E 'api_key|apikey|token|password|secret|BEGIN .* PRIVATE KEY|sk-'
rg -n -o '(/Users/|C:\\Users|home/)' notebooks/ sql/ scripts/ src/
git --no-optional-locks grep -n -I -o -F \
  -e '/Users/' -e 'C:\Users' -e 'C:\\Users' -e 'home/' -- notebooks/ sql/ scripts/ src/
```

| Tracked hit | Explanation |
|---|---|
| `.gitignore:24` — `Secret` | Comment above the ignored environment and key-file patterns. |
| `AGENTS.md:27` — `password`, `token` | Terms in the repository rule prohibiting credentials. |
| `docs/project_plan.md:145` — `password` | Final checklist requirement. |
| `tasks/T11_readme_and_final_checks.md:159` — `secret` twice, `api_key`, `apikey`, `token`, `password`, `BEGIN .* PRIVATE KEY`, `sk-` | The task's search instruction and literal patterns. |
| `tasks/reports/T05_report.md:27` — `token` | The words `Unexpected token '<'` in an earlier JSON parsing error. |

Every hit was explanatory text. Both path searches had empty output and returned the normal no-match status. The tracked-file grep excluded binary files as requested by the text search. Power BI parameter privacy was previously confirmed by Kang in the [T10 review](../reviews/T10_review.md).

### Scope and command notes

- `git --no-optional-locks status --short` and `git --no-optional-locks diff --stat` showed the six allowed tracked changes above. The seventh path is this new report. `git --no-optional-locks diff --check` returned no findings. The doc diff showed one change in each specified location.
- The initial file lookup from the supplied home directory found no Git repository or task there. `rg --files` and directory inspection located the project under `Projects/Sydney Housing Price`. A sandboxed here-document probe failed with `cannot create temp file for here document: Operation not permitted`. Equivalent Python `-c` probes succeeded.
- The macOS Git launcher emitted `couldn't create cache file ... (errno=Operation not permitted)` inside the read-only sandbox. Invoking the installed Git binary directly made the read-only Git checks run without that launcher diagnostic.
- The first sandboxed curl attempt failed with `curl: (6) Could not resolve host: dcj.nsw.gov.au`. The network-enabled retry and the final README-driven check succeeded. `uv pip install --help` confirmed the documented `--python` option. I inspected the downloader without executing it to avoid changes to raw inputs.

## Answers to the task questions

### Q1. Where each README number comes from

CSV line numbers below include the header as line 1. I independently recalculated the eight percentages from quarterly prices in `data/processed/fact_sales.csv` and the window flags and `cpi_sydney` in `data/processed/dim_date.csv`. All eight matched the unrounded growth CSV values within floating-point tolerance and the README percentages at one decimal place.

| Number or period in README | Evidence |
|---|---|
| 2019–2026 project span and Mar 2019–Mar 2026 sales and CPI coverage | `data/processed/dim_date.csv` lines 2 and 30, `quarter_label`, `quarter_date` and `cpi_sydney`. Both dates mark the start of their quarters. |
| Greater Sydney house growth, 67.5% nominal and 34.9% real | `data/processed/lga_growth.csv` line 26, `growth_pct=0.6746955345060892` and `growth_pct_real=0.3491381006693337`. |
| Greater Sydney unit growth, 18.1% nominal and 4.8% real decline | Same CSV line 27, `growth_pct=0.1814360770577934` and `growth_pct_real=-0.0482327132172905`. |
| Fairfield house growth, 83.0%, and Hawkesbury unit growth, 58.8% | Same CSV lines 22 and 29, `growth_pct=0.8298090040927695` and `0.5878693623639191`, each with `growth_rank=1`. |
| Seven of the 10 leading house LGAs in the Middle Ring | Same CSV lines 4, 8, 14, 16, 20, 22, 38, 54, 56 and 60, selected where `dwelling_type=house` and `growth_rank` is 1–10. Seven have `region=Middle Ring`. |
| About 7–21 km from the CBD | `data/processed/dim_lga.csv`, range of `distance_km` over the LGA rows marked `Middle Ring`. Hunters Hill at line 20 is 6.94 km and Cumberland at line 15 is 20.67 km. These are centroid distances for the classified LGAs. |
| Five unit factors and two exploratory factors | `data/processed/factor_tests.csv` lines 7–11 have `dwelling_type=unit` and `verdict=no clear relationship`. Lines 5–6 and 10–11 identify the two exploratory factors for each dwelling type via `family`, `factor` and `p_holm`. The house price, household income and rent relationships appear at lines 4–6 in `rho` and `verdict`. The factor overlap is shown in `docs/figures/factor_correlation.png` and `tasks/reports/T08_report.md`. |
| 2019 rents, June 2016 and June 2019 ERP, 2016 Census G02, 2025 boundaries | `data/raw/MANIFEST.csv` lines 31–35, 48 and 38, `filename` and `source_url`. The ERP workbook uses June reference dates. `data/interim/lga_factors.csv` records `pop_2016`, `pop_2019`, `income_2016_weekly` and the 2019 rent columns. Scope follows D07 and the source notes C2–C5. |
| Sydney CPI series A2325806K, Table 17 | `data/raw/MANIFEST.csv` line 46 identifies `6401017.xlsx`. In that workbook, `Data1!B10` is the series ID. The published table number is in C7 of `docs/data_sources.md`. |
| All download dates (2026-11-25) and licence version numbers | `data/raw/MANIFEST.csv` lines in Q2, columns `downloaded_on` and `licence`. |
| Four baseline quarters and four latest quarters, Jun 2025–Mar 2026 | `data/processed/dim_date.csv` lines 2–5 have `is_baseline_2019=true`. Lines 27–30 have `is_latest_4q=true`. `quarter_label` runs from `2025 Q2` through `2026 Q1` in the latter window. |
| The two constants of 1 in the real-growth formula | `sql/transform.sql`, the `growth_pct_real` expression, consuming `growth_pct` and `cpi_ratio` from the same two windows. These are mathematical constants. |
| Zero Power BI differences | The recorded check in `powerbi/page4_notes.png` and `tasks/T10_powerbi_report_guide.md` line 354. `powerbi/crosscheck.png` shows the two growth columns matching on the visible house rows. This is a recorded Power BI result. |
| Woollahra house growth, 43.0% first published and 64.8% revised estimate | `data/processed/lga_growth.csv` line 76, `growth_pct=0.43019693654266966` and `growth_pct_rev=0.6477876106194691`. |
| Threshold of 30 sales and low-sales examples | `docs/data_dictionary.md` line 23 gives the published small-count marker rule, also documented in DCJ sales notes item 3. In `data/processed/lga_growth.csv`, lines 8, 29 and 33 show `baseline_low_sales_quarters` and `latest_low_sales_quarters` respectively as Burwood houses 3 and 0, Hawkesbury units 3 and 1, and Hunters Hill units 4 and 3. |
| Wollondilly units' missing 2019 baseline and 34 LGAs | `data/processed/lga_growth.csv` line 75 has `baseline_quarters=0` and blank `price_2019` and `growth_rank` for Wollondilly units. `data/processed/dim_lga.csv` has 34 rows with `geo_level=lga`. |
| Three months for initial reporting and six months for fuller notifications | The official methodology documents both timings. The repository records that the March 2026 sales tables were listed in the August 2026 release, in the core sales row of `docs/data_sources.md`. [DCJ sales explanatory notes, item 6](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/explanatory-notes.html) |
| Python 3.12, SHA-256, decision IDs D04/D05/D06/D07/D08/D09, notebook and report page numbers | Configuration, algorithm, decision and file identifiers. Confirmed in `AGENTS.md`, `scripts/download_data.py`, `docs/decisions.md` and the repository filenames. The installed Python was 3.12.14. |

### Q2. Licences

The following are the manifest line numbers and file keys checked. The README source links come from the core row and rows C2–C5 and C7 in `docs/data_sources.md`.

| Source | Licence | Manifest evidence |
|---|---|---|
| DCJ sales tables | CC BY 4.0 | Lines 2–30, all `dcj_sales/` entries. |
| DCJ rent tables | CC BY 4.0 | Lines 31–34, all `dcj_rent/` entries. |
| ABS Regional Population | CC BY 4.0 | Line 35, `abs_erp/32180DS0004_2001-25.xlsx`. |
| ABS Census 2016 G02 | CC BY 2.5 AU | Line 48, `abs_census/2016Census_G02_NSW_LGA.csv`. The enclosing 2016 DataPack at line 36 has the same licence. |
| ABS CPI Sydney | CC BY 4.0 | Line 46, `abs_cpi/6401017.xlsx`. |
| ABS ASGS 2025 LGA boundaries | CC BY 4.0 | Line 38, `abs_asgs/LGA_2025_Sydney_region.geojson`. |
| Heritage NSW GPO point | CC BY 4.0 | Line 39, `abs_asgs/Sydney_GPO_00763.geojson`. |

### Q3. Downloader and notebook dependencies

Yes. `scripts/download_data.py` verifies SHA-256 for **existing files with a manifest entry** before any fetch or extraction (lines 258–270 and 327–333). A mismatch stops the run. An absent file is fetched or extracted, then hashed and recorded (lines 273–324). The script does not compare a newly fetched file to a previously recorded hash for that missing file.

The script supplies the notebooks' external data files, including screening inputs such as the archived supply workbook and RBA data used by 01. `data/reference/lga_lookup.csv` is supplied by the repository. Both 01 and 02 execute `INSTALL spatial` and `LOAD spatial`. DuckDB downloads the extension if it is missing, so the first download can occur in 01 when following the README order. 03 reads the locally processed CSVs and fetches no external data.

### Q4. Figures changed by 03

Only `factor_scatter_house.png` and `growth_by_lga_house.png` changed. The bytes of `factor_correlation.png`, `factor_scatter_unit.png`, `growth_by_lga_unit.png` and `price_index_rings.png` matched their pre-run SHA-256 hashes. The plot helper reads `growth_pct` and `growth_pct_rev` from the existing Woollahra house row loaded from `lga_growth.csv`, and formats both values to one decimal place.

### Q5. Items the repository could not establish

- The approved finding uses the words “lower-income areas in 2019”. I kept the approved finding verbatim and stated the actual income vintage in the method. `dim_lga.csv` and D07 establish that the test uses 2016 Census household income.
- The requested approximate six-month publication lag could not be confirmed from the repository. The README describes the three- and six-month timings as defined by DCJ. [DCJ sales explanatory notes](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/explanatory-notes.html)
- The zero-difference Power BI check is recorded in the reviewed report, guide and screenshot. I did not rerun the Windows Power BI refresh or check whether the current local PBIX has been pushed.

## Acceptance checks

| Check | Pass/Fail | Evidence |
|---|---|---|
| A1. README order and content | Pass | Ten requested parts in order. Automated comparison matched all three findings to the approved words. The README contains no placeholder. The lag caveat follows the linked DCJ methodology. |
| A2. Numbers and reviewer spot check | Pass for recomputation. Reviewer check pending. | Eight percentages, both leaders' ranks and the Middle Ring count matched independently. Q1 records the sources and the provenance of non-data identifiers. Claude's review is pending. |
| A3. Links | Pass | Ten relative targets exist. All eight unique external targets returned HTTP 200. |
| A4. House plots | Pass | Confirmed title, two computed footnotes, successful execution and visual inspection. |
| A5. Stale text | Pass | Only C1's Notes cell in `docs/data_sources.md` and line 77 of `docs/project_plan.md` changed. |
| A6. Final checklist | Pass | Three notebook runs, byte-identical data, verified SQL features and report assets, 19 CSVs checked, all credential-pattern hits explained and both source path scans empty. |
| A7. Scope | Pass | Six allowed tracked files and this submission changed. Git commands were read-only. |

## Decisions needed (for Kang)

1. Keep the approved finding as written, with the 2016 income vintage in the method, or approve more precise wording in the finding itself. The second option makes the year of the input clear in the first read and requires a change to the confirmed wording.
2. Choose whether to license the repository code for reuse. A code licence such as MIT would give readers explicit reuse terms. The source datasets carry the licences listed above.

## Issues and risks

- The middle-ring distance range describes the centroids of the project's Middle Ring LGAs. DCJ's ring membership comes from the published regional classifications.
- The first-run spatial download and live source downloads require network access. The replay used the already installed extension and the checked-in or locally archived raw files.

## Suggested commit message(s)

`Write README and run final checks (T11)`
