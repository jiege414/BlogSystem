@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: .venv not found.
    echo Run: python -m venv .venv
    pause
    exit /b 1
)

set "FLASK_APP=app:create_app"

.venv\Scripts\python.exe -m flask init-db
.venv\Scripts\python.exe -m flask run --debug

pause
