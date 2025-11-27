import os
import shutil

def prepare():
    src_dir = "APK_Source"
    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)
    os.makedirs(src_dir)

    # 1. Copy Main App
    print("Copying main.py...")
    shutil.copy2("pizer/mobile_gui.py", os.path.join(src_dir, "main.py"))

    # 2. Copy Library
    print("Copying pizer library...")
    shutil.copytree("pizer", os.path.join(src_dir, "pizer"))

    # 3. Create buildozer.spec
    print("Creating buildozer.spec...")
    spec = """[app]
title = PiZer
package.name = pizer
package.domain = org.pizer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
"""
    with open(os.path.join(src_dir, "buildozer.spec"), "w") as f:
        f.write(spec)

    # 4. Create requirements.txt
    with open(os.path.join(src_dir, "requirements.txt"), "w") as f:
        f.write("kivy\npillow\n")

    print(f"Done! Source prepared in {os.path.abspath(src_dir)}")

if __name__ == "__main__":
    prepare()
