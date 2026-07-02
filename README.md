# Scope 3 Carbon Emissions Tracking & Optimization

> A production-grade, opensource-ready agent skill and executable engine for building a defensible Scope 3 emissions inventory across the 15 GHG Protocol categories, scoring data quality, and producing an SBTi-aligned reduction roadmap. Every figure carries a method, a cited emission factor, and a data-quality rating.

---

## Table of Contents
1. [Why this exists](#why-this-exists)
2. [What you get](#what-you-get)
3. [Architecture at a glance](#architecture-at-a-glance)
4. [The 15 GHG Protocol Scope 3 categories](#the-15-ghg-protocol-scope-3-categories)
5. [Data-quality tiers](#data-quality-tiers)
6. [Emission-factor reference](#emission-factor-reference)
7. [Installation](#installation)
8. [Quick start](#quick-start)
9. [CLI reference](#cli-reference)
10. [Profile schema](#profile-schema)
11. [Report / output format](#report--output-format)
12. [Quality gates](#quality-gates)
13. [SBTi credibility and anti-greenwashing gates](#sbti-credibility-and-anti-greenwashing-gates)
14. [Testing](#testing)
15. [Knowledge pipeline (self-updating brain)](#knowledge-pipeline-self-updating-brain)
16. [Project structure](#project-structure)
17. [Cluster integration](#cluster-integration)
18. [Design decisions](#design-decisions)
19. [Limitations and production checklist](#limitations-and-production-checklist)
20. [Contributing](#contributing)
21. [License](#license)

---

## Why this exists

Scope 3 (indirect value-chain) emissions are usually the **largest and hardest-to-measure** share of a corporate carbon footprint, often exceeding 70% of the total. Yet they are data-poor and methodologically tricky. Companies struggle to know:

- Which of the 15 GHG Protocol Scope 3 categories are **material** to them.
- Which **calculation method** to use per category (activity-based vs. spend-based).
- How to **cite factors** and **state uncertainty** defensibly.
- How to set **credible targets** that are SBTi-aligned and **not greenwashing**.

This project answers all four. It is both a set of agent sub-skills (markdown that guides an LLM) and a **deterministic, model-free executable engine** that runs the same pipeline end-to-end without any language model.

---

## What you get

- **5 sub-skills** (markdown) guiding the 5-stage harness:
  - `sub-requirements-gatherer` - boundary, activities, data, goal.
  - `sub-evaluation-framework-selector` - 15-category materiality + method.
  - `sub-emissions-calculator` - cited factors + uncertainty propagation.
  - `sub-scoring-engine` - completeness + per-category data quality (A/B/C/D).
  - `sub-improvement-roadmap` - MACC-ordered levers, SBTi gate, offsets separate.
- **A deterministic engine**: `tools/scope3_engine.py` (pure Python, stdlib only).
- **A curated, cited emission-factor reference**: `data/emission_factors.json`.
- **A self-updating knowledge pipeline**: `tools/knowledge_updater.py`.
- **A pytest suite**: `tests/test_scope3.py` (10 tests, all green).
- **A sample profile**: `examples/profile_manufacturer.json`.

No external services, no API keys, no model weights required to run the core pipeline.

---

## Architecture at a glance

~~~text
Stage 1 Intake      -> sub-requirements-gatherer         -> business / value-chain profile
Stage 2 Framework   -> sub-evaluation-framework-selector -> material categories + method
Stage 3 Calculate   -> sub-emissions-calculator           -> category emissions (cited)
Stage 4 Scoring     -> sub-scoring-engine                 -> completeness + data quality
Stage 5 Roadmap     -> sub-improvement-roadmap            -> SBTi-aligned MACC roadmap
~~~

Each stage is implemented both as a markdown sub-skill (for LLM guidance) and as a real Python function in `tools/scope3_engine.py` (for deterministic execution). The two are kept in lock-step: the markdown documents the output schema and quality gates; the engine enforces them.

---

## The 15 GHG Protocol Scope 3 categories

| # | Category | Typical method |
|---|----------|-----------------|
| 1 | Purchased goods & services | Spend-based (EEIO) or supplier-specific |
| 2 | Capital goods | Spend-based (EEIO) |
| 3 | Fuel- & energy-related activities (not in Scopes 1/2) | Activity-based |
| 4 | Upstream transportation & distribution | Activity-based (tonne-km) |
| 5 | Waste generated in operations | Activity-based (tonnes) |
| 6 | Business travel | Activity-based (passenger-km) |
| 7 | Employee commuting | Activity-based (passenger-km) |
| 8 | Upstream leased assets | Activity-based |
| 9 | Downstream transportation & distribution | Activity-based (tonne-km) |
| 10 | Processing of sold products | Activity-based / supplier |
| 11 | Use of sold products | Activity-based (kWh over lifetime) |
| 12 | End-of-life treatment of sold products | Activity-based (tonnes) |
| 13 | Downstream leased assets | Activity-based |
| 14 | Franchises | Activity-based |
| 15 | Investments | Activity-based / sector averages |

---

## Data-quality tiers

Every category result carries a data-quality (DQ) tier. The weighted average of these tiers (by emission share) produces an overall inventory confidence rating.

| Tier | Meaning | Score |
|------|---------|-------|
| A | Supplier-specific / primary PCF | 1.00 |
| B | Activity-based with a secondary emission factor | 0.75 |
| C | Spend-based EEIO proxy | 0.50 |
| D | Estimate / proxy / stale factor | 0.25 |

Overall rating: >= 0.85 High confidence | >= 0.65 Moderate | >= 0.45 Low | else Very low.

---

## Emission-factor reference

`data/emission_factors.json` is a curated, cited dataset. Each factor record includes:

- `factor_id`, `category` (1-15), `activity`, `unit_activity`
- `factor` (kgCO2e per unit_activity), `gwp_set` (AR5/AR6)
- `method` (activity-based | spend-based), `source`, `source_url`, `vintage`
- `uncertainty_pct` (one-sigma relative), `notes`

Current coverage spans categories 1, 2, 3, 4, 5, 6, 7, 9, 11, 12, drawing on:

- **UK DEFRA GHG Conversion Factors 2024** (activity-based)
- **US EPA GHG Emission Factors Hub / eGRID 2024** (activity-based)
- **EXIOBASE3 / USEEIO v2.0** (spend-based EEIO)

Refresh the dataset against the latest published values with:

~~~bash
python tools/knowledge_updater.py run
~~~

---

## Installation

~~~bash
git clone https://github.com/dungnotnull/scope3-carbon-emissions-tracking-agent-skill.git
cd scope3-carbon-emissions-tracking-agent-skill
~~~

Requirements:

- Python 3.9+ (uses `from __future__ import annotations`).
- No runtime dependencies. `pytest` is only needed to run the test suite.
- Optional: `requests` (the knowledge updater uses `urllib` by default and switches to `requests` automatically if installed).

Optional test dependency:

~~~bash
python -m pip install pytest
~~~

---

## Quick start

Run the bundled demo profile (no input file needed):

~~~bash
python tools/scope3_engine.py demo
~~~

Run on your own profile:

~~~bash
python tools/scope3_engine.py run --profile examples/profile_manufacturer.json
~~~

List emission factors for a category:

~~~bash
python tools/scope3_engine.py factors --category 1
~~~

Run the test suite:

~~~bash
pytest tests/test_scope3.py -q
~~~

---

## CLI reference

### scope3_engine.py

~~~text
python tools/scope3_engine.py run      --profile PATH   Run the full 5-stage pipeline on a profile JSON.
python tools/scope3_engine.py demo                        Run the bundled Scenario 1 demo profile.
python tools/scope3_engine.py factors  [--category N]    List emission factors (optionally filter by category 1-15).
~~~

### knowledge_updater.py

~~~text
python tools/knowledge_updater.py run         Fetch sources and append deduplicated entries to SECOND-KNOWLEDGE-BRAIN.md.
python tools/knowledge_updater.py run --dry-run   Print candidate entries without writing.
python tools/knowledge_updater.py sources     List configured source URLs.
~~~

---

## Profile schema

A profile is a JSON document describing the company, its boundary, the reporting goal, any proposed reduction target, planned offsets, and a list of activity/spend lines.

~~~json
{
  "company": "Acme Manufacturing Ltd",
  "boundary": "operational control",
  "reporting_goal": "SBTi target setting",
  "revenue_currency": "GBP",
  "proposed_target_annual_reduction_pct": 4.2,
  "offsets_planned_tco2e": 0.0,
  "activities": [
    {
      "category": 4,
      "description": "Inbound HGV freight",
      "quantity": 1200000,
      "unit_activity": "tonne-km",
      "factor_id": "DEFRA-TK-2024-HGV-RT",
      "method": "activity-based",
      "supplier_specific": false
    }
  ]
}
~~~

Each `factor_id` must exist in `data/emission_factors.json`. Unknown factor ids raise a clear `KeyError` (covered by a test).

---

## Report / output format

`scope3_engine.py run` prints a JSON report with this structure:

~~~text
{
  "company": "...",
  "profile": { "boundary", "goal", "n_activities" },
  "materiality": [ { category, name, material, method, dq_tier_expected, justification } x15 ],
  "inventory":   [ { category, name, description, activity_quantity, unit_activity,
                     method, factor_id, factor_value, factor_source, factor_source_url,
                     factor_vintage, gwp_set, tco2e, uncertainty_pct,
                     uncertainty_low_tco2e, uncertainty_high_tco2e, dq_tier } ],
  "score":       { completeness_pct, weighted_dq_score, overall_rating,
                   per_category[], improvement_priorities[], total_tco2e },
  "roadmap":     { levers[], sbti_target_aligned, sbti_min_required_rate,
                   proposed_rate, sbti_note, offsets_tco2e, offsets_note,
                   data_improvement_track[] },
  "total_tco2e", "total_uncertainty_low_tco2e", "total_uncertainty_high_tco2e"
}
~~~

The inventory is sorted descending by emissions. The roadmap levers are sorted ascending by marginal abatement cost (most cost-effective first).

---

## Quality gates

Each stage enforces explicit gates (also documented in each sub-skill):

- [ ] All 15 categories screened for materiality; every exclusion justified.
- [ ] Each material category shows method + factor source + vintage + DQ tier.
- [ ] Uncertainty range stated per category.
- [ ] Spend-based proxies flagged as low quality (Tier C).
- [ ] Completeness % and weighted overall DQ score computed.
- [ ] Improvement priorities identified (high emissions x low quality).
- [ ] Reduction levers carry abatement, cost, and MAC.
- [ ] Targets checked against SBTi 1.5C criteria.
- [ ] Offsets separated from reductions.
- [ ] Data-improvement track present for weak categories.

---

## SBTi credibility and anti-greenwashing gates

The roadmap stage runs two hard gates:

**SBTi target credibility.** A proposed annual reduction rate is credible only if it meets or exceeds the SBTi 1.5C absolute-contraction floor, encoded as `SBTI_MIN_ANNUAL_REDUCTION_PCT = 4.2` (%/yr). A below-floor rate is flagged as not science-based. A Scope 3 target is mandatory when Scope 3 exceeds 40% of the total footprint.

**Offsets separation (anti-greenwashing).** Planned offsets are reported in a separate field and are **never** counted as emission reductions inside the inventory or the roadmap. Heavy reliance on offsets (more than 25% of the footprint) combined with a below-target reduction rate triggers a greenwashing-risk warning.

---

## Testing

`tests/test_scope3.py` covers the six scenarios documented in `tests/test-scenarios.md`, plus four engine contract tests.

~~~bash
pytest tests/test_scope3.py -q
~~~

Scenario coverage:

1. First inventory - spend-based proxy flagged as low quality (Tier C).
2. Category 1 hotspot - data-improvement track and supplier-engagement lever.
3. SBTi target check - 1%/yr rejected, 4.2%/yr accepted.
4. Offsets separated - offsets never equal a lever abatement; greenwashing warning surfaced.
5. Use-phase (category 11) - quantified with uncertainty band and eco-design lever.
6. Cached factors - offline run uses the cited reference; every result carries source, method, and uncertainty.

Contract tests:

- Materiality screen covers all 15 categories.
- Unknown factor id raises.
- Inventory sorted descending by emissions.
- CLI `demo` produces valid JSON.

---

## Knowledge pipeline (self-updating brain)

`tools/knowledge_updater.py` keeps the knowledge base fresh. It:

- Fetches 7 authoritative sources (GHG Protocol, SBTi, DEFRA, EPA, CDP, ecoinvent, EXIOBASE).
- Uses stdlib `urllib` + `html.parser` (switches to `requests` if installed).
- Is fault-tolerant per source: one unreachable URL never aborts the run.
- Scores entries by keyword relevance and recency.
- Deduplicates by a stable URL hash stored as an HTML comment marker.
- Appends dated, deduplicated entries under a dated section in `SECOND-KNOWLEDGE-BRAIN.md`.

Run weekly in production (for example via cron / GitHub Actions).

---

## Project structure

~~~text
.
+- CLAUDE.md                              Skill manifest / context
+- PROJECT-detail.md                     Design document
+- PROJECT-DEVELOPMENT-PHASE-TRACKING.md Phase tracker (all phases 0-5 DONE)
+- SECOND-KNOWLEDGE-BRAIN.md             Self-updating knowledge base
+- README.md                             This file
+- .gitignore
+- data/
|   +- emission_factors.json              Curated, cited emission-factor reference
+- examples/
|   +- profile_manufacturer.json         Sample profile
+- skills/
|   +- main.md                            Harness / main skill
|   +- sub-requirements-gatherer.md       Stage 1
|   +- sub-evaluation-framework-selector.md Stage 2
|   +- sub-emissions-calculator.md        Stage 3
|   +- sub-scoring-engine.md              Stage 4
|   +- sub-improvement-roadmap.md         Stage 5
+- tests/
|   +- test-scenarios.md                  Scenario documentation
|   +- test_scope3.py                     pytest suite (10 tests)
+- tools/
    +- scope3_engine.py                   Deterministic 5-stage engine (CLI)
    +- knowledge_updater.py               Source crawler + dedup append (CLI)
~~~

---

## Cluster integration

This skill is part of the **science-industry cluster** and shares the framework-selector and scoring-engine sub-skills with siblings:

- **Idea 214** - shares `sub-evaluation-framework-selector` materiality logic.
- **Idea 179** - shares `sub-scoring-engine` data-quality pedigree matrix.
- **Idea 146** - shares `sub-evaluation-framework-selector` method-selection decision tree.

Import or alias these sub-skills across the cluster rather than duplicating the materiality and pedigree logic.

---

## Design decisions

1. **Materiality-first.** Focus on the few categories that drive the footprint.
2. **Method transparency.** Spend-based proxies are clearly flagged as lower quality (Tier C).
3. **Cited factors.** Every figure carries a source, vintage, and GWP set.
4. **Uncertainty stated.** A one-sigma band is computed and reported per category.
5. **SBTi alignment.** Credible targets must meet the 1.5C absolute-contraction floor.
6. **Offsets != reductions.** Kept strictly separate to avoid greenwashing.
7. **Deterministic engine.** The same pipeline runs without an LLM, for reproducibility and CI.
8. **Pure stdlib.** No runtime dependencies; runs anywhere Python 3.9+ is available.

---

## Limitations and production checklist

The engine is production-grade and runnable today. Before external reporting, complete this checklist:

- [ ] Run `python tools/knowledge_updater.py run` once to refresh factors against the latest published DEFRA / EPA / EXIOBASE datasets.
- [ ] Validate each `factor_id` against the latest source vintage for your reporting year.
- [ ] Add supplier-specific (Tier A) data where available to upgrade low-quality categories.
- [ ] Confirm the organizational boundary and excluded entities with your auditor.
- [ ] For materiality beyond data availability, apply the size/influence/risk judgement described in `sub-evaluation-framework-selector.md`.

Note: the deterministic engine treats a category as material when the profile provides data for it. The markdown sub-skill generalises this with size/influence/risk judgement. This is intentional for an agent skill; promote richer heuristic materiality into the engine if you need a pure-CLI scorer.

---

## Contributing

Contributions are welcome. Please:

1. Keep the markdown sub-skills and the engine in lock-step (output schema + quality gates).
2. Add or update a test for any behavioural change.
3. Cite any new emission factor with a source URL and vintage.
4. Keep the code stdlib-only at runtime (no new hard runtime dependencies).

~~~bash
pytest tests/test_scope3.py -q
~~~

must stay green before merging.

---

## License

MIT. See `LICENSE` for terms.
