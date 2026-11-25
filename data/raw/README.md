# Raw DCJ sales workbooks

`dcj_sales/` contains NSW Rent and Sales Report sales tables for March 2019 to March 2026.
The workbooks contain published aggregate sales statistics by LGA and postcode.
`MANIFEST.csv` records each original source URL, download date, SHA-256, byte size and licence.
From the repository root, run `.venv/bin/python scripts/download_data.py` to fetch missing workbooks.
The script skips workbooks already on disk. Raw workbooks retain their published filenames and are never edited.
© State of New South Wales (Department of Communities and Justice). [DCJ copyright and disclaimer](https://dcj.nsw.gov.au/statements/copyright-and-disclaimer.html)
