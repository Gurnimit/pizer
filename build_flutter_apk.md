# How to Build the Flutter APK (Cloud Method)

> **🔴 STOP! READ THIS IF YOU GET AN ERROR:**
> If you see `Unexpected token 'P', "PK..."`, it means you tried to **OPEN** the zip file.
> **DO NOT OPEN THE ZIP FILE.**
> You must create a **Blank Notebook** first, and then upload the zip *inside* it.

## Step 1: Create a Blank Notebook
1.  Go to [Google Colab](https://colab.research.google.com/).
2.  Click **New Notebook** (Blue Button).
3.  You should see a blank page with a "Play" button.

## Step 2: Upload the Zip (The Right Way)
1.  Look at the **Left Sidebar**. Click the **Folder Icon** 📁.
2.  It will expand a panel showing `sample_data`.
3.  Click the **Upload Icon** (Paper with Up Arrow) at the top of that panel.
4.  Select **`PiZer_Flutter_Source.zip`**.
5.  Wait for the orange circle to finish uploading.

## Step 3: Build the APK
Copy this code, paste it into the blank cell, and click **Play**:

```python
!git clone https://github.com/flutter/flutter.git -b stable
!/content/flutter/bin/flutter doctor
!/content/flutter/bin/flutter config --enable-web

!unzip -o PiZer_Flutter_Source.zip -d pizer_app
%cd pizer_app
!/content/flutter/bin/flutter build apk --release
```

## Step 4: Download
1.  In that same Left Sidebar, navigate to:
    `pizer_app` > `build` > `app` > `outputs` > `flutter-apk`
2.  Right-click `app-release.apk` and **Download**.
