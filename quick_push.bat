# 快速更新脚本 - 提交并推送
# 用法: .\quick_push.bat [提交说明]

@echo off
chcp 65001 >nul

if "%~1"=="" (
    echo 请输入提交说明:
    set /p COMMIT_MSG=
) else (
    set COMMIT_MSG=%~1
)

echo 正在提交并推送...
git add .
git commit -m "%COMMIT_MSG%"
git push origin main

echo.
echo ✓ 推送完成！
echo.
pause
