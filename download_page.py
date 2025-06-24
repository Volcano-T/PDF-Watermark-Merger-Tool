import tkinter as tk
from tkinter import filedialog, messagebox
import os
from config import settings

class DownloadPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f4f4")
        self.controller = controller

        self.save_path = tk.StringVar()
        self.filename = tk.StringVar(value="output.pdf")
        self.status_message = tk.StringVar()

        # ===== Title =====
        tk.Label(self, text="Download PDF", font=("Arial", 16, "bold"), bg="#f4f4f4").place(relx=0.05, rely=0.05)

        # ===== Save Location =====
        tk.Label(self, text="Save Location:", bg="#f4f4f4").place(relx=0.05, rely=0.15)
        tk.Entry(self, textvariable=self.save_path).place(relx=0.2, rely=0.15, relwidth=0.5)
        tk.Button(self, text="Browse", command=self.browse_folder).place(relx=0.72, rely=0.15)

        # ===== Filename =====
        tk.Label(self, text="Filename:", bg="#f4f4f4").place(relx=0.05, rely=0.25)
        tk.Entry(self, textvariable=self.filename).place(relx=0.2, rely=0.25, relwidth=0.5)

        # ===== Save Button =====
        tk.Button(self, text="Save PDF", bg="#32B5E4", fg="white", font=("Arial", 12, "bold"),
                  command=self.save_pdf).place(relx=0.2, rely=0.4, relwidth=0.3, relheight=0.08)

        # ===== Status =====
        tk.Label(self, textvariable=self.status_message, fg="green", bg="#f4f4f4", font=("Arial", 10, "italic")).place(relx=0.2, rely=0.5)

        # ===== Back Button =====
        back_button = tk.Button(self, text="BACK", bg="#aaaaaa", fg="white", font=("Arial", 12, "bold"),
                                command=lambda: controller.previous_step())
        back_button.place(relx=0.68, rely=0.85, relwidth=0.1, relheight=0.07)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path.set(path)

    def save_pdf(self):
        path = self.save_path.get()
        name = self.filename.get()

        if not path or not name:
            self.status_message.set("Please specify both save path and filename.")
            return

        full_path = os.path.join(path, name)

        # Placeholder PDF save logic
        try:
            # Call your PDF generation logic here
            # apply_all_settings_and_save_pdf(full_path, settings)
            with open(full_path, 'w') as f:
                f.write("Dummy PDF content.\n")
                f.write(str(settings))  # Just to confirm it's working

            self.status_message.set("PDF saved successfully!")
        except Exception as e:
            self.status_message.set("Failed to save PDF.")
            messagebox.showerror("Error", str(e))
