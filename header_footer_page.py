import tkinter as tk
from config import settings
from datetime import datetime

class HeaderFooterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6e6e6")
        self.controller = controller

        self.header_text = tk.StringVar()
        self.footer_text = tk.StringVar()
        self.font_size = tk.IntVar(value=12)
        self.range_type = tk.StringVar(value="All")
        self.custom_range = tk.StringVar()

        self.include_time = tk.BooleanVar()
        self.include_date = tk.BooleanVar()
        self.include_page_number = tk.BooleanVar()

        # ===== Header =====
        tk.Label(self, text="Header Text", bg="#e6e6e6", font=("Arial", 10, "bold")).place(relx=0.1, rely=0.1)
        tk.Entry(self, textvariable=self.header_text).place(relx=0.1, rely=0.15, relwidth=0.3)

        # ===== Footer =====
        tk.Label(self, text="Footer Text", bg="#e6e6e6", font=("Arial", 10, "bold")).place(relx=0.1, rely=0.25)
        tk.Entry(self, textvariable=self.footer_text).place(relx=0.1, rely=0.3, relwidth=0.3)

        # ===== Font Size =====
        tk.Label(self, text="Font Size", bg="#e6e6e6").place(relx=0.1, rely=0.4)
        tk.Spinbox(self, from_=8, to=48, textvariable=self.font_size).place(relx=0.1, rely=0.45, relwidth=0.15)

        # ===== Date/Time/Page Number Checkboxes =====
        tk.Checkbutton(self, text="Include Time", variable=self.include_time, bg="#e6e6e6",
                       command=self.update_preview).place(relx=0.1, rely=0.63)
        tk.Checkbutton(self, text="Include Date", variable=self.include_date, bg="#e6e6e6",
                       command=self.update_preview).place(relx=0.1, rely=0.68)
        tk.Checkbutton(self, text="Include Page Number", variable=self.include_page_number, bg="#e6e6e6",
                       command=self.update_preview).place(relx=0.1, rely=0.73)

        # ===== Page Range =====
        range_box = tk.LabelFrame(self, text="Apply to Pages", bg="#e6e6e6", font=("Arial", 11, "bold"))
        range_box.place(relx=0.1, rely=0.85, relwidth=0.3, relheight=0.15)

        tk.Radiobutton(range_box, text="All Pages", variable=self.range_type,
                       value="All", bg="#e6e6e6", command=self.toggle_range_entry).place(relx=0.05, rely=0.2)
        tk.Radiobutton(range_box, text="Specific Pages:", variable=self.range_type,
                       value="Custom", bg="#e6e6e6", command=self.toggle_range_entry).place(relx=0.05, rely=0.5)

        self.range_entry = tk.Entry(range_box, textvariable=self.custom_range)
        self.range_entry.place(relx=0.45, rely=0.5, relwidth=0.5)
        self.range_entry.configure(state="disabled")

        # ===== Preview Canvas =====
        tk.Label(self, text="Preview", bg="#e6e6e6", font=("Arial", 12, "bold")).place(relx=0.55, rely=0.1)
        self.preview_canvas = tk.Canvas(self, bg="white", highlightbackground="black")
        self.preview_canvas.place(relx=0.55, rely=0.15, relwidth=0.35, relheight=0.6)

        # ===== Navigation =====
        back_button = tk.Button(self, text="BACK", bg="#aaaaaa", fg="white", font=("Arial", 12, "bold"),
                                command=lambda: controller.previous_step())
        back_button.place(relx=0.68, rely=0.85, relwidth=0.1, relheight=0.07)

        next_button = tk.Button(self, text="NEXT", bg="#00bfff", fg="white", font=("Arial", 12, "bold"),
                                command=self.save_settings_and_continue)
        next_button.place(relx=0.8, rely=0.85, relwidth=0.1, relheight=0.07)

        self.bind_all("<KeyRelease>", lambda e: self.update_preview())
        self.update_preview()

    def toggle_range_entry(self):
        if self.range_type.get() == "Custom":
            self.range_entry.configure(state="normal")
        else:
            self.range_entry.configure(state="disabled")

    def update_preview(self):
        self.preview_canvas.delete("all")
        w = self.preview_canvas.winfo_width()
        h = self.preview_canvas.winfo_height()
        if w < 10 or h < 10:
            self.after(100, self.update_preview)
            return

        self.preview_canvas.create_rectangle(10, 10, w - 10, h - 10, fill="#f0f0f0")
        font = ("Arial", self.font_size.get())

        # ===== Header Section =====
        y_header_base = 30
        self.preview_canvas.create_text(w / 2, y_header_base, text=self.header_text.get().strip(), font=font)

        y_header_info = y_header_base + 20
        info_parts = []
        if self.include_time.get():
            info_parts.append(datetime.now().strftime('%H:%M:%S'))
        if self.include_date.get():
            info_parts.append(datetime.now().strftime('%Y-%m-%d'))

        if info_parts:
            self.preview_canvas.create_text(w / 2, y_header_info, text="   ".join(info_parts),
                                            font=("Arial", self.font_size.get() - 2))

        # ===== Footer Section =====
        y_footer_base = h - 50
        self.preview_canvas.create_text(w / 2, y_footer_base, text=self.footer_text.get().strip(), font=font)

        y_footer_info = y_footer_base + 20
        if self.include_page_number.get():
            self.preview_canvas.create_text(w / 2, y_footer_info, text="Page 1 of 5",
                                            font=("Arial", self.font_size.get() - 2))

    def save_settings_and_continue(self):
        settings["header_footer"] = {
            "header_text": self.header_text.get(),
            "footer_text": self.footer_text.get(),
            "font_size": self.font_size.get(),
            "page_range": self.custom_range.get() if self.range_type.get() == "Custom" else "All",
            "include_time": self.include_time.get(),
            "include_date": self.include_date.get(),
            "include_page_number": self.include_page_number.get()
        }
        self.controller.next_step()
