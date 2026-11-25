"""Download the official DCJ sales and candidate-factor sources.

Run from the repository root with .venv/bin/python scripts/download_data.py.
"""

import csv
import hashlib
from datetime import datetime
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import quote
from zipfile import BadZipFile, ZipFile, is_zipfile
from zoneinfo import ZoneInfo

import requests


RAW_DIR = Path("data/raw")
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

# The two ArcGIS responses lack publisher filenames. Their filenames describe
# the feature queries, and the manifest records both exact URLs.
CORRESPONDENCE_URL = (
    "https://www.abs.gov.au/statistics/standards/"
    "australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/"
    "access-and-downloads/correspondences/"
)
LGA_QUERY_URL = (
    "https://geo.abs.gov.au/arcgis/rest/services/Hosted/LGA_Regional_Population_2025/FeatureServer/1/query"
    "?where=state_code_2021+%3D+1&geometry=150.05%2C-34.4%2C151.65%2C-33.01"
    "&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects"
    "&outFields=lga_code_2025%2Clga_name_2025&outSR=4326&f=geojson&orderByFields=lga_code_2025"
)
GPO_QUERY_URL = (
    "https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/HMS/Heritage/MapServer/5/query"
    "?where=HOITEMID+%3D+5045424&outFields=HOITEMID%2CITEMNAME%2CLISTINGNO"
    "&outSR=4326&f=geojson"
)
CENSUS_URL = "https://www.abs.gov.au/census/find-census-data/datapacks/download/"

CANDIDATE_DOWNLOADS = [
    (
        ARCHIVE_URL + "issue-127-rent-tables-march-2019.xlsx",
        "dcj_rent/issue-127-rent-tables-march-2019.xlsx", "CC BY 4.0",
    ),
    (
        ARCHIVE_URL + "issue-128-rent-tables-june-2019.xlsx",
        "dcj_rent/issue-128-rent-tables-june-2019.xlsx", "CC BY 4.0",
    ),
    (
        ARCHIVE_URL + "issue-129-rent-tables-september-2019.xlsx",
        "dcj_rent/issue-129-rent-tables-september-2019.xlsx", "CC BY 4.0",
    ),
    (
        ARCHIVE_URL + "issue-130-rent-tables-december-2019.xlsx",
        "dcj_rent/issue-130-rent-tables-december-2019.xlsx", "CC BY 4.0",
    ),
    (
        "https://www.abs.gov.au/statistics/people/population/regional-population/2024-25/32180DS0004_2001-25.xlsx",
        "abs_erp/32180DS0004_2001-25.xlsx", "CC BY 4.0",
    ),
    (
        CENSUS_URL + "2016_GCP_LGA_for_NSW_short-header.zip",
        "_archives/2016_GCP_LGA_for_NSW_short-header.zip", "CC BY 2.5 AU",
    ),
    (
        CENSUS_URL + "2021_GCP_LGA_for_NSW_short-header.zip",
        "_archives/2021_GCP_LGA_for_NSW_short-header.zip", "CC BY 4.0",
    ),
    (
        LGA_QUERY_URL,
        "abs_asgs/LGA_2025_Sydney_region.geojson", "CC BY 4.0",
    ),
    (
        GPO_QUERY_URL,
        "abs_asgs/Sydney_GPO_00763.geojson", "CC BY 4.0",
    ),
    (
        CORRESPONDENCE_URL + "CG_LGA_2016_LGA_2021.csv",
        "abs_asgs/CG_LGA_2016_LGA_2021.csv", "CC BY 4.0",
    ),
    (
        CORRESPONDENCE_URL + "CG_LGA_2020_LGA_2021.csv",
        "abs_asgs/CG_LGA_2020_LGA_2021.csv", "CC BY 4.0",
    ),
    (
        CORRESPONDENCE_URL + "CG_LGA_2021_LGA_2022.csv",
        "abs_asgs/CG_LGA_2021_LGA_2022.csv", "CC BY 4.0",
    ),
    (
        CORRESPONDENCE_URL + "CG_2022_LGA_2023_LGA.csv",
        "abs_asgs/CG_2022_LGA_2023_LGA.csv", "CC BY 4.0",
    ),
    (
        CORRESPONDENCE_URL + "CG_LGA_2023_LGA_2024.csv",
        "abs_asgs/CG_LGA_2023_LGA_2024.csv", "CC BY 4.0",
    ),
    (
        CORRESPONDENCE_URL + "CG_LGA_2024_LGA_2025.csv",
        "abs_asgs/CG_LGA_2024_LGA_2025.csv", "CC BY 4.0",
    ),
    (
        "https://www.abs.gov.au/methodologies/data-region-methodology/2011-25/14100DO0003_2011-25.xlsx",
        "supply/14100DO0003_2011-25.xlsx", "CC BY 4.0",
    ),
    (
        "https://www.abs.gov.au/methodologies/data-region-methodology/2015-20/14100DO0003_2015-20.xlsx",
        "_archives/14100DO0003_2015-20.xlsx", "CC BY 4.0",
    ),
    (
        "https://www.ausstats.abs.gov.au/ausstats/meisubs.nsf/0/FC34A9D4142DCD11CA258176001A57D9/$File/87310do004_201706.xls",
        "supply/87310do004_201706.xls", "CC BY 4.0",
    ),
    (
        "https://www.ausstats.abs.gov.au/ausstats/meisubs.nsf/0/F0ACB95FA5B0CCADCA258176001A5897/$File/87310do005_201706.xls",
        "supply/87310do005_201706.xls", "CC BY 4.0",
    ),
    (
        "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/sep-2026/6401017.xlsx",
        "abs_cpi/6401017.xlsx", "CC BY 4.0",
    ),
    (
        "https://www.rba.gov.au/statistics/tables/xls/a02hist.xlsx",
        "rba/a02hist.xlsx", "CC BY 4.0",
    ),
]

# Extract the useful Census tables and their geography descriptors unchanged.
CENSUS_MEMBERS = [
    (
        "_archives/2016_GCP_LGA_for_NSW_short-header.zip",
        "2016 Census GCP Local Government Areas for NSW/2016Census_G02_NSW_LGA.csv",
        "abs_census/2016Census_G02_NSW_LGA.csv",
    ),
    (
        "_archives/2016_GCP_LGA_for_NSW_short-header.zip",
        "2016 Census GCP Local Government Areas for NSW/2016Census_G32_NSW_LGA.csv",
        "abs_census/2016Census_G32_NSW_LGA.csv",
    ),
    (
        "_archives/2016_GCP_LGA_for_NSW_short-header.zip",
        "Metadata/2016Census_geog_desc_1st_and_2nd_release.xlsx",
        "abs_census/2016Census_geog_desc_1st_and_2nd_release.xlsx",
    ),
    (
        "_archives/2021_GCP_LGA_for_NSW_short-header.zip",
        "2021 Census GCP Local Government Areas for NSW/2021Census_G02_NSW_LGA.csv",
        "abs_census/2021Census_G02_NSW_LGA.csv",
    ),
    (
        "_archives/2021_GCP_LGA_for_NSW_short-header.zip",
        "Metadata/2021Census_geog_desc_1st_2nd_3rd_release.xlsx",
        "abs_census/2021Census_geog_desc_1st_2nd_3rd_release.xlsx",
    ),
]


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        temporary_path.write_bytes(content)
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def fetch_file(session, url, path):
    response = session.get(url, timeout=60)
    response.raise_for_status()
    content = response.content
    if path.suffix in {".xlsx", ".zip"} and not is_zipfile(BytesIO(content)):
        raise ValueError(f"Expected an Excel or ZIP file from {url}")
    if path.suffix == ".xls" and not content.startswith(bytes.fromhex("D0 CF 11 E0 A1 B1 1A E1")):
        raise ValueError(f"Expected an XLS workbook from {url}")
    if path.suffix == ".geojson":
        features = response.json()
        if features.get("type") != "FeatureCollection" or not features.get("features"):
            raise ValueError(f"Expected a GeoJSON feature collection from {url}")
    if path.suffix == ".csv" and content.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        raise ValueError(f"Expected CSV data from {url}")
    write_file(path, content)


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


def sha256(path):
    with path.open("rb") as raw_file:
        return hashlib.file_digest(raw_file, "sha256").hexdigest()


def verify_existing(rows):
    verified = True
    for filename, row in rows.items():
        path = RAW_DIR / filename
        if not path.exists():
            continue
        actual = sha256(path)
        if actual != row["sha256"]:
            print(f"WARNING: SHA-256 mismatch for {path}")
            print(f"  expected {row['sha256']}")
            print(f"  actual   {actual}")
            verified = False
    return verified


def record_file(rows, filename, url, licence, downloaded_on):
    path = RAW_DIR / filename
    rows[filename] = {
        "filename": filename,
        "source_url": url,
        "downloaded_on": downloaded_on,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "licence": licence,
    }


def ensure_download(session, rows, url, filename, licence):
    path = RAW_DIR / filename
    if path.exists():
        print(f"Present {filename}")
        if filename not in rows:
            record_file(rows, filename, url, licence, "")
        return True
    try:
        fetch_file(session, url, path)
    except (OSError, requests.RequestException, ValueError) as error:
        print(f"Failed {filename}: {error}")
        return False
    downloaded_on = datetime.now(ZoneInfo("Australia/Sydney")).date().isoformat()
    record_file(rows, filename, url, licence, downloaded_on)
    print(f"Downloaded {filename}")
    return True


def ensure_member(rows, archive_name, member, filename):
    path = RAW_DIR / filename
    if path.exists() and filename in rows:
        print(f"Present {filename}")
        return True
    archive = rows.get(archive_name)
    if not archive or not (RAW_DIR / archive_name).is_file():
        print(f"Failed {filename}: archive unavailable: {archive_name}")
        return False
    if not path.exists():
        try:
            with ZipFile(RAW_DIR / archive_name) as bundle:
                write_file(path, bundle.read(member))
        except (BadZipFile, KeyError, OSError) as error:
            print(f"Failed {filename}: {error}")
            return False
        print(f"Extracted {filename}")
    record_file(
        rows, filename, f"{archive['source_url']}#{quote(member)}",
        archive["licence"], archive["downloaded_on"],
    )
    return True


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_manifest()
    # Verify before fetching or extracting so a mismatch cannot update provenance.
    if not verify_existing(rows):
        print("Raw files and recorded manifest left untouched.")
        return 1

    downloads = [(url, f"dcj_sales/{name}", LICENCE) for url, name in DOWNLOADS]
    downloads.extend(CANDIDATE_DOWNLOADS)
    failures = 0
    with requests.Session() as session:
        for url, filename, licence in downloads:
            if not ensure_download(session, rows, url, filename, licence):
                failures += 1
    for archive_name, member, filename in CENSUS_MEMBERS:
        if not ensure_member(rows, archive_name, member, filename):
            failures += 1

    write_manifest(rows)
    total = len(downloads) + len(CENSUS_MEMBERS)
    print(f"{total - failures}/{total} listed files on disk.")
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(main())
