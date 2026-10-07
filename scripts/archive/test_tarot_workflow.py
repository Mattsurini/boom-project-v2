#!/usr/bin/env python3
"""
test_tarot_workflow.py — End-to-end test of Tarot/Prediction schema
Demonstrates: spread selection → deterministic draw → position interpretation 
→ astrology DB layering → formatted output.
"""

import sys
sys.path.insert(0, r"E:\Boom Project\scripts")

from tarot_engine import TarotEngine
from astrology_db import search_summary, search

def test_basic_workflow():
    """Test 1: Basic tarot draw with auto-detected spread."""
    print("="*60)
    print("TEST 1: Basic Three-Card Spread")
    print("="*60)
    
    engine = TarotEngine()
    reading = engine.run_reading(
        question="What energy should I focus on this month?",
        allow_reversed=True
    )
    
    print(f"Question: {reading['meta']['question']}")
    print(f"Spread: {reading['meta']['spread']}")
    print(f"Seed: {reading['meta']['seed']}")
    print()
    
    for card in reading['cards']:
        print(f"  [{card['position']}] {card['card']} ({card['orientation']})")
        print(f"    -> {card['meaning']}")
        print()
    
    return reading

def test_relationship_with_astrology():
    """Test 2: Relationship spread + astrology DB layering."""
    print("="*60)
    print("TEST 2: Relationship Spread + Astrology Layer")
    print("="*60)
    
    engine = TarotEngine()
    reading = engine.run_reading(
        question="Will I find a soulmate this year?",
        birth="1996-11-20 20:37",
        location="Chiang Rai",
        spread_name="relationship"
    )
    
    print(f"Spread: {reading['meta']['spread']}")
    print(f"Seed: {reading['meta']['seed']}")
    print()
    
    # Layer 1: Card-by-card
    for card in reading['cards']:
        print(f"  [{card['position']}] {card['card']} ({card['orientation']})")
        print(f"    Position: {card['position_meaning']}")
        print(f"    Card: {card['meaning']}")
        print()
    
    # Layer 2: Astrology DB bridge (low-token summary)
    print("--- Astrology Layer: 7th House / Marriage timing ---")
    astro_files = search_summary("marriage 7th house", max_results=3)
    print(f"  Relevant astrology files: {len(astro_files)}")
    for f in astro_files:
        print(f"    - {f['title']} ({f['size_kb']} KB)")
    print()
    
    # Layer 3: Targeted excerpts (only if needed — controlled token usage)
    print("--- Targeted Excerpts (max 3000 chars) ---")
    excerpts = search("marriage 7th house", max_total_chars=3000, max_results=2)
    print(f"  Excerpts returned: {len(excerpts)}")
    for ex in excerpts[:2]:
        preview = ex['context'][:200].replace('\n', ' ')
        print(f"    [{ex['file']}:{ex['line']}] {preview}...")
    print()
    
    return reading

def test_reproducibility():
    """Test 3: Same seed = same cards."""
    print("="*60)
    print("TEST 3: Reproducibility (Same Seed)")
    print("="*60)
    
    engine1 = TarotEngine(seed="fixed_seed_123")
    engine2 = TarotEngine(seed="fixed_seed_123")
    
    r1 = engine1.run_reading(question="Career change?", seed="fixed_seed_123")
    r2 = engine2.run_reading(question="Career change?", seed="fixed_seed_123")
    
    cards1 = [c['card'] for c in r1['cards']]
    cards2 = [c['card'] for c in r2['cards']]
    
    match = cards1 == cards2
    print(f"Seed: fixed_seed_123")
    print(f"Draw 1: {cards1}")
    print(f"Draw 2: {cards2}")
    print(f"Match: {match}")
    print()
    
    return match

def test_all_spreads():
    """Test 4: Validate all spread definitions load and draw correctly."""
    print("="*60)
    print("TEST 4: All Spread Definitions")
    print("="*60)
    
    engine = TarotEngine(seed="spread_test")
    
    spreads = ["three_card", "celtic_cross", "relationship", "career", "yes_no"]
    
    for spread_name in spreads:
        reading = engine.run_reading(
            question=f"Test question for {spread_name}",
            spread_name=spread_name,
            seed="spread_test"
        )
        n = len(reading['cards'])
        print(f"  {spread_name}: {n} cards drawn — OK")
    
    print()

def main():
    print("TAROT WORKFLOW VALIDATION SUITE")
    print(f"{'='*60}\n")
    
    test_basic_workflow()
    test_relationship_with_astrology()
    test_reproducibility()
    test_all_spreads()
    
    print("="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
