import os
import re
from pathlib import Path

def is_pdf_extracted_text(lines):
    """Detect if file has typical PDF-extraction line breaking pattern"""
    if not lines:
        return False
    
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return False
    
    avg_len = sum(len(l.strip()) for l in non_empty) / len(non_empty)
    short_ratio = sum(1 for l in non_empty if len(l.strip()) < 90) / len(non_empty)
    
    # If average line < 90 and > 60% are short, treat as PDF-extracted
    return avg_len < 90 and short_ratio > 0.6

def aggressive_unwrap(lines):
    """Aggressively unwrap PDF-extracted text into paragraphs"""
    paragraphs = []
    current_para_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if not stripped:
            # Blank line — flush current paragraph
            if current_para_lines:
                para = " ".join(current_para_lines)
                # Clean up internal spaces
                para = re.sub(r'\s+', ' ', para)
                paragraphs.append(para)
                current_para_lines = []
            continue
        
        # Check if this is a heading
        is_heading = (
            stripped.startswith('#') or
            (len(stripped) < 60 and stripped.isupper() and len(stripped) > 5) or
            re.match(r'^\d+\.\s+[A-Z]', stripped) or
            re.match(r'^(Chapter|Section|Part)\s+\d+', stripped, re.IGNORECASE)
        )
        
        if is_heading:
            if current_para_lines:
                para = " ".join(current_para_lines)
                para = re.sub(r'\s+', ' ', para)
                paragraphs.append(para)
                current_para_lines = []
            paragraphs.append(stripped)
            continue
        
        # Check if line ends with a hyphen (broken word)
        if stripped.endswith('-') and i + 1 < len(lines) and lines[i + 1].strip():
            # Will be handled in post-processing
            pass
        
        current_para_lines.append(stripped)
    
    # Flush remaining
    if current_para_lines:
        para = " ".join(current_para_lines)
        para = re.sub(r'\s+', ' ', para)
        paragraphs.append(para)
    
    return paragraphs

def fix_hyphens_and_join(paragraphs):
    """Fix hyphenated words and clean up spacing"""
    result = []
    for para in paragraphs:
        # Fix word- word patterns (broken hyphenation)
        para = re.sub(r'(\w)-\s+(\w)', r'\1\2', para)
        # Fix word- at end of string
        para = re.sub(r'(\w)-\s*$', r'\1', para)
        # Clean multiple spaces
        para = re.sub(r'\s+', ' ', para)
        result.append(para.strip())
    return result

def remove_boilerplate_patterns(lines):
    """Remove known boilerplate from the start and throughout"""
    # Patterns to remove completely
    remove_patterns = [
        r'^Skip to main content\s*$',
        r'^\s*[•\-]\s*\[image\]\s*$',
        r'^\s*[•\-]\s*(Web|Books|Video|Audio|Software|Images|uploadUPLOAD|ABOUT|CONTACT|BLOG|PROJECTS|HELP|DONATE|JOBS|VOLUNTEER|PEOPLE)\s*$',
        r'^Item not available\s*$',
        r'^The item is not available.*$',
        r'^Digitized by:.*$',
        r'^on \d+ \w+ \d{4}\s*$',
        r'^\s*Item not available due to issues.*$',
        r'^\s*•\s*$',
        r'^Item not available due to issues with the item\'s content\.\s*$',
    ]
    
    cleaned = []
    for line in lines:
        stripped = line.strip()
        skip = False
        for pattern in remove_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                skip = True
                break
        if not skip:
            cleaned.append(line)
    
    # Remove leading blank lines
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    
    return cleaned

def remove_consecutive_duplicate_paragraphs(paragraphs):
    """Remove exact duplicate paragraphs that appear consecutively"""
    if not paragraphs:
        return paragraphs
    
    result = [paragraphs[0]]
    for i in range(1, len(paragraphs)):
        if paragraphs[i] != paragraphs[i-1]:
            result.append(paragraphs[i])
    
    return result

def optimize_file(filepath):
    """Optimize a single markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None, None, f"Read error: {e}"
    
    original_size = len(content)
    original_lines = content.count('\n')
    
    lines = content.split('\n')
    
    # Step 1: Remove boilerplate
    lines = remove_boilerplate_patterns(lines)
    
    # Step 2: Detect PDF extraction pattern
    if is_pdf_extracted_text(lines):
        # Aggressive unwrap
        paragraphs = aggressive_unwrap(lines)
        paragraphs = fix_hyphens_and_join(paragraphs)
        paragraphs = remove_consecutive_duplicate_paragraphs(paragraphs)
        
        # Rebuild with proper spacing
        result_lines = []
        for p in paragraphs:
            if p.startswith('#'):
                result_lines.append(p)
                result_lines.append("")
            else:
                # Wrap very long paragraphs to ~120 chars for readability
                if len(p) > 120:
                    words = p.split(' ')
                    current = ""
                    for word in words:
                        if len(current) + len(word) + 1 > 120:
                            result_lines.append(current.strip())
                            current = word + " "
                        else:
                            current += word + " "
                    if current:
                        result_lines.append(current.strip())
                else:
                    result_lines.append(p)
                result_lines.append("")
        
        lines = result_lines
    else:
        # Light optimization for already well-formatted files
        paragraphs = aggressive_unwrap(lines)
        paragraphs = fix_hyphens_and_join(paragraphs)
        paragraphs = remove_consecutive_duplicate_paragraphs(paragraphs)
        
        result_lines = []
        for p in paragraphs:
            if p.startswith('#'):
                result_lines.append(p)
                result_lines.append("")
            else:
                result_lines.append(p)
                result_lines.append("")
        lines = result_lines
    
    # Step 3: Collapse excessive blank lines
    cleaned = []
    blank_count = 0
    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 2:
                cleaned.append("")
        else:
            blank_count = 0
            cleaned.append(line)
    
    # Trim leading/trailing blanks
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    
    new_content = '\n'.join(cleaned)
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
    pdf_extracted_count = 0
    
    print(f"Optimizing {len(files)} markdown files...")
    print(f"{'='*60}")
    
    for i, filepath in enumerate(files, 1):
        orig, new, err = optimize_file(filepath)
        
        if err:
            failed += 1
            errors.append(f"{os.path.basename(filepath)}: {err}")
        else:
            total_original += orig
            total_new += new
            saved = orig - new
            pct = (saved / orig * 100) if orig > 0 else 0
            success += 1
            
            if saved > 10000 or i <= 3:
                print(f"[{i}/{len(files)}] {os.path.basename(filepath)}: {orig//1024}KB -> {new//1024}KB (-{pct:.1f}%)")
            elif i % 30 == 0:
                print(f"[{i}/{len(files)}] ...")
    
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
