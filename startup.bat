@echo off
setlocal enabledelayedexpansion

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%"
set "VENV_DIR=%PROJECT_DIR%venv"
set "SERVER_PORT=8000"
set "SERVER_URL=http://localhost:%SERVER_PORT%"

:: Hide the console window after a brief moment
title Church Management System - Starting...

echo Starting Church Management System...
echo Please wait while we prepare your application...

:: Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo.
    echo ERROR: Virtual environment not found!
    echo Please run installer.bat first to set up the system.
    echo.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: Change to project directory
cd /d "%PROJECT_DIR%"

:: Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to activate virtual environment
    echo Please run installer.bat to reinstall the system.
    echo.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: Check if Django is installed
python -c "import django" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Django not found in virtual environment
    echo Please run installer.bat to reinstall dependencies.
    echo.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: Check if manage.py exists
if not exist "manage.py" (
    echo.
    echo ERROR: manage.py not found in project directory
    echo Please ensure this script is in the Django project root directory.
    echo.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: Check if server is already running on the port
echo Checking if server is already running...

:: Use netstat to check if port is in use
netstat -an | findstr ":%SERVER_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo Server is already running on port %SERVER_PORT%
    echo Opening browser to existing server...
    goto :open_browser
)

:: Check for any Python processes that might be running Django
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo Checking for existing Django processes...

    :: More thorough check - look for Django runserver process
    for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr "python.exe"') do (
        set "PID=%%i"
        set "PID=!PID:"=!"

        :: Check if this Python process is running Django
        wmic process where "ProcessId=!PID!" get CommandLine /format:list 2>nul | findstr "manage.py.*runserver" >nul 2>&1
        if !errorlevel! equ 0 (
            echo Django development server is already running (PID: !PID!)
            echo Opening browser to existing server...
            goto :open_browser
        )
    )
)

echo Starting Django development server...

:: Run database migrations if needed
echo Checking database migrations...
python manage.py migrate --check >nul 2>&1
if %errorlevel% neq 0 (
    echo Applying database migrations...
    python manage.py migrate

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Database migration failed
        echo Please check your database configuration.
        echo.
        echo Press any key to close...
        pause >nul
        exit /b 1
    )
    echo ✓ Database migrations applied successfully
)

:: Collect static files if needed (silently)
python manage.py collectstatic --noinput >nul 2>&1

:: Start Django development server in background
echo Launching server on %SERVER_URL%...

:: Create a VBS script to run Django server without visible window
set "VBS_SCRIPT=%TEMP%\start_django.vbs"
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo WshShell.Run "cmd /c cd /d ""%PROJECT_DIR%"" && ""%VENV_DIR%\Scripts\activate.bat"" && python manage.py runserver %SERVER_PORT%", 0, False >> "%VBS_SCRIPT%"

:: Execute the VBS script to start server in background
cscript //nologo "%VBS_SCRIPT%"

:: Clean up VBS script
if exist "%VBS_SCRIPT%" del "%VBS_SCRIPT%"

:: Wait a moment for server to start
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

:: Verify server started successfully
set "RETRY_COUNT=0"
:check_server
set /a RETRY_COUNT+=1

netstat -an | findstr ":%SERVER_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Server started successfully
    goto :open_browser
)

if %RETRY_COUNT% lss 10 (
    timeout /t 2 /nobreak >nul
    goto :check_server
)

echo.
echo WARNING: Server may not have started properly
echo Attempting to open browser anyway...
echo If the page doesn't load, please check for error messages.

:open_browser
echo Opening Church Management System in your default browser...

:: Open browser to the application
start "" "%SERVER_URL%"

if %errorlevel% neq 0 (
    echo.
    echo Could not open browser automatically.
    echo Please manually open your browser and go to: %SERVER_URL%
    echo.
    echo Press any key to close...
    pause >nul
)

:: Wait a moment to ensure browser opens
timeout /t 3 /nobreak >nul

echo.
echo Church Management System is now running!
echo.
echo • Application URL: %SERVER_URL%
echo • To stop the server: Close this window or press Ctrl+C in any Django terminal
echo • To restart: Run this startup script again
echo.

:: Close the startup script automatically
exit /b 0
