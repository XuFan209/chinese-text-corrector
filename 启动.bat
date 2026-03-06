@echo off
chcp 65001 >nul
title 中文文本纠错系统
color 0A

echo ============================================
echo    中文文本纠错系统
echo ============================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请确保Python已安装并添加到环境变量
    pause
    exit /b 1
)

:: 启动服务
echo 正在启动服务...
echo.
python start.py

pause
