@echo off
chcp 65001 >nul
title PDF Tool Unified Installer
color 0A

echo ===================================================
echo      PDF Processing Tool - Unified Installer
echo ===================================================
echo.
echo This script will set up the environment and install
echo ALL required dependencies for the project.
echo.

cd /d "%~dp0backend"

:: Check if venv exists
if not exist "venv" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        echo Please ensure Python is installed and added to PATH.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Virtual environment already exists.
)

:: Activate venv
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install dependencies
echo [3/3] Installing/Updating dependencies...
echo.
echo Installing core requirements...
pip install --no-cache-dir -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    echo Please check your internet connection.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo      Installation Complete!  SUCCESS
echo ===================================================
echo.
echo You can now run 'start.bat' to launch the application.
echo.
pause
