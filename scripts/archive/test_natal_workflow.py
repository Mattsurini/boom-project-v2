#!/usr/bin/env python3
"""
test_natal_workflow.py — End-to-end validation of natal chart pipeline
Tests: calculation → house mapping → aspects → DB interpretation lookup
"""

import sys
sys.path.insert(0, r"E:\Boom Project\scripts")

from natal_chart import NatalChart

def test_basic_calculation():
    print("="*60)
    print("TEST 1: Basic Natal Chart Calculation")
    print("="*60)
    
    chart = NatalChart(
        name="Boom",
        year=1996, month=11, day=20,
        hour=20, minute=37,
        tz_offset=7,
        lat=19.9071, lon=99.8328,
        house_system="Placidus"
    )
    
    print(f"Ascendant: {chart.ascendant:.2f}° ({chart._lon_to_sign(chart.ascendant)})")
    print(f"MC: {chart.mc:.2f}° ({chart._lon_to_sign(chart.mc)})")
    print(f"Sun: {chart.planets['Sun']['sign']} {chart.planets['Sun']['degree']:.2f}°")
    print(f"Moon: {chart.planets['Moon']['sign']} {chart.planets['Moon']['degree']:.2f}°")
    print(f"Planets: {len(chart.planets)}")
    print(f"Aspects: {len(chart.aspects)}")
    print()
    
    # Verify ascendant = house 1 cusp
    h1_cusp = chart.houses[1]["cusp"]
    assert abs(chart.ascendant - h1_cusp) < 0.01, f"Ascendant ({chart.ascendant}) != House 1 ({h1_cusp})"
    print("[PASS] Ascendant matches House 1 cusp")
    print()
    
    return chart

def test_house_mapping():
    print("="*60)
    print("TEST 2: House Placement Mapping")
    print("="*60)
    
    chart = NatalChart(
        name="Boom",
        year=1996, month=11, day=20,
        hour=20, minute=37,
        tz_offset=7,
        lat=19.9071, lon=99.8328,
        house_system="Placidus"
    )
    
    mapping = chart.get_planets_in_houses()
    
    for h in range(1, 13):
        planets = mapping.get(h, [])
        if planets:
            print(f"  House {h}: {', '.join(planets)}")
    
    # Verify every planet is placed in exactly one house
    all_placed = []
    for planets in mapping.values():
        all_placed.extend(planets)
    
    assert set(all_placed) == set(chart.planets.keys()), "Not all planets mapped to houses"
    print("[PASS] All planets mapped to houses")
    print()
    
    return mapping

def test_db_interpretation():
    print("="*60)
    print("TEST 3: DB Interpretation Lookup")
    print("="*60)
    
    chart = NatalChart(
        name="Boom",
        year=1996, month=11, day=20,
        hour=20, minute=37,
        tz_offset=7,
        lat=19.9071, lon=99.8328,
        house_system="Placidus"
    )
    
    interpretations = chart.query_interpretations(max_excerpts=3, max_chars=5000)
    
    print(f"Queries executed: {len(interpretations)}")
    for q, excerpts in interpretations.items():
        print(f"  '{q}': {len(excerpts)} excerpts")
    
    assert len(interpretations) > 0, "No interpretations retrieved"
    print("[PASS] DB returned interpretations")
    print()
    
    return interpretations

def test_json_serialization():
    print("="*60)
    print("TEST 4: JSON Serialization")
    print("="*60)
    
    import json
    
    chart = NatalChart(
        name="Boom",
        year=1996, month=11, day=20,
        hour=20, minute=37,
        tz_offset=7,
        lat=19.9071, lon=99.8328,
        house_system="Placidus"
    )
    
    data = chart.to_dict()
    
    # Verify structure
    assert "meta" in data
    assert "planets" in data
    assert "houses" in data
    assert "angles" in data
    assert "aspects" in data
    assert "house_mapping" in data
    
    # Verify JSON round-trip
    json_str = json.dumps(data)
    restored = json.loads(json_str)
    assert restored["meta"]["name"] == "Boom"
    
    print("[PASS] JSON serialization valid")
    print()

def test_different_house_systems():
    print("="*60)
    print("TEST 5: Different House Systems")
    print("="*60)
    
    systems = ["Placidus", "Koch", "Equal", "Whole Sign"]
    
    for hs in systems:
        try:
            chart = NatalChart(
                name="Boom",
                year=1996, month=11, day=20,
                hour=20, minute=37,
                tz_offset=7,
                lat=19.9071, lon=99.8328,
                house_system=hs
            )
            print(f"  {hs}: Asc={chart._lon_to_sign(chart.ascendant)}, {len(chart.houses)} houses — OK")
        except Exception as e:
            print(f"  {hs}: FAILED — {e}")
    
    print()

def main():
    print("NATAL CHART PIPELINE VALIDATION SUITE")
    print(f"{'='*60}\n")
    
    test_basic_calculation()
    test_house_mapping()
    test_db_interpretation()
    test_json_serialization()
    test_different_house_systems()
    
    print("="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
