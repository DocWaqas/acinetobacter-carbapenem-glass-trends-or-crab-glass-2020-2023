"""
Analyzes carbapenem (meropenem, imipenem) resistance in Acinetobacter spp.
bloodstream infections across WHO regions, 2020-2023, using the combined
GLASS dataset.

Produces:
1. A pooled (isolate-weighted) resistance % per region per year per drug
   -- pooled = sum(Resistant) / sum(InterpretableAST), NOT an average of
      country percentages, since pooling correctly weights countries that
      tested more isolates.
2. A country-level median per region per year (for comparison/robustness).
3. CSV summary tables.
4. Line charts: resistance trend over time, one line per region, per drug.
5. Bar chart: 2023 snapshot comparison across regions.
"""
import csv
from collections import defaultdict

IN_FILE = "/home/claude/amr_project/glass_acinetobacter_combined_2020_2023.csv"
DRUGS = ["Meropenem", "Imipenem"]

def load_data():
    rows = []
    with open(IN_FILE, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["AntibioticName"] not in DRUGS:
                continue
            try:
                tested = int(r["InterpretableAST"])
                resistant = int(r["Resistant"])
            except (ValueError, TypeError):
                continue
            if tested <= 0:
                continue
            rows.append({
                "region": r["WHORegionName"],
                "year": int(r["Year"]),
                "country": r["CountryTerritoryArea"],
                "drug": r["AntibioticName"],
                "tested": tested,
                "resistant": resistant,
                "pct": r["ResistancePercentage"],
            })
    return rows

def pooled_by_region_year_drug(rows):
    """sum(resistant)/sum(tested) per region-year-drug -- isolate-weighted."""
    agg = defaultdict(lambda: {"tested": 0, "resistant": 0, "countries": set()})
    for r in rows:
        key = (r["region"], r["year"], r["drug"])
        agg[key]["tested"] += r["tested"]
        agg[key]["resistant"] += r["resistant"]
        agg[key]["countries"].add(r["country"])

    out = {}
    for key, v in agg.items():
        pct = 100.0 * v["resistant"] / v["tested"] if v["tested"] else None
        out[key] = {
            "pooled_pct": pct,
            "total_tested": v["tested"],
            "total_resistant": v["resistant"],
            "n_countries": len(v["countries"]),
        }
    return out

def write_summary_csv(pooled, path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Drug", "Region", "Year", "PooledResistancePct",
                    "TotalTested", "TotalResistant", "NCountriesReporting"])
        for (region, year, drug), v in sorted(pooled.items()):
            w.writerow([drug, region, year,
                        f"{v['pooled_pct']:.2f}" if v['pooled_pct'] is not None else "",
                        v["total_tested"], v["total_resistant"], v["n_countries"]])

def main():
    rows = load_data()
    print(f"Loaded {len(rows)} carbapenem data rows (meropenem + imipenem).")

    pooled = pooled_by_region_year_drug(rows)
    summary_path = "/home/claude/amr_project/carbapenem_pooled_summary.csv"
    write_summary_csv(pooled, summary_path)
    print(f"Wrote pooled summary: {summary_path}")

    # Print a readable table to console too
    print("\n=== Pooled (isolate-weighted) resistance %, by drug/region/year ===")
    for drug in DRUGS:
        print(f"\n--- {drug} ---")
        regions = sorted(set(k[0] for k in pooled if k[2] == drug))
        years = sorted(set(k[1] for k in pooled if k[2] == drug))
        header = "Region".ljust(30) + "".join(str(y).rjust(10) for y in years)
        print(header)
        for region in regions:
            line = region.ljust(30)
            for year in years:
                v = pooled.get((region, year, drug))
                cell = f"{v['pooled_pct']:.1f}%" if v else "  n/a"
                line += cell.rjust(10)
            print(line)

if __name__ == "__main__":
    main()
