import os
import sys
import zipfile
from typer.testing import CliRunner
from pizer.cli import app

runner = CliRunner()

def create_dummy_zip(filename):
    with zipfile.ZipFile(filename, 'w') as zf:
        zf.writestr('test.txt', 'This is a test file.')
        zf.writestr('folder/inside.txt', 'Another file.')

def test_cli_inspect():
    zip_name = "test_cli.zip"
    create_dummy_zip(zip_name)
    
    try:
        print(f"Testing CLI inspection of {zip_name}...")
        result = runner.invoke(app, ["inspect", zip_name])
        
        print("Exit Code:", result.exit_code)
        print("Output:\n", result.stdout)
        
        if result.exit_code == 0 and "test.txt" in result.stdout:
            print("SUCCESS: CLI inspection passed.")
        else:
            print("FAILURE: CLI inspection failed.")
            
    except Exception as e:
        print(f"FAILURE: Exception occurred: {e}")
    finally:
        if os.path.exists(zip_name):
            os.remove(zip_name)

if __name__ == "__main__":
    test_cli_inspect()
