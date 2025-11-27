# πzer (PiZer) - Advanced Cyber Defence & Recovery Tool

![PiZer Logo](pizer/assets/logo.png)

**πzer** is a professional-grade utility designed for authorized security testing, password recovery, and archive hygiene. It combines high-performance multithreaded decryption with deep archive inspection capabilities.

> **⚠️ LEGAL DISCLAIMER**: This tool is for **EDUCATIONAL PURPOSES ONLY**. You must only use this tool on files you own or have explicit permission to audit. The developers assume no liability for misuse.

## 🚀 Key Features

### 1. Advanced Password Recovery
*   **Dictionary Attack**: Rapidly test against wordlists.
*   **Brute Force Engine**: 
    *   **Multithreaded**: Uses all available CPU cores (32+ threads) for maximum speed.
    *   **Smart Sequencing**: Automatically tests 1-character, then 2-character, etc., up to infinite length.
    *   **Real-time Feedback**: "Hacker-style" dashboard showing current attempts.

### 2. Archive Inspection
*   **Deep Scan**: View contents of encrypted archives without extracting them.
*   **Metadata Analysis**: Analyze file sizes, compression ratios, and headers.

### 3. Archive Cleaning
*   **Metadata Scrubbing**: Remove identifying metadata from archives.
*   **Junk Removal**: Automatically strip `__MACOSX`, `.DS_Store`, and `Thumbs.db`.
*   **Secure Extraction**: Extract clean files and optionally delete the source.

## 📥 Installation

We provide a professional Windows Installer for easy setup.

1.  Navigate to the `dist` folder.
2.  Run **`PiZer_Setup.exe`**.
3.  Follow the wizard to accept the license and install.
4.  Launch **PiZer** from your Desktop shortcut.

## 🖥️ Usage

### GUI Mode (Recommended)
Launch the app from the Desktop shortcut.
*   **Recovery Tab**: Select your zip, choose attack mode, and click "INITIATE SEQUENCE".
*   **Inspect Tab**: Peek inside archives.
*   **Clean Tab**: Sanitize archives.

### CLI Mode (Command Line)
For power users who prefer the terminal:

```bash
# Brute Force Recovery (Infinite Length)
python -m pizer.cli recover-brute "target.zip" --max-length 0

# Dictionary Recovery
python -m pizer.cli recover "target.zip" --wordlist "passwords.txt"
```

## ⚙️ Technical Details
*   **Engine**: Python 3.13 + Custom ThreadPoolExecutor
*   **Interface**: Tkinter (Custom Dark/Cyan Theme)
*   **Build**: PyInstaller (OneFile + Windowed)

---
*v1.0.1 | © 2025 PiZer Security*
