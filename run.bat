@echo off
chcp 65001 >nul
REM Flask博客系统启动脚本
REM 使用虚拟环境中的Python运行应用

echo 正在启动Flask博客系统...
echo.

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\python.exe" (
    echo 错误：虚拟环境不存在！
    echo 请先运行: python -m venv venv
    pause
    exit /b 1
)

REM 使用虚拟环境中的Python运行应用
venv\Scripts\python.exe app.py

pause

