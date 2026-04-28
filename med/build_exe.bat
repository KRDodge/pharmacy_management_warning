@echo off
setlocal

chcp 65001 >nul
cd /d "%~dp0"

set "APP_NAME=med_tool"
set "DIST_DIR=dist\%APP_NAME%"
set "REQUIREMENTS=requirements.txt"
set "VENV_DIR=.venv-build"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "BUILD_TMP=.tmp-build"
if not exist "%BUILD_TMP%" mkdir "%BUILD_TMP%"
for %%I in ("%BUILD_TMP%") do set "BUILD_TMP_ABS=%%~fI"
set "TEMP=%BUILD_TMP_ABS%"
set "TMP=%BUILD_TMP_ABS%"

call :find_python
if errorlevel 1 goto :fail

if not exist "%VENV_PY%" (
    echo [INFO] Creating build virtual environment...
    %PY_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 goto :fail
)

echo [INFO] Installing/checking build dependencies...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 goto :fail

if exist "%REQUIREMENTS%" (
    "%VENV_PY%" -m pip install -r "%REQUIREMENTS%"
    if errorlevel 1 goto :fail
) else (
    "%VENV_PY%" -m pip install pandas requests pyinstaller
    if errorlevel 1 goto :fail
)

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [INFO] Building %APP_NAME%.exe...
"%VENV_PY%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --name "%APP_NAME%" ^
    --exclude-module tensorflow ^
    --exclude-module torch ^
    --exclude-module torchvision ^
    --exclude-module torchaudio ^
    main.py
if errorlevel 1 goto :fail

if not exist "%DIST_DIR%" (
    echo [ERROR] Dist folder not found: %DIST_DIR%
    goto :fail
)

if exist "HIRA.csv" (
    echo [INFO] Copying HIRA.csv...
    copy /y "HIRA.csv" "%DIST_DIR%\HIRA.csv" >nul
)

if exist "config.ini" (
    echo [INFO] Copying config.ini...
    copy /y "config.ini" "%DIST_DIR%\config.ini" >nul
) else if exist "config.example.ini" (
    echo [INFO] Copying config.example.ini...
    copy /y "config.example.ini" "%DIST_DIR%\config.example.ini" >nul
)

if exist "약국만.csv" (
    echo [INFO] Copying sample input csv...
    copy /y "약국만.csv" "%DIST_DIR%\약국만.csv" >nul
)

echo [INFO] Build complete.
echo [INFO] Output: %DIST_DIR%\%APP_NAME%.exe
echo [INFO] You can also run:
echo        %APP_NAME%.exe --config "config.ini" --input "약국만.csv" --output "약국만_API결과.csv" --hira "HIRA.csv"
goto :end

:find_python
where python >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=python"
    exit /b 0
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 --version >nul 2>nul
    if not errorlevel 1 (
        set "PY_CMD=py -3"
        exit /b 0
    )
)

echo [ERROR] Python was not found. Install Python or add it to PATH.
exit /b 1

:fail
echo [ERROR] Build failed.
pause
exit /b 1

:end
pause
exit /b 0
