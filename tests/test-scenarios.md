# Test Scenarios - Scope 3 Carbon Emissions Tracking (Idea 217)

Authoritative, executable tests live in tests/test_scope3.py (pytest). The scenarios below map 1:1 to test functions and document intent, inputs, expected behaviour, and the pass criterion.

Run all: `pytest tests/test_scope3.py -q` (currently 10 tests, 6 scenario tests + 4 contract tests, all green).

## Scenario 1 - First inventory
**Input:** Manufacturer with spend data only.
**Expected:** Materiality screen, spend-based method, factor sources cited, data quality flagged low, roadmap.
**Pass:** Method + factor + DQ per category; spend-based flagged (Tier C).
**Test:** test_scenario_1_first_inventory_spend_based_flagged

## Scenario 2 - Category 1 hotspot
**Input:** Purchased-goods dominates footprint.
**Expected:** Identifies cat 1 hotspot; supplier-engagement lever; improvement to activity-based data.
**Pass:** Hotspot + data-improvement track includes category 1.
**Test:** test_scenario_2_category_1_hotspot_improvement_track

## Scenario 3 - SBTi target check
**Input:** Company proposes a 1%/yr reduction target.
**Expected:** Flags as below 1.5C trajectory; recommends SBTi-aligned rate (>=4.2%/yr).
**Pass:** Target credibility checked; 4.2%/yr accepted, 1%/yr rejected.
**Test:** test_scenario_3_sbti_below_target_flagged

## Scenario 4 - Offsets separated
**Input:** Company plans to "offset" a large share of its footprint with a weak target.
**Expected:** Offsets reported separately; not counted as reductions; greenwashing risk flagged.
**Pass:** Clear separation enforced; no lever equals offset figure; warning surfaced.
**Test:** test_scenario_4_offsets_separated_from_reductions

## Scenario 5 - Use-phase (category 11)
**Input:** Sells electrical appliances.
**Expected:** Estimates use-phase emissions with assumptions + uncertainty.
**Pass:** Cat 11 quantified with stated uncertainty band and eco-design lever.
**Test:** test_scenario_5_use_phase_category_11_quantified

## Scenario 6 - Factor source unavailable
**Input:** DEFRA/EPA unreachable (offline run).
**Expected:** Uses cached factors (data/emission_factors.json), flags vintage, lowers confidence.
**Pass:** Every result carries a cited factor source + method + uncertainty; vintage >= 2024.
**Test:** test_scenario_6_cached_factors_and_staleness

## Contract tests (engine integrity)
- test_materiality_screen_covers_all_15_categories
- test_unknown_factor_id_raises
- test_inventory_sorted_descending_by_emissions
- test_cli_demo_runs
