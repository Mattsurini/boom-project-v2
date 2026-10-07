import os
import sys
import json
import re
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

INDEX_PATH = r"E:\Boom Project\Knowledge\indexes\astrology_db_index.json"
DB_BASE = r"E:\Boom Project\Knowledge\Astrology-Database"

# Maximum context to return per query (in characters)
MAX_CONTEXT = 15000

def load_index():
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_query(q):
    """Normalize query to topic/keyword keys"""
    q = q.lower().strip()
    # Remove punctuation
    q = re.sub(r'[^\w\s]', '', q)
    # Try as phrase first, then individual terms
    phrase = q.replace(' ', '_')
    terms = q.split()
    return phrase, terms

def find_files(index, phrase, terms):
    """Find relevant files from index"""
    topic_index = index.get('topic_index', {})
    files = index.get('files', [])
    
    matches = []
    matched_paths = set()
    
    # Exact phrase match
    if phrase in topic_index:
        for entry in topic_index[phrase]:
            if entry['path'] not in matched_paths:
                matches.append(entry)
                matched_paths.add(entry['path'])
    
    # Individual term matches
    for term in terms:
        term_key = term
        if term_key in topic_index:
            for entry in topic_index[term_key]:
                if entry['path'] not in matched_paths:
                    matches.append(entry)
                    matched_paths.add(entry['path'])
    
    # Fallback: search filenames if no index match
    if not matches:
        for f in files:
            f_name = f['path'].lower()
            if any(term in f_name for term in terms) or phrase.replace('_', '-') in f_name:
                if f['path'] not in matched_paths:
                    matches.append({'path': f['path'], 'title': f['title'], 'size_kb': f['size_kb']})
                    matched_paths.add(f['path'])
    
    return matches

def grep_excerpts(filepath, terms, max_chars=3000):
    """Greppable excerpt extraction from a file with deduplication"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None
    
    lines = content.split('\n')
    excerpts = []
    seen_contexts = set()
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(term in line_lower for term in terms):
            # Get context: 3 lines before, the match line, 3 lines after
            start = max(0, i - 3)
            end = min(len(lines), i + 4)
            context = '\n'.join(lines[start:end])
            
            # Skip if we've seen this exact context (dedupe duplicates)
            ctx_hash = hash(context.strip())
            if ctx_hash in seen_contexts:
                continue
            seen_contexts.add(ctx_hash)
            
            # Highlight the match
            for term in terms:
                context = re.sub(
                    rf'(?i)(\b{re.escape(term)}\b)',
                    r'**\1**',
                    context
                )
            
            excerpts.append({
                'file': os.path.basename(filepath),
                'line': i + 1,
                'context': context
            })
            
            # Stop if we have enough content
            total = sum(len(e['context']) for e in excerpts)
            if total > max_chars:
                break
    
    return excerpts

def query(q, max_results=5, max_chars_per_file=2000):
    """Main query function"""
    index = load_index()
    phrase, terms = normalize_query(q)
    
    print(f"Query: '{q}'")
    print(f"Parsed: phrase='{phrase}', terms={terms}")
    print(f"{'='*60}")
    
    matches = find_files(index, phrase, terms)
    
    if not matches:
        print("No files found in index.")
        return []
    
    print(f"Found {len(matches)} relevant file(s):\n")
    
    all_excerpts = []
    total_chars = 0
    
    for match in matches[:max_results]:
        filepath = os.path.join(DB_BASE, match['path'])
        print(f"--- {match['title']} ({match['size_kb']} KB) ---")
        
        excerpts = grep_excerpts(filepath, terms, max_chars=max_chars_per_file)
        
        if excerpts:
            for ex in excerpts[:10]:  # Cap at 10 excerpts per file
                if total_chars + len(ex['context']) > MAX_CONTEXT:
                    print("\n[Context limit reached]")
                    return all_excerpts
                
                print(f"\n{ex['file']}:{ex['line']}")
                print(ex['context'])
                all_excerpts.append(ex)
                total_chars += len(ex['context'])
        else:
            print("  (no exact keyword matches in file — file is relevant via index topic)")
        
        print()
    
    print(f"{'='*60}")
    print(f"Returned {len(all_excerpts)} excerpts (~{total_chars} chars)")
    
    return all_excerpts

def main():
    if len(sys.argv) < 2:
        print("Usage: python query_db.py \"<search query>\"")
        print("Example: python query_db.py \"Jaimini Chara Dasha\"")
        sys.exit(1)
    
    query_str = ' '.join(sys.argv[1:])
    query(query_str)

if __name__ == "__main__":
    main()
