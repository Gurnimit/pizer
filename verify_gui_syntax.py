import sys
import os
import tkinter as tk

try:
    from pizer.gui import PiZerGUI
    print("GUI module imported successfully.")
    root = tk.Tk()
    app = PiZerGUI(root)
    print("GUI initialized successfully.")
    root.destroy()
except Exception as e:
    print(f"GUI Error: {e}")
    sys.exit(1)
