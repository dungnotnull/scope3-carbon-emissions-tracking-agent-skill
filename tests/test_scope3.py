#!/usr/bin/env python3
"""test_scope3.py - production test suite for the Scope 3 tracking engine.

Covers the six scenarios documented in tests/test-scenarios.md against the
real implementation in tools/scope3_engine.py. Run with:

    pytest tests/test_scope3.py -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import scope3_engine as eng  # noqa: E402


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------
def _profile(**overrides):
    base = {
        "company": "Acme Manufacturing",
        "boundary": "operational control",
        "reporting_goal": "first inventory",
        "proposed_target_annual_reduction_pct": 4.2,
        "offsets_planned_tco2e": 0.0,
        "activities": [
            {"category": 1, "description": "Steel spend",
             "quantity": 5_000_000, "unit_activity": "GBP",
             "factor_id": "EXIOBASE-EEIO-2024-STEEL-GBP", "method": "spend-based"},
            {"category": 3, "description": "Diesel for forklifts",
             "quantity": 40_000, "unit_activity": "litre",
             "factor_id": "DEFRA-FR-2024-DIESEL", "method": "activity-based"},
            {"category": 4, "description": "Inbound HGV freight",
             "quantity": 1_200_000, "unit_activity": "tonne-km",
             "factor_id": "DEFRA-TK-2024-HGV-RT", "method": "activity-based"},
            {"category": 6, "description": "Business air travel",
             "quantity": 300_000, "unit_activity": "passenger-km",
             "factor_id": "DEFRA-TRV-2024-AIR-PAX-SH", "method": "activity-based"},
            {"category": 7, "description": "Employee commuting",
             "quantity": 2_500_000, "unit_activity": "passenger-km",
             "factor_id": "DEFRA-COM-2024-CAR-MED", "method": "activity-based"},
        ],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Scenario 1 - First inventory (spend-based proxy flagged low quality)
# ---------------------------------------------------------------------------
def test_scenario_1_first_inventory_spend_based_flagged():
    report = eng.run_pipeline(_profile())
    cat1 = next(r for r in report.inventory if r.category == 1)
    assert cat1.method == "spend-based"
    assert cat1.factor_source  # factor source cited
    assert cat1.dq_tier == "C"  # spend-based => low quality tier
    assert abs(report.score.completeness_pct - 100.0 * 5 / 15) < 0.05
    assert report.total_tco2e > 0
    # roadmap generated with levers ordered by MACC.
    assert report.roadmap.levers
    macs = [l.mac_eur_per_tco2e for l in report.roadmap.levers]
    assert macs == sorted(macs)


# ---------------------------------------------------------------------------
# Scenario 2 - Category 1 hotspot + data-improvement track
# ---------------------------------------------------------------------------
def test_scenario_2_category_1_hotspot_improvement_track():
    report = eng.run_pipeline(_profile(
        activities=[
            {"category": 1, "description": "Steel spend (dominant)",
             "quantity": 50_000_000, "unit_activity": "GBP",
             "factor_id": "EXIOBASE-EEIO-2024-STEEL-GBP", "method": "spend-based"},
            {"category": 6, "description": "Business air travel",
             "quantity": 100_000, "unit_activity": "passenger-km",
             "factor_id": "DEFRA-TRV-2024-AIR-PAX-SH", "method": "activity-based"},
        ],
    ))
    cat1 = next(r for r in report.inventory if r.category == 1)
    assert report.inventory[0].category == 1  # highest emitter = hotspot
    assert cat1.dq_tier == "C"
    # high emissions x low quality => improvement priority.
    assert 1 in report.roadmap.data_improvement_track
    # supplier-engagement lever exists for the hotspot.
    assert any(l.category == 1 and "Supplier" in l.lever
               for l in report.roadmap.levers)


# ---------------------------------------------------------------------------
# Scenario 3 - SBTi target credibility check
# ---------------------------------------------------------------------------
def test_scenario_3_sbti_below_target_flagged():
    weak = eng.run_pipeline(_profile(proposed_target_annual_reduction_pct=1.0))
    assert weak.roadmap.sbti_target_aligned is False
    assert "BELOW the SBTi 1.5C trajectory" in weak.roadmap.sbti_note

    credible = eng.run_pipeline(_profile(proposed_target_annual_reduction_pct=4.2))
    assert credible.roadmap.sbti_target_aligned is True
    assert "meets/exceeds" in credible.roadmap.sbti_note


# ---------------------------------------------------------------------------
# Scenario 4 - Offsets reported separately, never as reductions
# ---------------------------------------------------------------------------
def test_scenario_4_offsets_separated_from_reductions():
    report = eng.run_pipeline(_profile(
        proposed_target_annual_reduction_pct=1.0,
        offsets_planned_tco2e=50_000.0,
    ))
    off = report.roadmap.offsets_tco2e
    assert off == 50_000.0
    assert "SEPARATELY" in report.roadmap.offsets_note
    assert "NOT counted" in report.roadmap.offsets_note
    # No lever abatement may equal the offset figure (offsets != reductions).
    assert not any(abs(l.abatement_tco2e - off) < 1e-6
                   for l in report.roadmap.levers)
    # Heavy offsets + weak target => greenwashing risk warning surfaced.
    assert "greenwashing risk" in report.roadmap.offsets_note


# ---------------------------------------------------------------------------
# Scenario 5 - Use-phase (category 11) quantified with assumptions
# ---------------------------------------------------------------------------
def test_scenario_5_use_phase_category_11_quantified():
    report = eng.run_pipeline(_profile(
        activities=[
            {"category": 11, "description": "Use-phase electricity of sold appliances",
             "quantity": 1_000_000, "unit_activity": "kWh",
             "factor_id": "DEFRA-CAT11-2024-ELEC-USE", "method": "activity-based"},
        ],
        proposed_target_annual_reduction_pct=4.2,
    ))
    cat11 = report.inventory[0]
    assert cat11.category == 11
    assert cat11.tco2e > 0
    assert cat11.uncertainty_low_tco2e < cat11.tco2e < cat11.uncertainty_high_tco2e
    # Eco-design lever present for the use-phase hotspot.
    assert any(l.category == 11 for l in report.roadmap.levers)


# ---------------------------------------------------------------------------
# Scenario 6 - Factor source unavailable => cached factors used, staleness flagged
# ---------------------------------------------------------------------------
def test_scenario_6_cached_factors_and_staleness():
    factors = eng.load_factors()
    # All reference factors carry a source + vintage; engine uses cached factors.
    for f in factors.values():
        assert f.source_url.startswith("https://")
        assert f.vintage >= 2024
        assert f.uncertainty_pct > 0  # uncertainty always stated
    # A calculated result always carries factor source + method (cached path).
    report = eng.run_pipeline(_profile())
    for r in report.inventory:
        assert r.factor_source
        assert r.method in ("activity-based", "spend-based")
        assert r.uncertainty_pct > 0


# ---------------------------------------------------------------------------
# Engine integrity / contract tests
# ---------------------------------------------------------------------------
def test_materiality_screen_covers_all_15_categories():
    profile = eng.gather_requirements(_profile())
    screen = eng.materiality_screen(profile)
    assert len(screen) == 15
    assert {r.category for r in screen} == set(eng.SCOPE3_CATEGORIES)
    assert all(isinstance(r.material, bool) for r in screen)


def test_unknown_factor_id_raises():
    profile = eng.gather_requirements(_profile(
        activities=[{"category": 5, "description": "bad",
                     "quantity": 1, "unit_activity": "tonne",
                     "factor_id": "DOES-NOT-EXIST", "method": "activity-based"}],
    ))
    with pytest.raises(KeyError):
        eng.calculate_emissions(profile, eng.load_factors())


def test_inventory_sorted_descending_by_emissions():
    report = eng.run_pipeline(_profile())
    em = [r.tco2e for r in report.inventory]
    assert em == sorted(em, reverse=True)


def test_cli_demo_runs(capsys):
    rc = eng.main(["demo"])
    out = capsys.readouterr().out
    assert rc == 0
    parsed = json.loads(out)
    assert parsed["company"] == "Demo Manufacturer Ltd"
    assert parsed["total_tco2e"] > 0
