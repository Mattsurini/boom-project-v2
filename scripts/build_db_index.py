import os
import json
import re
from pathlib import Path
from collections import defaultdict

DB_BASE = r"E:\Boom Project\Knowledge\Astrology-Database"
INDEX_PATH = r"E:\Boom Project\Knowledge\indexes\astrology_db_index.json"

def extract_headings(lines):
    """Extract all markdown headings"""
    headings = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            # Clean heading
            h = re.sub(r'^#+\s*', '', stripped).strip()
            if h:
                headings.append(h)
    return headings

def extract_keywords(text):
    """Extract capitalized multi-word terms as keywords"""
    # Find capitalized phrases like "Jaimini Chara Dasha", "Vimshottari Dasa"
    pattern = r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+\b'
    matches = re.findall(pattern, text)
    
    # Filter out common noise words
    noise = {'The', 'And', 'For', 'With', 'From', 'This', 'That', 'But', 'Not', 'Are', 'Was', 'Had', 'His', 'Her', 'Has', 'Have', 'Will', 'Would', 'Could', 'Should', 'They', 'Them', 'Their', 'There', 'Where', 'When', 'What', 'How', 'Why', 'Who', 'Which', 'While', 'During', 'Before', 'After', 'Above', 'Below', 'Under', 'Over', 'Into', 'Onto', 'Upon', 'About', 'Against', 'Between', 'Among', 'Through', 'Throughout', 'Within', 'Without'}
    
    keywords = []
    for match in matches:
        words = match.split()
        # Keep only if at least one word is not a common noise word
        if any(w not in noise for w in words):
            keywords.append(match)
    
    return list(set(keywords))

def infer_topics(filename, folder, headings):
    """Infer topic tags from filename, folder path, and headings"""
    topics = set()
    
    # From folder
    folder_lower = folder.lower()
    topic_map = {
        'bhrigu': ['bhrigu', 'nadi', 'palmistry'],
        'bv raman': ['bv raman', 'vedic astrology'],
        'jaimini': ['jaimini', 'chara dasha', 'sthira dasha', 'karaka'],
        'kn rao': ['kn rao', 'kp astrology', 'predictive'],
        'nadi': ['nadi', 'nadi jyotish', 'palm-leaf'],
        'classics': ['classics', 'bphs', 'parashara', 'varahamihira'],
        'uranian': ['uranian', 'hamburg school', 'transneptunian'],
        'articles': ['articles', 'techniques', 'research'],
        'good books': ['good books', 'advanced techniques'],
        'birth-detail': ['birth charts', 'case studies', 'rectification'],
    }
    
    for key, tags in topic_map.items():
        if key in folder_lower:
            topics.update(tags)
    
    # From filename
    name_lower = filename.lower().replace('.md', '')
    name_topics = {
        'jaimini': 'jaimini',
        'chara': 'chara dasha',
        'dasha': 'dasha systems',
        'dasa': 'dasha systems',
        'bphs': 'bphs',
        'parashara': 'parashara',
        'nadi': 'nadi',
        'kp': 'kp astrology',
        'krishnamurti': 'kp astrology',
        'horary': 'horary',
        'prashna': 'prashna',
        'navamsa': 'navamsa',
        'nakshatra': 'nakshatra',
        'rahu': 'nodes',
        'ketu': 'nodes',
        'saturn': 'saturn',
        'mars': 'mars',
        'venus': 'venus',
        'jupiter': 'jupiter',
        'mercury': 'mercury',
        'sun': 'sun',
        'moon': 'moon',
        'house': 'houses',
        'yoga': 'yogas',
        'raja': 'raja yoga',
        'profession': 'career',
        'marriage': 'marriage',
        'financial': 'financial astrology',
        'medical': 'medical astrology',
        'rectification': 'birth time rectification',
        'transit': 'transits',
        'synastry': 'synastry',
        'divisional': 'divisional charts',
        'varga': 'divisional charts',
    }
    
    for key, topic in name_topics.items():
        if key in name_lower:
            topics.add(topic)
    
    # From headings
    for h in headings:
        h_lower = h.lower()
        for key, topic in name_topics.items():
            if key in h_lower:
                topics.add(topic)
    
    return sorted(topics)

def build_index():
    files = []
    for root, dirs, filenames in os.walk(DB_BASE):
        for f in filenames:
            if f.endswith('.md') and f != 'index.md':
                filepath = os.path.join(root, f)
                relpath = os.path.relpath(filepath, DB_BASE)
                folder = os.path.dirname(relpath)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                except Exception as e:
                    print(f"  Skip {f}: {e}")
                    continue
                
                lines = content.split('\n')
                headings = extract_headings(lines)
                keywords = extract_keywords(content[:20000])  # First 20KB for speed
                topics = infer_topics(f, folder, headings)
                
                # Title from first H1 or filename
                title = f.replace('.md', '')
                if headings:
                    title = headings[0]
                
                entry = {
                    'path': relpath,
                    'folder': folder,
                    'title': title,
                    'headings': headings[:20],  # Cap at 20 headings
                    'keywords': keywords[:30],  # Cap at 30 keywords
                    'topics': topics,
                    'size_kb': round(len(content) / 1024, 1),
                    'lines': len(lines)
                }
                files.append(entry)
    
    # Build reverse index: topic -> files
    topic_index = defaultdict(list)
    for entry in files:
        for topic in entry['topics']:
            topic_index[topic].append({
                'path': entry['path'],
                'title': entry['title'],
                'size_kb': entry['size_kb']
            })
        for kw in entry['keywords']:
            # Simple keyword normalization
            kw_lower = kw.lower().replace(' ', '_')
            topic_index[kw_lower].append({
                'path': entry['path'],
                'title': entry['title'],
                'size_kb': entry['size_kb']
            })
    
    # Convert to regular dict for JSON
    topic_index = {k: v for k, v in topic_index.items()}
    
    index = {
        'meta': {
            'version': '1.0',
            'total_files': len(files),
            'total_topics': len(topic_index),
            'db_path': str(DB_BASE)
        },
        'files': files,
        'topic_index': topic_index
    }
    
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"Index built: {INDEX_PATH}")
    print(f"  Files: {len(files)}")
    print(f"  Topics/keywords: {len(topic_index)}")
    print(f"  Total size: {sum(e['size_kb'] for e in files):.0f} KB")
    
    # Show top topics
    print(f"\nTop topics by file count:")
    sorted_topics = sorted(topic_index.items(), key=lambda x: len(x[1]), reverse=True)[:15]
    for topic, entries in sorted_topics:
        print(f"  {topic}: {len(entries)} files")

if __name__ == "__main__":
    build_index()
