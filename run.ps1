# Flask博客系统启动脚本 (PowerShell版本)
# 使用虚拟环境中的Python运行应用

Write-Host "正在启动Flask博客系统..." -ForegroundColor Green
Write-Host ""

# 检查虚拟环境是否存在
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "错误：虚拟环境不存在！" -ForegroundColor Red
    Write-Host "请先运行: python -m venv venv" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 使用虚拟环境中的Python运行应用
& "venv\Scripts\python.exe" app.py

Read-Host "按回车键退出"

