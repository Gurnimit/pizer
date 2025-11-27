@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%"
python -m pizer.cli %*
endlocal
