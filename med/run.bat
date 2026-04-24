@echo off
setlocal

chcp 65001 >nul
cd /d "%~dp0"

if not exist "main.py" (
    echo [ERROR] main.py not found.
    pause
    exit /b 1
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 main.py
    set "exit_code=%errorlevel%"
    goto :finish
)

where python >nul 2>nul
if %errorlevel%==0 (
    python main.py
    set "exit_code=%errorlevel%"
    goto :finish
)

echo [ERROR] Python was not found. Install Python or add it to PATH.
set "exit_code=1"

:finish
if not "%exit_code%"=="0" (
    echo.
    echo [ERROR] Execution failed with exit code %exit_code%.
)

pause
exit /b %exit_code%
