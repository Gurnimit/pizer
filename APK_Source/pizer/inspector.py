import zipfile
import os
try:
    import rarfile
except ImportError:
    rarfile = None

class FileInspector:
    @staticmethod
    def inspect(file_path):
        """
        Inspects a file and returns a list of its contents.
        Returns a list of tuples: (filename, file_size)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".zip":
            return FileInspector._inspect_zip(file_path)
        elif ext == ".rar":
            return FileInspector._inspect_rar(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _inspect_zip(file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                return [(info.filename, info.file_size) for info in zf.infolist()]
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file")

    @staticmethod
    def _inspect_rar(file_path):
        if rarfile is None:
            raise ImportError("rarfile library is not installed")
        
        try:
            with rarfile.RarFile(file_path) as rf:
                return [(info.filename, info.file_size) for info in rf.infolist()]
        except rarfile.Error as e:
             raise ValueError(f"Error reading RAR file: {e}")
        except Exception as e:
             # rarfile might raise other exceptions if unrar is missing
             if "unrar" in str(e).lower():
                 raise EnvironmentError("Unrar not found. Please ensure unrar is installed and in your PATH.")
             raise e
