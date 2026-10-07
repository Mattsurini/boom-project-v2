#!/usr/bin/env python3
"""
Synastry Calculator — compatibility analysis between two natal charts.
Uses planetary positions from natal_chart.py.
No external dependencies required.
"""

import math
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ─── Import natal chart functions ───
# We import from the sibling skill's script directory
import importlib.util
import os

# Load natal_chart module from astro-natal-chart skill
NATAL_CHART_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "astro-natal-chart", "scripts", "natal_chart_swe.py"
)
NATAL_CHART_PATH = os.path.normpath(NATAL_CHART_PATH)

spec = importlib.util.spec_from_file_location("natal_chart", NATAL_CHART_PATH)
nc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nc)

# ─── Constants ───

PLANETS = nc.PLANETS
SIGNS = nc.SIGNS

# Synastry orbs (tighter than natal)
SYNSTRY_ORBS = {
    "conjunction": 7,
    "opposition": 7,
    "trine": 6,
    "square": 6,
    "sextile": 4,
    "semisextile": 1.5,
    "semisquare": 1.5,
    "quincunx": 1.5,
}

# Aspect scoring
ASPECT_SCORES = {
    "conjunction": 3,    # Can be positive or negative depending on planets
    "trine": 5,          # Very harmonious
    "sextile": 3,        # Harmonious
    "opposition": -1,    # Mixed — can be complementary or conflicting
    "square": -3,        # Tension
    "semisextile": 1,    # Mild positive
    "semisquare": -1,    # Mild tension
    "quincunx": -1,      # Adjustment needed
}

# Key planet pairs and their weights
KEY_PAIRS = {
    ("Sun", "Sun"): 3.0,
    ("Moon", "Moon"): 3.0,
    ("Sun", "Moon"): 4.0,
    ("Moon", "Sun"): 4.0,
    ("Venus", "Mars"): 4.0,
    ("Mars", "Venus"): 4.0,
    ("Venus", "Venus"): 2.0,
    ("Mars", "Mars"): 2.0,
    ("Mercury", "Mercury"): 1.5,
    ("Jupiter", "Jupiter"): 1.5,
    ("Saturn", "Sun"): 2.5,
    ("Saturn", "Moon"): 2.5,
    ("Sun", "Saturn"): 2.5,
    ("Moon", "Saturn"): 2.5,
    ("Pluto", "Sun"): 2.0,
    ("Pluto", "Moon"): 2.0,
    ("Sun", "Pluto"): 2.0,
    ("Moon", "Pluto"): 2.0,
    ("Uranus", "Venus"): 1.5,
    ("Neptune", "Venus"): 1.5,
}

HOUSE_MEANINGS = {
    1: "personality and self-expression",
    2: "finances and values",
    3: "communication and surroundings",
    4: "home and family",
    5: "romance and creativity",
    6: "work and health",
    7: "partnership and marriage",
    8: "transformation and intimacy",
    9: "philosophy and travel",
    10: "career and status",
    11: "friends and hopes",
    12: "subconscious and solitude",
}


def normalize_degrees(deg):
    while deg < 0:
        deg += 360
    while deg >= 360:
        deg -= 360
    return deg


def calc_synastry_aspects(pos1, pos2):
    """Calculate aspects between two sets of planetary positions.

    Each unordered planet pair is scored ONCE. Iterating both (Sun,Moon) and
    (Moon,Sun) would otherwise count the same cross-aspect twice and inflate
    every score; the orientation that matches KEY_PAIRS / the interpretation
    table is the one kept, so labels stay canonical (Sun-Moon, not Moon-Sun).
    """
    aspects = []
    handled = set()

    for p1_name, p1_lon in pos1.items():
        for p2_name, p2_lon in pos2.items():
            pair_key = (p1_name, p2_name)
            if pair_key in handled:
                continue
            handled.add(pair_key)
            if p2_name in pos1 and p1_name in pos2:
                handled.add((p2_name, p1_name))

            # Keep the canonical orientation when one exists.
            if pair_key not in KEY_PAIRS and (p2_name, p1_name) in KEY_PAIRS:
                p1_name, p2_name = p2_name, p1_name
                p1_lon, p2_lon = p2_lon, p1_lon
                pair_key = (p1_name, p2_name)

            diff = abs(p1_lon - p2_lon)
            if diff > 180:
                diff = 360 - diff

            aspect_types = [
                ("conjunction", 0),
                ("sextile", 60),
                ("square", 90),
                ("trine", 120),
                ("opposition", 180),
                ("semisextile", 30),
                ("semisquare", 45),
                ("quincunx", 150),
            ]

            for asp_name, asp_angle in aspect_types:
                orb = SYNSTRY_ORBS[asp_name]
                orb_diff = abs(diff - asp_angle)
                if orb_diff <= orb:
                    weight = KEY_PAIRS.get(pair_key, 1.0)

                    aspects.append({
                        "p1": p1_name,
                        "p2": p2_name,
                        "type": asp_name,
                        "angle": asp_angle,
                        "orb": orb_diff,
                        "weight": weight,
                        "score": ASPECT_SCORES[asp_name] * weight,
                    })
                    break

    # Sort by absolute weight (most important first)
    aspects.sort(key=lambda x: abs(x["score"]), reverse=True)
    return aspects


def calc_house_overlaps(pos_other, houses_self):
    """Determine which houses of self are activated by other's planets."""
    overlaps = {}
    for pname, plon in pos_other.items():
        for h in range(12):
            next_h = (h + 1) % 12
            h_start = houses_self[h]
            h_end = houses_self[next_h]
            if h_start < h_end:
                if h_start <= plon < h_end:
                    house_num = h + 1
                    if house_num not in overlaps:
                        overlaps[house_num] = []
                    overlaps[house_num].append(pname)
                    break
            else:
                if plon >= h_start or plon < h_end:
                    house_num = h + 1
                    if house_num not in overlaps:
                        overlaps[house_num] = []
                    overlaps[house_num].append(pname)
                    break
    return overlaps


def calculate_compatibility_score(aspects):
    """Calculate overall compatibility score (0-100)."""
    if not aspects:
        return 50  # Neutral

    total_score = 0
    max_possible = 0

    for asp in aspects:
        total_score += asp["score"]
        max_possible += abs(ASPECT_SCORES[asp["type"]]) * asp["weight"]

    if max_possible == 0:
        return 50

    # Normalize to 0-100 range
    raw = (total_score / max_possible) * 100
    # Scale: 50 is neutral, range roughly 20-80
    score = 50 + raw * 0.5
    score = max(10, min(95, score))
    return round(score)


def get_sphere_scores(aspects):
    """Calculate scores for different relationship spheres."""
    spheres = {
        "passion": {"planets": ["Mars", "Venus", "Pluto", "Sun"], "score": 0, "count": 0},
        "emotion": {"planets": ["Moon", "Venus", "Neptune", "Sun"], "score": 0, "count": 0},
        "communication": {"planets": ["Mercury", "Uranus", "Jupiter"], "score": 0, "count": 0},
        "values": {"planets": ["Jupiter", "Saturn", "Sun", "MC"], "score": 0, "count": 0},
        "family": {"planets": ["Moon", "Venus", "Saturn", "IC"], "score": 0, "count": 0},
    }

    for asp in aspects:
        p1, p2 = asp["p1"], asp["p2"]
        for sphere_name, sphere in spheres.items():
            if p1 in sphere["planets"] or p2 in sphere["planets"]:
                sphere["score"] += asp["score"]
                sphere["count"] += 1

    # Convert to 1-10 scale
    result = {}
    for name, sphere in spheres.items():
        if sphere["count"] > 0:
            raw = sphere["score"] / sphere["count"]
            # Map to 1-10
            score = 5 + raw * 1.5
            result[name] = max(1, min(10, round(score)))
        else:
            result[name] = 5  # Neutral

    return result


def get_aspect_description(asp):
    """Get human-readable description of a synastry aspect."""
    p1_info = PLANETS.get(asp["p1"], {"name_rus": asp["p1"]})
    p2_info = PLANETS.get(asp["p2"], {"name_rus": asp["p2"]})

    aspect_names = {
        "conjunction": "conjunction",
        "opposition": "opposition",
        "trine": "trine",
        "square": "square",
        "sextile": "sextile",
        "semisextile": "semisextile",
        "semisextile": "semisextile",
        "semisquare": "semisquare",
        "quincunx": "quincunx",
    }

    symbols = {
        "conjunction": "☌",
        "opposition": "☍",
        "trine": "△",
        "square": "□",
        "sextile": "✶",
        "semisextile": "⚺",
        "semisquare": "∠",
        "quincunx": "⚹",
    }

    return {
        "text": f"{symbols.get(asp['type'], '?')} {p1_info['name_rus']}-{p2_info['name_rus']} ({aspect_names.get(asp['type'], asp['type'])}, orb {asp['orb']:.1f}°)",
        "positive": asp["score"] > 0,
        "weight": asp["weight"],
    }


def format_synastry(name1, name2, chart1, chart2, aspects, house_overlaps_1, house_overlaps_2):
    """Format complete synastry report."""
    lines = []

    # Header
    lines.append("💕 SYNASTRY — Compatibility Report")
    lines.append(f"👤 {name1}: {chart1['date']}, {chart1['city_full']}")
    lines.append(f"👤 {name2}: {chart2['date']}, {chart2['city_full']}")
    lines.append("")

    # Overall score
    score = calculate_compatibility_score(aspects)
    lines.append("═" * 50)
    lines.append(f"📊 OVERALL COMPATIBILITY SCORE: {score}/100")
    lines.append("═" * 50)
    lines.append("")

    # Sphere scores
    spheres = get_sphere_scores(aspects)
    sphere_labels = {
        "passion": "🔥 PASSION & PHYSICAL ATTRACTION",
        "emotion": "💞 EMOTIONAL COMPATIBILITY",
        "communication": "🗣️ COMMUNICATION & INTELLECT",
        "values": "🎯 SHARED GOALS & VALUES",
        "family": "🏠 FAMILY & DOMESTIC LIFE",
    }

    for key, label in sphere_labels.items():
        s = spheres.get(key, 5)
        bar = "█" * s + "░" * (10 - s)
        lines.append(f"{label}")
        lines.append(f"   Score: {s}/10  [{bar}]")
        lines.append("")

    # Key aspects
    lines.append("─" * 50)
    lines.append("🔑 KEY SYNASTRY ASPECTS:")
    lines.append("─" * 50)

    # Show top aspects by weight
    shown = 0
    for asp in aspects[:20]:
        desc = get_aspect_description(asp)
        marker = "✅" if desc["positive"] else "⚠️"
        lines.append(f"  {marker} {desc['text']}")
        shown += 1

    lines.append("")

    # Strong aspects (positive)
    positive_asps = [a for a in aspects if a["score"] > 0 and a["weight"] >= 2.0]
    if positive_asps:
        lines.append("✨ STRENGTHS OF THE PAIR:")
        lines.append("─" * 50)
        for asp in positive_asps[:8]:
            desc = get_aspect_description(asp)
            lines.append(f"  ✦ {desc['text']}")
            # Add interpretation
            lines.append(f"    {get_interpretation(asp, positive=True)}")
        lines.append("")

    # Conflict aspects (negative)
    negative_asps = [a for a in aspects if a["score"] < 0 and a["weight"] >= 1.5]
    if negative_asps:
        lines.append("⚡ CONFLICT POINTS:")
        lines.append("─" * 50)
        for asp in negative_asps[:8]:
            desc = get_aspect_description(asp)
            lines.append(f"  ✦ {desc['text']}")
            lines.append(f"    {get_interpretation(asp, positive=False)}")
        lines.append("")

    # House overlaps
    # calc_synastry(): overlaps_1 = partner1 planets in partner2 houses
    #                  overlaps_2 = partner2 planets in partner1 houses
    lines.append("─" * 50)
    lines.append(f"🏠 PLANETS OF {name1.upper()} IN THE HOUSES OF {name2.upper()}:")
    lines.append("─" * 50)
    for house_num in sorted(house_overlaps_1.keys()):
        planets = ", ".join([PLANETS.get(p, {"name_rus": p})["name_rus"] for p in house_overlaps_1[house_num]])
        meaning = HOUSE_MEANINGS.get(house_num, "")
        lines.append(f"  House {house_num}: {planets} — {meaning}")

    lines.append("")
    lines.append(f"🏠 PLANETS OF {name2.upper()} IN THE HOUSES OF {name1.upper()}:")
    lines.append("─" * 50)
    for house_num in sorted(house_overlaps_2.keys()):
        planets = ", ".join([PLANETS.get(p, {"name_rus": p})["name_rus"] for p in house_overlaps_2[house_num]])
        meaning = HOUSE_MEANINGS.get(house_num, "")
        lines.append(f"  House {house_num}: {planets} — {meaning}")

    lines.append("")

    # Recommendations
    lines.append("─" * 50)
    lines.append("📋 RECOMMENDATIONS:")
    lines.append("─" * 50)

    recs = generate_recommendations(spheres, positive_asps, negative_asps)
    for rec in recs:
        lines.append(f"  • {rec}")

    lines.append("")
    lines.append("─" * 50)
    lines.append("⚠️ Synastry is a self-discovery tool, not a verdict.")
    lines.append("Tense aspects indicate growth zones, not incompatibility.")

    return "\n".join(lines)


def get_interpretation(asp, positive=True):
    """Get brief interpretation of a synastry aspect."""
    p1, p2, atype = asp["p1"], asp["p2"], asp["type"]

    # Key interpretations for important pairs
    interp_map = {
        ("Sun", "Moon", "conjunction"): "Deep recognition, a strong connection at the level of essence",
        ("Sun", "Moon", "trine"): "Natural harmony, mutual understanding without words",
        ("Sun", "Moon", "opposition"): "Attraction of opposites, complementarity",
        ("Sun", "Moon", "square"): "Emotional friction, but also growth through conflict",
        ("Sun", "Sun", "conjunction"): "Similar core values, seeing yourself in the other",
        ("Sun", "Sun", "trine"): "Compatible at the level of personality, respect and support",
        ("Sun", "Sun", "square"): "Different approaches to life, possible ego clashes",
        ("Moon", "Moon", "conjunction"): "Same emotional needs, comfort",
        ("Moon", "Moon", "trine"): "Emotional harmony, they sense each other",
        ("Moon", "Moon", "square"): "Different emotional rhythms, adjustment needed",
        ("Venus", "Mars", "conjunction"): "Powerful sexual chemistry, passionate attraction",
        ("Venus", "Mars", "trine"): "Harmonious romantic and sexual bond",
        ("Venus", "Mars", "square"): "Passion with conflict, but strong attraction",
        ("Venus", "Mars", "opposition"): "Intense attraction, struggle for dominance",
        ("Saturn", "Sun", "conjunction"): "Serious relationship, sense of duty and responsibility",
        ("Saturn", "Moon", "trine"): "Stability and reliability, emotional support",
        ("Saturn", "Moon", "square"): "Emotional restrictions, a sense of heaviness",
        ("Pluto", "Sun", "conjunction"): "Intense transformative bond, obsession",
        ("Pluto", "Moon", "conjunction"): "Deep emotional transformation",
        ("Pluto", "Venus", "conjunction"): "Passionate, sometimes painful attachment",
        ("Mercury", "Mercury", "conjunction"): "Same communication style, easy contact",
        ("Mercury", "Mercury", "square"): "Different thinking styles, misunderstandings",
        ("Jupiter", "Sun", "trine"): "Support and inspiration, joint growth",
        ("Jupiter", "Moon", "trine"): "Emotional generosity, optimism as a couple",
        ("Uranus", "Venus", "conjunction"): "Unexpected romance, freedom in relationships",
        ("Neptune", "Venus", "trine"): "Romantic idealization, spiritual bond",
    }

    key = (p1, p2, atype)
    if key in interp_map:
        return interp_map[key]

    # Generic interpretations
    if positive:
        if atype == "trine":
            return "Harmonious interaction, ease in this sphere"
        elif atype == "sextile":
            return "Favorable influence, potential for growth"
        elif atype == "conjunction":
            return "Merging of energies, amplification of these planets' themes"
        else:
            return "Positive interaction"
    else:
        if atype == "square":
            return "Tension and conflict, but a growth zone"
        elif atype == "opposition":
            return "Opposite approaches, compromise needed"
        else:
            return "Requires conscious work"


def generate_recommendations(spheres, positive_asps, negative_asps):
    """Generate practical recommendations."""
    recs = []

    if spheres.get("passion", 5) >= 7:
        recs.append("Passion and physical attraction are a strength of this couple. Use it as a foundation.")
    elif spheres.get("passion", 5) <= 4:
        recs.append("Physical attraction may need attention. Try new shared activities.")

    if spheres.get("emotion", 5) >= 7:
        recs.append("Emotional compatibility is high — you sense each other. Value it.")
    elif spheres.get("emotion", 5) <= 4:
        recs.append("Emotional needs may differ. It is important to talk about feelings.")

    if spheres.get("communication", 5) >= 7:
        recs.append("Communication is a strength. You easily find common ground.")
    elif spheres.get("communication", 5) <= 4:
        recs.append("Communication styles may differ. Listen to each other more carefully.")

    if spheres.get("family", 5) >= 7:
        recs.append("Family life and household are a zone of harmony. Comfortable cohabitation.")
    elif spheres.get("family", 5) <= 4:
        recs.append("Disagreements are possible over everyday matters. Assign roles in advance.")

    if spheres.get("values", 5) >= 7:
        recs.append("Shared values and goals are the foundation of long-term relationships.")
    elif spheres.get("values", 5) <= 4:
        recs.append("Life goals may differ. Find common ground.")

    if not recs:
        recs.append("The relationship is balanced. Work on mutual understanding.")

    return recs


# ─── Main ───

def calc_synastry(chart1, chart2, name1="Partner 1", name2="Partner 2"):
    """Calculate complete synastry between two natal charts."""
    def flatten(planets):
        if planets and all(isinstance(v, dict) for v in planets.values()):
            return {k: v["lon"] for k, v in planets.items()}
        return planets

    # Calculate cross-aspects
    aspects = calc_synastry_aspects(flatten(chart1["planets"]), flatten(chart2["planets"]))

    # Calculate house overlaps
    # Planets of partner 1 in houses of partner 2
    house_overlaps_1 = calc_house_overlaps(flatten(chart1["planets"]), chart2["houses"])
    # Planets of partner 2 in houses of partner 1
    house_overlaps_2 = calc_house_overlaps(flatten(chart2["planets"]), chart1["houses"])

    return {
        "name1": name1,
        "name2": name2,
        "chart1": chart1,
        "chart2": chart2,
        "aspects": aspects,
        "house_overlaps_1": house_overlaps_1,
        "house_overlaps_2": house_overlaps_2,
    }


if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Usage: python synastry.py <date1> <time1> <city1> <date2> <time2> <city2>")
        print("Example: python synastry.py 24.04.1983 06:00 Izhevsk 25.10.1985 22:30 Mozhga")
        sys.exit(1)

    date1, time1, city1 = sys.argv[1], sys.argv[2], sys.argv[3]
    date2, time2, city2 = sys.argv[4], sys.argv[5], sys.argv[6]

    chart1 = nc.calc_natal_chart(date1, time1, city1)
    chart2 = nc.calc_natal_chart(date2, time2, city2)

    if "error" in chart1:
        print(f"❌ Error for partner 1: {chart1['error']}")
        sys.exit(1)
    if "error" in chart2:
        print(f"❌ Error for partner 2: {chart2['error']}")
        sys.exit(1)

    name1 = city1
    name2 = city2

    # Try to get names from args
    if len(sys.argv) >= 9:
        name1 = sys.argv[7]
        name2 = sys.argv[8]

    result = calc_synastry(chart1, chart2, name1, name2)
    print(format_synastry(name1, name2, chart1, chart2, result["aspects"],
                          result["house_overlaps_1"], result["house_overlaps_2"]))
