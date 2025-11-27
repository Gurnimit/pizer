import os
import shutil
import zipfile
import tarfile
from typing import List, Optional

try:
    import rarfile
except ImportError:
    rarfile = None

class ArchiveCleaner:
    JUNK_FILES = {
        '__MACOSX',
        '.DS_Store',
        'Thumbs.db',
        'desktop.ini',
    }
    
    JUNK_EXTENSIONS = {
        '.tmp',
        '.bak',
        '.log'
    }

    @staticmethod
    def clean_and_extract(archive_path: str, output_dir: Optional[str] = None) -> str:
        """
        Extracts the archive, removes junk files, and deletes the source archive.
        Returns the path to the extracted directory.
        """
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Archive not found: {archive_path}")

        # Determine output directory
        if output_dir is None:
            base_name = os.path.splitext(os.path.basename(archive_path))[0]
            output_dir = os.path.join(os.path.dirname(archive_path), base_name)
            
        # Ensure output directory is unique
        counter = 1
        original_output_dir = output_dir
        while os.path.exists(output_dir):
            output_dir = f"{original_output_dir}_{counter}"
            counter += 1
            
        os.makedirs(output_dir)

        # Extract
        try:
            ArchiveCleaner._extract(archive_path, output_dir)
        except Exception as e:
            # Clean up partial extraction if failed
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            raise e

        # Clean
        ArchiveCleaner._remove_junk(output_dir)

        # Delete source
        try:
            os.remove(archive_path)
        except OSError as e:
            print(f"Warning: Could not delete source file {archive_path}: {e}")

        return output_dir

    @staticmethod
    def _extract(archive_path: str, output_dir: str):
        ext = os.path.splitext(archive_path)[1].lower()
        
        if ext == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(output_dir)
        elif ext == '.rar':
            if rarfile is None:
                raise ImportError("rarfile library is not installed")
            with rarfile.RarFile(archive_path) as rf:
                rf.extractall(output_dir)
        elif ext in ['.tar', '.gz', '.tgz']:
             with tarfile.open(archive_path, 'r:*') as tf:
                tf.extractall(output_dir)
        else:
            raise ValueError(f"Unsupported archive type: {ext}")

    @staticmethod
    def _remove_junk(directory: str):
        for root, dirs, files in os.walk(directory, topdown=False):
            # Remove junk files
            for name in files:
                if name in ArchiveCleaner.JUNK_FILES or any(name.endswith(ext) for ext in ArchiveCleaner.JUNK_EXTENSIONS):
                    file_path = os.path.join(root, name)
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass
            
            # Remove junk directories
            for name in dirs:
                if name in ArchiveCleaner.JUNK_FILES:
                    dir_path = os.path.join(root, name)
                    try:
                        shutil.rmtree(dir_path)
                    except OSError:
                        pass
