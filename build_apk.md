# How to Build the PiZer APK

Since you are on Windows, the easiest way to convert this Python app into an Android APK is using **Google Colab** (a free Linux cloud computer).

## Step 1: Prepare Your Files
1.  Create a new folder named `PiZer_Mobile_Source`.
2.  Copy these files into it:
    *   `pizer/` (The whole folder)
    *   `pizer/mobile_gui.py` -> Rename this to **`main.py`** (Important!)
    *   `requirements.txt`

## Step 2: Open Google Colab
1.  Go to [Google Colab](https://colab.research.google.com/).
2.  Click **New Notebook**.

## Step 3: Run the Build Commands
Paste this code into the first cell and run it (Play button):

```python
!pip install buildozer cython==0.29.33

!sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev

!buildozer init
```

## Step 4: Upload & Configure
1.  Upload your `main.py` and `pizer` folder to the Colab file area (folder icon on left).
2.  Edit the `buildozer.spec` file that appeared:
    *   Change `title` to **PiZer**
    *   Change `package.name` to **pizer**
    *   Change `package.domain` to **org.pizer**
    *   In `requirements`, add: `python3,kivy,pillow`

## Step 5: Build!
Run this command in a new cell:

```python
!buildozer android debug
```

## Step 6: Download
Once finished, your APK will be in the `bin/` folder!
