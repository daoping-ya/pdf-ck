@echo off
chcp 65001 >nul
title Configure Port
color 0E

echo ================================
echo   Configure PDF Processor Port
echo ================================
echo.
echo Current port: %PDF_PROCESSOR_PORT%
if "%PDF_PROCESSOR_PORT%"=="" echo Current port: 5000 (default)
echo.

set /p NEW_PORT="Enter new port number (e.g., 9527): "

if "%NEW_PORT%"=="" (
    echo ERROR: Port cannot be empty
    pause
    exit /b 1
)

echo.
echo Setting port to %NEW_PORT%...

REM Update port in config.py
cd /d "%~dp0backend"

REM Create a temporary Python script to update config
echo import re > temp_update_port.py
echo with open('config.py', 'r', encoding='utf-8') as f: >> temp_update_port.py
echo     content = f.read() >> temp_update_port.py
echo content = re.sub(r"PORT = int\(os\.environ\.get\('PDF_PROCESSOR_PORT', \d+\)\)", "PORT = int(os.environ.get('PDF_PROCESSOR_PORT', %NEW_PORT%))", content) >> temp_update_port.py
echo with open('config.py', 'w', encoding='utf-8') as f: >> temp_update_port.py
echo     f.write(content) >> temp_update_port.py
echo print('Port updated successfully!') >> temp_update_port.py

python temp_update_port.py
del temp_update_port.py

echo.
echo ================================
echo   Port configured to: %NEW_PORT%
echo   You can now run start.bat
echo ================================
echo.

pause
