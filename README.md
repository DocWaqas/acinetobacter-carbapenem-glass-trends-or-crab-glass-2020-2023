# Regional and Temporal Trends in Carbapenem Resistance in *Acinetobacter* spp.

Analysis of carbapenem (meropenem, imipenem) resistance in *Acinetobacter* spp. bloodstream infections across WHO regions, 2020-2023, using WHO GLASS surveillance data.

## Research question

How does carbapenem resistance in *Acinetobacter* spp. bloodstream isolates vary by WHO region and over time (2020-2023), and how much of any apparent temporal trend is attributable to changes in which countries report to GLASS each year rather than genuine epidemiological change?

## Method summary

- Data source: WHO GLASS-AMR dashboard, filtered to bloodstream infections, *Acinetobacter* spp., 2020-2023, all six WHO regions.
- Because the set of countries reporting to GLASS changes year to year, the primary analysis restricts each region to a **fixed panel** of countries that reported continuously across all four years, and computes an isolate-weighted (not simple-average) resistance percentage from that fixed panel.
- A secondary, unrestricted (all-reporting-countries) analysis is included for comparison, to demonstrate the size of the panel-composition effect.

## Key findings

- The **Western Pacific Region** showed consistently and substantially lower carbapenem resistance than every other WHO region across all four years (~20-27%), a pattern that held even after fixed-panel correction.
- The **African Region**, **Region of the Americas**, and **Eastern Mediterranean Region** showed the highest resistance, frequently exceeding 70%.
- **Reporting-panel composition materially distorts apparent trends** if not controlled for: the unrestricted analysis suggested a steep decline in the Region of the Americas (84% to 35%, 2020-2023), while the fixed-panel analysis showed a much more modest decline (84% to 72%) once newly-added lower-resistance countries were excluded from the comparison.

## Repository structure

```
scripts/     - data combination, analysis, and figure-generation code (Python)
data/        - combined and summarized datasets (CSV)
figures/     - output figures (PNG)
manuscript/  - draft manuscript
```

## Reproducing this analysis

1. `scripts/combine_glass_data.py` — combines raw GLASS dashboard exports into a single dataset
2. `scripts/analyze_carbapenems.py` — computes pooled and fixed-panel resistance statistics
3. `scripts/make_figures.py` — generates the two primary figures from the fixed-panel data

Requires Python 3 with `matplotlib` (`pip install matplotlib`). No other dependencies.

## Manuscript

A draft manuscript describing this analysis in full (introduction, methods, results, discussion, references) is in `manuscript/`. Preprint submission link: *to be added once posted*.

## Limitations

This is a descriptive, hypothesis-generating pilot analysis of passive national surveillance data, not a causal or fully adjusted epidemiological study. See the manuscript's Limitations section for full detail, including small fixed-panel country counts in some regions and known biases in passive AMR surveillance reporting.

## Author

Dr. Mohammad Waqas Farhat
ORCID: [0000-0002-8789-8794](https://orcid.org/0000-0002-8789-8794)

## License

MIT
