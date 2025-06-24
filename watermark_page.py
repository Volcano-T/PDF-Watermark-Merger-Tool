import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class WatermarkPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6e6e6")
        self.controller = controller

        self.watermark_type = tk.StringVar(value="Text")
        self.watermark_text = tk.StringVar(value="Sample Watermark")
        self.font_size = tk.IntVar(value=16)
        self.opacity = tk.DoubleVar(value=0.3)
        self.position = tk.StringVar(value="Center")
        self.rotation = tk.IntVar(value=0)
        self.image_path = None

        # ========== Watermark Type ==========
        type_frame = tk.LabelFrame(self, text="Watermark Type", bg="#e6e6e6", font=("Arial", 11, "bold"))
        type_frame.place(relx=0.1, rely=0.12, relwidth=0.25, relheight=0.12)

        tk.Radiobutton(type_frame, text="Text", variable=self.watermark_type, value="Text",
                       command=self.toggle_input, bg="#e6e6e6").place(relx=0.1, rely=0.2)
        tk.Radiobutton(type_frame, text="Image", variable=self.watermark_type, value="Image",
                       command=self.toggle_input, bg="#e6e6e6").place(relx=0.55, rely=0.2)

        # ========== Text Input ==========
        self.text_label = tk.Label(self, text="Watermark Text:", bg="#e6e6e6")
        self.text_label.place(relx=0.1, rely=0.26)
        self.text_entry = tk.Entry(self, textvariable=self.watermark_text)
        self.text_entry.place(relx=0.1, rely=0.3, relwidth=0.25)

        # ========== Upload Image ==========
        self.upload_btn = tk.Button(self, text="Upload Image", command=self.upload_image)
        self.upload_btn.place_forget()  # Hidden by default

        # ========== Font Size ==========
        tk.Label(self, text="Font Size:", bg="#e6e6e6").place(relx=0.1, rely=0.36)
        tk.Spinbox(self, from_=8, to=72, textvariable=self.font_size, command=self.update_preview).place(relx=0.1, rely=0.4, relwidth=0.1)

        # ========== Opacity ==========
        tk.Label(self, text="Opacity:", bg="#e6e6e6").place(relx=0.1, rely=0.46)
        tk.Scale(self, from_=0.0, to=1.0, resolution=0.05, orient="horizontal", variable=self.opacity).place(relx=0.1, rely=0.5, relwidth=0.25)

        # ========== Position ==========
        tk.Label(self, text="Position:", bg="#e6e6e6").place(relx=0.1, rely=0.58)
        positions = ["Top-Left", "Top-Right", "Center", "Bottom-Left", "Bottom-Right"]
        tk.OptionMenu(self, self.position, *positions, command= lambda e: self.update_preview()).place(relx=0.1, rely=0.62, relwidth=0.25)

        # ========== Rotation ==========
        tk.Label(self, text="Rotation (°):", bg="#e6e6e6").place(relx=0.1, rely=0.68)
        tk.Spinbox(self, from_=-180, to=180, textvariable=self.rotation).place(relx=0.1, rely=0.72, relwidth=0.1)

        # ========== Page Range ==========
        self.page_range_type = tk.StringVar(value="All")
        self.custom_range = tk.StringVar(value="")

        range_box = tk.LabelFrame(self, text="Apply to Pages", bg="#e6e6e6", font=("Arial", 11, "bold"))
        range_box.place(relx=0.1, rely=0.78, relwidth=0.25, relheight=0.15)

        tk.Radiobutton(range_box, text="All Pages", variable=self.page_range_type,
                       value="All", bg="#e6e6e6", command=self.toggle_range_input).place(relx=0.05, rely=0.2)

        tk.Radiobutton(range_box, text="Specific Pages:", variable=self.page_range_type,
                       value="Custom", bg="#e6e6e6", command=self.toggle_range_input).place(relx=0.05, rely=0.5)

        self.range_entry = tk.Entry(range_box, textvariable=self.custom_range)
        self.range_entry.place(relx=0.45, rely=0.5, relwidth=0.5)
        self.range_entry.configure(state="disabled")  # initially disabled

        # ========== Preview ==========
        tk.Label(self, text="Preview", bg="#e6e6e6", font=("Arial", 12, "bold")).place(relx=0.55, rely=0.1)
        self.preview_canvas = tk.Canvas(self, bg="white", highlightbackground="black", highlightthickness=1)
        self.preview_canvas.place(relx=0.55, rely=0.15, relwidth=0.3, relheight=0.6)

        # ========== NEXT ==========
        back_button = tk.Button(self, text="BACK", bg="#aaaaaa", fg="white", font=("Arial", 12, "bold"),
                                command=lambda: self.controller.previous_step())
        back_button.place(relx=0.68, rely=0.85, relwidth=0.1, relheight=0.07)

        next_button = tk.Button(self, text="NEXT", bg="#00bfff", fg="white", font=("Arial", 12, "bold"),
                                command=lambda: self.controller.next_step())
        next_button.place(relx=0.8, rely=0.85, relwidth=0.1, relheight=0.07)

        # Live update
        self.bind_all("<KeyRelease>", lambda e: self.update_preview())
        self.bind_all("<ButtonRelease>", lambda e: self.update_preview())
        self.update_preview()

    def toggle_range_input(self):
        if self.page_range_type.get() == "Custom":
            self.range_entry.configure(state="normal")
        else:
            self.range_entry.configure(state="disabled")

    def toggle_input(self):
        if self.watermark_type.get() == "Text":
            self.text_label.place(relx=0.1, rely=0.26)
            self.text_entry.place(relx=0.1, rely=0.3, relwidth=0.25)
            self.upload_btn.place_forget()
        else:
            self.text_label.place_forget()
            self.text_entry.place_forget()
            self.upload_btn.place(relx=0.1, rely=0.3, relwidth=0.25)

        self.update_preview()

    def upload_image(self):
        file = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file:
            self.image_path = file
            self.update_preview()

    def update_preview(self):
        self.preview_canvas.delete("all")

        # Get canvas size
        canvas_w = self.preview_canvas.winfo_width()
        canvas_h = self.preview_canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            self.after(100, self.update_preview)
            return

        # Draw simulated PDF page
        self.preview_canvas.create_rectangle(10, 10, canvas_w - 10, canvas_h - 10, fill="#f0f0f0")

        # Draw watermark
        pos_map = {
            "Top-Left": (0.2, 0.2),
            "Top-Right": (0.8, 0.2),
            "Center": (0.5, 0.5),
            "Bottom-Left": (0.2, 0.8),
            "Bottom-Right": (0.8, 0.8),
        }
        x_ratio, y_ratio = pos_map.get(self.position.get(), (0.5, 0.5))
        x = int(canvas_w * x_ratio)
        y = int(canvas_h * y_ratio)

        if self.watermark_type.get() == "Text":
            self.preview_canvas.create_text(
                x, y,
                text=self.watermark_text.get(),
                font=("Arial", self.font_size.get()),
                angle=self.rotation.get(),
                fill=self._hex_opacity("#000000", self.opacity.get())
            )
        elif self.watermark_type.get() == "Image" and self.image_path:
            try:
                img = Image.open(self.image_path).convert("RGBA")
                img = img.resize((100, 100))
                img.putalpha(int(self.opacity.get() * 255))
                self.tk_img = ImageTk.PhotoImage(img)
                self.preview_canvas.create_image(x, y, image=self.tk_img)
            except:
                pass

    def _hex_opacity(self, hex_color, opacity):
        """Convert HEX to RGBA string for Tkinter text with opacity."""
        rgb = self.winfo_rgb(hex_color)
        r, g, b = [val // 256 for val in rgb]
        return f"#{r:02x}{g:02x}{b:02x}"
