import tkinter as tk
from config import settings
from PIL import Image, ImageTk
import fitz
import io
from io import BytesIO
from utils import convert_image_to_sized_pdf

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#c6f0f5")
        self.controller = controller

        self.page_size = tk.StringVar(value="A4")
        self.margin = tk.StringVar(value="No margin")

        self.page_size.trace_add("write", self.update_preview)
        self.margin.trace_add("write", self.update_preview)

        # ==== Left Controls ====
        size_box = tk.LabelFrame(self, text="Page size:", font=("Arial", 11, "bold"), bg="#e6e6e6")
        size_box.place(relx=0.1, rely=0.15, relwidth=0.25, relheight=0.18)

        tk.Radiobutton(size_box, text="A4", variable=self.page_size, value="A4", bg="#e6e6e6").place(relx=0.05, rely=0.2)
        tk.Radiobutton(size_box, text="Legal", variable=self.page_size, value="Legal", bg="#e6e6e6").place(relx=0.55, rely=0.2)
        tk.Radiobutton(size_box, text="Letter", variable=self.page_size, value="Letter", bg="#e6e6e6").place(relx=0.55, rely=0.55)

        margin_box = tk.LabelFrame(self, text="Margin:", font=("Arial", 11, "bold"), bg="#e6e6e6")
        margin_box.place(relx=0.1, rely=0.4, relwidth=0.25, relheight=0.22)

        tk.Radiobutton(margin_box, text="No margin", variable=self.margin, value="No margin", bg="#e6e6e6").place(relx=0.05, rely=0.2)
        tk.Radiobutton(margin_box, text="Normal margin", variable=self.margin, value="Normal margin", bg="#e6e6e6").place(relx=0.05, rely=0.5)
        tk.Radiobutton(margin_box, text="Narrow margin", variable=self.margin, value="Narrow margin", bg="#e6e6e6").place(relx=0.05, rely=0.8)

        # ==== Preview Area ====
        tk.Label(self, text="Preview", bg="#c6f0f5", font=("Arial", 12, "bold")).place(relx=0.55, rely=0.1)

        self.preview_container = tk.Frame(self)
        self.preview_container.place(relx=0.55, rely=0.15, relwidth=0.35, relheight=0.6)

        self.canvas = tk.Canvas(self.preview_container, bg="white")
        self.scroll_y = tk.Scrollbar(self.preview_container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="gray")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        # ==== Navigation Buttons ====
        tk.Button(self, text="BACK", bg="#aaaaaa", fg="white", font=("Arial", 12, "bold"),
                  command=lambda: self.controller.previous_step()).place(relx=0.68, rely=0.85, relwidth=0.1, relheight=0.07)

        tk.Button(self, text="NEXT", bg="#00bfff", fg="white", font=("Arial", 12, "bold"),
                  command=self.save_and_continue).place(relx=0.8, rely=0.85, relwidth=0.1, relheight=0.07)

        self.preview_images = []
        self.update_preview()

    def update_preview(self, *args):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.preview_images.clear()

        canvas_w = self.canvas.winfo_width()
        if canvas_w < 10:
            self.after(100, self.update_preview)
            return

        size_map = {
            "A4": (595, 842),
            "Legal": (612, 1008),
            "Letter": (612, 792)
        }
        margin_map = {
            "No margin": 0,
            "Normal margin": 40,
            "Narrow margin": 20
        }

        page_w_pt, page_h_pt = size_map[self.page_size.get()]
        margin_pt = margin_map[self.margin.get()]

        try:
            for file_obj in settings["processor"].files:
                if file_obj["type"] == "pdf":
                    stream = file_obj["stream"]
                    if not isinstance(stream, io.BytesIO):
                        continue
                    stream.seek(0)
                    doc = fitz.open(stream=stream.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap(dpi=72)
                        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                        self._draw_preview_page(img, page_w_pt, page_h_pt, margin_pt, canvas_w)
                elif file_obj["type"] == "image":
                    # Live convert to sized canvas for preview
                    image_path = file_obj["raw_image_path"]
                    img = Image.open(image_path).convert("RGB")

                    # Resize to fit layout (same as convert_image_to_sized_pdf)
                    img_ratio = img.width / img.height
                    page_ratio = page_w_pt / page_h_pt

                    if img_ratio > page_ratio:
                        new_width = page_w_pt
                        new_height = int(page_w_pt / img_ratio)
                    else:
                        new_height = page_h_pt
                        new_width = int(page_h_pt * img_ratio)

                    img = img.resize((new_width, new_height), Image.LANCZOS)

                    canvas_img = Image.new("RGB", (page_w_pt, page_h_pt), "white")
                    x = (page_w_pt - new_width) // 2
                    y = (page_h_pt - new_height) // 2
                    canvas_img.paste(img, (x, y))

                    self._draw_preview_page(canvas_img, page_w_pt, page_h_pt, margin_pt, canvas_w)

        except Exception as e:
            print("Preview error:", e)
            tk.Label(self.scroll_frame, text="No preview available", bg="white").pack(pady=50)

    def _draw_preview_page(self, img, page_w_pt, page_h_pt, margin_pt, canvas_w):
        scale = canvas_w / page_w_pt
        scaled_w = int(page_w_pt * scale)
        scaled_h = int(page_h_pt * scale)

        img = img.resize((scaled_w, scaled_h), Image.LANCZOS)
        preview_img = ImageTk.PhotoImage(img)
        self.preview_images.append(preview_img)

        page_frame = tk.Frame(self.scroll_frame, width=scaled_w, height=scaled_h, bg="white")
        page_frame.pack(pady=10)

        canvas = tk.Canvas(page_frame, width=scaled_w, height=scaled_h, bg="white", highlightthickness=1)
        canvas.pack()
        canvas.create_image(0, 0, anchor="nw", image=preview_img)

        if margin_pt > 0:
            margin_x = int(margin_pt * scale)
            margin_y = int(margin_pt * scale)
            margin_w = scaled_w - 2 * margin_x
            margin_h = scaled_h - 2 * margin_y

            canvas.create_rectangle(
                margin_x, margin_y,
                margin_x + margin_w, margin_y + margin_h,
                outline="blue", dash=(3, 3), width=2
            )

    def convert_image_to_sized_pdf(image_path):
        layout = settings.get("page_settings", {})
        page_width = layout.get("page_width", 595)
        page_height = layout.get("page_height", 842)

        # Open and resize image proportionally
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

        # Convert to PDF
        pdf_stream = BytesIO()
        canvas.save(pdf_stream, format="PDF")
        pdf_stream.seek(0)
        return pdf_stream

    def save_and_continue(self):
        size_map = {
            "A4": (595, 842),
            "Legal": (612, 1008),
            "Letter": (612, 792)
        }
        margin_map = {
            "No margin": 0,
            "Normal margin": 40,
            "Narrow margin": 20
        }

        page_w, page_h = size_map[self.page_size.get()]
        margin = margin_map[self.margin.get()]

        settings["page_size"] = self.page_size.get()

        for i, f in enumerate(settings["processor"].files):
            if f["type"] == "image":
                pdf_stream = convert_image_to_sized_pdf(f["raw_image_path"])
                f["type"] = "pdf"
                f["stream"] = pdf_stream
                f["pages"] = fitz.open(stream=pdf_stream.getvalue(), filetype="pdf").page_count

        settings["page_settings"] = {
            "page_size": self.page_size.get(),
            "page_width": page_w,
            "page_height": page_h,
            "margin_top": margin,
            "margin_bottom": margin,
            "margin_left": margin,
            "margin_right": margin
        }

        self.controller.next_step()
