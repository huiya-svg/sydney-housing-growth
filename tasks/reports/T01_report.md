# T01 report — Python environment + core DCJ sales data

## Summary

Set up the Python 3.12 environment, downloaded all 29 NSW DCJ sales workbooks from March 2019 through March 2026, and executed the exploration notebook. The workbooks cover every quarter, and DCJ groups 34 LGAs under Greater Sydney in each one. Wollondilly has no published strata median in 2019. The June workbook omits the row, and the other three quarters suppress the price. DCJ sometimes suppresses exact sales counts even when it publishes the price.

## Files created or changed

- `.venv/` — local Python 3.12 environment.
- `requirements.txt` — exact versions for the ten starter packages. All workbooks are XLSX, so the starter packages were sufficient.
- `data/raw/dcj_sales/` — the 29 original sales workbooks listed in Q1.
- `data/raw/MANIFEST.csv` — original filenames, URLs, download date, SHA-256, bytes and licence.
- `data/raw/README.md` — raw files, download command and attribution.
- `scripts/download_data.py` — downloads missing workbooks and records provenance.
- `notebooks/01_explore.ipynb` — eight inspection steps with saved outputs.
- `docs/data_sources.md` — updated the Core row with coverage and screening evidence.
- `tasks/reports/T01_report.md` — this submission.

## Commands run

| Command or check | Result |
|---|---|
| `cat AGENTS.md`, then read the task spec, project plan, starter requirements, data sources and decision register | Pass. Confirmed the allowed files, starter packages and open D04 decision. The initial `ls -ld .venv .uv-cache` returned `No such file or directory` for both, as expected on a fresh setup. |
| `uv venv --python 3.12 .venv` | Pass. Created the virtual environment with CPython 3.12.14. |
| `VIRTUAL_ENV="$PWD/.venv" uv pip install -r requirements.txt` | Pass. The initial install resolved and installed 111 packages including dependencies. uv reported two dependency version-specifier warnings and continued. After pinning the ten packages, the same command returned `Checked 10 packages`. |
| `.venv/bin/python --version` and `.venv/bin/python -c "import pandas, duckdb, scipy, matplotlib, seaborn, openpyxl, requests"` | Pass. Python 3.12.14 and all requested imports succeeded. |
| Official index and file-link checks via web search and Python | The web reader returned `(400) Unsupported content-type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` on direct workbook previews. An initial `urllib` HTML probe returned `HTTP Error 403: Forbidden`. A normal `requests.get` on the same DCJ pages and workbook links succeeded. |
| `.venv/bin/python -u scripts/download_data.py` | Pass. Downloaded 29 workbooks and wrote the manifest. |
| Repeat `.venv/bin/python scripts/download_data.py` and compare before and after with `.venv/bin/python -` | Pass. 29 `Present` messages, zero downloads, and `Manifest unchanged.` Manifest bytes, download dates and modification times were identical. All 29 workbook hashes and byte sizes matched the manifest, and all workbook ZIP CRC checks passed. |
| `.venv/bin/python -` with openpyxl to inspect headers, cell types, grouping and specific workbook cells | Initial duplicate-key probe raised `AssertionError` because it included blank spacer rows. The corrected check scoped to published rows passed. The three Q7 source cells also matched the notebook independently. |
| `.venv/bin/jupyter kernelspec list` | Pass. The `python3` kernel resolves to `.venv`. |
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_explore.ipynb` | Pass. nbconvert saved the executed notebook. Jupyter warned that its kernel TCP transport was unencrypted. |
| `.venv/bin/python -` with nbformat and nbconvert to validate the saved notebook and inspect an HTML preview | Pass. Valid notebook, eight executed code cells without error outputs, eight numbered headings and 15 output tables. |
| Headless Chrome preview of the notebook | Direct screenshots were blank with `CVDisplayLinkCreateWithCGDisplay failed` and compositor errors. The Chrome print preview rendered. `pdftoppm` opened the preview pages for visual inspection. `pdftotext` was unavailable (`command not found`). |
| Repository file inventory and SHA-256 comparison against the pre-task snapshot | Pass. Changes match the allowed files. |

## Answers to the task questions

### Q1. Sources, issues, latest release and licence

DCJ lists **March quarter 2026** as its latest sales release. The workbook’s `Explanatory Notes` cover identifies **Report No. 156** and records extraction on **31 July 2026**. The release page was updated on **18 August 2026**, which also matches the workbook’s HTTP `Last-Modified` date and embedded modification date. DCJ gives the page update date without a separately labelled release date. The archive lists issues **128–155**. DCJ’s site-wide licence is **CC BY 4.0**. [Current release page](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/rent-and-sales-report.html), [DCJ issue archive](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/previous-rent-and-sales-reports.html), [DCJ copyright and disclaimer](https://dcj.nsw.gov.au/statements/copyright-and-disclaimer.html)

| Sales year | March quarter | June quarter | September quarter | December quarter |
|---|---|---|---|---|
| 2019 | [Issue 128](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-128-sales-tables-march-2019.xlsx) | [Issue 129](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-129-sales-tables-june-2019.xlsx) | [Issue 130](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-130-sales-tables-september-2019.xlsx) | [Issue 131](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-131-sales-tables-december-2019.xlsx) |
| 2020 | [Issue 132](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-132-sales-tables-march-2020.xlsx) | [Issue 133](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-133-sales-tables-june-2020.xlsx) | [Issue 134](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-134-sales-tables-september-2020.xlsx) | [Issue 135](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-135-sales-tables-december-2020.xlsx) |
| 2021 | [Issue 136](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-136-sales-tables-march-2021.xlsx) | [Issue 137](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-137-sales-tables-june-2021.xlsx) | [Issue 138](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-138-sales-tables-september-2021.xlsx) | [Issue 139](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-139-sales-tables-december-2021.xlsx) |
| 2022 | [Issue 140](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-140-sales-tables-march-2022.xlsx) | [Issue 141](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-141-sales-tables-june-2022.xlsx) | [Issue 142](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-142-sales-tables-september-2022.xlsx) | [Issue 143](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-143-sales-tables-december-2022.xlsx) |
| 2023 | [Issue 144](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-144-sales-tables-march-2023.xlsx) | [Issue 145](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-145-sales-tables-june-2023.xlsx) | [Issue 146](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-146-sales-tables-september-2023.xlsx) | [Issue 147](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-147-sales-tables-december-2023-quarter.xlsx) |
| 2024 | [Issue 148](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/previous-rent-and-sales-reports/issue-148-sales-tables-march-2024-quarter.xlsx) | [Issue 149](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/issue-149-sales-tables-june-2024-quarter.xlsx) | [Issue 150](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/Sales_tables_September_2024_quarter.xlsx) | [Issue 151](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/issue-151-sales-tables-dec-2024.xlsx) |
| 2025 | [Issue 152](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/issue-152-sales-tables-mar-2025.xlsx) | [Issue 153](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/sales_tables_june_2025_quarter.xlsx) | [Issue 154](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/sales_tables_september_2025_quarter.xlsx) | [Issue 155](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/sales-tables-december-2025-quarter.xlsx) |
| 2026 | [Issue 156](https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/families-and-communities-statistics/housing-and-rent-sales/sales-tables-march-2026-quarter.xlsx) |  |  |  |

The [raw manifest](../../data/raw/MANIFEST.csv) records those direct file URLs with their original filenames and hashes. All downloads were recorded on 25 November 2026.

### Q2. Publication format and coverage

**29 quarterly workbooks, 29 downloaded, zero missing quarters.** Each `LGA` table reports one reference quarter and includes percentage changes relative to the previous quarter and year. The archive’s historical metropolitan LGA trend workbook ends in March 2017. The current release page and archive list the in-scope sales data as quarterly workbooks. The notebook read the reporting period from each workbook and matched it to every quarter from 2019 Q1 through 2026 Q1. [DCJ issue archive](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/previous-rent-and-sales-reports.html), [Current release page](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/rent-and-sales-report.html)

### Q3. Workbook and table layout

- Every workbook contains `Explanatory Notes`, `LGA` and `Postcode`. The notebook inspects `LGA` Table 3. Its column header is on row 5 in issues 128–129, row 6 in issue 130 and row 7 in issues 131–156. The issue 156 reporting period appears at `LGA!A2`.
- Columns A–D identify GMR, Greater Sydney, ring and LGA. Column E records `Total`, `Non Strata` or `Strata`. The table is long by dwelling type and wide by measure, with a single reporting quarter per workbook.
- F–I hold first quartile, median, third quartile and mean price in thousands of dollars. J is the number of sales. K–N hold quarterly and annual change in median and in sales count.
- The raw load has 81,127 published rows and 17 columns. The 14 workbook columns keep their cell values and the other three record quarter date, filename and Excel row.

### Q4. Missing values and small samples

In `LGA!A3` of issue 156, DCJ defines `-` as 10 or fewer sales and `s` as 30 or fewer. The explanatory notes specify price suppression at 10 or fewer. In the workbooks, `s` marks a small sample whose exact count is withheld. A numeric price can still be published, as in the March 2026 Hawkesbury strata row `G1884 = 808` and `J1884 = s`. The issue 128 legend uses the wording “bonds lodged” even though it is a sales table. Issue 156 and the sales notes explicitly refer to property sales. [DCJ sales explanatory notes](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/explanatory-notes.html)

| Marker and measure | All published `LGA` rows | Statewide LGA block | DCJ Sydney LGA rows |
|---|---:|---:|---:|
| `-`, per price column | 8,016 | 1,002 | 15 |
| `-`, sales count | 8,016 | 1,002 | 15 |
| `s`, sales count | 12,992 | 1,624 | 133 |
| `-`, per change column | 8,016 | 1,002 | 15 |
| Blank, per change column | 32 | 4 | 0 |

The full sheet includes repeated geography levels and published aggregate rows. The statewide block counts one row per published LGA and dwelling type in each quarter. The Sydney column counts each LGA row in its DCJ ring once per quarter and includes the workbook’s dwelling-type `Total` frequency. There were no other non-numeric markers and no blank price or count cells in the published rows. See notebook section 6.

Sydney has 986 published non-strata rows and 985 strata rows. Of these, 949 and 877 respectively have numeric counts, with medians of 264 and 261 sales. The displayed counts start at 31 for both types. There are 37 non-strata and 93 strata `s` counts, plus 15 strata dashes. Since `s` can include exactly 30, the strict under-30 total among published house and unit rows is **15–145** (non-strata **0–37**, strata **15–108**). The absent Wollondilly cell has no published count. See notebook section 7.

### Q5. Geography labels and aggregate rows

The workbooks have **128 distinct LGA labels** across all quarters, with **126–128** per quarter. There are **1,057** distinct combinations of columns A–D including **33** combinations with `Total` in column D. Those combinations repeat aggregates for NSW, Greater Metropolitan Region, Greater Sydney, Inner / Middle / Outer Ring, Rest of GMR, Newcastle SSD, Wollongong SSD and Rest of State. The published Greater Sydney median rows in issue 156 are `LGA!G1691` for non-strata and `LGA!G1692` for strata.

No within-series LGA spelling variants were found. Five labels are absent in one or more issues (Balranald, Bogan, Bourke, Brewarrina and Central Darling). Notebook section 5 lists the exact labels and periods.

### Q6. DCJ's Greater Sydney grouping

DCJ publishes **34 Sydney LGAs** in each quarter, with **8 Inner Ring, 12 Middle Ring and 14 Outer Ring**. All four named areas appear in the **Outer Ring** throughout. In the latest workbook, the `LGA` sheet’s A–E geography and dwelling-type columns show Blue Mountains on row 1867, Central Coast on row 1876, Hawkesbury on row 1882 and Wollondilly on row 1903, each at dwelling-type `Total`. The ring and LGA labels are tabulated in notebook section 5.

### Q7. Three values for checking in Excel

All three come from `data/raw/dcj_sales/sales-tables-march-2026-quarter.xlsx`, sheet `LGA`, issue 156, March quarter 2026.

| LGA | Dwelling type | Measure | Raw value | Excel cell |
|---|---|---|---:|---|
| Blacktown | Non Strata (house proxy) | Median price, $'000 | 1250 | G1865 |
| Sydney | Strata (unit proxy) | Median price, $'000 | 967 | G1815 |
| Parramatta | Strata (unit proxy) | Sales count | 835 | J1851 |

### Q8. Series breaks, revisions and price units

- DCJ documents a production break in September 2017, before the requested series. The post-2019 workbooks have a header and storage-format change. For example, the March 2019 statewide all-dwellings count at `LGA!J6` is numeric, while March 2026 `LGA!J8` contains the text `31,434`. The March 2026 median header `LGA!G7` identifies the price scale as $'000. The notebook retains the workbook values. [DCJ sales explanatory notes](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/explanatory-notes.html)
- The newer issue can use a revised prior-quarter base. December 2025 issue 155 gives 1,265 Sydney strata sales at `LGA!J1823`. March 2026 issue 156 gives 1,004 at `LGA!J1815` and a quarterly count change of −22.83% at `LGA!M1815`. That percentage implies a December base of about 1,301. The change computed from 1,265 is −20.63%. DCJ reports that notifications arrive over time. [DCJ sales explanatory notes](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/explanatory-notes.html)
- Title type is a proxy for dwelling type. DCJ includes townhouses and terraces or villas under strata where applicable. It counts multi-unit dwellings with Torrens title under non-strata. [DCJ sales explanatory notes](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/explanatory-notes.html)
- All 29 quarters contain both dwelling types somewhere in the Sydney grouping. The June 2019 Wollondilly strata row is the only absent Sydney LGA-quarter-type combination of 1,972 expected. Wollondilly strata prices are also suppressed in March, September and December 2019 (issues 128, 130 and 131 at `LGA!G1863`, `LGA!G1872` and `LGA!G1885`). Statewide row omissions are listed in notebook section 5.

## Acceptance checks

| Check | Pass/Fail | Evidence |
|---|---|---|
| A1 | Pass | Python 3.12.14, requested imports succeed, 10 exact package pins. |
| A2 | Pass | All 29 original filenames present and all SHA-256 hashes and byte sizes match the manifest. |
| A3 | Pass | Second run skipped every workbook. Manifest bytes, dates and modification time match the first run. |
| A4 | Pass | Exact nbconvert command succeeded, with outputs for all eight code cells. Data reads use only the raw workbooks and the notebook contains no data writes. |
| A5 | Pass | Each code cell follows a plain-English markdown explanation. The notebook retains Excel row numbers and explains each subset and count. |
| A6 | Pass | Core screening row completed and seven-line raw README added. |
| A7 | Pass | This report follows the requested template and gives evidence for Q1–Q8. |
| A8 | Pass | File inventory and pre/post hashes show only allowed changes. No git commands ran. |

## Decisions needed (for Kang)

1. **D04 — Greater Sydney boundary.** Use DCJ’s 34-LGA boundary to align the project’s LGA coverage with its ring labels and published aggregate, use the ABS GCCSA as the external geographic standard after verifying the LGA mapping, or use the 33-LGA metro definition to exclude Central Coast. A different boundary can change the rankings and how the published DCJ aggregate is described.
2. **Wollondilly’s 2019 strata baseline.** The agreed 2019 baseline leaves growth unavailable for this series because all four medians are absent or suppressed. A different baseline would require an explicit change to the agreed period and would affect comparability with other LGAs.

## Issues and risks

- The 29 official workbook links all fetched with the script. The earlier web preview and HTML probe errors are recorded under Commands run.
- Excel verification of the three source cells is Kang’s review step. I verified the cells programmatically against the original workbook.
- DCJ’s website identifies the latest posted workbook and its publication-page update date. The workbook cover supplies the report number and extraction date.

## Suggested commit message(s)

- `feat: set up Python and document NSW DCJ quarterly sales data`
