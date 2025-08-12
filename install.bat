@echo off
echo 🎵 NasmyTunes CLI - One-Click Installer
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run setup
echo 🚀 Running setup...
python setup.py

echo.
echo 🎉 Installation complete!
echo.
echo To use NasmyTunes:
echo 1. Edit .env file with your Spotify credentials
echo 2. Run: nasmytunes.bat "your_playlist_url"
echo.
pause