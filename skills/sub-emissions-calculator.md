---
name: sub-emissions-calculator
description: Computes Scope 3 category emissions by applying cited emission factors to activity or spend data, with uncertainty propagation. Stage 3 of the harness.
---

## Purpose
Produce sourced, reproducible category emission figures with explicit uncertainty.

## Inputs
Activity/spend data, selected methods, cited emission factors (web or cached in data/emission_factors.json).

## Procedure
For each material category:
1. **Apply the formula**:
   - activity-based: tCO2e = quantity x emission_factor / 1000
   - spend-based (EEIO): tCO2e = spend x EEIO_factor / 1000
2. **Cite the factor source** (DEFRA / EPA / ecoinvent / EXIOBASE) and vintage; record GWP set (AR5/AR6).
3. **Convert to tCO2e** including relevant GHGs via GWP.
4. **Propagate uncertainty**: one-sigma band +/- factor_value x (uncertainty_pct/100); report low/high tCO2e.
5. **Sum to a total** with a clear breakdown, sorted descending by emissions.

## Output
Per-category emissions row:
category | name | activity/spend | unit | method | factor_id | factor (source/vintage) | tCO2e | uncertainty_low | uncertainty_high | DQ tier.

## Quality Gate
- [ ] Every figure has a factor source + method + vintage.
- [ ] Uncertainty range stated per category.
- [ ] Spend-based proxies flagged Tier C.
- [ ] Inventory sorted descending; total reconciles.

## Factor Reference
data/emission_factors.json - curated, cited factors (DEFRA 2024, EPA 2024, EXIOBASE/USEEIO EEIO) covering categories 1,2,3,4,5,6,7,9,11,12. Refresh via tools/knowledge_updater.py.

## Backing Implementation
tools/scope3_engine.py :: calculate_emissions() / CategoryResult / load_factors().
