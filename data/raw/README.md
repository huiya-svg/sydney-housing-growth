# Raw sales and candidate data

`dcj_sales/` contains published sales tables from March 2019 through March 2026. `dcj_rent/` contains the four 2019 rent tables.
Other source folders hold ABS population, Census, LGA boundaries and correspondences, approvals and CPI, the Heritage NSW GPO point, and the RBA cash rate target.
`MANIFEST.csv` records original URLs, download dates, SHA-256 hashes, byte sizes and licences. Files retain their original names when the source supplies one.
From the repository root, run `.venv/bin/python scripts/download_data.py` to verify existing files, fetch missing originals and extract the listed Census members.
On a hash mismatch the script stops and preserves both the file and the manifest.
`_archives/` is local-only. It holds the two Census ZIPs and the 28,396,865-byte historical ABS approvals workbook. Read the latter directly in place.
The five Census files in `abs_census/` are unchanged ZIP members. Their manifest URLs give the archive URL followed by the member path.
If the historical workbook transfer ends early, open the ABS release, find **Economy and Industry, ASGS and LGA, 2011, 2015–2020** under Data downloads, and save the original in `_archives/`. [ABS 2015–20 release](https://www.abs.gov.au/methodologies/data-region-methodology/2015-20)
Rent and sales tables © State of New South Wales (Department of Communities and Justice). ABS data used with permission from the Australian Bureau of Statistics. Cash rate source is Reserve Bank of Australia, 2026. [DCJ copyright](https://dcj.nsw.gov.au/statements/copyright-and-disclaimer.html), [ABS copyright](https://www.abs.gov.au/website-privacy-copyright-and-disclaimer), [RBA copyright](https://www.rba.gov.au/copyright/index.html)
