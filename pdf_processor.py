import fitz  # PyMuPDF
from PIL import Image
import os

class PDFProcessor:
    def __init__(self):
        self.files = []
        self.pages = []

    def add_file(self, file_path):
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == '.pdf':
            self._load_pdf(file_path)
        elif ext in ['.jpg', '.jpeg', '.png']:
            self._load_image_as_pdf(file_path)

    def _load_pdf(self, file_path):
        doc = fitz.open(file_path)
        for i in range(len(doc)):
            self.pages.append({
                'file': file_path,
                'page_number': i
            })
        self.files.append(file_path)

    def _load_image_as_pdf(self, image_path):
        image = Image.open(image_path).convert("RGB")
        temp_pdf_path = image_path + ".temp.pdf"
        image.save(temp_pdf_path, "PDF", resolution=100.0)
        self._load_pdf(temp_pdf_path)

    def get_total_pages(self):
        return len(self.pages)

    def get_pages(self):
        return self.pages

    def clear(self):
        self.files.clear()
        self.pages.clear()
