import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import main from pizer.gui...")
    from pizer.gui import main
    print("Import successful.")
    print("GUI module syntax is correct.")
except Exception as e:
    print(f"Error verifying GUI module: {e}")
