@echo off
chcp 65001 >nul
title 修复虚拟环境并启动
color 0E

echo ========================================
echo   PDF工具 - 虚拟环境修复脚本
echo ========================================
echo.

cd /d "%~dp0backend"

:: 检查venv是否存在
if exist "venv" (
    echo [1/4] 发现旧的虚拟环境,正在删除...
    rmdir /s /q venv
    echo       ✓ 已删除旧环境
) else (
    echo [1/4] 未发现旧虚拟环境
)

echo.
echo [2/4] 创建新的虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo       ✗ 创建失败!
    echo.
    echo 请确认:
    echo 1. Python已正确安装
    echo 2. Python版本 ^>= 3.8
    pause
    exit /b 1
)
echo       ✓ 虚拟环境创建成功

echo.
echo [3/4] 安装依赖包(可能需要1-2分钟)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo       ✗ 依赖安装失败!
    pause
    exit /b 1
)
echo       ✓ 依赖安装完成

echo.
echo [4/4] 验证关键库...
python -c "import flask, fitz, pdf2docx, magic" >nul 2>&1
if errorlevel 1 (
    echo       ✗ 验证失败!
    echo.
    echo 关键库导入失败,请检查错误信息
    python -c "import flask, fitz, pdf2docx, magic"
    pause
    exit /b 1
)
echo       ✓ 所有关键库验证通过

echo.
echo ========================================
echo   环境修复完成! 正在启动应用...
echo ========================================
echo.

timeout /t 2 >nul

:: 启动应用
echo [启动] PDF在线处理工具
echo.
start http://localhost:5000
python app.py

pause
