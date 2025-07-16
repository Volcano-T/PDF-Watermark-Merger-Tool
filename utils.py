from PIL import Image
from io import BytesIO
from config import settings

def convert_image_to_sized_pdf(image_path):
    page_settings = settings.get("page_settings", {})
    page_width = page_settings.get("page_width", 595)
    page_height = page_settings.get("page_height", 842)

    img = Image.open(image_path).convert("RGB")
    img_ratio = img.width / img.height
    page_ratio = page_width / page_height

    if img_ratio > page_ratio:
        new_width = page_width
        new_height = int(page_width / img_ratio)
    else:
        new_height = page_height
        new_width = int(page_height * img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Paste on white canvas
    canvas = Image.new("RGB", (page_width, page_height), "white")
    x = (page_width - new_width) // 2
    y = (page_height - new_height) // 2
    canvas.paste(img, (x, y))

    pdf_stream = BytesIO()
    canvas.save(pdf_stream, format="PDF")
    pdf_stream.seek(0)
    return pdf_stream
