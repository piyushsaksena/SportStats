@echo off
setlocal enabledelayedexpansion
title SportStats Platform Launcher
color 0F

set "ROOT_DIR=%~dp0"

echo ======================================================================
echo                SPORTSTATS MULTI-SPORT PLATFORM
echo            Next-Gen Sports Analytics & Intelligence 2026
echo ======================================================================
echo.
echo  How would you like to launch SportStats?
echo.
echo  [1] Instant 1-Click Browser Mode (Recommended - No Python needed!)
echo  [2] Full-Stack Server Mode (Starts FastAPI Backend on port 8000)
echo.
echo ======================================================================

set /p CHOICE="Enter choice [1 or 2] (Default is 1): "
if "%CHOICE%"=="" set CHOICE=1

if "%CHOICE%"=="1" (
    echo.
    echo Launching SportStats in your default web browser...
    start "" "%ROOT_DIR%index.html"
    echo Done! The dashboard is now open in your browser.
    timeout /t 3 >nul
    exit /b 0
)

if "%CHOICE%"=="2" (
    echo.
    echo Checking for Python installation...
    set "PYTHON_CMD="
    
    where python >nul 2>nul
    if !errorlevel! equ 0 set "PYTHON_CMD=python"
    
    if "!PYTHON_CMD!"=="" (
        if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
            set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        ) else if exist "C:\Python312\python.exe" (
            set "PYTHON_CMD=C:\Python312\python.exe"
        ) else if exist "C:\Python311\python.exe" (
            set "PYTHON_CMD=C:\Python311\python.exe"
        )
    )

    if "!PYTHON_CMD!"=="" (
        echo.
        echo [NOTICE] Python was not detected in PATH.
        echo Falling back to Instant Browser Mode so you can use the app immediately!
        start "" "%ROOT_DIR%index.html"
        pause
        exit /b 0
    )

    echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
    start "SportStats Backend Server" /min "!PYTHON_CMD!" -m uvicorn sportstats.api.main:app --app-dir "%ROOT_DIR%backend\src" --host 127.0.0.1 --port 8000 --reload

    echo [2/3] Waiting for server initialization...
    timeout /t 2 /nobreak >nul

    echo [3/3] Opening live web application...
    start http://localhost:8000/

    echo.
    echo ======================================================================
    echo  SPORTSTATS PLATFORM IS LIVE & RUNNING!
    echo ======================================================================
    echo  - Web Application:     http://localhost:8000/
    echo  - Interactive Swagger: http://localhost:8000/docs
    echo  - Health Heartbeat:    http://localhost:8000/health
    echo ======================================================================
    echo.
    echo  Keep this console window open while using the platform.
    echo  Press any key to exit when you are done.
    pause >nul
    exit /b 0
)

rem Fallback
start "" "%ROOT_DIR%index.html"
exit /b 0
