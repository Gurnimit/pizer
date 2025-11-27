import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import shutil
import threading
import time
import winshell
from win32com.client import Dispatch

# --- THEME ---
THEME = {
    "bg": "#121212",
    "fg": "#00FFFF",
    "text": "#E0E0E0",
    "btn": "#2D2D2D",
    "btn_hover": "#3D3D3D"
}

EULA_TEXT = """END USER LICENSE AGREEMENT

IMPORTANT: PLEASE READ CAREFULLY.

1. ACCEPTANCE OF TERMS
By installing and using the PiZer software ("Tool"), you agree to be bound by the terms of this agreement.

2. INTENDED USE
This Tool is designed and provided solely for:
   a) Educational purposes.
   b) Recovering passwords for files you own or have explicit permission to access.
   c) Security testing of your own systems.

3. PROHIBITED USE
You strictly agree NOT to use this Tool for:
   a) Any illegal activity.
   b) Accessing data, files, or systems without authorization.
   c) Causing damage or disruption to any system.

4. LIABILITY DISCLAIMER
The developers and distributors of this Tool assume NO LIABILITY for any misuse, damage, data loss, or legal consequences resulting from your use of this Tool. 
YOU ARE SOLELY RESPONSIBLE FOR YOUR ACTIONS.

5. INDEMNIFICATION
You agree to indemnify and hold harmless the developers from any claims arising out of your use of the Tool.

IF YOU DO NOT AGREE TO THESE TERMS, DO NOT INSTALL THIS SOFTWARE.
"""

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PiZer Setup")
        self.root.geometry("600x450")
        self.root.configure(bg=THEME["bg"])
        self.root.resizable(False, False)
        
        try:
            icon_path = resource_path(os.path.join("pizer", "assets", "logo.ico"))
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except: pass

        self.frames = {}
        self.current_frame = None
        
        self.init_frames()
        self.show_frame("Welcome")

    def init_frames(self):
        # Welcome Frame
        f1 = tk.Frame(self.root, bg=THEME["bg"])
        tk.Label(f1, text="Welcome to PiZer Setup", font=("Segoe UI", 20, "bold"), bg=THEME["bg"], fg=THEME["fg"]).pack(pady=40)
        tk.Label(f1, text="This wizard will install PiZer on your computer.", font=("Segoe UI", 12), bg=THEME["bg"], fg=THEME["text"]).pack(pady=10)
        tk.Label(f1, text="Click Next to continue.", font=("Segoe UI", 10), bg=THEME["bg"], fg="#888").pack(pady=40)
        self.add_nav(f1, next_cmd=lambda: self.show_frame("License"))
        self.frames["Welcome"] = f1

        # License Frame
        f2 = tk.Frame(self.root, bg=THEME["bg"])
        tk.Label(f2, text="License Agreement", font=("Segoe UI", 16, "bold"), bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
        
        txt = tk.Text(f2, height=12, width=60, bg="#1E1E1E", fg=THEME["text"], relief="flat", padx=10, pady=10)
        txt.insert("1.0", EULA_TEXT)
        txt.config(state="disabled")
        txt.pack(pady=10)
        
        self.agree_var = tk.BooleanVar()
        cb = tk.Checkbutton(f2, text="I accept the terms and take full responsibility", variable=self.agree_var, 
                            bg=THEME["bg"], fg=THEME["fg"], selectcolor=THEME["bg"], activebackground=THEME["bg"],
                            command=self.check_agree)
        cb.pack(pady=10)
        
        self.f2_nav = tk.Frame(f2, bg=THEME["bg"])
        self.f2_nav.pack(side="bottom", fill="x", pady=20, padx=20)
        self.f2_next = tk.Button(self.f2_nav, text="Next >", command=lambda: self.show_frame("Install"), state="disabled", bg=THEME["btn"], fg=THEME["text"], width=10)
        self.f2_next.pack(side="right")
        tk.Button(self.f2_nav, text="< Back", command=lambda: self.show_frame("Welcome"), bg=THEME["btn"], fg=THEME["text"], width=10).pack(side="right", padx=10)
        
        self.frames["License"] = f2

        # Install Frame
        f3 = tk.Frame(self.root, bg=THEME["bg"])
        tk.Label(f3, text="Installing PiZer...", font=("Segoe UI", 16, "bold"), bg=THEME["bg"], fg=THEME["fg"]).pack(pady=40)
        
        self.progress = ttk.Progressbar(f3, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)
        
        self.status_lbl = tk.Label(f3, text="Preparing...", bg=THEME["bg"], fg=THEME["text"])
        self.status_lbl.pack(pady=10)
        
        self.frames["Install"] = f3

        # Finish Frame
        f4 = tk.Frame(self.root, bg=THEME["bg"])
        tk.Label(f4, text="Installation Complete", font=("Segoe UI", 20, "bold"), bg=THEME["bg"], fg="#00FF00").pack(pady=40)
        tk.Label(f4, text="PiZer has been successfully installed.", font=("Segoe UI", 12), bg=THEME["bg"], fg=THEME["text"]).pack(pady=10)
        tk.Label(f4, text="You can launch it from your Desktop.", font=("Segoe UI", 10), bg=THEME["bg"], fg="#888").pack(pady=20)
        
        nav = tk.Frame(f4, bg=THEME["bg"])
        nav.pack(side="bottom", fill="x", pady=20, padx=20)
        tk.Button(nav, text="Finish", command=self.root.quit, bg=THEME["btn"], fg=THEME["text"], width=15).pack(side="right")
        self.frames["Finish"] = f4

    def add_nav(self, parent, next_cmd=None, back_cmd=None):
        nav = tk.Frame(parent, bg=THEME["bg"])
        nav.pack(side="bottom", fill="x", pady=20, padx=20)
        if next_cmd:
            tk.Button(nav, text="Next >", command=next_cmd, bg=THEME["btn"], fg=THEME["text"], width=10).pack(side="right")
        if back_cmd:
            tk.Button(nav, text="< Back", command=back_cmd, bg=THEME["btn"], fg=THEME["text"], width=10).pack(side="right", padx=10)

    def check_agree(self):
        if self.agree_var.get():
            self.f2_next.config(state="normal", bg=THEME["fg"], fg="black")
        else:
            self.f2_next.config(state="disabled", bg=THEME["btn"], fg=THEME["text"])

    def show_frame(self, name):
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = self.frames[name]
        self.current_frame.pack(fill="both", expand=True)
        
        if name == "Install":
            threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self):
        try:
            self.update_status("Locating files...", 10)
            time.sleep(0.5)
            
            # Source EXE
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
                src_exe = os.path.join(base_path, "PiZer.exe")
            else:
                src_exe = "dist/PiZer.exe"

            if not os.path.exists(src_exe):
                # Fallback
                if os.path.exists("PiZer.exe"): src_exe = "PiZer.exe"
                else:
                    messagebox.showerror("Error", "Installer corrupted: PiZer.exe not found.")
                    self.root.quit()
                    return

            self.update_status("Creating directories...", 30)
            app_data = os.getenv('LOCALAPPDATA')
            install_dir = os.path.join(app_data, "PiZer")
            dest_exe = os.path.join(install_dir, "PiZer.exe")

            if not os.path.exists(install_dir):
                os.makedirs(install_dir)
            
            self.update_status("Copying files...", 50)
            shutil.copy2(src_exe, dest_exe)
            time.sleep(0.5)

            self.update_status("Creating shortcuts...", 80)
            desktop = winshell.desktop()
            path = os.path.join(desktop, "PiZer.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = dest_exe
            shortcut.WorkingDirectory = install_dir
            shortcut.IconLocation = dest_exe
            shortcut.save()
            
            self.update_status("Finalizing...", 100)
            time.sleep(0.5)
            
            self.root.after(0, lambda: self.show_frame("Finish"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Installation Failed: {e}")
            self.root.quit()

    def update_status(self, text, val):
        self.status_lbl.config(text=text)
        self.progress["value"] = val
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
