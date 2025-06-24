import os
import tempfile
from tkinterdnd2 import DND_FILES
import tkinter as tk
from tkinter import filedialog
from config import settings
from pdf_processor import PDFProcessor
from docx2pdf import convert

class ImportPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6e6e6")
        self.controller = controller

        self.file_list = []
        self.temp_files = []  # store converted temp PDFs
        settings["files"] = self.file_list

        self.drop_area = tk.Label(self, bg="#ffffff", text="Drag and Drop File/s here\nor", font=("Arial", 12),
                                  relief="solid", bd=1, justify="center")
        self.drop_area.place(relx=0.1, rely=0.15, relwidth=0.3, relheight=0.5)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.on_drop)

        self.browse_button = tk.Button(self.drop_area, text="Browse files", bg="#00bfff", fg="white", command=self.browse_files)
        self.browse_button.place(relx=0.5, rely=0.65, relwidth=0.5, anchor="center")

        self.file_box = tk.Frame(self, bg="#ffffff", highlightbackground="black", highlightthickness=1)
        self.file_box.place(relx=0.55, rely=0.15, relwidth=0.3, relheight=0.5)

        self.file_title = tk.Label(self, text="File list", bg="#e6e6e6", font=("Arial", 12, "bold"))
        self.file_title.place(relx=0.55, rely=0.1)

        self.page_count_label = tk.Label(self, text="Total Pages: 0", bg="#e6e6e6", font=("Arial", 10, "bold"))
        self.page_count_label.place(relx=0.1, rely=0.7)

        self.next_button = tk.Button(self, text="NEXT", bg="#00bfff", fg="white",
                                     font=("Arial", 12, "bold"),
                                     command=lambda: self.controller.next_step())
        self.next_button.place(relx=0.8, rely=0.85, relwidth=0.1, relheight=0.07)

    def browse_files(self):
        files = filedialog.askopenfilenames(filetypes=[
            ("Supported Files", "*.pdf *.jpg *.jpeg *.png *.doc *.docx"),
            ("All files", "*.*")
        ])
        self.add_files(files)

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        self.add_files(files)

    def add_files(self, files):
        for file in files:
            if file not in self.file_list and os.path.isfile(file):
                ext = os.path.splitext(file)[1].lower()

                if ext in [".doc", ".docx"]:
                    # Convert to PDF temporarily
                    try:
                        tmp_dir = tempfile.mkdtemp()
                        out_pdf = os.path.join(tmp_dir, os.path.basename(file) + ".pdf")
                        convert(file, out_pdf)
                        self.temp_files.append(out_pdf)
                        self.file_list.append(file)  # original name shown
                        settings["processor"].add_file(out_pdf)  # use converted file
                    except Exception as e:
                        print(f"Failed to convert {file}: {e}")
                else:
                    self.file_list.append(file)
                    settings["processor"].add_file(file)

        self.refresh_file_list()
        self.update_page_count()

    def remove_file(self, index):
        if 0 <= index < len(self.file_list):
            removed_file = self.file_list.pop(index)

            # If corresponding temp file exists, delete it
            if index < len(self.temp_files):
                try:
                    os.remove(self.temp_files[index])
                except:
                    pass
                del self.temp_files[index]

            # Reset processor and re-add
            settings["processor"] = PDFProcessor()
            for i, f in enumerate(self.file_list):
                ext = os.path.splitext(f)[1].lower()
                if ext in [".doc", ".docx"]:
                    settings["processor"].add_file(self.temp_files[i])
                else:
                    settings["processor"].add_file(f)

            self.refresh_file_list()
            self.update_page_count()

    def refresh_file_list(self):
        for widget in self.file_box.winfo_children():
            widget.destroy()

        for idx, file_path in enumerate(self.file_list):
            file_name = os.path.basename(file_path)
            label = tk.Label(self.file_box, text=file_name, bg="white", anchor="w")
            label.place(relx=0.05, rely=0.05 + idx * 0.15, relwidth=0.75, relheight=0.12)

            remove_btn = tk.Button(self.file_box, text="✖", bg="white", fg="red",
                                   command=lambda i=idx: self.remove_file(i), bd=0)
            remove_btn.place(relx=0.82, rely=0.05 + idx * 0.15, relwidth=0.1, relheight=0.12)

    def update_page_count(self):
        total = settings["processor"].get_total_pages()
        self.page_count_label.config(text=f"Total Pages: {total}")
