import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from config import settings
import tkinter.messagebox as messagebox
from io import BytesIO
from fitz import open as fitz_open

class WatermarkPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6e6e6")
        self.controller = controller
        self.image_scale = tk.IntVar(value=50)
        self.watermark_type = tk.StringVar(value="None")
        self.watermark_text = tk.StringVar(value="")
        self.font_size = tk.IntVar(value=16)
        self.opacity = tk.DoubleVar(value=0.3)
        self.position = tk.StringVar(value="Center")
        self.rotation = tk.IntVar(value=0)
        self.image_path = None

        # ========== Watermark Type ==========
        type_frame = tk.LabelFrame(self, text="Watermark Type", bg="#e6e6e6", font=("Arial", 11, "bold"))
        type_frame.place(relx=0.1, rely=0.12, relwidth=0.25, relheight=0.12)

        tk.Radiobutton(type_frame, text="None", variable=self.watermark_type, value="None",
                       command=self.toggle_input, bg="#e6e6e6").place(relx=0.1, rely=0.2)
        tk.Radiobutton(type_frame, text="Text", variable=self.watermark_type, value="Text",
                       command=self.toggle_input, bg="#e6e6e6").place(relx=0.35, rely=0.2)
        tk.Radiobutton(type_frame, text="Image", variable=self.watermark_type, value="Image",
                       command=self.toggle_input, bg="#e6e6e6").place(relx=0.55, rely=0.2)

        # ========== Text Input ==========
        self.text_label = tk.Label(self, text="Watermark Text:", bg="#e6e6e6")
        self.text_label.place(relx=0.1, rely=0.26)
        self.text_entry = tk.Entry(self, textvariable=self.watermark_text)
        self.text_entry.place(relx=0.1, rely=0.3, relwidth=0.25)


        # ========== Upload Image ==========
        self.upload_btn = tk.Button(self, text="Upload Image", command=self.upload_image)
        self.upload_btn.place_forget()

        # ========== Image Size ==========
        self.scale_label = tk.Label(self, text="Image Size (%):", bg="#e6e6e6")
        self.scale_slider = tk.Scale(self, from_=1, to=100, orient="horizontal", variable=self.image_scale)
        self.scale_label.place_forget()
        self.scale_slider.place_forget()

        # ========== Font Size ==========
        self.font_label = tk.Label(self, text="Font Size:", bg="#e6e6e6")
        self.font_spinbox = tk.Spinbox(self, from_=8, to=72, textvariable=self.font_size, command=self.update_preview)
        self.font_label.place(relx=0.1, rely=0.36)
        self.font_spinbox.place(relx=0.1, rely=0.4, relwidth=0.1)

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
        self.range_entry.configure(state="disabled")
        self.total_pages_label = tk.Label(range_box, text="", bg="#e6e6e6", fg="gray", font=("Arial", 9))
        self.total_pages_label.place(relx=0.05, rely=0.75)


        # ========== Preview ==========
        tk.Label(self, text="Preview", bg="#e6e6e6", font=("Arial", 12, "bold")).place(relx=0.55, rely=0.1)
        self.preview_canvas = tk.Canvas(self, bg="white", highlightbackground="black", highlightthickness=1)
        self.preview_canvas.place(relx=0.55, rely=0.15, relwidth=0.3, relheight=0.6)

        # ========== NEXT ==========
        back_button = tk.Button(self, text="BACK", bg="#aaaaaa", fg="white", font=("Arial", 12, "bold"),
                                command=lambda: self.controller.previous_step())
        back_button.place(relx=0.68, rely=0.85, relwidth=0.1, relheight=0.07)

        next_button = tk.Button(self, text="NEXT", bg="#00bfff", fg="white", font=("Arial", 12, "bold"),
                                command=self.save_and_continue)
        next_button.place(relx=0.8, rely=0.85, relwidth=0.1, relheight=0.07)

        self.text_label.place_forget()
        self.text_entry.place_forget()
        self.upload_btn.place_forget()
        self.scale_label.place_forget()
        self.scale_slider.place_forget()
        self.font_label.place_forget()
        self.font_spinbox.place_forget()

        # Live update
        self.bind_all("<KeyRelease>", lambda e: self.update_preview())
        self.bind_all("<ButtonRelease>", lambda e: self.update_preview())
        self.update_preview()

    def update_total_pages_label(self):
        try:
            total = settings["processor"].get_total_pages()
            self.total_pages_label.config(text=f"Total Pages: {total}")
        except:
            self.total_pages_label.config(text="Total Pages: Unknown")

    def toggle_range_input(self):
        if self.page_range_type.get() == "Custom":
            self.range_entry.configure(state="normal")
        else:
            self.range_entry.configure(state="disabled")

    def toggle_input(self):
        selected = self.watermark_type.get()
        if selected == "None":
            self.text_label.place_forget()
            self.text_entry.place_forget()
            self.upload_btn.place_forget()
            self.scale_label.place_forget()
            self.scale_slider.place_forget()
            self.font_label.place_forget()
            self.font_spinbox.place_forget()
        elif selected == "Text":
            self.text_label.place(relx=0.1, rely=0.26)
            self.text_entry.place(relx=0.1, rely=0.3, relwidth=0.25)
            self.font_label.place(relx=0.1, rely=0.36)
            self.font_spinbox.place(relx=0.1, rely=0.4, relwidth=0.1)
            self.upload_btn.place_forget()
            self.scale_label.place_forget()
            self.scale_slider.place_forget()

        elif selected == "Image":
            self.upload_btn.place(relx=0.1, rely=0.3, relwidth=0.25)
            self.scale_label.place(relx=0.1, rely=0.36)
            self.scale_slider.place(relx=0.1, rely=0.4, relwidth=0.25)
            self.text_label.place_forget()
            self.text_entry.place_forget()
            self.font_label.place_forget()
            self.font_spinbox.place_forget()

        self.update_preview()

    def upload_image(self):
        file = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file:
            self.image_path = file
            self.update_preview()

    def update_preview(self):

        self.update_total_pages_label()
        self.preview_canvas.delete("all")

        canvas_w = self.preview_canvas.winfo_width()
        canvas_h = self.preview_canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            self.after(100, self.update_preview)
            return

        try:
            streams = settings["processor"].get_all_streams()
            if not streams:
                raise Exception("No PDF streams available.")

            stream = streams[0]  # Preview first file
            if not isinstance(stream, BytesIO):
                raise Exception("Invalid stream type")

            stream.seek(0)
            doc = fitz_open(stream=stream.read(), filetype="pdf")
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=72)

            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

            # Resize to canvas
            img.thumbnail((canvas_w - 20, canvas_h - 20))
            self.page_img = ImageTk.PhotoImage(img)
            img_x = (canvas_w - self.page_img.width()) // 2
            img_y = (canvas_h - self.page_img.height()) // 2

            # Draw page background
            self.preview_canvas.create_image(img_x, img_y, anchor="nw", image=self.page_img)

            # Calculate watermark position
            pos_map = {
                "Top-Left": (0.2, 0.2),
                "Top-Right": (0.8, 0.2),
                "Center": (0.5, 0.5),
                "Bottom-Left": (0.2, 0.8),
                "Bottom-Right": (0.8, 0.8),
            }
            x_ratio, y_ratio = pos_map.get(self.position.get(), (0.5, 0.5))
            wm_x = int(canvas_w * x_ratio)
            wm_y = int(canvas_h * y_ratio)

            if self.watermark_type.get() == "Text":
                self.preview_canvas.create_text(
                    wm_x, wm_y,
                    text=self.watermark_text.get(),
                    font=("Arial", self.font_size.get()),
                    angle=self.rotation.get(),
                    fill=self._hex_opacity("#000000", self.opacity.get())
                )

            elif self.watermark_type.get() == "Image" and self.image_path:
                try:
                    wm_img = Image.open(self.image_path).convert("RGBA")
                    scale_percent = self.image_scale.get()
                    new_w = int(wm_img.width * scale_percent / 100)
                    new_h = int(wm_img.height * scale_percent / 100)

                    wm_img = wm_img.resize((new_w, new_h), Image.LANCZOS)
                    wm_img = wm_img.rotate(self.rotation.get(), expand=True)
                    wm_img.putalpha(int(self.opacity.get() * 255))

                    self.tk_wm_img = ImageTk.PhotoImage(wm_img)
                    self.preview_canvas.create_image(wm_x, wm_y, image=self.tk_wm_img)

                except Exception as e:
                    print("Image watermark error:", e)

        except Exception as e:
            print("Preview error:", e)
            self.preview_canvas.create_rectangle(10, 10, canvas_w - 10, canvas_h - 10, fill="#f0f0f0")
            self.preview_canvas.create_text(canvas_w // 2, canvas_h // 2, text="No preview available",
                                            font=("Arial", 14))

    def _hex_opacity(self, hex_color, opacity):
        """Convert HEX to RGBA string for Tkinter text with opacity."""
        rgb = self.winfo_rgb(hex_color)
        r, g, b = [val // 256 for val in rgb]
        return f"#{r:02x}{g:02x}{b:02x}"

    def save_and_continue(self):
        if self.page_range_type.get() == "Custom":
            try:
                total = settings["processor"].get_total_pages()
                custom_pages = self.custom_range.get().replace(" ", "")
                valid = True

                for part in custom_pages.split(","):
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        if start < 1 or end > total or start > end:
                            valid = False
                            break
                    else:
                        page = int(part)
                        if page < 1 or page > total:
                            valid = False
                            break

                if not valid:
                    tk.messagebox.showerror("Invalid Range", f"Page range must be within 1 to {total}.")
                    return
            except Exception as e:
                tk.messagebox.showerror("Error", "Invalid page range format.")
                return

        # SAVE WATERMARK SETTINGS
        settings["watermark"] = {
            "type": self.watermark_type.get(),
            "text": self.watermark_text.get(),
            "image_path": self.image_path,
            "font_size": self.font_size.get(),
            "opacity": self.opacity.get(),
            "rotation": self.rotation.get(),
            "position": self.position.get(),
            "page_range_type": self.page_range_type.get(),
            "page_range_custom": self.custom_range.get()
        }

        self.controller.next_step()
