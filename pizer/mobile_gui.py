import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
import queue
import re
import time

# Ensure we can import pizer modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pizer.recovery.runner import ZipRip

# --- THEME ---
THEME = {
    "bg": "#050505",        # Deep Black
    "surface": "#121212",   # Dark Gray
    "primary": "#00FFFF",   # Cyan (Brand)
    "secondary": "#FF0055", # Pink/Red Accent
    "text": "#FFFFFF",
    "subtext": "#888888",
    "success": "#00FF41",   # Hacker Green
    "error": "#FF3333"
}

FONTS = {
    "hero": ("Helvetica", 40, "bold"),
    "h2": ("Helvetica", 20, "bold"),
    "body": ("Helvetica", 12),
    "mono": ("Consolas", 18, "bold"),
    "btn": ("Helvetica", 12, "bold")
}

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class CyberButton(tk.Canvas):
    def __init__(self, parent, text, command, width=250, height=50, bg_color=THEME["surface"], fg_color=THEME["primary"], border_color=THEME["primary"]):
        super().__init__(parent, width=width, height=height, bg=THEME["bg"], highlightthickness=0)
        self.command = command
        self.text = text
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.width = width
        self.height = height
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        self._draw(self.bg_color, self.fg_color)

    def _draw(self, bg, fg):
        self.delete("all")
        w, h = self.width, self.height
        
        # Techy Border
        self.create_line(0, 0, w, 0, fill=self.border_color, width=2)
        self.create_line(0, h, w, h, fill=self.border_color, width=2)
        self.create_line(0, 0, 0, h, fill=self.border_color, width=2)
        self.create_line(w, 0, w, h, fill=self.border_color, width=2)
        
        # Fill
        self.create_rectangle(4, 4, w-4, h-4, fill=bg, outline="")
        
        # Text
        self.create_text(w/2, h/2, text=self.text, fill=fg, font=FONTS["btn"])

    def _on_enter(self, e): self._draw(self.border_color, "#000000")
    def _on_leave(self, e): self._draw(self.bg_color, self.fg_color)
    def _on_click(self, e): self._draw("#FFFFFF", "#000000")
    def _on_release(self, e): 
        self._draw(self.border_color, "#000000")
        if self.command: self.command()

class MobileApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PiZer Mobile")
        self.root.geometry("375x812")
        self.root.configure(bg=THEME["bg"])
        self.root.resizable(False, False)
        
        self.gui_queue = queue.Queue()
        self.frames = {}
        self.current_frame = None
        
        # App State
        self.target_file = None
        self.mode_var = tk.StringVar(value="brute")
        self.use_lower = tk.BooleanVar(value=True)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        
        self._init_screens()
        self.show_frame("Splash")
        self.root.after(50, self._process_queue)

    def _init_screens(self):
        # --- 1. SPLASH SCREEN ---
        f1 = tk.Frame(self.root, bg=THEME["bg"])
        
        # Logo Area
        tk.Label(f1, text="πzer", font=("Helvetica", 60, "bold"), bg=THEME["bg"], fg=THEME["primary"]).pack(pady=(150, 10))
        tk.Label(f1, text="Advanced Cyber Defence", font=("Helvetica", 14), bg=THEME["bg"], fg=THEME["text"]).pack()
        tk.Label(f1, text="Professional Recovery Suite", font=("Helvetica", 10), bg=THEME["bg"], fg=THEME["subtext"]).pack(pady=(5, 50))
        
        # Status
        tk.Label(f1, text="SYSTEM ONLINE", font=("Consolas", 10), bg=THEME["bg"], fg=THEME["success"]).pack(pady=20)
        
        # Button
        CyberButton(f1, "INITIALIZE SYSTEM", lambda: self.show_frame("Terms")).pack(side="bottom", pady=60)
        
        self.frames["Splash"] = f1

        # --- 2. TERMS SCREEN ---
        f2 = tk.Frame(self.root, bg=THEME["bg"])
        
        tk.Label(f2, text="ACCESS PROTOCOLS", font=FONTS["h2"], bg=THEME["bg"], fg=THEME["primary"]).pack(pady=(60, 30))
        
        terms_frame = tk.Frame(f2, bg=THEME["surface"], padx=20, pady=20)
        terms_frame.pack(fill="x", padx=20)
        
        terms = [
            "1. AUTHORIZED USE ONLY",
            "   Use this tool only on files you own.",
            "",
            "2. NO LIABILITY",
            "   Developers are not responsible for misuse.",
            "",
            "3. EDUCATIONAL PURPOSE",
            "   Designed for security testing."
        ]
        
        for line in terms:
            tk.Label(terms_frame, text=line, font=("Consolas", 10), bg=THEME["surface"], fg=THEME["text"], justify="left", anchor="w").pack(fill="x")
            
        CyberButton(f2, "ACCEPT & PROCEED", lambda: self.show_frame("Main")).pack(side="bottom", pady=60)
        
        self.frames["Terms"] = f2

        # --- 3. MAIN APP ---
        f3 = tk.Frame(self.root, bg=THEME["bg"])
        
        # Header
        header = tk.Frame(f3, bg=THEME["surface"], height=60)
        header.pack(fill="x")
        tk.Label(header, text="πzer // COMMAND", font=("Consolas", 14, "bold"), bg=THEME["surface"], fg=THEME["primary"]).pack(pady=20)
        
        # Target
        tk.Label(f3, text="TARGET ARCHIVE", font=("Helvetica", 10, "bold"), bg=THEME["bg"], fg=THEME["subtext"]).pack(anchor="w", padx=20, pady=(30, 5))
        
        self.file_card = tk.Frame(f3, bg=THEME["surface"], height=60)
        self.file_card.pack(fill="x", padx=20)
        self.file_card.pack_propagate(False)
        self.file_lbl = tk.Label(self.file_card, text="[ TAP TO SELECT ]", font=("Consolas", 12), bg=THEME["surface"], fg=THEME["text"])
        self.file_lbl.place(relx=0.5, rely=0.5, anchor="center")
        self.file_card.bind("<Button-1>", lambda e: self.browse_zip())
        self.file_lbl.bind("<Button-1>", lambda e: self.browse_zip())

        # Config
        tk.Label(f3, text="ATTACK CONFIGURATION", font=("Helvetica", 10, "bold"), bg=THEME["bg"], fg=THEME["subtext"]).pack(anchor="w", padx=20, pady=(20, 5))
        
        cfg = tk.Frame(f3, bg=THEME["bg"])
        cfg.pack(fill="x", padx=20)
        
        # Mode
        tk.Label(cfg, text="MODE:", font=("Consolas", 10), bg=THEME["bg"], fg=THEME["primary"]).pack(anchor="w")
        mode_frame = tk.Frame(cfg, bg=THEME["bg"])
        mode_frame.pack(fill="x", pady=5)
        
        self.btn_brute = tk.Label(mode_frame, text="[ BRUTE FORCE ]", bg=THEME["bg"], fg=THEME["primary"], font=("Consolas", 10, "bold"))
        self.btn_brute.pack(side="left", padx=(0, 10))
        self.btn_brute.bind("<Button-1>", lambda e: self.set_mode("brute"))
        
        self.btn_dict = tk.Label(mode_frame, text="[ DICTIONARY ]", bg=THEME["bg"], fg=THEME["subtext"], font=("Consolas", 10))
        self.btn_dict.pack(side="left")
        self.btn_dict.bind("<Button-1>", lambda e: self.set_mode("dict"))
        
        # Toggles
        self.toggles_frame = tk.Frame(cfg, bg=THEME["bg"])
        self.toggles_frame.pack(fill="x", pady=10)
        for txt, var in [("a-z", self.use_lower), ("A-Z", self.use_upper), ("0-9", self.use_digits), ("#@!", self.use_symbols)]:
            cb = tk.Checkbutton(self.toggles_frame, text=txt, variable=var, bg=THEME["bg"], fg=THEME["text"], selectcolor=THEME["bg"], activebackground=THEME["bg"], font=("Consolas", 10))
            cb.pack(side="left", padx=(0, 10))

        # Decryption Stream
        tk.Label(f3, text="DECRYPTION STREAM", font=("Helvetica", 10, "bold"), bg=THEME["bg"], fg=THEME["subtext"]).pack(anchor="w", padx=20, pady=(30, 5))
        
        self.stream_box = tk.Frame(f3, bg="#000000", height=80, highlightbackground=THEME["surface"], highlightthickness=1)
        self.stream_box.pack(fill="x", padx=20)
        self.stream_box.pack_propagate(False)
        
        self.attempt_lbl = tk.Label(self.stream_box, text="WAITING...", font=FONTS["mono"], bg="#000000", fg=THEME["primary"])
        self.attempt_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Start
        CyberButton(f3, "EXECUTE", self.start, width=335, bg_color=THEME["secondary"], fg_color="#FFFFFF", border_color=THEME["secondary"]).pack(side="bottom", pady=40)

        self.frames["Main"] = f3

    def show_frame(self, name):
        if self.current_frame: self.current_frame.pack_forget()
        self.current_frame = self.frames[name]
        self.current_frame.pack(fill="both", expand=True)

    def set_mode(self, mode):
        self.mode_var.set(mode)
        if mode == "brute":
            self.btn_brute.config(fg=THEME["primary"], font=("Consolas", 10, "bold"))
            self.btn_dict.config(fg=THEME["subtext"], font=("Consolas", 10))
            self.toggles_frame.pack(fill="x", pady=10)
        else:
            self.btn_dict.config(fg=THEME["primary"], font=("Consolas", 10, "bold"))
            self.btn_brute.config(fg=THEME["subtext"], font=("Consolas", 10))
            self.toggles_frame.pack_forget()

    def browse_zip(self):
        f = filedialog.askopenfilename(filetypes=[("Archives", "*.zip *.rar"), ("All", "*.*")])
        if f:
            self.target_file = f
            name = os.path.basename(f)
            if len(name) > 20: name = name[:17] + "..."
            self.file_lbl.config(text=name, fg=THEME["primary"])

    def start(self):
        if not self.target_file: return
        self.attempt_lbl.config(text="INITIALIZING...")
        threading.Thread(target=self._run_engine, daemon=True).start()

    def _process_queue(self):
        try:
            while True:
                msg_type, data = self.gui_queue.get_nowait()
                if msg_type == "attempt":
                    self.attempt_lbl.config(text=data)
                elif msg_type == "success":
                    self.attempt_lbl.config(text=data, fg=THEME["success"])
                elif msg_type == "fail":
                    self.attempt_lbl.config(text="FAILED", fg=THEME["error"])
                self.gui_queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.root.after(50, self._process_queue)

    def _run_engine(self):
        class CleanRedirect:
            def __init__(self, q): self.q = q
            def write(self, s):
                clean = ANSI_ESCAPE.sub('', s)
                if "Trying Password:" in clean:
                    parts = clean.split("Trying Password:")
                    if len(parts) > 1:
                        pwd = parts[1].strip()
                        self.q.put(("attempt", pwd))
            def flush(self): pass

        try:
            old_stdout = sys.stdout
            sys.stdout = CleanRedirect(self.gui_queue)
            
            ripper = ZipRip()
            ripper.ZipFile = self.target_file
            
            if self.mode_var.get() == "brute":
                ripper.AttackMode = "bruteforce"
                ripper.BruteForceConfig = {
                    "max_length": 0,
                    "use_lower": self.use_lower.get(),
                    "use_upper": self.use_upper.get(),
                    "use_digits": self.use_digits.get(),
                    "use_symbols": self.use_symbols.get()
                }
            else:
                ripper.AttackMode = "dictionary"
                # Fallback
                ripper.AttackMode = "bruteforce" 
                ripper.BruteForceConfig["max_length"] = 0
            
            ripper.SetZipFileDirectory()
            ripper.SetPasswords()
            ripper.CrackPassword()
            
            if ripper.FoundPassword:
                self.gui_queue.put(("success", ripper.FoundPassword))
            else:
                self.gui_queue.put(("fail", ""))
        except Exception as e:
            print(e)
        finally:
            sys.stdout = old_stdout

if __name__ == "__main__":
    root = tk.Tk()
    app = MobileApp(root)
    root.mainloop()
