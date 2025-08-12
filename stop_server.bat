@echo off
setlocal enabledelayedexpansion
title Church Management System - Stop Server

echo.
echo ========================================================
echo    CHURCH MANAGEMENT SYSTEM - STOP SERVER
echo ========================================================
echo.

:: Check for Django server processes
echo Searching for Django development server processes...

set "FOUND_PROCESS=0"

:: Look for Python processes running Django
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV 2^>nul ^| findstr "python.exe"') do (
    set "PID=%%i"
    set "PID=!PID:"=!"
    
    :: Check if this Python process is running Django
    wmic process where "ProcessId=!PID!" get CommandLine /format:list 2>nul | findstr "manage.py.*runserver" >nul 2>&1
    if !errorlevel! equ 0 (
        echo Found Django server process (PID: !PID!)
        echo Stopping server...
        taskkill /PID !PID! /F >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✓ Server stopped successfully (PID: !PID!)
            set "FOUND_PROCESS=1"
        ) else (
            echo ✗ Failed to stop server process (PID: !PID!)
        )
    )
)

if %FOUND_PROCESS% equ 0 (
    echo No Django development server processes found.
    echo The server may already be stopped.
)

:: Also check for any processes using port 8000
echo.
echo Checking for processes using port 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo Found process using port 8000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        set "PORT_PID=%%a"
        echo Stopping process on port 8000 (PID: !PORT_PID!)
        taskkill /PID !PORT_PID! /F >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✓ Process stopped successfully
        ) else (
            echo ✗ Failed to stop process
        )
    )
) else (
    echo ✓ Port 8000 is free
)

echo.
echo ========================================================
echo Server stop operation completed.
echo.
echo You can now:
echo • Run startup.bat to restart the server
echo • Close this window
echo ========================================================
echo.
echo Press any key to close...
pause >nul
