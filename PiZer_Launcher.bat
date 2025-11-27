@echo off
setlocal
title πzer - Zip Defence Tool
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%"

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found in your PATH. Please install Python.
    pause
    exit /b 1
)

:: Run the CLI in interactive mode
python -m pizer.cli

:: Pause only if it crashes or exits unexpectedly (though the loop handles exit)
if %errorlevel% neq 0 (
    echo.
    echo An error occurred.
    pause
)
endlocal
