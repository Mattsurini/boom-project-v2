import os
import json
import re

INDEX_PATH = r"E:\Boom Project\Knowledge\indexes\astrology_db_index.json"
DB_BASE = r"E:\Boom Project\Knowledge\Astrology-Database"

def _load_index():
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def _normalize(q):
    q = q.lower().strip()
    q = re.sub(r'[^\w\s]', '', q)
    return q.replace(' ', '_'), q.split()

def search(query, max_results=5, max_chars_per_file=2000, max_total_chars=15000):
    """
    Search the astrology DB and return relevant excerpts.
    
    Args:
        query: search string (e.g., "Jaimini Chara Dasha")
        max_results: max files to search
        max_chars_per_file: max characters to extract per file
        max_total_chars: max total characters to return
    
    Returns:
        list of dicts: {file, line, context}
    """
    index = _load_index()
    phrase, terms = _normalize(query)
    topic_index = index.get('topic_index', {})
    files = index.get('files', [])
    
    # Find files
    matched_paths = set()
    matches = []
    
    if phrase in topic_index:
        for e in topic_index[phrase]:
            if e['path'] not in matched_paths:
                matches.append(e); matched_paths.add(e['path'])
    
    for term in terms:
        if term in topic_index:
            for e in topic_index[term]:
                if e['path'] not in matched_paths:
                    matches.append(e); matched_paths.add(e['path'])
    
    if not matches:
        # Fallback: search filenames
        for f in files:
            if any(t in f['path'].lower() for t in terms):
                if f['path'] not in matched_paths:
                    matches.append({'path': f['path'], 'title': f['title'], 'size_kb': f['size_kb']})
                    matched_paths.add(f['path'])
    
    # Extract excerpts
    all_excerpts = []
    total_chars = 0
    
    for match in matches[:max_results]:
        filepath = os.path.join(DB_BASE, match['path'])
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue
        
        lines = content.split('\n')
        seen = set()
        file_chars = 0
        
        for i, line in enumerate(lines):
            if any(t in line.lower() for t in terms):
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                ctx = '\n'.join(lines[start:end]).strip()
                
                h = hash(ctx)
                if h in seen:
                    continue
                seen.add(h)
                
                if total_chars + len(ctx) > max_total_chars:
                    return all_excerpts
                if file_chars + len(ctx) > max_chars_per_file:
                    break
                
                all_excerpts.append({
                    'file': os.path.basename(filepath),
                    'path': match['path'],
                    'line': i + 1,
                    'context': ctx
                })
                total_chars += len(ctx)
                file_chars += len(ctx)
    
    return all_excerpts

def search_summary(query, max_results=5):
    """Return just file matches without full excerpts (low token)"""
    index = _load_index()
    phrase, terms = _normalize(query)
    topic_index = index.get('topic_index', {})
    files = index.get('files', [])
    
    matched = []
    seen = set()
    
    if phrase in topic_index:
        for e in topic_index[phrase]:
            if e['path'] not in seen:
                matched.append(e); seen.add(e['path'])
    
    for term in terms:
        if term in topic_index:
            for e in topic_index[term]:
                if e['path'] not in seen:
                    matched.append(e); seen.add(e['path'])
    
    if not matched:
        for f in files:
            if any(t in f['path'].lower() for t in terms):
                if f['path'] not in seen:
                    matched.append({'path': f['path'], 'title': f['title'], 'size_kb': f['size_kb']})
                    seen.add(f['path'])
    
    return matched[:max_results]
