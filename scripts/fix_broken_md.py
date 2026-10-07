import os
import fitz  # PyMuPDF
from pathlib import Path

def find_pdf_for_md(md_path, source_base):
    """Find matching PDF for a broken .md file"""
    md_name = Path(md_path).stem
    md_base = md_name.lower().replace(' ', '_').replace('-', '_')
    
    # Search recursively in source directory
    for root, dirs, files in os.walk(source_base):
        for f in files:
            if f.lower().endswith('.pdf'):
                pdf_name = Path(f).stem
                pdf_base = pdf_name.lower().replace(' ', '_').replace('-', '_')
                # Check if names match (with some tolerance)
                if md_base == pdf_base or md_base in pdf_base or pdf_base in md_base:
                    return os.path.join(root, f)
    return None

def convert_pdf_to_md(pdf_path, md_path):
    """Extract text from PDF and save as markdown"""
    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_parts.append(text)
        
        doc.close()
        
        if not text_parts:
            print(f"  WARNING: No text extracted from {pdf_path}")
            return False
        
        full_text = "\n\n".join(text_parts)
        
        # Add markdown header
        title = Path(pdf_path).stem
        md_content = f"# {title}\n\n{full_text}\n"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return True
    except Exception as e:
        print(f"  ERROR converting {pdf_path}: {e}")
        return False

def main():
    db_base = r"E:\Boom Project\Knowledge\Astrology-Database"
    source_base = r"E:\Boom Project\Knowledge\Astrology-Database"
    
    # Find all broken .md files (< 1000 bytes)
    broken_files = []
    for root, dirs, files in os.walk(db_base):
        # Skip subdirectories that contain original PDFs (not converted)
        for f in files:
            if f.endswith('.md'):
                md_path = os.path.join(root, f)
                size = os.path.getsize(md_path)
                if size < 1000 and f != 'index.md':  # Skip small index files
                    broken_files.append(md_path)
    
    print(f"Found {len(broken_files)} broken .md files")
    
    fixed = 0
    failed = 0
    not_found = 0
    
    for md_path in broken_files:
        md_name = os.path.basename(md_path)
        print(f"\nProcessing: {md_name}")
        
        pdf_path = find_pdf_for_md(md_path, source_base)
        
        if pdf_path:
            print(f"  Found PDF: {pdf_path}")
            if convert_pdf_to_md(pdf_path, md_path):
                new_size = os.path.getsize(md_path)
                print(f"  SUCCESS: Re-converted ({new_size} bytes)")
                fixed += 1
            else:
                failed += 1
        else:
            print(f"  ERROR: No matching PDF found")
            not_found += 1
    
    print(f"\n{'='*50}")
    print(f"SUMMARY:")
    print(f"  Fixed: {fixed}")
    print(f"  Failed: {failed}")
    print(f"  PDF not found: {not_found}")

if __name__ == "__main__":
    main()
