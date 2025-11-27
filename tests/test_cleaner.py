import unittest
import os
import shutil
import zipfile
from pizer.cleaner import ArchiveCleaner

class TestArchiveCleaner(unittest.TestCase):
    TEST_DIR = "test_data"
    ZIP_NAME = "test_archive.zip"
    
    def setUp(self):
        # Create test directory
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)
        os.makedirs(self.TEST_DIR)
        
        # Create dummy files including junk
        self.files = {
            "good_file.txt": "This is a good file.",
            "__MACOSX/._good_file.txt": "Junk data",
            ".DS_Store": "Junk data",
            "Thumbs.db": "Junk data",
            "folder/good_file_2.txt": "Another good file.",
            "folder/.tmp": "Junk file"
        }
        
        # Create zip file
        self.zip_path = os.path.join(self.TEST_DIR, self.ZIP_NAME)
        with zipfile.ZipFile(self.zip_path, 'w') as zf:
            for name, content in self.files.items():
                zf.writestr(name, content)
                
    def tearDown(self):
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)

    def test_clean_and_extract(self):
        # Run cleaner
        output_dir = ArchiveCleaner.clean_and_extract(self.zip_path)
        
        # Verify output directory exists
        self.assertTrue(os.path.exists(output_dir))
        
        # Verify source zip is deleted
        self.assertFalse(os.path.exists(self.zip_path))
        
        # Verify good files exist
        self.assertTrue(os.path.exists(os.path.join(output_dir, "good_file.txt")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "folder/good_file_2.txt")))
        
        # Verify junk files are gone
        self.assertFalse(os.path.exists(os.path.join(output_dir, "__MACOSX")))
        self.assertFalse(os.path.exists(os.path.join(output_dir, ".DS_Store")))
        self.assertFalse(os.path.exists(os.path.join(output_dir, "Thumbs.db")))
        self.assertFalse(os.path.exists(os.path.join(output_dir, "folder/.tmp")))

if __name__ == '__main__':
    unittest.main()
