# T02 report — Candidate factors for Sydney house and unit price growth

## Summary

Downloaded and inspected the official rent, population, Census, geographic, supply, CPI and cash rate sources. Population and distance have data for all 34 DCJ Sydney LGAs once the six ABS label differences are accounted for. The 2016 Census has no single Bayside median, and the oldest approvals vintage contains only 26 of the 34 current codes. I recommend testing baseline-period population growth and CBD distance, with 2016 income as an optional third factor.

## Files created or changed

- `data/raw/` — 21 original downloads and five byte-for-byte Census members, all recorded in `MANIFEST.csv`. The two Census ZIPs and the older supply workbook are in `_archives/`.
- `data/raw/README.md` — source storage, redownload instructions, archive lineage and attribution.
- `scripts/download_data.py` — candidate files and ZIP extraction plus SHA-256 verification before downloads.
- `requirements.txt` — pinned `xlrd==2.0.2` for two historical ABS XLS workbooks.
- `notebooks/01_explore.ipynb` — appended Part B, C2–C8, with saved outputs. Part A cell sources and eight plain-text outputs match the T01 version exactly.
- `docs/data_sources.md` — four screening checks and a verdict for every candidate C1–C9.
- `tasks/reports/T02_report.md` — this submission.

## Commands run

| Command or check | Result |
|---|---|
| `cat AGENTS.md` and read the T02 spec, project plan, screening table and T01 review | Pass. Confirmed the allowed scope and T01 downloader issue. Recorded pre-task file hashes, notebook cell hashes and Part A outputs. |
| Official release and dataset probes using web search and `.venv/bin/python -` with requests | The first 2015–20 workbook transfer raised `requests.exceptions.ChunkedEncodingError: Response ended prematurely`. A normal retry and the downloader both fetched the original. Guessed `2011-20` and `2011-19` Data by region routes, one heritage copyright route and a preliminary Commonwealth heritage route returned HTTP 404. The NSW HMS item page returned `403 Client Error: Forbidden` to requests. The public NSW State Heritage Register feature layer returned the identified GPO point. |
| `.venv/bin/python -u scripts/download_data.py` | Pass. Downloaded 21 originals and extracted five Census members across acquisition runs. Final output `55/55 listed files on disk.` |
| `uv pip install --python .venv/bin/python xlrd` | Pass. Installed `xlrd==2.0.2`. The initial pandas XLS reader emitted `Pandas4Warning: The xlrd engine is deprecated and will be removed in a future version`. Part B now reads the two XLS input sheets directly through xlrd. |
| `uv pip check --python .venv/bin/python` | Pass. All 112 installed packages are compatible. |
| `.venv/bin/python -` to verify manifest sizes, hashes and archive members and run `scripts/download_data.py` again | Pass. All 55 rows match and five Census members equal their ZIP entries byte-for-byte. Second run printed 55 `Present` rows and `Manifest unchanged.` |
| `.venv/bin/python -` to execute the downloader on a separate temporary fixture | Pass. Appended bytes to a copy of issue 128. The script returned status 1 with `WARNING: SHA-256 mismatch for data/raw/dcj_sales/issue-128-sales-tables-march-2019.xlsx`. The fixture file and its manifest were preserved. The workspace originals were verified afterward. |
| `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_explore.ipynb` | First run failed with `In DuckDB v2.0, the 'geometry_always_xy' setting must be set explicitly to use this functionality.` Set longitude-first axis order for both inputs and reran successfully. Jupyter printed its kernel TCP transport warning. |
| `.venv/bin/python -` to validate saved inputs, outputs and file scope | An output audit raised `AssertionError` because it required an output from the setup cell. The corrected audit checked execution and allowed the setup cell to produce no output. A first workspace-wide comparison also flagged two concurrent edits outside the task. The scoped comparison accounted for those edits. |

## Answers to the task questions

### Q1. Official files and coverage

The [manifest](../../data/raw/MANIFEST.csv) contains every direct file URL and ZIP-member path. Dates below identify releases, extracts or snapshots as labelled.

| Candidate | Source files and licence | Reference period, release and geography |
|---|---|---|
| C2 Rent | `issue-127-rent-tables-march-2019.xlsx`, `issue-128-rent-tables-june-2019.xlsx`, `issue-129-rent-tables-september-2019.xlsx`, `issue-130-rent-tables-december-2019.xlsx`. CC BY 4.0. [DCJ archive](https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/previous-rent-and-sales-reports.html) | Four 2019 quarters. Covers record extracts on 16 April, 8 July and 23 October 2019, and 20 January 2020. Table 1 gives DCJ reporting LGAs and Sydney rings. The notes refer to ASGS geography without specifying a dated LGA vintage. |
| C3 Population | `32180DS0004_2001-25.xlsx`, Table 1. CC BY 4.0. [ABS Regional population](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25) | Released 31 March 2026. June 2001–2025, on LGA 2025 boundaries. 548 area rows after removing headings and notes. The 34 codes have all 25 yearly counts. The 2025 estimate is preliminary. |
| C4 Income | `2016_GCP_LGA_for_NSW_short-header.zip` and `2021_GCP_LGA_for_NSW_short-header.zip`. Used each G02 CSV and geography descriptor. The in-pack notices give CC BY 2.5 AU and CC BY 4.0 respectively. [DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks), [2016 release](https://www.abs.gov.au/ausstats/abs%40.nsf/PrimaryMainFeatures/2011.0.55.001), [2021 release](https://www.abs.gov.au/census/guide-census-data/2021-census-product-release-guide) | Census LGA 2016, released 27 June 2017, and Census LGA 2021, released 28 June 2022. The NSW G02 CSVs have 132 and 131 rows. `Median_tot_hhd_inc_weekly` is dollars per week. |
| C5 Distance | `LGA_2025_Sydney_region.geojson`, `Sydney_GPO_00763.geojson` and six official ABS correspondence CSVs listed in Q4. CC BY 4.0. [ABS boundary layer](https://geo.abs.gov.au/arcgis/rest/services/Hosted/LGA_Regional_Population_2025/FeatureServer/1), [GeoJSON boundary query](https://geo.abs.gov.au/arcgis/rest/services/Hosted/LGA_Regional_Population_2025/FeatureServer/1/query?where=state_code_2021+%3D+1&geometry=150.05%2C-34.4%2C151.65%2C-33.01&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=lga_code_2025%2Clga_name_2025&outSR=4326&f=geojson&orderByFields=lga_code_2025), [NSW heritage layer](https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/HMS/Heritage/MapServer/5), [GPO query](https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/HMS/Heritage/MapServer/5/query?where=HOITEMID+%3D+5045424&outFields=HOITEMID%2CITEMNAME%2CLISTINGNO&outSR=4326&f=geojson), [Heritage NSW copyright](https://www.environment.nsw.gov.au/about-us/copyright-and-disclaimer) | ASGS Edition 3, LGA 2025. Boundary layer accompanies the 31 March 2026 ERP release. The GPO register point was retrieved 25 November 2026. The service returned 43 full polygons, including all 34 DCJ areas, and one GPO point. |
| C6 Supply | `87310do004_201706.xls`, `87310do005_201706.xls`, `14100DO0003_2015-20.xlsx`, `14100DO0003_2011-25.xlsx` and Census `2016Census_G32_NSW_LGA.csv`. ABS approvals CC BY 4.0. Stock CC BY 2.5 AU. [ABS approvals archive](https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/8731.0Jun%202017), [2015–20 workbook page](https://www.abs.gov.au/methodologies/data-region-methodology/2015-20), [2011–25 workbook page](https://www.abs.gov.au/methodologies/data-region-methodology/2011-25), [Census DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks) | The two NSW cubes were released 9 August 2017 and provide FY ends 2016 and 2017 on the pre-amalgamation and 2016 LGA vintages respectively. The 26 November 2021 release provides numeric FY2018–2020 counts on LGA 2020 rows, with vintage notes in Table 2. The 10 November 2026 release provides FY2021–2025 counts on LGA 2021 rows. G32 stock is Census LGA 2016. |
| C7 CPI | `6401017.xlsx`, Table 17 `Data1`, series A2325806K. CC BY 4.0. [ABS CPI](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/sep-2026) | Released 28 October 2026. Sydney capital-city All groups quarterly index, September 1948–September 2026. 313 published values with zero blanks. |
| C8 Cash rate | `a02hist.xlsx`, Table A2 `Data`, series ARBAMPCNCRT. CC BY 4.0. [RBA cash rate and A2](https://www.rba.gov.au/statistics/cash-rate/), [RBA copyright](https://www.rba.gov.au/copyright/index.html) | Workbook publication date 3 November 2026. Australia, 100 dated target observations from 23 January 1990 through effective date 4 November 2026. A2 publishes target events in per cent. |

Each rent issue has 68 Sydney `House` or `Flat/Unit` rows with `Total` bedrooms. All 272 medians are present. Issue 129's `LGA!A1` repeats the June heading, while `LGA!F1`, the cover and archive identify September. March examples in issue 127 are Blacktown house **$470** (`LGA!H21629`), Sydney flat/unit **$650** (`LGA!H21062`) and Wollondilly flat/unit **$320** (`LGA!H22099`). The Wollondilly flat/unit bond count is marked `s` in all four quarters.

### Q2. Four screening checks

| Candidate | 1 Geography and time | 2 Varies by LGA | 3 Timing | 4 Licence and privacy |
|---|---|---|---|---|
| C1. 2019 price level | Pass with gaps. All four issues exist. Wollondilly has no published strata median. | Yes. Medians differ by LGA and title type. | Baseline year, before the later outcome window. | Pass. Aggregate sales tables already in the repo. |
| C2. Median weekly rent and gross yield | Pass for rent. All 34 labels and all 272 type-quarter medians present. Yield also needs the sale price. | Yes. Weekly rents vary by LGA and dwelling type. | 2019 baseline. Later rents would be concurrent. | Pass. Aggregate new-bond results only. |
| C3. Population | Pass. All 34 codes represented, six label differences. | Yes. Population and growth inputs vary by LGA. | 2016–June 2019 ends within the baseline year. Growth after June 2019 is concurrent. | Pass. Aggregate ERP. |
| C4. Median household income | Partial for 2016. 33 current codes plus two Bayside predecessors. Full 2021 code coverage. | Yes. Weekly household income varies by LGA. | 2016 pre-period. 2021 concurrent. | Pass. Aggregate G02 medians. |
| C5. Distance to Sydney CBD | Pass. All 34 centroids available. Six raw label differences. | Yes. Distances vary across LGAs. | Static location measure calculated on the 2025 boundary vintage. | Pass. Public aggregate boundaries and one public landmark. |
| C6. New dwelling supply proxy | Partial. 26/34 direct codes in FY2016, 33/34 in FY2017 and 34/34 from FY2018. Census stock has 33 direct codes. | Yes. Approval counts and stock vary by LGA. | FY2019 straddles the baseline start. Subsequent years are concurrent. | Pass for used aggregate columns. |
| C7. Sydney All groups CPI | No LGA rows. Covers the full sales period as a Sydney series. | No within Sydney. | Contemporaneous price deflator. | Pass. Published aggregate index. |
| C8. RBA cash rate target | No LGA rows. Covers the full sales period as a national series. | No. One national policy target. | Concurrent event series. | Pass. Public national policy series. |
| C9. Individual property sales | Fail for this task. Address-level grain would require aggregation. | Yes. Transaction records vary geographically. | Transactions span baseline and outcome years. | Fail for project privacy scope. Address-level rows excluded. |

The [screening register](../../docs/data_sources.md) records the verdicts. C2 gross yield would compare physical rent types to title-based sale types. Wollondilly has 2019 flat/unit rents, while its strata price baseline is unavailable. CPI and cash rate have zero LGA rows and apply as shared series to all 34. C9's CC BY-NC-ND 4.0 data remain outside T02 because they are individual sales records. [Valuer General data description and licence](https://valuation.property.nsw.gov.au/embed/propertySalesInformation/)

### Q3. Exact name matching

The **28 labels common to LGA 2025 and DCJ** are Blacktown, Blue Mountains, Burwood, Camden, Canada Bay, Canterbury-Bankstown, Cumberland, Fairfield, Georges River, Hawkesbury, Hornsby, Hunters Hill, Inner West, Lane Cove, Liverpool, Mosman, North Sydney, Northern Beaches, Parramatta, Penrith, Randwick, Ryde, Strathfield, Sydney, Waverley, Willoughby, Wollondilly and Woollahra.

| Source | Exact labels | Mismatches and missing source geography |
|---|---:|---|
| C1 DCJ sales, C2 DCJ rent | 34/34 each | All labels exact. C1 has a missing Wollondilly strata price baseline. C2 has no missing median among the selected rows. |
| C3 ABS ERP and C5 ABS polygons, LGA 2025 | 28/34 each | Bayside → `Bayside (NSW)`, Campbelltown → `Campbelltown (NSW)`, Central Coast → `Central Coast (NSW)`, Ku-Ring-Gai → `Ku-ring-gai`, Sutherland Shire → `Sutherland`, The Hills Shire → `The Hills`. All 34 codes are present. |
| C4 Census 2021 and C6 2011–25 workbook, LGA 2021 | 30/34 each | The 28 above plus Sutherland Shire and The Hills Shire. The remaining four mismatches follow the first four LGA 2025 spellings above. All 34 codes are present. |
| C4 Census 2016 and C6 Census G32 stock | 0/34 | 33 direct current codes with ABS suffixes, plus `Botany Bay (C)` and `Rockdale (C)` in place of Bayside. The raw names are listed below. The present income and stock values have zero blanks. |
| C6 FY2015–16 NSW cube | 0/34 | 26 direct current codes. The 2016 names below apply to the 26 after setting aside the eight reorganised areas in Q4 and using `Campbelltown (C)` without `(NSW)`. |
| C6 FY2016–17 NSW cube | 0/34 | Same 33 direct current codes and two Bayside predecessor labels as Census 2016. |
| C6 2015–20 workbook, LGA 2020 | 0/34 | Same 33 current-area spellings as Census 2016. Adds `Bayside (A)` in place of the two predecessors. |
| C7 CPI, C8 cash rate, C9 individual sales | N/A | Shared Sydney or national series have no LGA labels. Individual sales were screened from source documentation, so no label matching was attempted. |

**ABS 2016 raw labels.** Blacktown (C), Blue Mountains (C), Burwood (A), Camden (A), Campbelltown (C) (NSW), Canada Bay (A), Canterbury-Bankstown (A), Central Coast (C) (NSW), Cumberland (A), Fairfield (C), Georges River (A), Hawkesbury (C), Hornsby (A), Hunters Hill (A), Inner West (A), Ku-ring-gai (A), Lane Cove (A), Liverpool (C), Mosman (A), North Sydney (A), Northern Beaches (A), Parramatta (C), Penrith (C), Randwick (C), Ryde (C), Strathfield (A), Sutherland Shire (A), Sydney (C), The Hills Shire (A), Waverley (A), Willoughby (C), Wollondilly (A) and Woollahra (A). Bayside has no 2016 counterpart at a single code.

### Q4. Boundary and name changes

- **Pre-amalgamation to 2016.** The FY2015–16 approvals cube lacks the current codes for Bayside, Canterbury-Bankstown, Central Coast, Cumberland, Georges River, Inner West, Northern Beaches and Parramatta. The published labels include `Botany Bay (C)` and `Rockdale (C)` for Bayside, `Bankstown (C)` and `Canterbury (C)`, `Gosford (C)` and `Wyong (A)`, `Auburn (C)` and `Holroyd (C)`, `Hurstville (C)` and `Kogarah (C)`, `Ashfield (A)`, `Leichhardt (A)` and `Marrickville (A)`, and `Manly (A)`, `Pittwater (A)` and `Warringah (A)`. The old `Parramatta (C)` uses 16250, while the new `Parramatta (C)` uses 16260. Several predecessors were split. The 2016 Census still has separate Bayside predecessors because Bayside was proclaimed on 9 September 2016. [NSW Audit Office amalgamation list](https://www.audit.nsw.gov.au/our-work/reports/report-on-local-government-2017), [ABS 2016 changes](https://www.abs.gov.au/ausstats/abs%40.nsf/Previousproducts/3218.0Appendix12015-16?issue=2015-16&num=&opendocument=&prodno=3218.0&tabname=Notes&view=)
- **2016 and 2020 to 2021.** `CG_LGA_2016_LGA_2021.csv` gives unit weights from both `Botany Bay (C)` and `Rockdale (C)` to `Bayside (NSW)`. Both that file and `CG_LGA_2020_LGA_2021.csv` report small positive population weights from Blacktown to Cumberland, Camden to Campbelltown, Campbelltown to Camden, Cumberland to Parramatta and Sutherland Shire to an unallocated destination. The non-merger weights range from 0.0000114 to 0.0004083. The 2020→2021 file also removes status suffixes from all 34 same-code labels.
- **2021 to 2025.** `CG_LGA_2021_LGA_2022.csv` records the same-code label changes `Sutherland Shire` → `Sutherland` and `The Hills Shire` → `The Hills`. That file and `CG_2022_LGA_2023_LGA.csv`, `CG_LGA_2023_LGA_2024.csv` and `CG_LGA_2024_LGA_2025.csv` each have 34 one-to-one Sydney rows with unit weights. The ABS change history identifies no other changes to the Sydney statistical boundaries in those updates. ABS LGA geometry approximates gazetted boundaries with Mesh Blocks, and a unit correspondence weight does not prove identical legal boundaries. [ABS correspondences](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/correspondences), [ABS LGA change history](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/non-abs-structures/local-government-areas)

### Q5. CBD distance

DuckDB spatial projected the full ABS polygons to Australian Albers (EPSG:9473), calculated area-weighted geometric centroids, transformed them back to WGS84 (EPSG:4326) and measured ellipsoidal straight-line distance. Coordinates were kept longitude-first in the computation. The GPO point is **−33.8677553191 latitude, 151.2077070290 longitude**, NSW State Heritage Register item **5045424**, listing **00763**. [NSW register feature](https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/HMS/Heritage/MapServer/5/query?where=HOITEMID+%3D+5045424&outFields=HOITEMID%2CITEMNAME%2CLISTINGNO&outSR=4326&f=geojson)

| LGA | Centroid latitude | Centroid longitude | GPO distance (km) |
|---|---:|---:|---:|
| Blue Mountains | −33.697431 | 150.411147 | 76.16 |
| Central Coast (NSW) | −33.307863 | 151.285535 | 62.52 |
| Hawkesbury | −33.334510 | 150.773405 | 71.57 |
| Wollondilly | −34.101865 | 150.443696 | 75.22 |

The four large LGAs have extensive bushland or rural areas that can move their centroids away from settlements. A population-weighted alternative is feasible with the ABS population grid or small-area Census counts on a boundary-compatible vintage. It would measure where residents are concentrated and would warrant a timing choice of its own. [ABS Regional population grid files](https://www.abs.gov.au/statistics/people/population/regional-population/2024-25)

### Q6. Supply source and available years

I selected **ABS total dwelling units approved**. The current NSW housing dashboard workbook publishes completions on a statewide tab. The older NSW Urban Development Program has a shorter aggregate series and a separate file whose schema includes individual project coordinates. ABS approvals provide aggregate, annual LGA inputs through FY2025. Approvals measure dwellings authorised for building. Development can be delayed, withdrawn or revised. [NSW Housing Supply dataset](https://data.nsw.gov.au/data/dataset/housing-supply), [NSW Urban Development Program](https://www.planningportal.nsw.gov.au/opendata/dataset/greater-sydney-urban-development-program), [ABS approvals methodology](https://www.abs.gov.au/methodologies/building-approvals-australia-methodology/sep-2026)

The four retained approvals workbooks contribute numeric FY2016, FY2017, FY2018–2020 and FY2021–2025 respectively. Their LGA or LGA-year row counts are 154, 132, 3,808 and 6,017. Counts are numeric for every present Sydney code in those selected years. The broad printed workbook coverage includes years with dashes in all 34 approval rows. Census G32 `Total_PDs_Dwellings` supplies occupied plus unoccupied private dwelling counts at 2016. Examples are Blacktown **106,205**, Sydney **96,925** and Wollondilly **16,048**. Part B displays approval counts and Census stock separately. No approvals-per-1,000 rate was computed.

### Q7. Likely proxies

- **CBD distance and 2019 price.** Both can capture accessibility, land scarcity and proximity to jobs.
- **Household income and 2019 price.** Purchasing power and household sorting can make affluent areas expensive at baseline.
- **Weekly rent or yield and 2019 price.** Rent and price can reflect the same local demand. Gross yield also contains price in its denominator.
- **Approvals and population growth.** Both can reflect development corridors. New construction can also accommodate population growth, making direction ambiguous in concurrent periods.

## Acceptance checks

| Check | Pass/Fail | Evidence |
|---|---|---|
| A1 | Pass | 55 manifest rows and verified files. 26 are new. All five extracted members match their archives byte-for-byte. The only file above 25 MB is under `_archives/`. |
| A2 | Pass | Ordinary repeat fetched zero files and left manifest bytes and timestamps unchanged. The isolated modified-file test printed the SHA-256 warning and preserved the fixture manifest and raw file. |
| A3 | Pass | Exact nbconvert command completed with Part B outputs. Original Part A cell sources and all eight plain-text output fingerprints match. |
| A4 | Pass | `docs/data_sources.md` covers C1–C9, with a source, licence, four checks and verdict per row. |
| A5 | Pass | Q1–Q7 above and Q8 below contain the evidence and options. D07 remains open. |
| A6 | Pass | T02 edits match the allowed paths. The wider workspace comparison identified concurrent edits to `docs/decisions.md` and `docs/workflow.md` outside T02. The sources used are aggregate or the specified public landmark. No git commands or address-level data files. |

## Decisions needed (for Kang)

1. **D07 / Q8 — Recommended pair.** Test C3 2016→2019 population growth and C5 geometric distance. All 34 codes have both inputs. They cover baseline demand and location, with the centroid caveat for large LGAs.
2. **D07 / Q8 — Third-factor options.** Add C4 2016 household income if a pre-period socioeconomic variable is worth the missing Bayside value. Alternatively try the 2019 rent level as a demand measure, or gross yield if the rent/title category proxy and absent Wollondilly price input are acceptable. Keep 2021 income, later population growth and later approvals labelled concurrent.
3. **D07 / Q8 — Baseline-price diagnostic.** Consider C1 separately to test catch-up by dwelling type. A percentage-growth outcome shares the starting-price denominator, so baseline measurement error and mechanical coupling complicate interpretation. Kang's D05 excludes Wollondilly from unit rankings. C6 has weaker pre-period comparability and can wait for a boundary and year definition.

## Issues and risks

- A boundary-standardised 2016–2019 supply rate needs a decision about predecessor areas, financial-year cutoffs and the 2016 stock denominator. The older and newer approvals vintages retain their original labels and counts.
- The 2016 Census household median for Bayside cannot be reconstructed by averaging Botany Bay and Rockdale medians.
- The downloads for RBA A2 and the two feature services are live official URLs. The manifest verifies the retained releases and the script records fresh provenance if an original is fetched again.
- The Data by region workbooks include other aggregate indicators. Part B reads only the approvals fields and geography identifiers used in T02.
- During T02, the decision log recorded Kang's D04 adoption of the 34 DCJ LGAs and the D05 and D06 choices. The task board was also updated separately.

## Suggested commit message(s)

- `feat: screen candidate factors and verify raw data integrity`
