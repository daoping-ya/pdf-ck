@echo off
chcp 65001 >nul
title Install pdf2docx
color 0A

echo ================================
echo   Installing pdf2docx
echo   (PDF to Word Converter)
echo ================================
echo.

cd /d "%~dp0backend"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing pdf2docx and pdfplumber...
pip install --no-cache-dir pdf2docx==0.5.6 pdfplumber==0.10.3

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo ================================
echo   Installation complete!
echo   PDF to Word feature is now available
echo ================================
echo.

pause
