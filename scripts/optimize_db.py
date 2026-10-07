import os
import re
from pathlib import Path

def remove_boilerplate(lines):
    """Remove known boilerplate patterns"""
    cleaned = []
    skip_patterns = [
        r'^Skip to main content',
        r'^\s*[•\-]\s*\[image\]',
        r'^\s*[•\-]\s*(Web|Books|Video|Audio|Software|Images)',
        r'^\s*[•\-]\s*(uploadUPLOAD|ABOUT|CONTACT|BLOG|PROJECTS|HELP|DONATE|JOBS|VOLUNTEER|PEOPLE)',
        r'^Item not available',
        r'^The item is not available',
        r'^Digitized by:',
        r'^on \d+ \w+ \d{4}',
        r'^\s*Item not available due to issues',
        r'^\s*•\s*$',
    ]
    
    for line in lines:
        stripped = line.strip()
        skip = False
        for pattern in skip_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                skip = True
                break
        if not skip:
            cleaned.append(line)
    
    return cleaned

def remove_consecutive_duplicates(lines):
    """Remove exact duplicate lines that appear consecutively"""
    if not lines:
        return lines
    
    result = [lines[0]]
    for i in range(1, len(lines)):
        if lines[i].strip() != lines[i-1].strip() or not lines[i].strip():
            result.append(lines[i])
    
    return result

def unwrap_paragraphs(lines):
    """Join broken lines into paragraphs"""
    if not lines:
        return lines
    
    result = []
    current_para = []
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            if current_para:
                result.append(" ".join(current_para))
                current_para = []
            result.append("")
            continue
        
        # Check if line ends with sentence terminator
        ends_sentence = stripped.endswith(('.', '!', '?', ':', ';', '"', "'", ')', ']', '}'))
        
        # Check if line is a heading
        is_heading = stripped.startswith('#') or (len(stripped) < 50 and stripped.isupper())
        
        # Check if next logical continuation
        if is_heading:
            if current_para:
                result.append(" ".join(current_para))
                current_para = []
            result.append(stripped)
        elif ends_sentence:
            current_para.append(stripped)
            result.append(" ".join(current_para))
            current_para = []
        elif len(stripped) < 80:
            # Short line that doesn't end sentence — might be part of paragraph or standalone
            if current_para:
                # Check if previous para line is also short — if so, flush previous and start new
                prev_len = len(current_para[-1]) if current_para else 0
                if prev_len < 80 and len(current_para) >= 1:
                    result.append(" ".join(current_para))
                    current_para = [stripped]
                else:
                    current_para.append(stripped)
            else:
                current_para = [stripped]
        else:
            current_para.append(stripped)
    
    if current_para:
        result.append(" ".join(current_para))
    
    return result

def fix_broken_hyphens(lines):
    """Fix words broken across lines with hyphens"""
    result = []
    
    for i, line in enumerate(lines):
        if i == 0:
            result.append(line)
            continue
        
        prev_line = lines[i-1].rstrip()
        curr_line = line.lstrip()
        
        # Check if previous line ends with hyphen and current starts with text
        if prev_line.endswith('-') and curr_line and curr_line[0].isalpha():
            # Join them
            if result:
                result[-1] = prev_line[:-1] + curr_line
            else:
                result.append(prev_line[:-1] + curr_line)
        else:
            result.append(line)
    
    return result

def collapse_whitespace(lines):
    """Collapse multiple blank lines to max 2, strip trailing whitespace"""
    result = []
    blank_count = 0
    
    for line in lines:
        stripped = line.rstrip()
        
        if not stripped:
            blank_count += 1
            if blank_count <= 2:
                result.append("")
        else:
            blank_count = 0
            result.append(stripped)
    
    # Remove leading/trailing blank lines
    while result and not result[0]:
        result.pop(0)
    while result and not result[-1]:
        result.pop()
    
    return result

def optimize_markdown(filepath):
    """Optimize a single markdown file for token efficiency"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 0, 0, f"Read error: {e}"
    
    original_size = len(content)
    original_lines = content.count('\n')
    
    lines = content.split('\n')
    
    # Step 1: Remove boilerplate
    lines = remove_boilerplate(lines)
    
    # Step 2: Remove consecutive duplicates
    lines = remove_consecutive_duplicates(lines)
    
    # Step 3: Fix broken hyphens
    lines = fix_broken_hyphens(lines)
    
    # Step 4: Unwrap paragraphs
    lines = unwrap_paragraphs(lines)
    
    # Step 5: Remove consecutive duplicates again (after unwrapping may reveal more)
    lines = remove_consecutive_duplicates(lines)
    
    # Step 6: Collapse whitespace
    lines = collapse_whitespace(lines)
    
    new_content = '\n'.join(lines)
    
    # Ensure file ends with newline
    if not new_content.endswith('\n'):
        new_content += '\n'
    
    new_size = len(new_content)
    new_lines = new_content.count('\n')
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except Exception as e:
        return original_size, original_size, f"Write error: {e}"
    
    return original_size, new_size, None

def main():
    db_base = r"E:\Boom Project\Knowledge\Astrology-Database"
    
    files = []
    for root, dirs, filenames in os.walk(db_base):
        for f in filenames:
            if f.endswith('.md'):
                files.append(os.path.join(root, f))
    
    total_original = 0
    total_new = 0
    success = 0
    failed = 0
    errors = []
    
    print(f"Optimizing {len(files)} markdown files...")
    print(f"{'='*60}")
    
    for i, filepath in enumerate(files, 1):
        orig, new, err = optimize_markdown(filepath)
        
        if err:
            failed += 1
            errors.append(f"{os.path.basename(filepath)}: {err}")
        else:
            total_original += orig
            total_new += new
            saved = orig - new
            pct = (saved / orig * 100) if orig > 0 else 0
            success += 1
            
            if i <= 5 or saved > 50000:
                print(f"[{i}/{len(files)}] {os.path.basename(filepath)}: {orig//1024}KB -> {new//1024}KB (-{pct:.1f}%)")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Files processed: {success}/{len(files)}")
    print(f"  Failed: {failed}")
    print(f"  Original: {total_original//1024} KB ({total_original//4:,} est. tokens)")
    print(f"  Optimized: {total_new//1024} KB ({total_new//4:,} est. tokens)")
    print(f"  Saved: {(total_original-total_new)//1024} KB ({(total_original-total_new)//4:,} est. tokens)")
    print(f"  Reduction: {((total_original-total_new)/total_original*100):.1f}%")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors[:5]:
            print(f"  {e}")

if __name__ == "__main__":
    main()
