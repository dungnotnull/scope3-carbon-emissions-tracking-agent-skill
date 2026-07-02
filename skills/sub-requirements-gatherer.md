---
name: sub-requirements-gatherer
description: Captures business model, value-chain activities, available data, and reporting goal for a Scope 3 inventory. Stage 1 of the harness.
---

## Purpose
Establish the accounting boundary and the data basis for the Scope 3 inventory before any category is calculated. Everything downstream depends on this intake.

## Inputs
- User business description; organizational structure (subsidiaries, JVs, franchises, leased assets).
- Procurement spend data (by category/SKU, currency).
- Physical activity quantities (litres, kWh, tonne-km, passenger-km, tonnes waste).
- Supplier-specific data available (PCF/PACT/CDP Supply Chain).
- Travel, commute, logistics records.
- Product use-phase assumptions (energy rating, units sold, lifetime, geography/grid).
- Reporting goal: first inventory, CDP disclosure, SBTi target, regulatory (CSRD/SEC).

## Procedure
1. **Organizational & operational boundary** - confirm equity share vs. operational/financial control consolidation; list excluded entities with rationale.
2. **Value-chain activity inventory** - map activities to the 15 GHG Protocol Scope 3 categories (SCOPE3_CATEGORIES in tools/scope3_engine.py). Record at least an order-of-magnitude estimate per category.
3. **Data availability register** - for each of the 15 categories tag the best available tier:
   - Tier A: supplier-specific / primary PCF.
   - Tier B: activity-based with secondary emission factor (DEFRA/EPA/ecoinvent).
   - Tier C: spend-based EEIO proxy (EXIOBASE/USEEIO).
   - Tier D: estimate / proxy / stale factor.
4. **Currency & units** - record base currency; EEIO spend must match the factor currency (deflate annually).
5. **Reporting goal** - capture audience and any proposed reduction target (%/yr, base year).
6. **Data gaps** - list categories with no data and the effort to obtain it (feeds the Stage 5 data-improvement track).

## Output Schema
~~~json
{
  "company": "string",
  "boundary": "operational control | financial control | equity share",
  "reporting_goal": "first inventory | CDP | SBTi | regulatory",
  "revenue_currency": "GBP | USD | EUR",
  "activities": [
    {"category": 1, "description": "...", "quantity": 0.0,
     "unit_activity": "...", "factor_id": "...",
     "method": "activity-based | spend-based",
     "supplier_specific": false, "currency": null}
  ],
  "proposed_target_annual_reduction_pct": null,
  "offsets_planned_tco2e": 0.0,
  "notes": "per-category data gaps"
}
~~~

## Quality Gate
- [ ] All 15 categories have at least an explicit excluded/not-applicable decision.
- [ ] Each activity carries a declared method tier.
- [ ] Currency of spend matches the EEIO factor currency.
- [ ] Reporting goal and any proposed target captured.

## Backing Implementation
tools/scope3_engine.py :: gather_requirements() / Profile / ActivityInput. Consumed verbatim by Stage 2.
