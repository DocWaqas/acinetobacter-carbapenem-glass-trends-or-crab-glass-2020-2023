"""
Combines all GLASS dashboard export CSVs (one per region/year) into a single
master table of country-level Acinetobacter spp. bloodstream resistance data.

Each source file has three stacked sections; we only want the third section,
"Data for boxplots", which has real country-level rows:
Specimen, PathogenName, AntibioticName, Iso3, CountryTerritoryArea,
WHORegionName, InterpretableAST, Resistant, ResistancePercentage
"""
import csv
import glob
import os
import re

SRC_DIR = "/mnt/user-data/uploads"
OUT_FILE = "/home/claude/amr_project/glass_acinetobacter_combined_2020_2023.csv"

# Extract year from filename, e.g. "...in_2021_European_Region-..." -> 2021
YEAR_RE = re.compile(r"in_(\d{4})_")

def extract_year(filename):
    m = YEAR_RE.search(filename)
    return int(m.group(1)) if m else None

def parse_file(path, year):
    """Return list of dict rows from the 'Data for boxplots' section."""
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        content = f.read()

    lines = content.splitlines()

    # Find the boxplot section header
    start_idx = None
    for i, line in enumerate(lines):
        if "Data for boxplots" in line:
            start_idx = i
            break
    if start_idx is None:
        print(f"  WARNING: no boxplot section found in {os.path.basename(path)}")
        return rows

    # Header row is the next non-empty line after the section title
    header_idx = None
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip():
            header_idx = i
            break

    reader = csv.reader(lines[header_idx:])
    header = next(reader)
    header = [h.strip().strip('"') for h in header]

    for row in reader:
        if not row or not row[0].strip():
            continue
        row = [c.strip().strip('"') for c in row]
        if len(row) != len(header):
            continue
        record = dict(zip(header, row))
        record["Year"] = year
        record["SourceFile"] = os.path.basename(path)
        rows.append(record)

    return rows

def main():
    pattern = os.path.join(SRC_DIR, "*.csv")
    all_files = sorted(glob.glob(pattern))

    all_rows = []
    seen_signatures = set()  # to drop the duplicate 2023 Africa file
    file_summary = []

    for path in all_files:
        fname = os.path.basename(path)
        year = extract_year(fname)
        if year is None:
            print(f"  SKIPPING (no year found in name): {fname}")
            continue

        rows = parse_file(path, year)

        # Dedup signature: region+year+first row content (catches exact duplicate exports)
        sig = (year, tuple(sorted(r.get("CountryTerritoryArea","") for r in rows)))
        content_sig = (year, rows[0].get("WHORegionName") if rows else None, len(rows))

        file_summary.append((fname, year, len(rows)))
        all_rows.extend(rows)

    # Deduplicate exact repeat rows (same region+year+country+antibiotic+resistant count)
    dedup = {}
    for r in all_rows:
        key = (r.get("WHORegionName"), r["Year"], r.get("CountryTerritoryArea"),
               r.get("AntibioticName"), r.get("Resistant"), r.get("InterpretableAST"))
        dedup[key] = r  # later one overwrites, but content identical for true dupes

    final_rows = list(dedup.values())

    fieldnames = ["WHORegionName", "Year", "Iso3", "CountryTerritoryArea",
                  "Specimen", "PathogenName", "AntibioticName",
                  "InterpretableAST", "Resistant", "ResistancePercentage",
                  "SourceFile"]

    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in sorted(final_rows, key=lambda x: (x.get("WHORegionName",""), x["Year"], x.get("CountryTerritoryArea",""), x.get("AntibioticName",""))):
            writer.writerow(r)

    print("\n=== Per-file row counts ===")
    for fname, year, n in file_summary:
        print(f"  {year}  {n:4d} rows   {fname}")

    print(f"\nTotal raw rows parsed: {len(all_rows)}")
    print(f"Total rows after de-duplication: {len(final_rows)}")
    print(f"Written to: {OUT_FILE}")

if __name__ == "__main__":
    main()
