import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import ZipRip from pizer.recovery.runner...")
    from pizer.recovery.runner import ZipRip
    print("Import successful.")
    
    print("Attempting to instantiate ZipRip...")
    ripper = ZipRip()
    print("Instantiation successful.")
    print("Recovery module syntax is correct.")

except Exception as e:
    print(f"Error verifying recovery module: {e}")
