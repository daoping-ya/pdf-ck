# 版本发布脚本 - 推送到GitHub
# 使用方法: .\release.bat [版本号] [更新说明]
# 例如: .\release.bat v1.1.0 "添加PDF转HTML功能"

@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo    PDF工具 - 版本发布
echo ========================================
echo.

:: 检查参数
if "%~1"=="" (
    echo 错误: 请提供版本号
    echo 用法: release.bat [版本号] [更新说明]
    echo 例如: release.bat v1.1.0 "添加新功能"
    pause
    exit /b 1
)

set VERSION=%~1
set MESSAGE=%~2

if "%MESSAGE%"=="" (
    set MESSAGE=Release %VERSION%
)

echo 版本号: %VERSION%
echo 更新说明: %MESSAGE%
echo.

:: 1. 检查Git状态
echo [1/6] 检查Git状态...
git status
echo.

:: 2. 添加所有修改
echo [2/6] 添加所有修改...
git add .

:: 3. 提交修改
echo [3/6] 提交修改...
git commit -m "release: %MESSAGE%"

:: 4. 创建标签
echo [4/6] 创建版本标签...
git tag -a %VERSION% -m "%MESSAGE%"

:: 5. 推送代码
echo [5/6] 推送到GitHub...
git push origin main

:: 6. 推送标签
echo [6/6] 推送标签...
git push origin %VERSION%

echo.
echo ========================================
echo    ✓ 版本 %VERSION% 发布成功！
echo ========================================
echo.
echo GitHub仓库: https://github.com/daoping-ya/pdf-ck
echo.
echo 下一步:
echo 1. 在VPS上运行: bash update_vps.sh
echo 2. 或者SSH登录后执行: cd /var/www/pdf-tool ^&^& git pull ^&^& supervisorctl restart pdf-tool
echo.

pause
