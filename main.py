from tkinterdnd2 import TkinterDnD
import tkinter as tk
from import_page import ImportPage
from settings_page import SettingsPage
from watermark_page import WatermarkPage
from signature_page import SignaturePage
from header_footer_page import HeaderFooterPage
from download_page import DownloadPage

class PDFToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Watermark & Merger Tool")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)

        # Step definitions
        self.steps = [
            ("Import", ImportPage),
            ("Settings", SettingsPage),
            ("Watermark", WatermarkPage),
            ("Signature", SignaturePage),
            ("Header/Footer", HeaderFooterPage),
            ("Download", DownloadPage),
        ]

        self.frames = {}

        # ==== Sidebar Navigation ====
        self.sidebar = tk.Frame(self.root, bg="#ACDEF0")
        self.sidebar.place(relx=0, rely=0, relwidth=0.18, relheight=1)

        self.nav_buttons = []
        for index, (label, _) in enumerate(self.steps):
            btn = tk.Label(self.sidebar, text=label, bg="#ACDEF0", fg="black", highlightthickness=1, highlightcolor="#000000", font=("Arial", 12),
                           anchor="w", padx=10)
            btn.place(relx=0, rely=index * (1 / len(self.steps)), relwidth=1, relheight=1 / len(self.steps))
            self.nav_buttons.append(btn)

        # ==== Main Content Area ====
        self.container = tk.Frame(self.root, bg="#c6f0f5")
        self.container.place(relx=0.18, rely=0, relwidth=0.82, relheight=1)

        for i, (_, FrameClass) in enumerate(self.steps):
            frame = FrameClass(self.container, self)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.frames[i] = frame

        self.current_step = 0
        self.show_frame(0)

    def show_frame(self, index):
        # Hide all frames
        for frame in self.frames.values():
            frame.place_forget()

        # Show selected frame
        self.frames[index].place(relx=0, rely=0, relwidth=1, relheight=1)
        self.current_step = index

        # Update sidebar highlight
        for i, btn in enumerate(self.nav_buttons):
            btn.config(bg="#32B5E4" if i == index else "#ACDEF0", fg="white" if i == index else "black")

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.show_frame(self.current_step + 1)

    def previous_step(self):
        if self.current_step > 0:
            self.show_frame(self.current_step - 1)



if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFToolApp(root)
    root.mainloop()
