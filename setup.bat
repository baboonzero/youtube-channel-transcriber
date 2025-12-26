@echo off
REM YouTube Channel Transcriber - Windows Setup Launcher
REM Double-click this file to run the setup wizard

echo ======================================================================
echo         YouTube Channel Transcriber - Setup
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.9 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Show Python version
echo Detected Python:
python --version
echo.

REM Run the setup script
echo Running setup wizard...
echo.
python setup.py

REM Pause at the end so user can read the output
echo.
echo ======================================================================
pause
