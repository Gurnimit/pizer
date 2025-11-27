import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import sys
import os
import re
import time
import queue

# Ensure we can import pizer modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pizer.cleaner import ArchiveCleaner
from pizer.inspector import FileInspector
from pizer.recovery.runner import ZipRip

# --- THEME CONFIGURATION ---
THEME = {
    "bg": "#121212",
    "sidebar_bg": "#0A0A0A",
    "content_bg": "#121212",
    "fg": "#00FFFF",          # Cyan
    "text_light": "#E0E0E0",
    "accent": "#FF0055",      # Pink/Red
    "hacker_green": "#00FF41",# Matrix Green
    "entry_bg": "#1E1E1E",
    "entry_fg": "#FFFFFF",
    "btn_default": "#2D2D2D",
    "btn_hover": "#3D3D3D",
    "btn_active": "#00FFFF",
    "btn_text_active": "#000000",
    "border": "#00FFFF",
    "panel_bg": "#1A1A1A"
}

FONTS = {
    "header": ("Consolas", 24, "bold"),
    "sub_header": ("Consolas", 16, "bold"),
    "normal": ("Consolas", 10),
    "bold": ("Consolas", 10, "bold"),
    "small": ("Consolas", 9),
    "hacker": ("Consolas", 20, "bold"),
    "dashboard": ("Consolas", 12, "bold")
}

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=150, height=40, corner_radius=10, bg_color=THEME["btn_default"], fg_color=THEME["fg"], hover_color=THEME["btn_hover"]):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.text = text
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.corner_radius = corner_radius
        
        self.rect_id = self._draw_rounded_rect(2, 2, width-2, height-2, corner_radius, bg_color, outline=THEME["border"])
        self.text_id = self.create_text(width/2, height/2, text=text, fill=fg_color, font=FONTS["bold"])
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, outline):
        points = [
            x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r,
            x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, fill=fill, outline=outline, width=2)

    def _on_enter(self, event):
        self.itemconfig(self.rect_id, fill=self.hover_color)

    def _on_leave(self, event):
        self.itemconfig(self.rect_id, fill=self.bg_color)

    def _on_click(self, event):
        self.itemconfig(self.rect_id, fill=THEME["btn_active"])
        self.itemconfig(self.text_id, fill=THEME["btn_text_active"])

    def _on_release(self, event):
        self.itemconfig(self.rect_id, fill=self.hover_color)
        self.itemconfig(self.text_id, fill=self.fg_color)
        if self.command:
            self.command()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PiZerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("πzer - Cyber Defence Tool")
        self.root.geometry("1000x750")
        self.root.configure(bg=THEME["bg"])
        
        # Thread-safe queue for UI updates
        self.gui_queue = queue.Queue()
        
        # --- LAYOUT ---
        self.sidebar = tk.Frame(self.root, bg=THEME["sidebar_bg"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        self.content_area = tk.Frame(self.root, bg=THEME["content_bg"])
        self.content_area.pack(side="right", fill="both", expand=True)
        
        self._setup_sidebar()
        
        self.pages = {}
        self.current_page = None
        
        self._init_pages()
        self.show_page("Home")
        
        # Start queue processing loop
        self.root.after(100, self._process_queue)

    def _process_queue(self):
        try:
            while True:
                msg_type, data = self.gui_queue.get_nowait()
                
                if msg_type == "log":
                    # Find the active page log area
                    if isinstance(self.current_page, RecoveryPage):
                        self.current_page.log_area.insert(tk.END, data)
                        self.current_page.log_area.see(tk.END)
                    elif isinstance(self.current_page, CleanPage):
                        self.current_page.log_area.insert(tk.END, data)
                        self.current_page.log_area.see(tk.END)
                        
                elif msg_type == "key":
                    if isinstance(self.current_page, RecoveryPage):
                        self.current_page.key_var.set(data)
                        
                elif msg_type == "status":
                    if isinstance(self.current_page, RecoveryPage):
                        self.current_page.status_var.set(data)
                        
                self.gui_queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.root.after(50, self._process_queue)

    def _setup_sidebar(self):
        try:
            # Use resource_path for PyInstaller compatibility
            if getattr(sys, 'frozen', False):
                logo_path = resource_path(os.path.join("pizer", "assets", "logo.png"))
            else:
                logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

            if os.path.exists(logo_path):
                pil_image = Image.open(logo_path)
                pil_image = pil_image.resize((150, 150), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(pil_image)
                tk.Label(self.sidebar, image=self.logo_img, bg=THEME["sidebar_bg"]).pack(pady=20)
                self.root.iconphoto(False, self.logo_img)
            else:
                tk.Label(self.sidebar, text="πzer", font=FONTS["header"], bg=THEME["sidebar_bg"], fg=THEME["fg"]).pack(pady=20)
        except Exception as e:
            print(f"Logo Error: {e}")
            tk.Label(self.sidebar, text="πzer", font=FONTS["header"], bg=THEME["sidebar_bg"], fg=THEME["fg"]).pack(pady=20)

        nav_opts = ["Home", "Recovery", "Inspect", "Clean"]
        for opt in nav_opts:
            btn = RoundedButton(self.sidebar, text=opt.upper(), width=180, height=45, 
                                command=lambda o=opt: self.show_page(o),
                                bg_color=THEME["sidebar_bg"], hover_color="#1F1F1F")
            btn.pack(pady=10)
            
        tk.Label(self.sidebar, text="v1.0.1", font=FONTS["small"], bg=THEME["sidebar_bg"], fg="#555555").pack(side="bottom", pady=10)

    def _init_pages(self):
        self.pages["Home"] = HomePage(self.content_area, self)
        self.pages["Recovery"] = RecoveryPage(self.content_area, self)
        self.pages["Inspect"] = InspectPage(self.content_area, self)
        self.pages["Clean"] = CleanPage(self.content_area, self)

    def show_page(self, page_name):
        if self.current_page:
            self.current_page.pack_forget()
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)

class Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["content_bg"])
        self.controller = controller

class HomePage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Label(self, text="SYSTEM STATUS: ONLINE", font=FONTS["header"], bg=THEME["content_bg"], fg=THEME["fg"]).pack(pady=50)
        info_text = """
        WELCOME TO πzer
        
        ADVANCED ZIP ARCHIVE DEFENCE & RECOVERY
        
        [ MODULES ACTIVE ]
        > PASSWORD RECOVERY (DICTIONARY/BRUTE FORCE)
        > ARCHIVE INSPECTION (DEEP SCAN)
        > METADATA CLEANING & EXTRACTION
        
        SELECT A MODULE FROM THE SIDEBAR TO BEGIN.
        """
        tk.Label(self, text=info_text, font=FONTS["normal"], bg=THEME["content_bg"], fg=THEME["text_light"], justify="left").pack()

class RecoveryPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        header_frame = tk.Frame(self, bg=THEME["content_bg"])
        header_frame.pack(fill="x", padx=30, pady=20)
        tk.Label(header_frame, text="DECRYPTION PROTOCOL", font=FONTS["header"], bg=THEME["content_bg"], fg=THEME["fg"]).pack(side="left")
        
        container = tk.Frame(self, bg=THEME["content_bg"])
        container.pack(fill="both", expand=True, padx=30)
        
        config_col = tk.Frame(container, bg=THEME["content_bg"])
        config_col.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self._create_section_header(config_col, "1. TARGET ACQUISITION")
        self.zip_path = tk.StringVar()
        self._create_input(config_col, "Archive File:", self.zip_path, self.browse_zip)
        
        self._create_section_header(config_col, "2. ATTACK VECTOR")
        self.attack_mode = tk.StringVar(value="dictionary")
        
        mode_frame = tk.Frame(config_col, bg=THEME["content_bg"])
        mode_frame.pack(fill="x", pady=5)
        self._create_radio(mode_frame, "Dictionary Attack", "dictionary")
        self._create_radio(mode_frame, "Brute Force", "bruteforce")
        
        self.opts_container = tk.Frame(config_col, bg=THEME["content_bg"])
        self.opts_container.pack(fill="x", pady=10)
        
        self.wordlist_path = tk.StringVar()
        self.brute_max_len = tk.IntVar(value=0)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        
        self.toggle_mode()
        
        tk.Frame(config_col, height=20, bg=THEME["content_bg"]).pack()
        self.start_btn = RoundedButton(config_col, text="INITIATE SEQUENCE", command=self.start_recovery, width=250, height=50, bg_color=THEME["content_bg"], fg_color=THEME["fg"])
        self.start_btn.pack(anchor="center", pady=20)

        dash_col = tk.Frame(container, bg=THEME["content_bg"])
        dash_col.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        self._create_section_header(dash_col, "3. TACTICAL DASHBOARD")
        
        self.dash_frame = tk.Frame(dash_col, bg=THEME["panel_bg"], bd=2, relief="solid")
        self.dash_frame.pack(fill="x", pady=10, ipady=10)
        
        self.status_var = tk.StringVar(value="SYSTEM READY")
        self.target_var = tk.StringVar(value="NONE")
        self.key_var = tk.StringVar(value="---")
        
        self._add_dash_item(self.dash_frame, "STATUS", self.status_var, THEME["accent"])
        self._add_dash_item(self.dash_frame, "TARGET", self.target_var, THEME["text_light"])
        self._add_dash_item(self.dash_frame, "CURRENT KEY", self.key_var, THEME["hacker_green"], font=FONTS["hacker"])

        tk.Label(dash_col, text="SYSTEM LOG", font=FONTS["bold"], bg=THEME["content_bg"], fg=THEME["text_light"]).pack(anchor="w", pady=(20, 5))
        self.log_area = scrolledtext.ScrolledText(dash_col, height=15, bg="#000000", fg="#00FF00", font=("Consolas", 9), insertbackground="#00FF00", bd=0)
        self.log_area.pack(fill="both", expand=True)

    def _create_section_header(self, parent, text):
        tk.Label(parent, text=text, font=FONTS["bold"], bg=THEME["content_bg"], fg=THEME["fg"]).pack(anchor="w", pady=(10, 5))
        tk.Frame(parent, height=2, bg=THEME["fg"]).pack(fill="x", pady=(0, 10))

    def _create_input(self, parent, label, var, cmd):
        f = tk.Frame(parent, bg=THEME["content_bg"])
        f.pack(fill="x", pady=5)
        tk.Label(f, text=label, width=15, anchor="w", bg=THEME["content_bg"], fg=THEME["text_light"], font=FONTS["normal"]).pack(side="left")
        tk.Entry(f, textvariable=var, bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["fg"], font=FONTS["normal"], relief="flat").pack(side="left", fill="x", expand=True, padx=10)
        RoundedButton(f, text="...", command=cmd, width=30, height=25, corner_radius=5).pack(side="left")

    def _create_radio(self, parent, text, val):
        tk.Radiobutton(parent, text=text, variable=self.attack_mode, value=val, command=self.toggle_mode,
                       bg=THEME["content_bg"], fg=THEME["text_light"], selectcolor=THEME["content_bg"],
                       activebackground=THEME["content_bg"], activeforeground=THEME["fg"], font=FONTS["normal"]).pack(side="left", padx=(0, 20))

    def _add_dash_item(self, parent, label, var, color, font=FONTS["dashboard"]):
        f = tk.Frame(parent, bg=THEME["panel_bg"])
        f.pack(fill="x", padx=20, pady=5)
        tk.Label(f, text=label + ":", width=12, anchor="w", bg=THEME["panel_bg"], fg=THEME["text_light"], font=FONTS["normal"]).pack(side="left")
        tk.Label(f, textvariable=var, bg=THEME["panel_bg"], fg=color, font=font).pack(side="left")

    def browse_zip(self):
        f = filedialog.askopenfilename(filetypes=[("Archives", "*.zip *.rar"), ("All", "*.*")])
        if f: 
            self.zip_path.set(f)
            self.target_var.set(os.path.basename(f))

    def browse_wordlist(self):
        f = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if f: self.wordlist_path.set(f)

    def toggle_mode(self):
        for w in self.opts_container.winfo_children(): w.destroy()
        
        if self.attack_mode.get() == "dictionary":
            self._create_input(self.opts_container, "Wordlist:", self.wordlist_path, self.browse_wordlist)
        else:
            f = tk.Frame(self.opts_container, bg=THEME["content_bg"])
            f.pack(fill="x")
            tk.Label(f, text="Max Len (0=Inf):", bg=THEME["content_bg"], fg=THEME["text_light"], font=FONTS["normal"]).pack(side="left")
            tk.Entry(f, textvariable=self.brute_max_len, width=5, bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["fg"]).pack(side="left", padx=10)
            for t, v in [("a-z", self.use_lower), ("A-Z", self.use_upper), ("0-9", self.use_digits), ("!@#", self.use_symbols)]:
                tk.Checkbutton(f, text=t, variable=v, bg=THEME["content_bg"], fg=THEME["text_light"], selectcolor=THEME["content_bg"], activebackground=THEME["content_bg"], font=FONTS["normal"]).pack(side="left", padx=5)

    def start_recovery(self):
        zip_file = self.zip_path.get()
        wordlist = self.wordlist_path.get()
        mode = self.attack_mode.get()
        
        if not zip_file: return
        if mode == "dictionary" and not wordlist: return
        
        self.status_var.set("RUNNING PROTOCOL...")
        self.log_area.delete(1.0, tk.END)
        self.log_area.insert(tk.END, f"> INITIALIZING {mode.upper()}...\n")
        
        threading.Thread(target=self.run_recovery, args=(zip_file, wordlist), daemon=True).start()

    def run_recovery(self, zip_file, wordlist):
        try:
            old_stdout = sys.stdout
            sys.stdout = RedirectText(self.controller.gui_queue)
            
            ripper = ZipRip()
            ripper.ZipFile = zip_file
            if self.attack_mode.get() == "dictionary":
                ripper.Wordlist = wordlist
                ripper.AttackMode = "dictionary"
            else:
                ripper.AttackMode = "bruteforce"
                ripper.BruteForceConfig = {
                    "max_length": self.brute_max_len.get(),
                    "use_lower": self.use_lower.get(),
                    "use_upper": self.use_upper.get(),
                    "use_digits": self.use_digits.get(),
                    "use_symbols": self.use_symbols.get()
                }
            ripper.SetZipFileDirectory()
            ripper.SetPasswords()
            ripper.CrackPassword()
            
            if ripper.FoundPassword:
                self.controller.gui_queue.put(("status", "SUCCESS: KEY FOUND"))
                self.controller.gui_queue.put(("key", ripper.FoundPassword))
                self.controller.gui_queue.put(("log", f"\n> PASSWORD FOUND: {ripper.FoundPassword}\n"))
            else:
                self.controller.gui_queue.put(("status", "FAILURE: KEY NOT FOUND"))
                self.controller.gui_queue.put(("key", "---"))
                self.controller.gui_queue.put(("log", "\n> PASSWORD NOT FOUND.\n"))
        except Exception as e:
            self.controller.gui_queue.put(("log", f"\n> ERROR: {e}\n"))
            self.controller.gui_queue.put(("status", "SYSTEM ERROR"))
        finally:
            sys.stdout = old_stdout

class InspectPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Label(self, text="ARCHIVE INSPECTION", font=FONTS["sub_header"], bg=THEME["content_bg"], fg=THEME["fg"]).pack(pady=20)
        self.zip_path = tk.StringVar()
        self._create_input("Target Archive:", self.zip_path, self.browse_zip)
        RoundedButton(self, text="SCAN CONTENTS", command=self.inspect, width=200, height=50).pack(pady=20)
        self.listbox = tk.Listbox(self, bg="#000000", fg=THEME["fg"], font=FONTS["normal"], bd=2, relief="sunken")
        self.listbox.pack(fill="both", expand=True, padx=40, pady=20)

    def _create_input(self, label, var, cmd):
        f = tk.Frame(self, bg=THEME["content_bg"])
        f.pack(fill="x", padx=40, pady=5)
        tk.Label(f, text=label, width=15, anchor="w", bg=THEME["content_bg"], fg=THEME["fg"], font=FONTS["normal"]).pack(side="left")
        tk.Entry(f, textvariable=var, bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["fg"], font=FONTS["normal"]).pack(side="left", fill="x", expand=True, padx=10)
        RoundedButton(f, text="...", command=cmd, width=40, height=25, corner_radius=5).pack(side="left")

    def browse_zip(self):
        f = filedialog.askopenfilename(filetypes=[("Archives", "*.zip *.rar"), ("All", "*.*")])
        if f: self.zip_path.set(f)

    def inspect(self):
        f = self.zip_path.get()
        if not f: return
        try:
            self.listbox.delete(0, tk.END)
            files = FileInspector.inspect(f)
            for name, size in files:
                self.listbox.insert(tk.END, f"{name} | {size} bytes")
        except Exception as e:
            self.listbox.insert(tk.END, f"Error: {e}")

class CleanPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Label(self, text="CLEAN & EXTRACT", font=FONTS["sub_header"], bg=THEME["content_bg"], fg=THEME["fg"]).pack(pady=20)
        self.zip_path = tk.StringVar()
        self._create_input("Target Archive:", self.zip_path, self.browse_zip)
        RoundedButton(self, text="EXECUTE CLEANUP", command=self.clean, width=200, height=50, fg_color="#00FF00").pack(pady=20)
        self.log_area = scrolledtext.ScrolledText(self, height=10, bg="#000000", fg="#00FF00", font=("Consolas", 9), insertbackground="#00FF00", bd=2, relief="sunken")
        self.log_area.pack(fill="both", expand=True, padx=40, pady=20)

    def _create_input(self, label, var, cmd):
        f = tk.Frame(self, bg=THEME["content_bg"])
        f.pack(fill="x", padx=40, pady=5)
        tk.Label(f, text=label, width=15, anchor="w", bg=THEME["content_bg"], fg=THEME["fg"], font=FONTS["normal"]).pack(side="left")
        tk.Entry(f, textvariable=var, bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["fg"], font=FONTS["normal"]).pack(side="left", fill="x", expand=True, padx=10)
        RoundedButton(f, text="...", command=cmd, width=40, height=25, corner_radius=5).pack(side="left")

    def browse_zip(self):
        f = filedialog.askopenfilename(filetypes=[("Archives", "*.zip *.rar"), ("All", "*.*")])
        if f: self.zip_path.set(f)

    def clean(self):
        f = self.zip_path.get()
        if not f: return
        if not messagebox.askyesno("Confirm", "Extract and DELETE original?"): return
        self.log_area.delete(1.0, tk.END)
        self.log_area.insert(tk.END, "> PROCESSING...\n")
        threading.Thread(target=self.run_clean, args=(f,), daemon=True).start()

    def run_clean(self, f):
        try:
            old_stdout = sys.stdout
            sys.stdout = RedirectText(self.controller.gui_queue)
            out = ArchiveCleaner.clean_and_extract(f)
            self.controller.gui_queue.put(("log", f"\n> DONE. Extracted to: {out}\n"))
        except Exception as e:
            self.controller.gui_queue.put(("log", f"\n> ERROR: {e}\n"))
        finally:
            sys.stdout = old_stdout

class RedirectText:
    def __init__(self, queue):
        self.queue = queue

    def write(self, string):
        clean_str = ANSI_ESCAPE.sub('', string)
        if "\r" in string or "Trying Password" in clean_str:
            if "Trying Password:" in clean_str:
                parts = clean_str.split("Trying Password:")
                if len(parts) > 1:
                    self.queue.put(("key", parts[1].strip()))
                else:
                    self.queue.put(("key", clean_str.strip()))
            else:
                self.queue.put(("key", clean_str.strip()))
            return
        self.queue.put(("log", clean_str))

    def flush(self): pass

def main():
    root = tk.Tk()
    app = PiZerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
