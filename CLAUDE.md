# CLAUDE.md - Scope 3 Carbon Emissions Tracking & Optimization (Idea 217)

**Skill name:** scope3-carbon-emissions-tracking
**Tagline:** Inventories and reduces value-chain (Scope 3) emissions across the 15 GHG Protocol categories, with SBTi-aligned reduction roadmaps.
**Cluster:** science-industry (siblings: 214, 179, 146)
**Source idea:** 217
**Current phase:** Complete - all phases 0-5 delivered, production-grade.

## Problem This Skill Solves
Scope 3 (indirect value-chain) emissions are usually the largest and hardest-to-measure share of a company footprint. This skill maps activities to the 15 GHG Protocol Scope 3 categories, selects calculation methods (spend-based vs. activity-based), applies cited emission factors, assesses data quality, scores the inventory, and produces an SBTi-aligned reduction roadmap.

## Harness Flow Summary
1. **Intake** -> sub-requirements-gatherer - business, value chain, data available, reporting goal.
2. **Framework selection** -> sub-evaluation-framework-selector - material Scope 3 categories + method per category.
3. **Emissions calculation** -> sub-emissions-calculator - apply emission factors, compute category totals, propagate uncertainty.
4. **Data-quality + scoring** -> sub-scoring-engine - inventory completeness + data-quality score.
5. **Roadmap** -> sub-improvement-roadmap - SBTi-aligned reduction levers by impact/cost (MACC).

## Sub-skills
- sub-requirements-gatherer.md
- sub-evaluation-framework-selector.md
- sub-emissions-calculator.md
- sub-scoring-engine.md
- sub-improvement-roadmap.md

## Executable Backing (no model required)
- tools/scope3_engine.py - deterministic 5-stage engine (materiality, calculator, scoring, roadmap). Run: `python tools/scope3_engine.py demo` or `python tools/scope3_engine.py run --profile profile.json`.
- tools/knowledge_updater.py - crawls GHG/SBTi/emission-factor sources; dedup append. Run: `python tools/knowledge_updater.py run`.
- data/emission_factors.json - curated, cited factor reference (DEFRA 2024, EPA 2024, EXIOBASE/USEEIO EEIO).
- tests/test_scope3.py - pytest suite covering all 6 scenarios. Run: `pytest tests/test_scope3.py -q`.

## Tools Required
WebSearch, WebFetch (DEFRA/EPA factors, GHG Protocol), Read, Write, Bash.

## Knowledge Sources
GHG Protocol Corporate Value Chain (Scope 3) Standard; SBTi; ISO 14064; emission-factor databases (DEFRA, US EPA, ecoinvent, EXIOBASE for spend-based); CDP; PCF (ISO 14067).

## Active Development Tasks
- [x] Scaffold deliverables
- [x] Add emission-factor reference table (data/emission_factors.json)
- [x] Implement executable engine (tools/scope3_engine.py)
- [x] Implement knowledge pipeline (tools/knowledge_updater.py)
- [x] Test suite covering 6 scenarios (tests/test_scope3.py)
- [x] Cluster cross-links (siblings 214/179/146)
- [ ] Track SBTi criteria updates (ongoing via knowledge_updater.py)

## Reference Docs
PROJECT-detail.md, PROJECT-DEVELOPMENT-PHASE-TRACKING.md, SECOND-KNOWLEDGE-BRAIN.md.
