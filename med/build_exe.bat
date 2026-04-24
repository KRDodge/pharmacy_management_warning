@echo off
setlocal

chcp 65001 >nul
cd /d "%~dp0"

set "APP_NAME=med_tool"
set "DIST_DIR=dist\%APP_NAME%"

call :find_python
if errorlevel 1 goto :fail

echo [INFO] Checking PyInstaller...
%PY_CMD% -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Installing...
    %PY_CMD% -m pip install pyinstaller
    if errorlevel 1 goto :fail
)

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [INFO] Building %APP_NAME%.exe...
%PY_CMD% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --name "%APP_NAME%" ^
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

if exist "약국만.csv" (
    echo [INFO] Copying sample input csv...
    copy /y "약국만.csv" "%DIST_DIR%\약국만.csv" >nul
)

echo [INFO] Build complete.
echo [INFO] Output: %DIST_DIR%\%APP_NAME%.exe
echo [INFO] You can also run:
echo        %APP_NAME%.exe --input "약국만.csv" --output "약국만_API결과.csv" --hira "HIRA.csv"
goto :end

:find_python
where py >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=py -3"
    exit /b 0
)

where python >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=python"
    exit /b 0
)

echo [ERROR] Python was not found. Install Python or add it to PATH.
exit /b 1

:fail
echo [ERROR] Build failed.
exit /b 1

:end
pause
exit /b 0
