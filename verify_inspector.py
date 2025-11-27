import os
import sys
import zipfile

# Ensure we can import pizer modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pizer.inspector import FileInspector

def create_dummy_zip(filename):
    with zipfile.ZipFile(filename, 'w') as zf:
        zf.writestr('test.txt', 'This is a test file.')
        zf.writestr('folder/inside.txt', 'Another file.')

def test_inspector():
    zip_name = "test_inspector.zip"
    create_dummy_zip(zip_name)
    
    try:
        print(f"Testing inspection of {zip_name}...")
        files = FileInspector.inspect(zip_name)
        print("Files found:")
        for name, size in files:
            print(f" - {name}: {size} bytes")
            
        if len(files) == 2:
            print("SUCCESS: Found correct number of files.")
        else:
            print("FAILURE: Incorrect number of files found.")
            
    except Exception as e:
        print(f"FAILURE: Exception occurred: {e}")
    finally:
        if os.path.exists(zip_name):
            os.remove(zip_name)

if __name__ == "__main__":
    test_inspector()
