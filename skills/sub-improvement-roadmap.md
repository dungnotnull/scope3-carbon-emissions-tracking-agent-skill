---
name: sub-improvement-roadmap
description: Builds an SBTi-aligned Scope 3 reduction roadmap ranked by abatement potential and cost (MACC), keeping offsets separate from reductions. Shared across the science-industry cluster.
---

## Purpose
Turn the inventory into a credible, science-based decarbonization plan.

## Inputs
Inventory, data-quality scores, proposed target, planned offsets.

## Procedure
1. **Reduction levers** per hotspot category from the lever library (supplier engagement, low-carbon materials, modal shift, renewable PPA, eco-design, circularity, zero-waste, travel demand management, etc.). Each lever: abatement (% of category emissions) and annualised cost.
2. **Marginal Abatement Cost (MAC)** = cost / abatement_tco2e; order levers ascending by MAC (most cost-effective first).
3. **Priority** by abatement share of total footprint: high >=5% | medium >=2% | low.
4. **SBTi target credibility gate**: aligned only if proposed_annual_reduction_pct >= 4.2%/yr (1.5C absolute-contraction floor). Scope 3 target mandatory when Scope 3 > 40% of total.
5. **Offsets gate (anti-greenwashing)**: offsets reported SEPARATELY, never counted as reductions. Heavy offsets (>25% of footprint) combined with a below-target rate => greenwashing risk warning.
6. **Data-improvement track** for low-quality high-emission categories (from Stage 4).

## Output
Roadmap:
lever | category | abatement (tCO2e) | annual_cost | MAC (EUR/tCO2e) | SBTi-aligned? | priority,
plus sbti_target_aligned | sbti_note | offsets_tco2e | offsets_note | data_improvement_track[].

## Quality Gate
- [ ] Levers carry abatement + cost + MAC.
- [ ] SBTi check performed; below-target flagged.
- [ ] Offsets separated from reductions.
- [ ] Data-improvement track present.

## Backing Implementation
tools/scope3_engine.py :: build_roadmap() / Roadmap / SBTI_MIN_ANNUAL_REDUCTION_PCT.
