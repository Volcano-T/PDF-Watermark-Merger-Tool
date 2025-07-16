import tkinter as tk
from config import settings
from datetime import datetime
from PIL import Image, ImageTk
import fitz


class HeaderFooterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6e6e6")
        self.controller = controller

        self.align = tk.StringVar(value="Center")
        self.font_family = tk.StringVar(value="Arial")
        self.current_page_index = 0
        self.total_pages = 1
        self.page_images = []
        self.tk_img = None

        self.header_text = tk.StringVar()
        self.footer_text = tk.StringVar()
        self.font_size = tk.IntVar(value=12)
        self.range_type = tk.StringVar(value="All")
        self.custom_range = tk.StringVar()

        self.include_time = tk.BooleanVar()
        self.include_date = tk.BooleanVar()
        self.include_page_number = tk.BooleanVar()

        # Load PDF pages
        self.load_pdf_images()

        # === UI Elements ===
        tk.Label(self, text="Header Text", bg="#e6e6e6", font=("Arial", 10, "bold")).place(relx=0.1, rely=0.1)
        tk.Entry(self, textvariable=self.header_text).place(relx=0.1, rely=0.15, relwidth=0.3)

        tk.Label(self, text="Footer Text", bg="#e6e6e6", font=("Arial", 10, "bold")).place(relx=0.1, rely=0.22)
        tk.Entry(self, textvariable=self.footer_text).place(relx=0.1, rely=0.27, relwidth=0.3)

        tk.Label(self, text="Font Size", bg="#e6e6e6").place(relx=0.1, rely=0.32)
        tk.Spinbox(self, from_=8, to=48, textvariable=self.font_size, command=self.update_preview).place(relx=0.1, rely=0.36, relwidth=0.15)

        tk.Label(self, text="Text Alignment", bg="#e6e6e6").place(relx=0.1, rely=0.42)
        tk.OptionMenu(self, self.align, "Left", "Center", "Right", command=lambda e: self.update_preview()).place(relx=0.1, rely=0.48, relwidth=0.3)

        tk.Label(self, text="Font Style", bg="#e6e6e6").place(relx=0.1, rely=0.53)
        tk.OptionMenu(self, self.font_family, "Arial", "Times", "Courier", "Helvetica", command=lambda e: self.update_preview()).place(relx=0.1, rely=0.58, relwidth=0.3)

        tk.Checkbutton(self, text="Include Time", variable=self.include_time, bg="#e6e6e6", command=self.update_preview).place(relx=0.1, rely=0.67)
        tk.Checkbutton(self, text="Include Date", variable=self.include_date, bg="#e6e6e6", command=self.update_preview).place(relx=0.1, rely=0.72)
        tk.Checkbutton(self, text="Include Page Number", variable=self.include_page_number, bg="#e6e6e6", command=self.update_preview).place(relx=0.1, rely=0.77)

        range_box = tk.LabelFrame(self, text="Apply to Pages", bg="#e6e6e6", font=("Arial", 11, "bold"))
        range_box.place(relx=0.1, rely=0.83, relwidth=0.3, relheight=0.15)

        tk.Radiobutton(range_box, text="All Pages", variable=self.range_type, value="All", bg="#e6e6e6", command=self.toggle_range_entry).place(relx=0.05, rely=0.2)
        tk.Radiobutton(range_box, text="Specific Pages:", variable=self.range_type, value="Custom", bg="#e6e6e6", command=self.toggle_range_entry).place(relx=0.05, rely=0.55)

        self.range_entry = tk.Entry(range_box, textvariable=self.custom_range)
        self.range_entry.place(relx=0.45, rely=0.55, relwidth=0.5)
        self.range_entry.configure(state="disabled")

        tk.Label(self, text="Preview", bg="#e6e6e6", font=("Arial", 12, "bold")).place(relx=0.55, rely=0.1)
        self.preview_canvas = tk.Canvas(self, bg="white", highlightbackground="black")
        self.preview_canvas.place(relx=0.55, rely=0.15, relwidth=0.35, relheight=0.6)

        tk.Button(self, text="Previous", command=self.show_previous_page).place(relx=0.55, rely=0.78, relwidth=0.1)
        tk.Button(self, text="Next", command=self.show_next_page).place(relx=0.68, rely=0.78, relwidth=0.1)

        self.page_label = tk.Label(self, text="Page 1", bg="#e6e6e6", font=("Arial", 9))
        self.page_label.place(relx=0.8, rely=0.78)

        tk.Button(self, text="BACK", bg="#aaaaaa", fg="white", font=("Arial", 12, "bold"),
                  command=lambda: self.controller.previous_step())\
            .place(relx=0.68, rely=0.88, relwidth=0.1, relheight=0.07)

        tk.Button(self, text="NEXT", bg="#00bfff", fg="white", font=("Arial", 12, "bold"),
                  command=self.save_settings_and_continue)\
            .place(relx=0.8, rely=0.88, relwidth=0.1, relheight=0.07)

        # Trigger initial preview
        self.after(300, self.update_preview)

        self.header_text.trace_add("write", lambda *args: self.update_preview())
        self.footer_text.trace_add("write", lambda *args: self.update_preview())
        self.font_size.trace_add("write", lambda *args: self.update_preview())
        self.font_family.trace_add("write", lambda *args: self.update_preview())
        self.align.trace_add("write", lambda *args: self.update_preview())

    def load_pdf_images(self):
        self.page_images.clear()
        if "processor" in settings:
            streams = settings["processor"].get_all_streams()
            for stream in streams:
                stream.seek(0)
                doc = fitz.open(stream=stream.read(), filetype="pdf")
                self.total_pages = len(doc)
                for page in doc:
                    pix = page.get_pixmap(dpi=72)
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                    self.page_images.append(img)
            self.current_page_index = 0

    def toggle_range_entry(self):
        if self.range_type.get() == "Custom":
            self.range_entry.configure(state="normal")
        else:
            self.range_entry.configure(state="disabled")
        self.update_preview()

    def show_previous_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.update_preview()

    def show_next_page(self):
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.update_preview()

    def _x_pos(self, width):
        align = self.align.get()
        if align == "Left":
            return 20
        elif align == "Right":
            return width - 20
        return width / 2

    def update_preview(self):
        self.preview_canvas.delete("all")
        w = self.preview_canvas.winfo_width()
        h = self.preview_canvas.winfo_height()

        if w < 10 or h < 10:
            self.after(100, self.update_preview)
            return

        # Update page label
        self.page_label.config(text=f"Page {self.current_page_index + 1} of {self.total_pages}")

        # Draw PDF background
        if self.page_images:
            bg_img = self.page_images[self.current_page_index].copy()
            bg_img = bg_img.resize((w, h))
            self.tk_img = ImageTk.PhotoImage(bg_img)
            self.preview_canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        align = self.align.get()
        anchor_map = {"Left": "w", "Center": "center", "Right": "e"}
        anchor = anchor_map.get(align, "center")
        x = self._x_pos(w)

        font_name = self.font_family.get()
        font_size = self.font_size.get()
        current_page = self.current_page_index + 1

        # Header text
        self.preview_canvas.create_text(x, 30, text=self.header_text.get(),
                                        font=(font_name, font_size), anchor=anchor, fill="black")

        # Time/Date
        info_parts = []
        if self.include_time.get():
            info_parts.append(datetime.now().strftime('%H:%M:%S'))
        if self.include_date.get():
            info_parts.append(datetime.now().strftime('%Y-%m-%d'))
        if info_parts:
            self.preview_canvas.create_text(x, 55, text="   ".join(info_parts),
                                            font=(font_name, font_size - 2), anchor=anchor, fill="black")

        # Footer
        self.preview_canvas.create_text(x, h - 50, text=self.footer_text.get(),
                                        font=(font_name, font_size), anchor=anchor, fill="black")

        if self.include_page_number.get():
            self.preview_canvas.create_text(x, h - 30,
                                            text=f"Page {current_page} of {self.total_pages}",
                                            font=(font_name, font_size - 2), anchor=anchor, fill="black")

    def save_settings_and_continue(self):
        settings["header_footer"] = {
            "font": self.font_family.get(),
            "alignment": self.align.get(),
            "header_text": self.header_text.get(),
            "footer_text": self.footer_text.get(),
            "font_size": self.font_size.get(),
            "page_range": self.custom_range.get() if self.range_type.get() == "Custom" else "All",
            "include_time": self.include_time.get(),
            "include_date": self.include_date.get(),
            "include_page_number": self.include_page_number.get()
        }
        self.controller.next_step()
