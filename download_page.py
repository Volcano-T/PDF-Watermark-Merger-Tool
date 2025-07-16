import tkinter as tk
from tkinter import filedialog, messagebox
from config import settings
import fitz
from PIL import Image
from datetime import datetime
import os
from pdf_processor import PDFProcessor


class DownloadPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6e6e6")
        self.controller = controller

        tk.Label(self, text="Download Final PDF", font=("Arial", 14, "bold"), bg="#e6e6e6").place(relx=0.1, rely=0.1)

        tk.Button(self, text="Download PDF", font=("Arial", 12), bg="#00bfff", fg="white",
                  command=self.save_final_pdf).place(relx=0.1, rely=0.2, relwidth=0.3)

        tk.Button(self, text="BACK", font=("Arial", 12, "bold"), bg="#aaaaaa", fg="white",
                  command=lambda: controller.previous_step()).place(relx=0.8, rely=0.85, relwidth=0.1)

        reset_button = tk.Button(self, text="RESET", bg="red", fg="white", font=("Arial", 12, "bold"),
                                 command=self.reset_app)
        reset_button.place(relx=0.1, rely=0.85, relwidth=0.1, relheight=0.07)

    def map_font(self, name):
        return {
            "Arial": "helv",
            "Helvetica": "helv",
            "Times": "times",
            "Courier": "cour"
        }.get(name, "helv")

    def save_final_pdf(self):
        try:
            output_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                       filetypes=[("PDF Files", "*.pdf")])
            if not output_path:
                return

            final_doc = fitz.open()
            all_streams = settings["processor"].get_all_streams()

            total_page_count = settings["processor"].get_total_pages()
            global_page_index = 0

            for stream in all_streams:
                stream.seek(0)
                temp_doc = fitz.open(stream=stream.read(), filetype="pdf")

                for page_index in range(len(temp_doc)):
                    page = temp_doc[page_index]
                    global_page_index += 1
                    rect = page.rect
                    width, height = rect.width, rect.height

                    # === WATERMARK ===
                    wm = settings.get("watermark", {})
                    wm_type = wm.get("type", "None")

                    if wm_type != "None":
                        wm_pages = self._resolve_page_range(
                            wm.get("page_range_custom") if wm.get("page_range_type") == "Custom" else "All",
                            len(temp_doc)
                        )

                        if page_index + 1 in wm_pages:
                            if wm_type == "Text":
                                text = wm.get("text", "")
                                font_size = wm.get("font_size", 20)
                                opacity = wm.get("opacity", 0.3)
                                rotate = wm.get("rotation", 0)

                                pos_map = {
                                    "Top-Left": (width * 0.1, height * 0.1),
                                    "Top-Right": (width * 0.7, height * 0.1),
                                    "Center": (width * 0.3, height * 0.4),
                                    "Bottom-Left": (width * 0.1, height * 0.9),
                                    "Bottom-Right": (width * 0.7, height * 0.9),
                                }
                                x, y = pos_map.get(wm.get("position", "Center"), (width / 2, height / 2))
                                wm_rect = fitz.Rect(x, y, x + 300, y + 100)

                                page.insert_textbox(
                                    wm_rect,
                                    text,
                                    fontsize=font_size,
                                    fontname="helv",
                                    color=(0, 0, 0),
                                    rotate=rotate,
                                    fill_opacity=opacity,
                                    align=1
                                )


                            elif wm_type == "Image" and wm.get("image_path"):

                                try:

                                    img = Image.open(wm["image_path"]).convert("RGBA")

                                    # === Scale and Rotate ===

                                    scale = wm.get("scale", 0.3)

                                    rotation = wm.get("rotation", 0)

                                    opacity = wm.get("opacity", 0.3)

                                    # Resize and rotate

                                    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)

                                    img = img.rotate(rotation, expand=True)

                                    # Apply opacity

                                    img.putalpha(int(opacity * 255))

                                    # Save to temp file

                                    temp_path = "_temp_watermark_img.png"

                                    img.save(temp_path)

                                    # Get final image size

                                    w_img, h_img = img.size

                                    # Position mapping (center-relative)

                                    pos_map = {

                                        "Top-Left": (0.0, 0.0),

                                        "Top-Right": (1.0, 0.0),

                                        "Center": (0.5, 0.5),

                                        "Bottom-Left": (0.0, 1.0),

                                        "Bottom-Right": (1.0, 1.0),

                                    }

                                    x_ratio, y_ratio = pos_map.get(wm.get("position", "Center"), (0.5, 0.5))

                                    # Compute top-left x, y to center image at relative position

                                    x = int(width * x_ratio - w_img / 2)

                                    y = int(height * y_ratio - h_img / 2)

                                    # Clamp to keep within page

                                    x = max(0, min(x, width - w_img))

                                    y = max(0, min(y, height - h_img))

                                    # Insert image

                                    page.insert_image(

                                        fitz.Rect(x, y, x + w_img, y + h_img),

                                        filename=temp_path,

                                        overlay=True

                                    )
                                    if os.path.exists(temp_path):
                                        try:
                                            os.remove(temp_path)
                                        except Exception as e:
                                            print("Could not delete temp watermark image:", e)


                                except Exception as e:

                                    print("Watermark image error:", e)

                    # === SIGNATURE ===
                    sig = settings.get("signature_settings", {})
                    sig_pages = self._resolve_page_range(sig.get("apply_to"), len(temp_doc), sig.get("custom_range"))

                    if global_page_index in sig_pages and sig.get("path"):
                        try:
                            img = Image.open(sig["path"]).convert("RGBA")
                            img = img.rotate(sig.get("rotation", 0), expand=1)

                            scale = sig.get("scale", 0.3)
                            w_img = int(img.width * scale)
                            h_img = int(img.height * scale)
                            img = img.resize((w_img, h_img))

                            x_ratio = sig.get("custom_x", 0.8)
                            y_ratio = sig.get("custom_y", 0.8)

                            x = rect.width * x_ratio
                            y = rect.height * y_ratio

                            # Prevent going off page
                            if x + w_img > rect.width:
                                x = rect.width - w_img
                            if y + h_img > rect.height:
                                y = rect.height - h_img

                            temp_path = "_temp_sign.png"
                            img.save(temp_path)

                            page.insert_image(fitz.Rect(x, y, x + w_img, y + h_img), filename=temp_path)

                            if os.path.exists(temp_path):
                                try:
                                    os.remove(temp_path)
                                except Exception as e:
                                    print("Could not delete temp watermark image:", e)

                        except Exception as e:
                            print("Signature error:", e)

                    # === HEADER & FOOTER ===
                    hf = settings.get("header_footer", {})
                    hf_pages = self._resolve_page_range(hf.get("page_range"), len(temp_doc))
                    if page_index + 1 in hf_pages:
                        fontname = self.map_font(hf.get("font", "Arial"))
                        size = hf.get("font_size", 12)
                        align_name = hf.get("alignment", "Center")
                        align_map = {"Left": 0, "Center": 1, "Right": 2}
                        align = align_map.get(align_name, 1)

                        # Header text
                        if hf.get("header_text"):
                            page.insert_textbox(
                                fitz.Rect(0, 30, width, 60),
                                hf["header_text"],
                                fontname=fontname,
                                fontsize=size,
                                color=(0, 0, 0),
                                align=align
                            )

                        # Date/Time
                        info_parts = []
                        if hf.get("include_time"):
                            info_parts.append(datetime.now().strftime("%H:%M:%S"))
                        if hf.get("include_date"):
                            info_parts.append(datetime.now().strftime("%Y-%m-%d"))
                        if info_parts:
                            page.insert_textbox(
                                fitz.Rect(0, 60, width, 80),
                                "   ".join(info_parts),
                                fontname=fontname,
                                fontsize=size - 2,
                                color=(0, 0, 0),
                                align=align
                            )

                        # Footer
                        if hf.get("footer_text"):
                            page.insert_textbox(
                                fitz.Rect(0, height - 30, width, height-10),
                                hf["footer_text"],
                                fontname=fontname,
                                fontsize=size,
                                color=(0, 0, 0),
                                align=align
                            )


                        # Page number
                        if hf.get("include_page_number"):
                            page.insert_textbox(
                                fitz.Rect(0, height - 40, width, height - 20),
                                f"Page {global_page_index} of {total_page_count}",
                                fontname=fontname,
                                fontsize=size - 2,
                                color=(0, 0, 0),
                                align=align
                            )

                final_doc.insert_pdf(temp_doc)

            final_doc.save(output_path)
            final_doc.close()
            messagebox.showinfo("Success", "PDF saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF:\n{e}")

    def reset_app(self):
        import os
        import tkinter.messagebox as messagebox
        from pdf_processor import PDFProcessor

        confirm = messagebox.askyesno("Reset App", "Are you sure you want to reset everything and start over?")
        if not confirm:
            return

        # Clear settings
        settings.clear()
        settings["processor"] = PDFProcessor()

        # If ImportPage stored any temp files, clear them (optional logic)
        if hasattr(self.controller, "frames"):
            import_frame = self.controller.frames[0]  # 0 = ImportPage
            if hasattr(import_frame, "temp_files"):
                for tmp in import_frame.temp_files:
                    try:
                        os.remove(tmp)
                    except:
                        pass
                import_frame.temp_files.clear()
                import_frame.file_list.clear()
                import_frame.refresh_file_list()
                import_frame.update_page_count()

        # Go back to ImportPage (index 0)
        self.controller.show_frame(0)

    def _resolve_page_range(self, range_type, total_pages, custom=None):
        if range_type == "All" or not range_type:
            return list(range(1, total_pages + 1))
        elif range_type == "Custom" and custom:
            try:
                pages = []
                parts = custom.replace(" ", "").split(",")
                for part in parts:
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        pages.extend(range(start, end + 1))
                    else:
                        pages.append(int(part))
                return [p for p in pages if 1 <= p <= total_pages]
            except:
                return []
        return []
