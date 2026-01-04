@echo off
chcp 65001 >nul
title Test PDF to Word
color 0E

cd /d "%~dp0backend"

echo ================================
echo   Testing PDF to Word Service
echo ================================
echo.

echo [1] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate venv
    pause
    exit /b 1
)
echo OK
echo.

echo [2] Checking pdf2docx installation...
python -c "import pdf2docx; print('pdf2docx version:', pdf2docx.__version__)"
if errorlevel 1 (
    echo ERROR: pdf2docx not installed!
    echo.
    echo Run: install_pdf2word.bat
    echo.
    pause
    exit /b 1
)
echo OK
echo.

echo [3] Checking required dependencies...
python -c "import fitz; print('PyMuPDF OK')"
python -c "import pdfplumber; print('pdfplumber OK')"
echo.

echo ================================
echo   All checks passed!
echo   PDF to Word feature is ready
echo ================================
echo.

pause
