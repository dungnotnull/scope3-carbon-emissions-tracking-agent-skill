# PROJECT-detail.md — Scope 3 Carbon Emissions Tracking & Optimization

## Executive Summary
A harness that builds a defensible Scope 3 emissions inventory and reduction plan. It maps business activities to the 15 GHG Protocol Scope 3 categories, selects spend-based or activity-based methods per category, applies cited emission factors, assesses data quality, scores completeness, and produces an SBTi-aligned reduction roadmap. Every figure carries a method, factor source, and data-quality rating.

## Problem Statement
Scope 3 often exceeds 70% of total corporate emissions but is data-poor and methodologically tricky. Companies struggle to know which categories are material, which method to use, and how to set credible targets without greenwashing.

## Target Users & Use Cases
- **Sustainability lead** — "Build our first Scope 3 inventory." → category-mapped inventory + data-quality.
- **Procurement** — "Which suppliers drive our purchased-goods emissions?" → category 1 hotspot.
- **CFO/ESG reporting** — "Are our targets SBTi-credible?" → target check + roadmap.
- **Logistics** — "Emissions from upstream/downstream transport?" → categories 4 & 9.
- **Product team** — "Use-phase emissions of our product?" → category 11 estimate.

## Harness Architecture
```
/scope3-carbon-emissions-tracking
  Stage 1 Intake     → sub-requirements-gatherer        → business/value-chain profile
  Stage 2 Framework  → sub-evaluation-framework-selector→ material categories + methods
  Stage 3 Calculate  → sub-emissions-calculator         → category emissions
  Stage 4 Scoring    → sub-scoring-engine               → completeness + data quality
  Stage 5 Roadmap    → sub-improvement-roadmap          → SBTi-aligned reduction plan
```

## Full Sub-Skill Catalog
| Sub-skill | Purpose | Inputs | Outputs | Tools | Quality gate |
|-----------|---------|--------|---------|-------|--------------|
| requirements-gatherer | Profile | user | business/value-chain | Read | Activities + data sources captured |
| framework-selector | Categories/methods | profile | material categories + method | WebSearch | Materiality screen done |
| emissions-calculator | Compute | activity data, factors | category totals | WebFetch | Factor source + method per figure |
| scoring-engine | Score | inventory | completeness + DQ | — | Data-quality rating per category |
| improvement-roadmap | Reduce | inventory | SBTi roadmap | — | Levers w/ abatement + cost |

## Skill File Format Specification
Standard Claude skill format. See `skills/main.md`.

## E2E Execution Flow
Intake → materiality + method selection → calculation → completeness/DQ scoring → roadmap. Fallback to cached/spend-based factors if web down (flag). Error: missing activity data → use spend-based proxy, mark low data-quality.

## SECOND-KNOWLEDGE-BRAIN Integration
`knowledge_updater.py` crawls GHG Protocol/SBTi/emission-factor sources; dated append.

## Quality Gates
- Each category: method (spend vs. activity), factor source, data-quality rating.
- Materiality screen identifies which categories matter.
- Reduction targets checked against SBTi criteria.
- Anti-greenwashing: offsets separated from actual reductions.
- Uncertainty stated.

## Test Scenarios
See `tests/test-scenarios.md` (6 scenarios).

## Key Design Decisions
1. Materiality-first: focus on the few categories driving the footprint.
2. Method transparency: spend-based proxies clearly flagged as lower quality.
3. SBTi alignment for credible targets.
4. Offsets ≠ reductions — kept separate.
5. Data-quality rating on every category.
