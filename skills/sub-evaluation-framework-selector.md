---
name: sub-evaluation-framework-selector
description: Runs a Scope 3 materiality screen over the 15 categories and selects the calculation method per material category. Shared across the science-industry cluster.
---

## Purpose
Focus effort on the few categories that matter (materiality) and choose the right calculation method per category, with an expected data-quality tier. Shared with cluster siblings 214/179/146.

## Inputs
Business/value-chain profile + per-category data availability from Stage 1.

## Procedure
1. **Screen all 15 categories** for materiality on three axes: size (estimated emission share), influence (ability to reduce), risk (stakeholder/regulatory). A category is material if data is available OR it is structurally relevant (e.g. cat 11 for appliance sellers, cat 15 for financials).
2. **Method-selection decision tree per material category**:
   - Supplier-specific PCF available? -> activity-based, Tier A.
   - Physical quantity + secondary factor available? -> activity-based, Tier B.
   - Only spend data? -> spend-based EEIO, Tier C.
   - Nothing? -> excluded with justification, or estimate flagged Tier D.
3. **Expected data-quality tier** recorded per category (A/B/C/D).
4. **Justify every exclusion** (immaterial / not applicable / no data) - no silent omissions.

## Output
Category table: category | name | material? | method | expected DQ tier | justification.

~~~text
| Cat | Name | Material? | Method | DQ | Justification |
|-----|------|-----------|--------|----|---------------|
~~~

## Quality Gate
- [ ] All 15 categories screened.
- [ ] Method + expected DQ tier per material category.
- [ ] Every exclusion justified.

## Backing Implementation
tools/scope3_engine.py :: materiality_screen() / MaterialityRow.
