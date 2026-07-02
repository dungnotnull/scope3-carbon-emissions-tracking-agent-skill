# SECOND-KNOWLEDGE-BRAIN - Scope 3 Carbon Emissions

## Core Concepts & Frameworks
- **GHG Protocol Scope 3 Standard** - 15 categories: (1) purchased goods/services, (2) capital goods, (3) fuel/energy-related, (4) upstream transport, (5) waste, (6) business travel, (7) employee commuting, (8) upstream leased assets, (9) downstream transport, (10) processing of sold products, (11) use of sold products, (12) end-of-life, (13) downstream leased assets, (14) franchises, (15) investments.
- **Calculation methods** - activity-based (quantity x emission factor; higher quality) vs. spend-based (spend x EEIO factor; lower quality, easier).
- **Emission factors** - DEFRA, US EPA, ecoinvent (process), EXIOBASE (spend/EEIO). Curated reference: data/emission_factors.json.
- **SBTi** - science-based targets aligned to 1.5C; Scope 3 target required if >40% of total; absolute-contraction floor ~4.2%/yr (encoded as SBTI_MIN_ANNUAL_REDUCTION_PCT).
- **Data quality** - pedigree/uncertainty rating per category (tiers A/B/C/D; see sub-scoring-engine.md).
- **ISO 14064/14067** - GHG inventory & product carbon footprint standards.
- **Offsets vs. reductions** - offsets are not emission reductions; report separately (avoid greenwashing).

## Key Reference Frameworks (citable)
| Framework | Source | Use |
|-----------|--------|-----|
| Scope 3 Standard | GHG Protocol/WRI-WBCSD | Category accounting |
| SBTi criteria | SBTi | Target setting (>=4.2%/yr 1.5C floor) |
| ISO 14064/14067 | ISO | Inventory/PCF |
| CDP questionnaire | CDP | Disclosure |

## Emission-Factor Reference (curated, cited)
Stored in data/emission_factors.json. Covers categories 1,2,3,4,5,6,7,9,11,12 with DEFRA 2024 (activity-based) and EXIOBASE/USEEIO 2024 (spend-based EEIO) factors, each with source URL, vintage, GWP set, and uncertainty. Refresh via tools/knowledge_updater.py.

## Key Research / References
| Title | Source | Year | Link | Relevance |
|-------|--------|------|------|-----------|
| Corporate Value Chain (Scope 3) Standard | GHG Protocol | 2011 | ghgprotocol.org | Core method |
| SBTi Corporate Net-Zero Standard | SBTi | 2021+ | sciencebasedtargets.org | Targets |
| UK GHG Conversion Factors 2024 | DEFRA | 2024 | gov.uk | Activity factors |
| GHG Emission Factors Hub | US EPA | 2024 | epa.gov | Activity + EEIO |

## State-of-the-Art Methods & Tools
Supplier-specific (primary) data collection; PCF exchange (PACT/WBCSD); hybrid spend+activity; carbon-accounting platforms; uncertainty propagation; marginal abatement cost curves (MACC).

## Authoritative Data Sources
ghgprotocol.org; sciencebasedtargets.org; gov.uk DEFRA factors; epa.gov; ecoinvent.org; exiobase.eu; cdp.net.

## Analytical Frameworks
15-category materiality screen; method-selection decision tree; data-quality pedigree matrix (A/B/C/D); marginal abatement cost curve (MACC) for roadmap; SBTi 1.5C credibility gate; offsets-separation greenwashing gate.

## Cluster Integration (science-industry)
This skill shares the framework-selector and scoring-engine sub-skills with cluster siblings:
- Idea 214 (science-industry sibling) - shares sub-evaluation-framework-selector + sub-scoring-engine.
- Idea 179 (science-industry sibling) - shares sub-scoring-engine data-quality pedigree.
- Idea 146 (science-industry sibling) - shares sub-evaluation-framework-selector materiality logic.
Cross-link: import/alias these sub-skills rather than duplicating the materiality + pedigree logic.

## Self-Update Protocol
tools/knowledge_updater.py weekly: crawl GHG/SBTi/factor sources; dedup by URL hash; append dated entries below.

## Knowledge Update Log
- 2026-06-18 - Seed: 15 categories, methods, SBTi, factors captured.
- 2026-07-02 - Phase 0-5 complete: factor reference dataset, executable engine, SBTi 4.2%/yr gate, cluster cross-links added.
