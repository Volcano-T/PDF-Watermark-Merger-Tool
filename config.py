from pdf_processor import PDFProcessor

settings = {
    "files": [],
    "page_size": "",
    "margin": "",

    "watermark": {
        "type": "Text",
        "text": "",
        "image_path": None,
        "font_size": 16,
        "opacity": 0.3,
        "rotation": 0,
        "position": "Center",
        "page_range": "All"
    },

    "signature": {
        "image_path": None,
        "position": "Bottom-Right",
        "scale": 0.3,
        "rotation": 0,
        "page_range": "All"
    },

    "header_footer": {
        "header_text": "",
        "footer_text": "",
        "font_size": 12,
        "page_range": "All",
        "include_time": False,
        "include_date": False,
        "include_page_number": False
    },
    "processor": PDFProcessor(),
}
