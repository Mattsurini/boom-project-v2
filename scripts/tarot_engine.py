#!/usr/bin/env python3
"""
tarot_engine.py - Tarot/Prediction Workflow Engine
Deterministic spread logic, card draw, interpretation pipeline.

Usage:
  python tarot_engine.py --question "Will I find a soulmate this year?" --spread three_card
  python tarot_engine.py --question "Career decision" --spread celtic_cross --birth "1996-11-20 20:37" --location "Chiang Rai"
"""

import argparse
import json
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 78-Card Rider-Waite-Smith Reference (Major + Minor Arcana)
# ---------------------------------------------------------------------------
TAROT_DECK = [
    # Major Arcana (22)
    {"name": "The Fool", "number": 0, "suit": "Major", "upright": "New beginnings, innocence, spontaneity, free spirit", "reversed": "Recklessness, risk-taking, holding back, naivety"},
    {"name": "The Magician", "number": 1, "suit": "Major", "upright": "Manifestation, resourcefulness, power, action", "reversed": "Manipulation, poor planning, untapped talents"},
    {"name": "The High Priestess", "number": 2, "suit": "Major", "upright": "Intuition, sacred knowledge, divine feminine, subconscious", "reversed": "Secrets, disconnected from intuition, withdrawal"},
    {"name": "The Empress", "number": 3, "suit": "Major", "upright": "Femininity, beauty, nature, nurturing, abundance", "reversed": "Creative block, dependence on others, emptiness"},
    {"name": "The Emperor", "number": 4, "suit": "Major", "upright": "Authority, structure, father figure, stability", "reversed": "Tyranny, rigidity, coldness, excessive control"},
    {"name": "The Hierophant", "number": 5, "suit": "Major", "upright": "Spiritual wisdom, religious beliefs, conformity, tradition", "reversed": "Personal beliefs, freedom, challenging the status quo"},
    {"name": "The Lovers", "number": 6, "suit": "Major", "upright": "Love, harmony, relationships, choices, alignment", "reversed": "Self-love, disharmony, imbalance, misalignment"},
    {"name": "The Chariot", "number": 7, "suit": "Major", "upright": "Control, willpower, success, action, determination", "reversed": "Self-discipline, opposition, lack of direction"},
    {"name": "Strength", "number": 8, "suit": "Major", "upright": "Strength, courage, persuasion, influence, compassion", "reversed": "Inner strength, self-doubt, low energy, raw emotion"},
    {"name": "The Hermit", "number": 9, "suit": "Major", "upright": "Soul-searching, introspection, being alone, inner guidance", "reversed": "Isolation, loneliness, withdrawal, rejection"},
    {"name": "Wheel of Fortune", "number": 10, "suit": "Major", "upright": "Good luck, karma, life cycles, destiny, turning point", "reversed": "Bad luck, resistance to change, breaking cycles"},
    {"name": "Justice", "number": 11, "suit": "Major", "upright": "Justice, fairness, truth, cause and effect, law", "reversed": "Unfairness, lack of accountability, dishonesty"},
    {"name": "The Hanged Man", "number": 12, "suit": "Major", "upright": "Pause, surrender, letting go, new perspectives", "reversed": "Delays, resistance, stalling, indecision"},
    {"name": "Death", "number": 13, "suit": "Major", "upright": "Endings, change, transformation, transition", "reversed": "Resistance to change, inability to move on, stagnation"},
    {"name": "Temperance", "number": 14, "suit": "Major", "upright": "Balance, moderation, patience, purpose, meaning", "reversed": "Imbalance, excess, self-healing, re-alignment"},
    {"name": "The Devil", "number": 15, "suit": "Major", "upright": "Shadow self, attachment, addiction, restriction, sexuality", "reversed": "Releasing limiting beliefs, exploring dark thoughts, detachment"},
    {"name": "The Tower", "number": 16, "suit": "Major", "upright": "Sudden change, upheaval, chaos, revelation, awakening", "reversed": "Personal transformation, fear of change, averting disaster"},
    {"name": "The Star", "number": 17, "suit": "Major", "upright": "Hope, faith, purpose, renewal, spirituality", "reversed": "Lack of faith, despair, self-trust, discouragement"},
    {"name": "The Moon", "number": 18, "suit": "Major", "upright": "Illusion, fear, anxiety, subconscious, intuition", "reversed": "Release of fear, repressed emotion, inner confusion"},
    {"name": "The Sun", "number": 19, "suit": "Major", "upright": "Positivity, fun, warmth, success, vitality", "reversed": "Inner child, feeling down, overly optimistic"},
    {"name": "Judgement", "number": 20, "suit": "Major", "upright": "Judgement, rebirth, inner calling, absolution", "reversed": "Self-doubt, refusal of self-examination, karma"},
    {"name": "The World", "number": 21, "suit": "Major", "upright": "Completion, integration, accomplishment, travel", "reversed": "Seeking closure, short-cuts, delays, unfulfillment"},
    # Minor Arcana - Wands (14)
    {"name": "Ace of Wands", "number": 1, "suit": "Wands", "upright": "Inspiration, new opportunities, growth, potential", "reversed": "Delays, lack of motivation, weighed down"},
    {"name": "Two of Wands", "number": 2, "suit": "Wands", "upright": "Future planning, progress, decisions, discovery", "reversed": "Fear of unknown, lack of planning, disorganization"},
    {"name": "Three of Wands", "number": 3, "suit": "Wands", "upright": "Expansion, foresight, overseas opportunities, leadership", "reversed": "Obstacles, delays, frustration, limited progress"},
    {"name": "Four of Wands", "number": 4, "suit": "Wands", "upright": "Celebration, joy, harmony, relaxation, homecoming", "reversed": "Lack of support, transience, home conflicts"},
    {"name": "Five of Wands", "number": 5, "suit": "Wands", "upright": "Conflict, disagreements, competition, tension, diversity", "reversed": "Resolution, compromise, agreement, truce"},
    {"name": "Six of Wands", "number": 6, "suit": "Wands", "upright": "Victory, success, public recognition, progress, self-confidence", "reversed": "Egotism, lack of recognition, punishment, no reward"},
    {"name": "Seven of Wands", "number": 7, "suit": "Wands", "upright": "Perseverance, defensive, maintaining control, fighting for beliefs", "reversed": "Give up, overwhelmed, exhaustion, inability to fight"},
    {"name": "Eight of Wands", "number": 8, "suit": "Wands", "upright": "Movement, fast-paced change, action, alignment, air travel", "reversed": "Delays, frustration, resisting change, internal alignment"},
    {"name": "Nine of Wands", "number": 9, "suit": "Wands", "upright": "Resilience, grit, last stand, persistence, nearing success", "reversed": "Exhaustion, fatigue, questioning motivations, bitterness"},
    {"name": "Ten of Wands", "number": 10, "suit": "Wands", "upright": "Burden, extra responsibility, hard work, completion", "reversed": "Inability to delegate, overstressed, burnt out"},
    {"name": "Page of Wands", "number": 11, "suit": "Wands", "upright": "Exploration, excitement, freedom, discovery", "reversed": "Lack of direction, procrastination, creating conflict"},
    {"name": "Knight of Wands", "number": 12, "suit": "Wands", "upright": "Energy, passion, inspired action, adventure, impulsiveness", "reversed": "Anger, recklessness, frustration, delays"},
    {"name": "Queen of Wands", "number": 13, "suit": "Wands", "upright": "Confidence, social butterfly, determination, charisma", "reversed": "Self-respect, self-assurance, introvert, re-establish boundaries"},
    {"name": "King of Wands", "number": 14, "suit": "Wands", "upright": "Natural-born leader, vision, entrepreneur, honour", "reversed": "Impulsiveness, haste, ruthless, high expectations"},
    # Minor Arcana - Cups (14)
    {"name": "Ace of Cups", "number": 1, "suit": "Cups", "upright": "New feelings, spirituality, intuition, creativity", "reversed": "Emotional loss, blocked creativity, emptiness"},
    {"name": "Two of Cups", "number": 2, "suit": "Cups", "upright": "Unified love, partnership, mutual attraction, union", "reversed": "Self-love, break-ups, disharmony, distrust"},
    {"name": "Three of Cups", "number": 3, "suit": "Cups", "upright": "Celebration, friendship, creativity, community, collaborations", "reversed": "Conformity, gossip, isolation, loneliness"},
    {"name": "Four of Cups", "number": 4, "suit": "Cups", "upright": "Apathy, contemplation, disconnectedness, re-evaluation", "reversed": "Retreat, withdrawal, checking in, awareness"},
    {"name": "Five of Cups", "number": 5, "suit": "Cups", "upright": "Regret, failure, disappointment, pessimism, grief", "reversed": "Acceptance, moving on, finding peace, contentment"},
    {"name": "Six of Cups", "number": 6, "suit": "Cups", "upright": "Revisiting the past, childhood memories, innocence, joy", "reversed": "Living in the past, forgiveness, lacking playfulness"},
    {"name": "Seven of Cups", "number": 7, "suit": "Cups", "upright": "Choices, searching for purpose, illusion, fantasy, wishful thinking", "reversed": "Alignment, values, personal truth, prioritization"},
    {"name": "Eight of Cups", "number": 8, "suit": "Cups", "upright": "Walking away, disillusionment, leaving behind, seeking truth", "reversed": "Avoidance, fear of moving on, staying in a bad situation"},
    {"name": "Nine of Cups", "number": 9, "suit": "Cups", "upright": "Contentment, satisfaction, gratitude, wish come true", "reversed": "Inner happiness, dissatisfaction, greed, indulgence"},
    {"name": "Ten of Cups", "number": 10, "suit": "Cups", "upright": "Divine love, blissful relationships, harmony, alignment", "reversed": "Disconnection, misalignment, conflict, values clash"},
    {"name": "Page of Cups", "number": 11, "suit": "Cups", "upright": "Creative opportunities, intuitive messages, curiosity, possibility", "reversed": "Emotional immaturity, insecurity, disappointment"},
    {"name": "Knight of Cups", "number": 12, "suit": "Cups", "upright": "Romance, charm, idealism, imagination, beauty", "reversed": "Unrealistic, jealousy, moodiness, disappointment"},
    {"name": "Queen of Cups", "number": 13, "suit": "Cups", "upright": "Compassion, calm, comfort, intuition, emotional security", "reversed": "Martyrdom, insecurity, dependence, giving too much"},
    {"name": "King of Cups", "number": 14, "suit": "Cups", "upright": "Emotional balance, compassion, diplomacy, control", "reversed": "Moodiness, manipulation, emotional volatility"},
    # Minor Arcana - Swords (14)
    {"name": "Ace of Swords", "number": 1, "suit": "Swords", "upright": "Breakthrough, clarity, sharp mind, new idea, communication", "reversed": "Inner clarity, re-thinking, clouded judgment, confusion"},
    {"name": "Two of Swords", "number": 2, "suit": "Swords", "upright": "Indecision, difficult choices, stalemate, avoidance", "reversed": "Information overload, indecision, confusion, stalemate"},
    {"name": "Three of Swords", "number": 3, "suit": "Swords", "upright": "Heartbreak, grief, sorrow, rejection, betrayal", "reversed": "Recovery, forgiveness, moving on, releasing pain"},
    {"name": "Four of Swords", "number": 4, "suit": "Swords", "upright": "Rest, restoration, contemplation, recuperation", "reversed": "Restlessness, burnout, lack of progress, stagnation"},
    {"name": "Five of Swords", "number": 5, "suit": "Swords", "upright": "Conflict, disagreements, competition, defeat, winning at all costs", "reversed": "Reconciliation, making amends, past resentment"},
    {"name": "Six of Swords", "number": 6, "suit": "Swords", "upright": "Transition, change, moving on, leaving behind, travel", "reversed": "Resistance to change, unfinished business, carrying baggage"},
    {"name": "Seven of Swords", "number": 7, "suit": "Swords", "upright": "Deception, strategy, sneakiness, cunning, getting away with something", "reversed": "Coming clean, re-thinking approach, conscience, turning over new leaf"},
    {"name": "Eight of Swords", "number": 8, "suit": "Swords", "upright": "Negative thoughts, self-imposed restriction, imprisonment, victim mentality", "reversed": "Opening up, releasing self-limiting beliefs, new perspective"},
    {"name": "Nine of Swords", "number": 9, "suit": "Swords", "upright": "Anxiety, worry, fear, nightmares, negative thinking", "reversed": "Inner turmoil, deep-seated fears, secrets, releasing worry"},
    {"name": "Ten of Swords", "number": 10, "suit": "Swords", "upright": "Painful endings, deep wounds, betrayal, loss, crisis", "reversed": "Recovery, regeneration, resisting an inevitable end"},
    {"name": "Page of Swords", "number": 11, "suit": "Swords", "upright": "Curiosity, new ideas, thirst for knowledge, communication", "reversed": "Deception, manipulation, all talk and no action"},
    {"name": "Knight of Swords", "number": 12, "suit": "Swords", "upright": "Action, impulsiveness, defending beliefs, haste", "reversed": "No direction, disregard for consequences, unprepared"},
    {"name": "Queen of Swords", "number": 13, "suit": "Swords", "upright": "Independent, unbiased judgement, clear boundaries, direct communication", "reversed": "Cold-hearted, cruel, bitterness, overly emotional"},
    {"name": "King of Swords", "number": 14, "suit": "Swords", "upright": "Mental clarity, intellectual power, authority, truth", "reversed": "Quiet power, inner truth, misuse of power, manipulation"},
    # Minor Arcana - Pentacles (14)
    {"name": "Ace of Pentacles", "number": 1, "suit": "Pentacles", "upright": "New financial opportunity, manifestation, abundance, prosperity", "reversed": "Lost opportunity, lack of planning, scarcity"},
    {"name": "Two of Pentacles", "number": 2, "suit": "Pentacles", "upright": "Balance, adaptability, time management, prioritization", "reversed": "Overwhelm, disorganization, reprioritization, too much at once"},
    {"name": "Three of Pentacles", "number": 3, "suit": "Pentacles", "upright": "Teamwork, collaboration, learning, implementation", "reversed": "Lack of teamwork, disregard for skills, poor quality"},
    {"name": "Four of Pentacles", "number": 4, "suit": "Pentacles", "upright": "Security, conservation, frugality, control, possessiveness", "reversed": "Greed, materialism, self-protection, releasing control"},
    {"name": "Five of Pentacles", "number": 5, "suit": "Pentacles", "upright": "Financial loss, poverty, lack mindset, isolation, worry", "reversed": "Recovery from loss, spiritual poverty, finding help"},
    {"name": "Six of Pentacles", "number": 6, "suit": "Pentacles", "upright": "Generosity, charity, giving, prosperity, sharing wealth", "reversed": "Debt, selfishness, one-sided charity, strings attached"},
    {"name": "Seven of Pentacles", "number": 7, "suit": "Pentacles", "upright": "Long-term view, sustainable results, perseverance, investment", "reversed": "Lack of long-term vision, limited success, impatience"},
    {"name": "Eight of Pentacles", "number": 8, "suit": "Pentacles", "upright": "Apprenticeship, repetitive tasks, mastery, skill development", "reversed": "Self-development, perfectionism, misdirected activity"},
    {"name": "Nine of Pentacles", "number": 9, "suit": "Pentacles", "upright": "Abundance, luxury, self-sufficiency, financial independence", "reversed": "Self-worth issues, superficiality, living beyond means"},
    {"name": "Ten of Pentacles", "number": 10, "suit": "Pentacles", "upright": "Wealth, financial security, family, long-term success, inheritance", "reversed": "Financial failure, loneliness, loss, family conflict"},
    {"name": "Page of Pentacles", "number": 11, "suit": "Pentacles", "upright": "Manifestation, financial opportunity, skill development, ambition", "reversed": "Lack of progress, procrastination, learn from failure"},
    {"name": "Knight of Pentacles", "number": 12, "suit": "Pentacles", "upright": "Hard work, productivity, routine, conservatism", "reversed": "Self-discipline, boredom, feeling stuck, perfectionism"},
    {"name": "Queen of Pentacles", "number": 13, "suit": "Pentacles", "upright": "Nurturing, practical, providing financially, working parent", "reversed": "Financial independence, self-care, work-home conflict"},
    {"name": "King of Pentacles", "number": 14, "suit": "Pentacles", "upright": "Wealth, business, leadership, security, discipline, abundance", "reversed": "Financially inept, obsessed with wealth, stubborn"},
]

# ---------------------------------------------------------------------------
# Spread Definitions
# ---------------------------------------------------------------------------
SPREADS = {
    "three_card": {
        "name": "Three-Card Spread",
        "description": "Past, Present, Future — or Situation, Action, Outcome",
        "positions": [
            {"name": "Past / Foundation", "meaning": "What led to the current situation, root cause, or past energy"},
            {"name": "Present / Challenge", "meaning": "Current energy, obstacle, or what is happening now"},
            {"name": "Future / Outcome", "meaning": "Likely direction, result, or advice moving forward"},
        ]
    },
    "celtic_cross": {
        "name": "Celtic Cross",
        "description": "Comprehensive 10-card spread for deep insight",
        "positions": [
            {"name": "Present Situation", "meaning": "The core of the matter — what is happening now"},
            {"name": "Challenge / Crossing", "meaning": "What blocks or opposes the situation"},
            {"name": "Foundation / Root", "meaning": "The underlying cause, past influence, subconscious driver"},
            {"name": "Recent Past", "meaning": "Events or energies that are fading but still relevant"},
            {"name": "Crown / Best Outcome", "meaning": "Highest potential, aspiration, or spiritual guidance"},
            {"name": "Near Future", "meaning": "What is approaching in the short term"},
            {"name": "Self / Attitude", "meaning": "The querent's current mindset, approach, or self-perception"},
            {"name": "Environment / External", "meaning": "People, circumstances, or influences around the querent"},
            {"name": "Hopes / Fears", "meaning": "What the querent wants or dreads"},
            {"name": "Final Outcome", "meaning": "The likely resolution if current energies continue"},
        ]
    },
    "relationship": {
        "name": "Relationship Spread",
        "description": "Five-card spread for love and partnership questions",
        "positions": [
            {"name": "You", "meaning": "Your current energy, feelings, and position in the relationship"},
            {"name": "Partner / Other", "meaning": "The other person's energy, feelings, and perspective"},
            {"name": "Relationship Dynamic", "meaning": "The energy between you — what binds or divides"},
            {"name": "Challenge / Block", "meaning": "What is standing in the way of harmony or growth"},
            {"name": "Outcome / Advice", "meaning": "The likely direction or what is needed to move forward"},
        ]
    },
    "soulmate": {
        "name": "Soulmate / เนื้อคู่ Spread",
        "description": "Nine-card spread for a full soulmate profile: who they are, how/when you meet, and whether it works",
        "positions": [
            {"name": "Appearance / Physical Presence", "meaning": "How the person presents physically — first impression, body type, style, aura"},
            {"name": "Personality / Character", "meaning": "Core temperament, habits, strengths, and shadow traits"},
            {"name": "Financial Foundation", "meaning": "Their relationship with money, stability, abundance or scarcity patterns"},
            {"name": "Career / Work Foundation", "meaning": "Life purpose, work style, professional path, ambition"},
            {"name": "Love Nature", "meaning": "How they express love, emotional style, what they need and give in love"},
            {"name": "How You Meet", "meaning": "The circumstances, setting, or path that brings you together"},
            {"name": "Timing / When", "meaning": "The period, season, or conditions under which the meeting or relationship begins"},
            {"name": "Relationship Potential", "meaning": "Whether the union is good, what it brings, its likely quality"},
            {"name": "Core Compatibility", "meaning": "Fundamental alignment of values, life direction, and soul-level fit"},
        ]
    },
    "career": {
        "name": "Career Path Spread",
        "description": "Five-card spread for work, finance, and professional direction",
        "positions": [
            {"name": "Current State", "meaning": "Your present career situation, job, or financial status"},
            {"name": "Strengths", "meaning": "Skills, talents, or assets that serve you"},
            {"name": "Weaknesses / Gaps", "meaning": "What is missing, needs development, or holds you back"},
            {"name": "Opportunity", "meaning": "A path, offer, or potential next step"},
            {"name": "Outcome / Advice", "meaning": "Where this leads or what action to take"},
        ]
    },
    "yes_no": {
        "name": "Yes / No Spread",
        "description": "Three-card spread for binary decisions",
        "positions": [
            {"name": "Yes Position", "meaning": "Energy supporting a 'yes' answer"},
            {"name": "No Position", "meaning": "Energy supporting a 'no' answer"},
            {"name": "Advice / Hidden Factor", "meaning": "What you are not seeing, or what to consider"},
        ]
    },
}

# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------

class TarotEngine:
    def __init__(self, seed: Optional[str] = None):
        self.deck = list(TAROT_DECK)
        self.rng = random.Random(seed)
    
    def draw(self, n: int = 1, allow_reversed: bool = True) -> List[Dict]:
        """Draw n cards from the deck without replacement."""
        if n > len(self.deck):
            raise ValueError(f"Cannot draw {n} cards from deck of {len(self.deck)}")
        
        drawn = self.rng.sample(self.deck, n)
        
        result = []
        for card in drawn:
            c = card.copy()
            if allow_reversed:
                is_reversed = self.rng.choice([True, False])
            else:
                is_reversed = False
            c["is_reversed"] = is_reversed
            c["orientation"] = "Reversed" if is_reversed else "Upright"
            c["reading"] = c["reversed"] if is_reversed else c["upright"]
            result.append(c)
        
        return result
    
    def select_spread(self, question: str, spread_name: Optional[str] = None) -> Tuple[str, Dict]:
        """Auto-select or validate spread based on question keywords."""
        if spread_name and spread_name in SPREADS:
            return spread_name, SPREADS[spread_name]
        
        q = question.lower()
        
        # Auto-detect
        if any(w in q for w in ["relationship", "love", "marriage", "partner", "soulmate", "boyfriend", "girlfriend", "date", "dating"]):
            return "relationship", SPREADS["relationship"]
        elif any(w in q for w in ["career", "job", "work", "business", "money", "finance", "promotion", "profession"]):
            return "career", SPREADS["career"]
        elif any(w in q for w in ["yes", "no", "should i", "will i", "can i", "is it"]):
            return "yes_no", SPREADS["yes_no"]
        else:
            return "three_card", SPREADS["three_card"]
    
    def generate_seed(self, question: str, birth: Optional[str] = None, timestamp: Optional[str] = None) -> str:
        """Generate deterministic seed from inputs for reproducible draws."""
        ts = timestamp or datetime.now().isoformat()
        raw = f"{question}::{birth or ''}::{ts}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    
    def run_reading(self, question: str, spread_name: Optional[str] = None,
                    birth: Optional[str] = None, location: Optional[str] = None,
                    allow_reversed: bool = True, seed: Optional[str] = None) -> Dict:
        """Full pipeline: spread selection → draw → interpretation structure."""
        
        # Step 1: Select spread
        spread_key, spread_def = self.select_spread(question, spread_name)
        n_cards = len(spread_def["positions"])
        
        # Step 2: Generate seed and draw
        if seed is None:
            seed = self.generate_seed(question, birth)
        self.rng = random.Random(seed)
        
        drawn = self.draw(n_cards, allow_reversed)
        
        # Step 3: Map cards to positions
        reading = {
            "meta": {
                "question": question,
                "spread": spread_def["name"],
                "spread_key": spread_key,
                "seed": seed,
                "birth": birth,
                "location": location,
                "timestamp": datetime.now().isoformat(),
                "deck": "Rider-Waite-Smith",
                "allow_reversed": allow_reversed,
            },
            "cards": []
        }
        
        for i, (position, card) in enumerate(zip(spread_def["positions"], drawn)):
            reading["cards"].append({
                "position": position["name"],
                "position_meaning": position["meaning"],
                "card": card["name"],
                "suit": card["suit"],
                "number": card["number"],
                "orientation": card["orientation"],
                "meaning": card["reading"],
            })
        
        return reading
    
    def format_reading(self, reading: Dict, style: str = "structured") -> str:
        """Format reading as structured markdown."""
        m = reading["meta"]
        
        lines = [
            f"# Tarot Reading: {m['question']}",
            "",
            f"**Spread:** {m['spread']}  ",
            f"**Deck:** {m['deck']}  ",
            f"**Seed:** `{m['seed']}`  ",
            f"**Timestamp:** {m['timestamp']}",
            "",
            "---",
            "",
        ]
        
        for c in reading["cards"]:
            lines.append(f"## {c['position']}")
            lines.append("")
            lines.append(f"**Card:** {c['card']} ({c['orientation']})")
            lines.append("")
            lines.append(f"**Position meaning:** {c['position_meaning']}")
            lines.append("")
            lines.append(f"**Card meaning:** {c['meaning']}")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        lines.append("## Synthesis")
        lines.append("")
        lines.append("*Interpretation combining all cards and positions goes here. Use astrology_db.py or external sources for layered interpretation.*")
        lines.append("")
        
        return "\n".join(lines)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Tarot Engine — deterministic spread and draw")
    parser.add_argument("--question", "-q", required=True, help="The querent's question")
    parser.add_argument("--spread", "-s", choices=list(SPREADS.keys()), help="Spread type (auto-detected if omitted)")
    parser.add_argument("--birth", "-b", help="Birth datetime (YYYY-MM-DD HH:MM)")
    parser.add_argument("--location", "-l", help="Birth location")
    parser.add_argument("--seed", help="Fixed seed for reproducible draws")
    parser.add_argument("--no-reversed", action="store_true", help="Only upright cards")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of markdown")
    
    args = parser.parse_args()
    
    engine = TarotEngine()
    reading = engine.run_reading(
        question=args.question,
        spread_name=args.spread,
        birth=args.birth,
        location=args.location,
        allow_reversed=not args.no_reversed,
        seed=args.seed
    )
    
    if args.json:
        print(json.dumps(reading, indent=2, ensure_ascii=False))
    else:
        print(engine.format_reading(reading))

if __name__ == "__main__":
    main()
