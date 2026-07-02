---
name: sub-scoring-engine
description: Scores Scope 3 inventory completeness and per-category data quality using a pedigree matrix. Shared across the science-industry cluster.
---

## Purpose
Make the credibility of the inventory explicit and quantitative.

## Inputs
Computed inventory + methods used (from Stage 3).

## Procedure
1. **Completeness** = share of the 15 categories quantified and material: 100 x n_quantified / 15.
2. **Per-category data-quality (DQ) pedigree**:
   - Tier A (supplier-specific / primary): score 1.0
   - Tier B (activity-based, secondary factor): score 0.75
   - Tier C (spend-based EEIO proxy): score 0.5
   - Tier D (proxy/estimate/stale): score 0.25
3. **Weighted overall DQ score** = sum over categories of (emission_share x tier_score).
4. **Improvement priorities** = categories with high emissions AND low quality (Tier C/D, emissions >= 25% of total).
5. **Overall rating**: >=0.85 High | >=0.65 Moderate | >=0.45 Low | else Very low.

## Output
completeness_pct | weighted_dq_score | overall_rating | per_category (category, tco2e, dq_tier, dq_score, improvement_priority) | improvement_priorities[].

## Quality Gate
- [ ] Data-quality rating per category.
- [ ] Improvement priorities identified (high emissions x low quality).
- [ ] Overall rating stated.

## Backing Implementation
tools/scope3_engine.py :: score_inventory() / InventoryScore / DQ_TIERS.
