@echo off
setlocal
title πzer GUI
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%"

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found in your PATH. Please install Python.
    pause
    exit /b 1
)

:: Run the GUI
start "" /B python -m pizer.gui

endlocal
