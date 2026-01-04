@echo off
chcp 65001 >nul
title Simple Test
color 0E

cd /d "%~dp0backend"

echo Testing Python imports...
echo.

call venv\Scripts\activate.bat 2>nul

python -c "print('Python OK')"
python -c "import flask; print('Flask OK')"
python -c "import fitz; print('PyMuPDF OK')"
python -c "import pikepdf; print('pikepdf OK')"
python -c "from PIL import Image; print('Pillow OK')"

echo.
echo If you see errors above, run: pip install Flask PyMuPDF pikepdf Pillow
echo.

pause
