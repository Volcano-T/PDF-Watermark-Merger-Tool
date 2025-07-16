import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from config import settings
import fitz


class SignaturePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6e6e6")
        self.controller = controller
        self.current_page_index = 0
        self.total_pages = 0
        self.page_images = []

        self.signature_path = None
        self.position = tk.StringVar(value="Bottom-Right")
        self.scale = tk.DoubleVar(value=0.3)
        self.rotation = tk.IntVar(value=0)
        self.range_type = tk.StringVar(value="All")
        self.custom_range = tk.StringVar(value="")

        self.custom_x = tk.DoubleVar(value=0.8)
        self.custom_y = tk.DoubleVar(value=0.8)

        # ===== Upload Signature =====
        tk.Button(self, text="Upload Signature Image", command=self.upload_image).place(relx=0.1, rely=0.12, relwidth=0.25)

        # ===== Position =====
        tk.Label(self, text="Predefined Position:", bg="#e6e6e6").place(relx=0.1, rely=0.18)
        positions = ["Top-Left", "Top-Right", "Center", "Bottom-Left", "Bottom-Right", "Custom"]
        tk.OptionMenu(self, self.position, *positions, command=lambda e: self.toggle_custom_coords()).place(relx=0.1, rely=0.22, relwidth=0.25)

        # ===== Custom Coordinates Sliders =====
        self.x_label = tk.Label(self, text="Custom X Position:", bg="#e6e6e6")
        self.x_slider = tk.Scale(self, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", variable=self.custom_x, command=lambda e: self.update_preview())
        self.y_label = tk.Label(self, text="Custom Y Position:", bg="#e6e6e6")
        self.y_slider = tk.Scale(self, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", variable=self.custom_y, command=lambda e: self.update_preview())

        self.x_label.place(relx=0.1, rely=0.27)
        self.x_slider.place(relx=0.1, rely=0.31, relwidth=0.25)
        self.y_label.place(relx=0.1, rely=0.37)
        self.y_slider.place(relx=0.1, rely=0.41, relwidth=0.25)

        # ===== Scale and Rotation =====
        tk.Label(self, text="Scale (%):", bg="#e6e6e6").place(relx=0.1, rely=0.47)
        tk.Scale(self, from_=0.1, to=1.0, resolution=0.05, orient="horizontal", variable=self.scale, command=lambda e: self.update_preview()).place(relx=0.1, rely=0.51, relwidth=0.25)

        tk.Label(self, text="Rotation (°):", bg="#e6e6e6").place(relx=0.1, rely=0.58)
        tk.Spinbox(self, from_=-180, to=180, textvariable=self.rotation, command=self.update_preview).place(relx=0.1, rely=0.62, relwidth=0.1)

        # ===== Page Range =====
        range_box = tk.LabelFrame(self, text="Apply to Pages", bg="#e6e6e6", font=("Arial", 11, "bold"))
        range_box.place(relx=0.1, rely=0.7, relwidth=0.25, relheight=0.18)

        tk.Radiobutton(range_box, text="All Pages", variable=self.range_type, value="All", bg="#e6e6e6", command=self.toggle_range_entry).place(relx=0.05, rely=0.2)
        tk.Radiobutton(range_box, text="Specific Pages:", variable=self.range_type, value="Custom", bg="#e6e6e6", command=self.toggle_range_entry).place(relx=0.05, rely=0.5)

        self.range_entry = tk.Entry(range_box, textvariable=self.custom_range)
        self.range_entry.place(relx=0.45, rely=0.5, relwidth=0.5)
        self.range_entry.configure(state="disabled")

        self.page_count_label = tk.Label(range_box, text="", bg="#e6e6e6", fg="blue", font=("Arial", 9))
        self.page_count_label.place(relx=0.05, rely=0.75)

        # ===== Preview =====
        tk.Label(self, text="Preview", bg="#e6e6e6", font=("Arial", 12, "bold")).place(relx=0.55, rely=0.1)
        self.preview_canvas = tk.Canvas(self, bg="white", highlightbackground="black", highlightthickness=1)
        self.preview_canvas.place(relx=0.55, rely=0.15, relwidth=0.3, relheight=0.6)

        tk.Button(self, text="Previous", command=self.show_previous_page).place(relx=0.55, rely=0.78, relwidth=0.1)
        tk.Button(self, text="Next", command=self.show_next_page).place(relx=0.68, rely=0.78, relwidth=0.1)

        # ===== Navigation =====
        tk.Button(self, text="BACK", bg="#aaaaaa", fg="white", font=("Arial", 12, "bold"),
                  command=lambda: self.controller.previous_step()).place(relx=0.68, rely=0.85, relwidth=0.1, relheight=0.07)

        tk.Button(self, text="NEXT", bg="#00bfff", fg="white", font=("Arial", 12, "bold"),
                  command=self.save_and_continue).place(relx=0.8, rely=0.85, relwidth=0.1, relheight=0.07)

        self.current_page_label = tk.Label(self, text="", bg="#e6e6e6", font=("Arial", 10, "bold"))
        self.current_page_label.place(relx=0.8, rely=0.78)

        # Traces and Init
        self.scale.trace_add("write", lambda *args: self.update_preview())
        self.rotation.trace_add("write", lambda *args: self.update_preview())
        self.position.trace_add("write", lambda *args: self.toggle_custom_coords())
        self.custom_range.trace_add("write", lambda *args: self.update_preview())

        self.toggle_custom_coords()
        self.update_preview()
        self.after(300, self.update_preview)

    def show_next_page(self):
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.current_page_label.configure(text="Page: " + str(self.current_page_index + 1) + "/" + str(self.total_pages))
            self.update_preview()

    def show_previous_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.current_page_label.configure(text="Page: " + str(self.current_page_index + 1) + "/" + str(self.total_pages))
            self.update_preview()

    def load_pdf_images(self):
        self.page_images.clear()
        self.total_pages = 0
        if "processor" in settings:
            streams = settings["processor"].get_all_streams()
            for stream in streams:
                stream.seek(0)
                doc = fitz.open(stream=stream.read(), filetype="pdf")
                self.total_pages += len(doc)
                for page in doc:
                    pix = page.get_pixmap(dpi=72)
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                    self.page_images.append(img)
        self.current_page_index = 0

    def upload_image(self):
        file = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file:
            self.signature_path = file
            self.load_pdf_images()
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
            self.after(300, self.update_preview)
            return

        # Draw PDF page background even if no signature
        if not self.page_images:
            self.load_pdf_images()
            if not self.page_images:
                return

        bg_img = self.page_images[self.current_page_index].copy()
        bg_img = bg_img.resize((canvas_w, canvas_h))
        self.tk_preview_img = ImageTk.PhotoImage(bg_img)
        self.preview_canvas.create_image(0, 0, anchor="nw", image=self.tk_preview_img)
        # Always show page count
        try:
            total_pages = settings["processor"].get_total_pages()
            self.page_count_label.config(text=f"Total pages: {total_pages}")
            self.current_page_label.configure(text="Page: " + str(self.current_page_index + 1) + "/" + str(total_pages))
        except:
            self.page_count_label.config(text="Total pages: ?")

        # Only draw signature if uploaded
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

            # Save settings per page
            if "signature_pages" not in settings:
                settings["signature_pages"] = {}

            settings["signature_pages"][self.current_page_index] = {
                "x_ratio": x_ratio,
                "y_ratio": y_ratio,
                "scale": self.scale.get(),
                "rotation": self.rotation.get(),
                "position_type": self.position.get(),
                "range": self.range_type.get(),
                "custom_range": self.custom_range.get()
            }

            self.preview_canvas.create_image(x, y, image=self.tk_sig)

        except Exception as e:
            print("Signature preview error:", e)

    def save_and_continue(self):
        # Validate page range
        total_pages = settings["processor"].get_total_pages()
        if self.range_type.get() == "Custom":
            try:
                pages = [int(p) for p in self.custom_range.get().split(",") if p.strip().isdigit()]
                if not all(1 <= p <= total_pages for p in pages):
                    raise ValueError
            except:
                tk.messagebox.showerror("Invalid Range", f"Pages must be numbers between 1 and {total_pages}")
                return

        # Save to settings
        settings["signature_settings"] = {
            "path": self.signature_path,
            "position": self.position.get(),
            "scale": self.scale.get(),
            "rotation": self.rotation.get(),
            "apply_to": self.range_type.get(),
            "custom_range": self.custom_range.get(),
            "custom_x": self.custom_x.get(),
            "custom_y": self.custom_y.get()
        }

        self.controller.next_step()
        
