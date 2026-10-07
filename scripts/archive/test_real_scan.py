import fitz
import pytesseract
from PIL import Image
import io

pdf_path = r"E:\Boom Project\Knowledge\Astrology-Database\Nadi jyotish\SukarNadi1.pdf"

doc = fitz.open(pdf_path)
print(f"Pages: {len(doc)}")

# Test first 3 pages
for i in range(min(3, len(doc))):
    page = doc[i]
    pix = page.get_pixmap(matrix=fitz.Matrix(200/72, 200/72))
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    text = pytesseract.image_to_string(img, lang='eng')
    preview = text[:300].replace('\n', ' ')
    print(f"Page {i+1}: {preview}...")
    pix = None

doc.close()
print("Real scan test complete!")
