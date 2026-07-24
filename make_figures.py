"""
Generates the two primary figures for the manuscript, using the fixed-panel
(countries reporting continuously 2020-2023) isolate-weighted resistance
estimates, per the decision to use fixed-panel as the primary analysis.

Figure 1: Trend lines, meropenem and imipenem side by side, one line per
          WHO region, 2020-2023.
Figure 2: Bar chart, 2023 snapshot comparison across regions, both drugs.
"""
import csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

IN_FILE = "/home/claude/amr_project/glass_acinetobacter_combined_2020_2023.csv"
DRUGS = ["Meropenem", "Imipenem"]
YEARS = [2020, 2021, 2022, 2023]

REGION_COLORS = {
    "African Region": "#D95F02",
    "Region of the Americas": "#1B9E77",
    "Eastern Mediterranean Region": "#7570B3",
    "European Region": "#E7298A",
    "South-East Asia Region": "#66A61E",
    "Western Pacific Region": "#E6AB02",
}
REGION_SHORT = {
    "African Region": "Africa",
    "Region of the Americas": "Americas",
    "Eastern Mediterranean Region": "E. Mediterranean",
    "European Region": "Europe",
    "South-East Asia Region": "SE Asia",
    "Western Pacific Region": "W. Pacific",
}

def load_rows():
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
            })
    return rows

def fixed_panel_series(rows):
    """
    For each region+drug, find countries present in ALL 4 years, then compute
    isolate-weighted % resistant per year using only those countries.
    Returns: {(region, drug): {year: pct}}
    """
    by_region_drug = defaultdict(list)
    for r in rows:
        by_region_drug[(r["region"], r["drug"])].append(r)

    series = {}
    for (region, drug), recs in by_region_drug.items():
        by_year_countries = defaultdict(set)
        for r in recs:
            by_year_countries[r["year"]].add(r["country"])
        years_present = set(by_year_countries.keys())
        if years_present != set(YEARS):
            continue  # only keep regions with all 4 years available
        fixed = set.intersection(*by_year_countries.values())
        if len(fixed) < 1:
            continue

        year_pct = {}
        for year in YEARS:
            tested = resistant = 0
            for r in recs:
                if r["year"] == year and r["country"] in fixed:
                    tested += r["tested"]
                    resistant += r["resistant"]
            year_pct[year] = (100.0 * resistant / tested) if tested else None
        series[(region, drug)] = {"pct_by_year": year_pct, "n_fixed": len(fixed)}
    return series

def make_figure1(series):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
    for ax, drug in zip(axes, DRUGS):
        for region in REGION_COLORS:
            key = (region, drug)
            if key not in series:
                continue
            pct = series[key]["pct_by_year"]
            ys = [pct[y] for y in YEARS]
            ax.plot(YEARS, ys, marker="o", linewidth=2, markersize=5,
                     color=REGION_COLORS[region], label=REGION_SHORT[region])
        ax.set_title(drug, fontsize=12, fontweight="bold")
        ax.set_xlabel("Year")
        ax.set_xticks(YEARS)
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter())
        ax.grid(axis="y", alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[0].set_ylabel("Isolate-weighted resistance (%)\n(fixed-panel countries)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.08), fontsize=9)
    fig.suptitle("Figure 1. Carbapenem resistance trends in Acinetobacter spp.\nbloodstream isolates by WHO region, 2020-2023 (fixed-panel countries)",
                 fontsize=12, y=1.03)
    fig.tight_layout()
    out = "/home/claude/amr_project/figure1_trends.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out

def make_figure2(series):
    regions = [r for r in REGION_COLORS if (r, "Meropenem") in series or (r, "Imipenem") in series]
    # order by meropenem 2023 value descending, for readability
    def sort_key(r):
        v = series.get((r, "Meropenem"), {}).get("pct_by_year", {}).get(2023)
        return -(v if v is not None else -1)
    regions = sorted(regions, key=sort_key)

    x = range(len(regions))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5.5))

    mero_vals = [series.get((r, "Meropenem"), {}).get("pct_by_year", {}).get(2023) for r in regions]
    imi_vals = [series.get((r, "Imipenem"), {}).get("pct_by_year", {}).get(2023) for r in regions]

    b1 = ax.bar([i - width/2 for i in x], mero_vals, width, label="Meropenem", color="#3182BD")
    b2 = ax.bar([i + width/2 for i in x], imi_vals, width, label="Imipenem", color="#E6550D")

    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            if h is not None:
                ax.annotate(f"{h:.0f}%", (bar.get_x() + bar.get_width()/2, h),
                            ha="center", va="bottom", fontsize=8)

    ax.set_xticks(list(x))
    ax.set_xticklabels([REGION_SHORT[r] for r in regions], rotation=20, ha="right")
    ax.set_ylabel("Isolate-weighted resistance (%)\n(fixed-panel countries)")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.set_title("Figure 2. Carbapenem resistance in Acinetobacter spp. bloodstream\nisolates by WHO region, 2023 (fixed-panel countries)", fontsize=12)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out = "/home/claude/amr_project/figure2_2023_comparison.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out

if __name__ == "__main__":
    rows = load_rows()
    series = fixed_panel_series(rows)
    print("Regions/drugs with complete 4-year fixed panels:")
    for (region, drug), v in sorted(series.items()):
        print(f"  {region} / {drug}: {v['n_fixed']} fixed countries, values={v['pct_by_year']}")

    f1 = make_figure1(series)
    f2 = make_figure2(series)
    print(f"\nSaved: {f1}")
    print(f"Saved: {f2}")
