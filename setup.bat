@echo off
setlocal enabledelayedexpansion
title Church Management System - Setup & Management

:: Set colors for better visibility
color 0A

:main_menu
cls
echo.
echo ========================================================
echo    CHURCH MANAGEMENT SYSTEM - SETUP & MANAGEMENT
echo ========================================================
echo.
echo Please select an option:
echo.
echo 1. Install/Setup System (First time installation)
echo 2. Start Church Management System
echo 3. Stop Server
echo 4. Update Dependencies
echo 5. Create/Reset Superuser (admin/admin)
echo 6. Run Initial Data Setup (All Management Commands)
echo 7. Reset Installation (Clean reinstall)
echo 8. View System Status
echo 9. Open Project Folder
echo 0. Exit
echo.
set /p "choice=Enter your choice (0-9): "

if "%choice%"=="1" goto :install
if "%choice%"=="2" goto :start_system
if "%choice%"=="3" goto :stop_server
if "%choice%"=="4" goto :update_deps
if "%choice%"=="5" goto :create_superuser
if "%choice%"=="6" goto :run_management_commands
if "%choice%"=="7" goto :reset_install
if "%choice%"=="8" goto :system_status
if "%choice%"=="9" goto :open_folder
if "%choice%"=="0" goto :exit
goto :main_menu

:install
cls
echo.
echo ========================================================
echo    INSTALLING CHURCH MANAGEMENT SYSTEM
echo ========================================================
echo.
call installer.bat
echo.
echo Press any key to return to main menu...
pause >nul
goto :main_menu

:start_system
cls
echo.
echo ========================================================
echo    STARTING CHURCH MANAGEMENT SYSTEM
echo ========================================================
echo.
call startup.bat
echo.
echo Press any key to return to main menu...
pause >nul
goto :main_menu

:stop_server
cls
echo.
echo ========================================================
echo    STOPPING SERVER
echo ========================================================
echo.
call stop_server.bat
echo.
echo Press any key to return to main menu...
pause >nul
goto :main_menu

:create_superuser
cls
echo.
echo ========================================================
echo    CREATE/RESET SUPERUSER
echo ========================================================
echo.

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"

if not exist "%VENV_DIR%" (
    echo ✗ Virtual environment not found!
    echo Please run installation first (Option 1).
    echo.
    echo Press any key to return to main menu...
    pause >nul
    goto :main_menu
)

echo This will create or reset the admin superuser account:
echo Username: admin
echo Password: admin
echo Email: admin@church.local
echo.
set /p "confirm=Continue? (y/N): "

if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    echo.
    echo Press any key to return to main menu...
    pause >nul
    goto :main_menu
)

echo Activating virtual environment...
cd /d "%PROJECT_DIR%"
pushd "%VENV_DIR%\Scripts"
call activate.bat
popd

echo Running superuser creation script...
python create_superuser.py

echo.
echo Press any key to return to main menu...
pause >nul
goto :main_menu

:run_management_commands
cls
echo.
echo ========================================================
echo    RUN INITIAL DATA SETUP
echo ========================================================
echo.

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"

if not exist "%VENV_DIR%" (
    echo ✗ Virtual environment not found!
    echo Please run installation first (Option 1).
    echo.
    echo Press any key to return to main menu...
    pause >nul
    goto :main_menu
)

echo This will run all management commands to set up initial data:
echo • Respect titles (Mr., Mrs., Rev., etc.)
echo • Family relations (Father, Mother, Son, etc.)
echo • Account categories and types
echo • Income and expense categories
echo.
set /p "confirm=Continue? (y/N): "

if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    echo.
    echo Press any key to return to main menu...
    pause >nul
    goto :main_menu
)

echo Activating virtual environment...
cd /d "%PROJECT_DIR%"
pushd "%VENV_DIR%\Scripts"
call activate.bat
popd

echo.
echo Running congregation management commands...
echo ==========================================

echo Creating respect titles...
python manage.py create_respect_titles

echo Creating family relations...
python manage.py create_relations

echo.
echo Running accounts management commands...
echo =====================================

echo Creating default account categories...
python manage.py create_default_categories

echo Creating income categories...
python manage.py create_income_categories

echo Creating expense categories...
python manage.py create_expense_categories

echo.
echo ✓ All management commands completed!
echo.
echo Press any key to return to main menu...
pause >nul
goto :main_menu

:update_deps
cls
echo.
echo ========================================================
echo    UPDATING DEPENDENCIES
echo ========================================================
echo.

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"

if not exist "%VENV_DIR%" (
    echo ✗ Virtual environment not found!
    echo Please run installation first (Option 1).
    echo.
    echo Press any key to return to main menu...
    pause >nul
    goto :main_menu
)

echo Activating virtual environment...
cd /d "%PROJECT_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

echo Updating pip...
pip install --upgrade pip

echo Updating dependencies...
pip install -r requirements.txt --upgrade

echo ✓ Dependencies updated successfully!
echo.
echo Press any key to return to main menu...
pause >nul
goto :main_menu

:reset_install
cls
echo.
echo ========================================================
echo    RESET INSTALLATION
echo ========================================================
echo.
echo WARNING: This will delete the virtual environment and
echo reinstall everything from scratch.
echo.
set /p "confirm=Are you sure? (y/N): "

if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    echo.
    echo Press any key to return to main menu...
    pause >nul
    goto :main_menu
)

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"

echo Stopping any running servers...
call stop_server.bat >nul 2>&1

echo Removing virtual environment...
if exist "%VENV_DIR%" (
    rmdir /s /q "%VENV_DIR%"
    echo ✓ Virtual environment removed
)

echo Starting fresh installation...
call installer.bat

echo.
echo Press any key to return to main menu...
pause >nul
goto :main_menu

:system_status
cls
echo.
echo ========================================================
echo    SYSTEM STATUS
echo ========================================================
echo.

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo ✓ Python installed: !PYTHON_VERSION!
) else (
    echo ✗ Python not found
)

:: Check virtual environment
if exist "%VENV_DIR%" (
    echo ✓ Virtual environment exists
    
    :: Check Django installation
    pushd "%VENV_DIR%\Scripts"
    call activate.bat
    popd
    python -c "import django; print('✓ Django installed:', django.get_version())" 2>nul
    if %errorlevel% neq 0 (
        echo ✗ Django not found in virtual environment
    )
) else (
    echo ✗ Virtual environment not found
)

:: Check if server is running
netstat -an | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Server is running on port 8000
) else (
    echo ✗ Server is not running
)

:: Check project files
if exist "manage.py" (
    echo ✓ Django project files found
) else (
    echo ✗ Django project files not found
)

if exist "requirements.txt" (
    echo ✓ Requirements file found
) else (
    echo ✗ Requirements file not found
)

echo.
echo Press any key to return to main menu...
pause >nul
goto :main_menu

:open_folder
start "" "%~dp0"
goto :main_menu

:exit
echo.
echo Thank you for using Church Management System!
echo.
pause
exit /b 0
