@echo off
chcp 65001 >nul
title PDF Tool - Starting...
color 0A

cd /d "%~dp0backend"

echo ===================================================
echo      PDF Processing Tool - Startup Script
echo ===================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

:: 2. Check/Create Virtual Environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: 3. Activate Virtual Environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: 4. Check Dependencies (Simple check)
python -c "import flask, pdf2docx, pdfplumber" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

:: 5. Start Application
echo.
echo [INFO] Starting server on port 5000...
echo [INFO] Opening browser...
start http://localhost:5000

:: Set default port explicitly
set PDF_PROCESSOR_PORT=5000

python app.py

echo.
echo [INFO] Server stopped.
pause
