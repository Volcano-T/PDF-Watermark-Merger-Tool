import tkinter as tk
from config import settings
import fitz
from PIL import Image, ImageTk

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6e6e6")
        self.controller = controller

        self.page_size = tk.StringVar(value="A4")
        self.margin = tk.StringVar(value="No margin")

        self.page_size.trace_add("write", self.update_preview)
        self.margin.trace_add("write", self.update_preview)

        # Page size box
        page_size_box = tk.LabelFrame(self, text="Page size:", font=("Arial", 11, "bold"), bg="#e6e6e6")
        page_size_box.place(relx=0.1, rely=0.15, relwidth=0.25, relheight=0.18)

        tk.Radiobutton(page_size_box, text="A4", variable=self.page_size, value="A4", bg="#e6e6e6").place(relx=0.05, rely=0.2)
        tk.Radiobutton(page_size_box, text="Legal", variable=self.page_size, value="Legal", bg="#e6e6e6").place(relx=0.55, rely=0.2)
        tk.Radiobutton(page_size_box, text="Letter", variable=self.page_size, value="Letter", bg="#e6e6e6").place(relx=0.55, rely=0.55)

        # Margin box
        margin_box = tk.LabelFrame(self, text="Margin:", font=("Arial", 11, "bold"), bg="#e6e6e6")
        margin_box.place(relx=0.1, rely=0.4, relwidth=0.25, relheight=0.22)

        tk.Radiobutton(margin_box, text="No margin", variable=self.margin, value="No margin", bg="#e6e6e6").place(relx=0.05, rely=0.2)
        tk.Radiobutton(margin_box, text="Normal margin", variable=self.margin, value="Normal margin", bg="#e6e6e6").place(relx=0.05, rely=0.5)
        tk.Radiobutton(margin_box, text="Narrow margin", variable=self.margin, value="Narrow margin", bg="#e6e6e6").place(relx=0.05, rely=0.8)

        # Preview
        tk.Label(self, text="Preview", bg="#e6e6e6", font=("Arial", 12, "bold")).place(relx=0.55, rely=0.12)
        self.preview_canvas = tk.Canvas(self, bg="white", highlightbackground="black", highlightthickness=1)
        self.preview_canvas.place(relx=0.55, rely=0.15, relwidth=0.3, relheight=0.60)

        # Navigation
        back_button = tk.Button(self, text="BACK", bg="#aaaaaa", fg="white", font=("Arial", 12, "bold"),
                                command=lambda: self.controller.previous_step())
        back_button.place(relx=0.68, rely=0.85, relwidth=0.1, relheight=0.07)

        next_button = tk.Button(self, text="NEXT", bg="#00bfff", fg="white", font=("Arial", 12, "bold"),
                                command=self.save_and_continue)
        next_button.place(relx=0.8, rely=0.85, relwidth=0.1, relheight=0.07)

        self.update_preview()

    def update_preview(self, *args):
        self.preview_canvas.delete("all")
        canvas_w = self.preview_canvas.winfo_width()
        canvas_h = self.preview_canvas.winfo_height()

        if canvas_w <= 1 or canvas_h <= 1:
            self.after(100, self.update_preview)
            return

        try:
            if settings["files"]:
                first_file = settings["files"][0]
                ext = first_file.lower().split(".")[-1]

                if ext in ["pdf"]:
                    doc = fitz.open(first_file)
                    page = doc.load_page(0)
                    pix = page.get_pixmap(dpi=72)

                    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    image.thumbnail((int(canvas_w * 0.9), int(canvas_h * 0.9)))
                    self.tk_preview = ImageTk.PhotoImage(image)
                    self.preview_canvas.create_image(canvas_w / 2, canvas_h / 2, image=self.tk_preview)
                    return

                elif ext in ["png", "jpg", "jpeg"]:
                    image = Image.open(first_file)
                    image.thumbnail((int(canvas_w * 0.9), int(canvas_h * 0.9)))
                    self.tk_preview = ImageTk.PhotoImage(image)
                    self.preview_canvas.create_image(canvas_w / 2, canvas_h / 2, image=self.tk_preview)
                    return

        except Exception as e:
            print("Preview error:", e)

        # fallback: draw simulated paper
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

        page_width_pt, page_height_pt = size_map.get(self.page_size.get(), (595, 842))
        margin_pt = margin_map.get(self.margin.get(), 0)

        w_ratio = 0.8
        h_ratio = 0.8

        scaled_w = canvas_w * w_ratio
        scaled_h = scaled_w * (page_height_pt / page_width_pt)

        page_x = (canvas_w - scaled_w) / 2
        page_y = (canvas_h - scaled_h) / 2

        self.preview_canvas.create_rectangle(
            page_x, page_y,
            page_x + scaled_w, page_y + scaled_h,
            outline="black", fill="#f0f0f0"
        )

        if margin_pt > 0:
            margin_scale_x = margin_pt * (scaled_w / page_width_pt)
            margin_scale_y = margin_pt * (scaled_h / page_height_pt)
            self.preview_canvas.create_rectangle(
                page_x + margin_scale_x, page_y + margin_scale_y,
                page_x + scaled_w - margin_scale_x, page_y + scaled_h - margin_scale_y,
                outline="blue", dash=(3, 3)
            )

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

        page_w, page_h = size_map.get(self.page_size.get())
        margin = margin_map.get(self.margin.get())

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
