@echo off
chcp 65001 >nul
title Install pdfplumber
color 0A

echo ================================
echo   Installing pdfplumber
echo ================================
echo.

cd /d "%~dp0backend"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing pdfplumber...
pip install --no-cache-dir pdfplumber==0.10.3

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo ================================
echo   Installation complete!
echo   You can now use enhanced text extraction
echo ================================
echo.

pause
