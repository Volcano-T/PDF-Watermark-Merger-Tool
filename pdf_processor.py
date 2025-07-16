from io import BytesIO
import fitz

class PDFProcessor:
    def __init__(self):
        self.files = []  # store dicts with keys: name, type, stream, pages

    def add_file(self, file_path=None, stream=None, name=None, raw_image_path=None):
        if raw_image_path:
            self.files.append({
                "name": raw_image_path,
                "type": "image",
                "raw_image_path": raw_image_path,
                "stream": None,
                "pages": 1
            })
            return
        else:
            if stream:
                doc = fitz.open(stream=stream.getvalue(), filetype="pdf")
            elif file_path:
                doc = fitz.open(file_path)
                stream = BytesIO()
                doc.save(stream)
                stream.seek(0)
                name = file_path
            else:
                return
            self.files.append({
                "name": name,
                "type": "pdf",
                "stream": stream,
                "pages": doc.page_count
            })

    def get_total_pages(self):
        return sum(f["pages"] for f in self.files)

    def get_all_streams(self):
        return [f["stream"] for f in self.files]
