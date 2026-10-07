import os
import fitz  # PyMuPDF
from pathlib import Path
import io

def find_pdf_for_md(md_path, source_base):
    md_name = Path(md_path).stem
    md_base = md_name.lower().replace(' ', '_').replace('-', '_')
    
    for root, dirs, files in os.walk(source_base):
        for f in files:
            if f.lower().endswith('.pdf'):
                pdf_name = Path(f).stem
                pdf_base = pdf_name.lower().replace(' ', '_').replace('-', '_')
                if md_base == pdf_base or md_base in pdf_base or pdf_base in md_base:
                    return os.path.join(root, f)
    return None

def ocr_pdf_to_md(pdf_path, md_path):
    """OCR a scan-only PDF and save as markdown"""
    import pytesseract
    from PIL import Image
    
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"    ERROR opening PDF: {e}")
        return False
    
    all_text = []
    total_pages = len(doc)
    
    print(f"    Processing {total_pages} pages...")
    
    for page_num in range(total_pages):
        try:
            page = doc[page_num]
            
            # Render page to image at 200 DPI
            pix = page.get_pixmap(matrix=fitz.Matrix(200/72, 200/72))
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # OCR the image
            text = pytesseract.image_to_string(img, lang='eng')
            
            if text.strip():
                all_text.append(text)
            
            pix = None  # Free memory
            
        except Exception as e:
            print(f"    ERROR on page {page_num + 1}: {e}")
            continue
    
    doc.close()
    
    if not all_text:
        print(f"    WARNING: No text extracted")
        return False
    
    # Write to markdown
    title = Path(pdf_path).stem
    full_text = "\n\n".join(all_text)
    
    # Clean up excessive whitespace
    lines = full_text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)
    
    # Join with reasonable paragraph breaks
    paragraphs = []
    current_para = []
    for line in cleaned_lines:
        if len(line) < 50 and not line.endswith(('.', '!', '?', ':', ';')):
            # Likely a heading or short line
            if current_para:
                paragraphs.append(" ".join(current_para))
                current_para = []
            paragraphs.append(line)
        else:
            current_para.append(line)
    
    if current_para:
        paragraphs.append(" ".join(current_para))
    
    final_text = "\n\n".join(paragraphs)
    
    md_content = f"""---
date: '2026-08-01'
tags:
- astrology
- knowledge-base
- ocr-converted
source: ASTROLOGY-BOOKS-DATABASE
---

# {title}

> **Note**: This document was converted from a scanned PDF using OCR. Some errors may exist.

{final_text}
"""
    
    try:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        return True
    except Exception as e:
        print(f"    ERROR writing file: {e}")
        return False

def main():
    db_base = r"E:\Boom Project\Knowledge\Astrology-Database"
    source_base = r"E:\Boom Project\Knowledge\Astrology-Database"
    
    # Find all scan-only files
    scan_files = []
    for root, dirs, files in os.walk(db_base):
        for f in files:
            if f.endswith('.md') and f != 'index.md':
                md_path = os.path.join(root, f)
                try:
                    with open(md_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if 'needs-ocr' in content or 'SCAN-ONLY' in content:
                            scan_files.append(md_path)
                except:
                    pass
    
    print(f"Found {len(scan_files)} scan-only files to OCR")
    print(f"{'='*60}")
    
    success = 0
    failed = 0
    
    for i, md_path in enumerate(scan_files, 1):
        md_name = Path(md_path).stem
        print(f"\n[{i}/{len(scan_files)}] {md_name}")
        
        pdf_path = find_pdf_for_md(md_path, source_base)
        
        if not pdf_path:
            print(f"  ERROR: PDF not found")
            failed += 1
            continue
        
        if ocr_pdf_to_md(pdf_path, md_path):
            new_size = os.path.getsize(md_path)
            print(f"  SUCCESS: {new_size} bytes")
            success += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"OCR Complete: {success} succeeded, {failed} failed")

if __name__ == "__main__":
    main()
