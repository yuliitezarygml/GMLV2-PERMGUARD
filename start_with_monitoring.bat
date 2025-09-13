@echo off
title SwaWeb Server Launcher
color 0A

echo.
echo ===============================================
echo        SWAWEB SERVER WITH PERMGUARD MONITORING
echo ===============================================
echo.
echo Starting Flask server and PermGuard monitor...
echo.

REM Проверить наличие Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

REM Проверить наличие файлов
if not exist "app.py" (
    echo ERROR: app.py not found
    pause
    exit /b 1
)

if not exist "permguard_monitor.py" (
    echo ERROR: permguard_monitor.py not found
    pause
    exit /b 1
)

echo Starting Flask server in new window...
start "SwaWeb Flask Server" cmd /k "python app.py"

REM Небольшая пауза чтобы сервер успел запуститься
timeout /t 3 /nobreak >nul

echo Starting PermGuard monitor in new window...
start "PermGuard Monitor" cmd /k "python permguard_monitor.py"

echo.
echo ===============================================
echo Both windows started successfully!
echo.
echo Window 1: Flask Server (http://localhost:5000)
echo Window 2: PermGuard Real-time Monitor
echo.
echo Press any key to close this launcher...
echo ===============================================
pause >nul