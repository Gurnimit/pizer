import sys
import os

# Add current directory to path to allow importing pizer
sys.path.append(os.getcwd())

from pizer.stream_reader import ZipStreamReader

def verify():
    zip_path = "c:/Users/karan/Desktop/PiZer/test/hello.zip"
    print(f"Testing ZipStreamReader on {zip_path}")
    
    try:
        # Try without password first
        print("Attempting to list files...")
        reader = ZipStreamReader(zip_path)
        files = reader.list_files()
        print("Files found:")
        for f in files:
            print(f" - {f}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
