import os
import fitz
from pathlib import Path
import io
import pytesseract
from PIL import Image

def test_ocr_one_file():
    db_base = r"E:\Boom Project\Knowledge\Astrology-Database"
    source_base = r"E:\Boom Project\Knowledge\Astrology-Database"
    
    # Find first scan-only file
    for root, dirs, files in os.walk(db_base):
        for f in files:
            if f.endswith('.md') and f != 'index.md':
                md_path = os.path.join(root, f)
                with open(md_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if 'needs-ocr' in content or 'SCAN-ONLY' in content:
                        print(f"Testing on: {f}")
                        
                        # Find PDF
                        md_name = Path(md_path).stem
                        md_base = md_name.lower().replace(' ', '_').replace('-', '_')
                        pdf_path = None
                        for sroot, sdirs, sfiles in os.walk(source_base):
                            for sf in sfiles:
                                if sf.lower().endswith('.pdf'):
                                    pdf_name = Path(sf).stem
                                    pdf_base = pdf_name.lower().replace(' ', '_').replace('-', '_')
                                    if md_base == pdf_base or md_base in pdf_base or pdf_base in md_base:
                                        pdf_path = os.path.join(sroot, sf)
                                        break
                            if pdf_path:
                                break
                        
                        if not pdf_path:
                            print("PDF not found")
                            return
                        
                        print(f"PDF: {pdf_path}")
                        
                        try:
                            doc = fitz.open(pdf_path)
                            total = len(doc)
                            print(f"Pages: {total}")
                            
                            # Test first 3 pages
                            for i in range(min(3, total)):
                                page = doc[i]
                                pix = page.get_pixmap(matrix=fitz.Matrix(200/72, 200/72))
                                img_data = pix.tobytes("png")
                                img = Image.open(io.BytesIO(img_data))
                                text = pytesseract.image_to_string(img, lang='eng')
                                preview = text[:200].replace('\n', ' ')
                                print(f"  Page {i+1}: {preview}...")
                                pix = None
                            
                            doc.close()
                            print("Pipeline works!")
                            return
                        except Exception as e:
                            print(f"ERROR: {e}")
                            return
    
    print("No scan-only files found")

if __name__ == "__main__":
    test_ocr_one_file()
