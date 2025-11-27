import shutil
import os

def prepare():
    # Zip the Flutter project
    print("Zipping PiZer_Flutter project...")
    shutil.make_archive("PiZer_Flutter_Source", 'zip', "PiZer_Flutter")
    print(f"Created PiZer_Flutter_Source.zip")

if __name__ == "__main__":
    prepare()
