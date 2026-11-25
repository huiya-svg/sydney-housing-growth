"""Download the DCJ sales workbooks listed on its report and archive pages.

Run from the repository root with .venv/bin/python scripts/download_data.py.
"""

import csv
import hashlib
from datetime import datetime
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import is_zipfile
from zoneinfo import ZoneInfo

import requests


RAW_DIR = Path("data/raw")
SALES_DIR = RAW_DIR / "dcj_sales"
MANIFEST = RAW_DIR / "MANIFEST.csv"
LICENCE = "CC BY 4.0"
FIELDS = ["filename", "source_url", "downloaded_on", "sha256", "bytes", "licence"]

SALES_URL = (
    "https://dcj.nsw.gov.au/content/dam/dcj/dcj-website/documents/about-us/"
    "families-and-communities-statistics/housing-and-rent-sales/"
)
ARCHIVE_URL = SALES_URL + "previous-rent-and-sales-reports/"

# Issue 128 (March 2019) through the March 2026 sales release, in order.
DOWNLOADS = [
    (ARCHIVE_URL + "issue-128-sales-tables-march-2019.xlsx", "issue-128-sales-tables-march-2019.xlsx"),
    (ARCHIVE_URL + "issue-129-sales-tables-june-2019.xlsx", "issue-129-sales-tables-june-2019.xlsx"),
    (ARCHIVE_URL + "issue-130-sales-tables-september-2019.xlsx", "issue-130-sales-tables-september-2019.xlsx"),
    (ARCHIVE_URL + "issue-131-sales-tables-december-2019.xlsx", "issue-131-sales-tables-december-2019.xlsx"),
    (ARCHIVE_URL + "issue-132-sales-tables-march-2020.xlsx", "issue-132-sales-tables-march-2020.xlsx"),
    (ARCHIVE_URL + "issue-133-sales-tables-june-2020.xlsx", "issue-133-sales-tables-june-2020.xlsx"),
    (ARCHIVE_URL + "issue-134-sales-tables-september-2020.xlsx", "issue-134-sales-tables-september-2020.xlsx"),
    (ARCHIVE_URL + "issue-135-sales-tables-december-2020.xlsx", "issue-135-sales-tables-december-2020.xlsx"),
    (ARCHIVE_URL + "issue-136-sales-tables-march-2021.xlsx", "issue-136-sales-tables-march-2021.xlsx"),
    (ARCHIVE_URL + "issue-137-sales-tables-june-2021.xlsx", "issue-137-sales-tables-june-2021.xlsx"),
    (ARCHIVE_URL + "issue-138-sales-tables-september-2021.xlsx", "issue-138-sales-tables-september-2021.xlsx"),
    (ARCHIVE_URL + "issue-139-sales-tables-december-2021.xlsx", "issue-139-sales-tables-december-2021.xlsx"),
    (ARCHIVE_URL + "issue-140-sales-tables-march-2022.xlsx", "issue-140-sales-tables-march-2022.xlsx"),
    (ARCHIVE_URL + "issue-141-sales-tables-june-2022.xlsx", "issue-141-sales-tables-june-2022.xlsx"),
    (ARCHIVE_URL + "issue-142-sales-tables-september-2022.xlsx", "issue-142-sales-tables-september-2022.xlsx"),
    (ARCHIVE_URL + "issue-143-sales-tables-december-2022.xlsx", "issue-143-sales-tables-december-2022.xlsx"),
    (ARCHIVE_URL + "issue-144-sales-tables-march-2023.xlsx", "issue-144-sales-tables-march-2023.xlsx"),
    (ARCHIVE_URL + "issue-145-sales-tables-june-2023.xlsx", "issue-145-sales-tables-june-2023.xlsx"),
    (ARCHIVE_URL + "issue-146-sales-tables-september-2023.xlsx", "issue-146-sales-tables-september-2023.xlsx"),
    (ARCHIVE_URL + "issue-147-sales-tables-december-2023-quarter.xlsx", "issue-147-sales-tables-december-2023-quarter.xlsx"),
    (ARCHIVE_URL + "issue-148-sales-tables-march-2024-quarter.xlsx", "issue-148-sales-tables-march-2024-quarter.xlsx"),
    (SALES_URL + "issue-149-sales-tables-june-2024-quarter.xlsx", "issue-149-sales-tables-june-2024-quarter.xlsx"),
    (SALES_URL + "Sales_tables_September_2024_quarter.xlsx", "Sales_tables_September_2024_quarter.xlsx"),
    (SALES_URL + "issue-151-sales-tables-dec-2024.xlsx", "issue-151-sales-tables-dec-2024.xlsx"),
    (SALES_URL + "issue-152-sales-tables-mar-2025.xlsx", "issue-152-sales-tables-mar-2025.xlsx"),
    (SALES_URL + "sales_tables_june_2025_quarter.xlsx", "sales_tables_june_2025_quarter.xlsx"),
    (SALES_URL + "sales_tables_september_2025_quarter.xlsx", "sales_tables_september_2025_quarter.xlsx"),
    (SALES_URL + "sales-tables-december-2025-quarter.xlsx", "sales-tables-december-2025-quarter.xlsx"),
    (SALES_URL + "sales-tables-march-2026-quarter.xlsx", "sales-tables-march-2026-quarter.xlsx"),
]


def download_workbook(session, url, path):
    response = session.get(url, timeout=45)
    response.raise_for_status()
    if not is_zipfile(BytesIO(response.content)):
        raise ValueError(f"Expected an XLSX workbook from {url}")

    # Write the complete response before giving it the published filename.
    with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        temporary_path.write_bytes(response.content)
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def read_manifest():
    if not MANIFEST.exists():
        return {}
    with MANIFEST.open(encoding="utf-8", newline="") as manifest_file:
        return {row["filename"]: row for row in csv.DictReader(manifest_file)}


def write_manifest(rows):
    with NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", dir=RAW_DIR, delete=False
    ) as manifest_file:
        temporary_path = Path(manifest_file.name)
        writer = csv.DictWriter(manifest_file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows.values())
    try:
        if MANIFEST.exists() and MANIFEST.read_bytes() == temporary_path.read_bytes():
            print("Manifest unchanged.")
        else:
            temporary_path.replace(MANIFEST)
            print(f"Wrote {MANIFEST}.")
    finally:
        temporary_path.unlink(missing_ok=True)


def main():
    SALES_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_manifest()
    failures = 0

    with requests.Session() as session:
        for url, filename in DOWNLOADS:
            path = SALES_DIR / filename
            manifest_name = path.relative_to(RAW_DIR).as_posix()
            downloaded_on = rows.get(manifest_name, {}).get("downloaded_on", "")
            if path.exists():
                print(f"Present {filename}")
            else:
                try:
                    download_workbook(session, url, path)
                except (requests.RequestException, ValueError) as error:
                    print(f"Failed {filename}: {error}")
                    rows.pop(manifest_name, None)
                    failures += 1
                    continue
                downloaded_on = datetime.now(ZoneInfo("Australia/Sydney")).date().isoformat()
                print(f"Downloaded {filename}")

            content = path.read_bytes()
            rows[manifest_name] = {
                "filename": manifest_name,
                "source_url": url,
                "downloaded_on": downloaded_on,
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
                "licence": LICENCE,
            }

    write_manifest(rows)
    print(f"{len(DOWNLOADS) - failures}/{len(DOWNLOADS)} listed workbooks on disk.")
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(main())
