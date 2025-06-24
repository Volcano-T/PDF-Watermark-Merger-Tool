import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class SignaturePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6e6e6")
        self.controller = controller

        self.signature_path = None
        self.position = tk.StringVar(value="Bottom-Right")
        self.scale = tk.DoubleVar(value=0.3)
        self.rotation = tk.IntVar(value=0)
        self.range_type = tk.StringVar(value="All")
        self.custom_range = tk.StringVar(value="")

        self.custom_x = tk.DoubleVar(value=0.8)
        self.custom_y = tk.DoubleVar(value=0.8)

        # ===== Upload Signature =====
        upload_btn = tk.Button(self, text="Upload Signature Image", command=self.upload_image)
        upload_btn.place(relx=0.1, rely=0.12, relwidth=0.25)

        # ===== Position =====
        tk.Label(self, text="Predefined Position:", bg="#e6e6e6").place(relx=0.1, rely=0.18)
        positions = ["Top-Left", "Top-Right", "Center", "Bottom-Left", "Bottom-Right", "Custom"]
        pos_menu = tk.OptionMenu(self, self.position, *positions, command=lambda e: self.toggle_custom_coords())
        pos_menu.place(relx=0.1, rely=0.22, relwidth=0.25)

        # ===== Custom Coordinates Sliders =====
        self.x_label = tk.Label(self, text="Custom X Position:", bg="#e6e6e6")
        self.x_slider = tk.Scale(self, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", variable=self.custom_x,
                                 command=lambda e: self.update_preview())
        self.y_label = tk.Label(self, text="Custom Y Position:", bg="#e6e6e6")
        self.y_slider = tk.Scale(self, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", variable=self.custom_y,
                                 command=lambda e: self.update_preview())

        self.x_label.place(relx=0.1, rely=0.27)
        self.x_slider.place(relx=0.1, rely=0.31, relwidth=0.25)
        self.y_label.place(relx=0.1, rely=0.37)
        self.y_slider.place(relx=0.1, rely=0.41, relwidth=0.25)

        # ===== Scale =====
        tk.Label(self, text="Scale (%):", bg="#e6e6e6").place(relx=0.1, rely=0.47)
        tk.Scale(self, from_=0.1, to=1.0, resolution=0.05, orient="horizontal", variable=self.scale,
                 command=lambda e: self.update_preview()).place(relx=0.1, rely=0.51, relwidth=0.25)

        # ===== Rotation =====
        tk.Label(self, text="Rotation (°):", bg="#e6e6e6").place(relx=0.1, rely=0.58)
        tk.Spinbox(self, from_=-180, to=180, textvariable=self.rotation, command=self.update_preview).place(relx=0.1, rely=0.62, relwidth=0.1)

        # ===== Page Range =====
        range_box = tk.LabelFrame(self, text="Apply to Pages", bg="#e6e6e6", font=("Arial", 11, "bold"))
        range_box.place(relx=0.1, rely=0.7, relwidth=0.25, relheight=0.15)

        tk.Radiobutton(range_box, text="All Pages", variable=self.range_type,
                       value="All", bg="#e6e6e6", command=self.toggle_range_entry).place(relx=0.05, rely=0.2)

        tk.Radiobutton(range_box, text="Specific Pages:", variable=self.range_type,
                       value="Custom", bg="#e6e6e6", command=self.toggle_range_entry).place(relx=0.05, rely=0.5)

        self.range_entry = tk.Entry(range_box, textvariable=self.custom_range)
        self.range_entry.place(relx=0.45, rely=0.5, relwidth=0.5)
        self.range_entry.configure(state="disabled")
        self.custom_range.trace_add("write", lambda *args: self.update_preview())

        # ===== Preview =====
        tk.Label(self, text="Preview", bg="#e6e6e6", font=("Arial", 12, "bold")).place(relx=0.55, rely=0.1)
        self.preview_canvas = tk.Canvas(self, bg="white", highlightbackground="black", highlightthickness=1)
        self.preview_canvas.place(relx=0.55, rely=0.15, relwidth=0.3, relheight=0.6)

        # ===== Navigation =====
        back_button = tk.Button(self, text="BACK", bg="#aaaaaa", fg="white", font=("Arial", 12, "bold"),
                                command=lambda: self.controller.previous_step())
        back_button.place(relx=0.68, rely=0.85, relwidth=0.1, relheight=0.07)

        next_button = tk.Button(self, text="NEXT", bg="#00bfff", fg="white", font=("Arial", 12, "bold"),
                                command=lambda: self.controller.next_step())
        next_button.place(relx=0.8, rely=0.85, relwidth=0.1, relheight=0.07)

        self.scale.trace_add("write", lambda *args: self.update_preview())
        self.rotation.trace_add("write", lambda *args: self.update_preview())
        self.position.trace_add("write", lambda *args: self.toggle_custom_coords())

        self.toggle_custom_coords()
        self.update_preview()

    def upload_image(self):
        file = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file:
            self.signature_path = file
            self.update_preview()

    def toggle_range_entry(self):
        if self.range_type.get() == "Custom":
            self.range_entry.configure(state="normal")
        else:
            self.range_entry.configure(state="disabled")
        self.update_preview()

    def toggle_custom_coords(self):
        state = "normal" if self.position.get() == "Custom" else "disabled"
        self.x_slider.configure(state=state)
        self.y_slider.configure(state=state)
        self.update_preview()

    def update_preview(self):
        self.preview_canvas.delete("all")

        canvas_w = self.preview_canvas.winfo_width()
        canvas_h = self.preview_canvas.winfo_height()
        if canvas_w < 10 or canvas_h < 10:
            self.after(100, self.update_preview)
            return

        self.preview_canvas.create_rectangle(10, 10, canvas_w - 10, canvas_h - 10, fill="#f0f0f0")

        if not self.signature_path:
            return

        try:
            img = Image.open(self.signature_path).convert("RGBA")
            img = img.rotate(self.rotation.get(), expand=1)

            scaled_w = int(img.width * self.scale.get())
            scaled_h = int(img.height * self.scale.get())
            img = img.resize((scaled_w, scaled_h))

            self.tk_sig = ImageTk.PhotoImage(img)

            pos_map = {
                "Top-Left": (0.2, 0.2),
                "Top-Right": (0.8, 0.2),
                "Center": (0.5, 0.5),
                "Bottom-Left": (0.2, 0.8),
                "Bottom-Right": (0.8, 0.8),
                "Custom": (self.custom_x.get(), self.custom_y.get())
            }
            x_ratio, y_ratio = pos_map.get(self.position.get(), (0.5, 0.5))
            x = int(canvas_w * x_ratio)
            y = int(canvas_h * y_ratio)

            self.preview_canvas.create_image(x, y, image=self.tk_sig)
        except Exception as e:
            print("Signature preview error:", e)
