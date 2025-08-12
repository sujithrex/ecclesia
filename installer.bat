@echo off
setlocal enabledelayedexpansion
title Church Management System - Installer

:: Set colors for better visibility
color 0A

echo.
echo ========================================================
echo    CHURCH MANAGEMENT SYSTEM - INSTALLER
echo ========================================================
echo.
echo This installer will set up your Church Management System
echo by installing Python, creating a virtual environment,
echo and installing all required dependencies.
echo.
echo Please ensure you have an active internet connection.
echo.
pause

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%"
set "VENV_DIR=%PROJECT_DIR%venv"
set "PYTHON_INSTALLER=%TEMP%\python-installer.exe"

echo.
echo [1/6] Checking for Python installation...
echo ========================================================

:: Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python is already installed
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo   Version: !PYTHON_VERSION!
    goto :check_venv
)

echo ✗ Python not found. Downloading and installing Python...

:: Download Python installer
echo.
echo [2/6] Downloading Python installer...
echo ========================================================
echo Please wait while we download the latest Python installer...

:: Use PowerShell to download Python installer
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { $response = Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing; Write-Host 'Download completed successfully' } catch { Write-Host 'Download failed:' $_.Exception.Message; exit 1 } }"

if %errorlevel% neq 0 (
    echo.
    echo ✗ ERROR: Failed to download Python installer
    echo   Please check your internet connection and try again.
    echo   You can also manually download Python from https://python.org
    echo.
    goto :error_exit
)

echo ✓ Python installer downloaded successfully

:: Install Python
echo.
echo [3/6] Installing Python...
echo ========================================================
echo Installing Python... This may take a few minutes.
echo Please follow any prompts that appear.

"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Wait for installation to complete and refresh PATH
timeout /t 10 /nobreak >nul
call refreshenv.cmd >nul 2>&1

:: Verify Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ✗ ERROR: Python installation failed or PATH not updated
    echo   Please restart your command prompt and try again.
    echo   Or manually install Python from https://python.org
    echo.
    goto :error_exit
)

echo ✓ Python installed successfully
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo   Version: !PYTHON_VERSION!

:: Clean up installer
if exist "%PYTHON_INSTALLER%" del "%PYTHON_INSTALLER%"

:check_venv
echo.
echo [4/6] Setting up virtual environment...
echo ========================================================

:: Check if virtual environment already exists
if exist "%VENV_DIR%" (
    echo ✓ Virtual environment already exists at: %VENV_DIR%
    goto :install_deps
)

echo Creating virtual environment...
cd /d "%PROJECT_DIR%"
python -m venv venv

if %errorlevel% neq 0 (
    echo.
    echo ✗ ERROR: Failed to create virtual environment
    echo   Please ensure Python is properly installed.
    echo.
    goto :error_exit
)

echo ✓ Virtual environment created successfully

:install_deps
echo.
echo [5/6] Installing project dependencies...
echo ========================================================

:: Activate virtual environment and install dependencies
cd /d "%PROJECT_DIR%"
call venv\Scripts\activate.bat

if not exist "requirements.txt" (
    echo.
    echo ✗ ERROR: requirements.txt not found in project directory
    echo   Please ensure this installer is in the same directory as your Django project.
    echo.
    goto :error_exit
)

echo Installing dependencies from requirements.txt...
echo This may take several minutes...

pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ✗ ERROR: Failed to install some dependencies
    echo   Please check your internet connection and requirements.txt file.
    echo.
    goto :error_exit
)

echo ✓ All dependencies installed successfully

echo.
echo [6/8] Setting up Django database...
echo ========================================================

echo Running database migrations...
python manage.py migrate

if %errorlevel% neq 0 (
    echo.
    echo ✗ ERROR: Database migration failed
    echo   Please check your Django settings and database configuration.
    echo.
    goto :error_exit
)

echo ✓ Database migrations completed successfully

echo.
echo [7/8] Creating superuser account...
echo ========================================================

echo Creating admin superuser account...
echo Username: admin
echo Password: admin

:: Method 1: Try using Django management command with environment variables
set DJANGO_SUPERUSER_USERNAME=admin
set DJANGO_SUPERUSER_EMAIL=admin@church.local
set DJANGO_SUPERUSER_PASSWORD=admin

python manage.py createsuperuser --noinput >nul 2>&1

if %errorlevel% equ 0 (
    echo ✓ Superuser created successfully
    echo   Username: admin
    echo   Password: admin
    echo   Email: admin@church.local
) else (
    echo Method 1 failed, trying alternative method...

    :: Method 2: Use custom Python script
    python create_superuser.py

    if %errorlevel% neq 0 (
        echo.
        echo ⚠ Warning: Could not create superuser automatically
        echo   You can create one manually later using: python manage.py createsuperuser
        echo   Or run: python create_superuser.py
        echo.
    )
)

echo.
echo [8/10] Running initial data setup...
echo ========================================================

echo Setting up congregation data...

:: Run congregation management commands
echo Creating respect titles...
python manage.py create_respect_titles

if %errorlevel% neq 0 (
    echo ⚠ Warning: Could not create respect titles automatically
    echo   You may need to run this manually: python manage.py create_respect_titles
) else (
    echo ✓ Respect titles created successfully
)

echo Creating family relations...
python manage.py create_relations

if %errorlevel% neq 0 (
    echo ⚠ Warning: Could not create family relations automatically
    echo   You may need to run this manually: python manage.py create_relations
) else (
    echo ✓ Family relations created successfully
)

echo Setting up accounts data...

:: Run accounts management commands
echo Creating default account categories...
python manage.py create_default_categories

if %errorlevel% neq 0 (
    echo ⚠ Warning: Could not create default categories automatically
    echo   You may need to run this manually: python manage.py create_default_categories
) else (
    echo ✓ Default account categories created successfully
)

echo Creating income categories...
python manage.py create_income_categories

if %errorlevel% neq 0 (
    echo ⚠ Warning: Could not create income categories automatically
    echo   You may need to run this manually: python manage.py create_income_categories
) else (
    echo ✓ Income categories created successfully
)

echo Creating expense categories...
python manage.py create_expense_categories

if %errorlevel% neq 0 (
    echo ⚠ Warning: Could not create expense categories automatically
    echo   You may need to run this manually: python manage.py create_expense_categories
) else (
    echo ✓ Expense categories created successfully
)

echo.
echo [9/10] Collecting static files...
echo ========================================================

echo Collecting static files...
python manage.py collectstatic --noinput >nul 2>&1

if %errorlevel% neq 0 (
    echo ⚠ Warning: Could not collect static files
    echo   This may affect styling but won't prevent the system from working
) else (
    echo ✓ Static files collected successfully
)

echo.
echo [10/10] Creating desktop shortcut...
echo ========================================================

:: Create desktop shortcut using PowerShell
set "SHORTCUT_NAME=Church Management System"
set "STARTUP_SCRIPT=%PROJECT_DIR%startup.bat"
set "DESKTOP=%USERPROFILE%\Desktop"

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%.lnk'); $Shortcut.TargetPath = '%STARTUP_SCRIPT%'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'Launch Church Management System'; $Shortcut.Save()}"

if %errorlevel% equ 0 (
    echo ✓ Desktop shortcut created: %SHORTCUT_NAME%.lnk
) else (
    echo ⚠ Warning: Could not create desktop shortcut
    echo   You can manually create a shortcut to: %STARTUP_SCRIPT%
)

echo.
echo ========================================================
echo    INSTALLATION COMPLETED SUCCESSFULLY!
echo ========================================================
echo.
echo Your Church Management System has been installed and configured.
echo.
echo What was installed:
echo • Python !PYTHON_VERSION!
echo • Virtual environment at: %VENV_DIR%
echo • All project dependencies
echo • Database with migrations applied
echo • Admin superuser account created
echo • Congregation data (respect titles, family relations)
echo • Accounts data (categories, income/expense types)
echo • Static files collected
echo • Desktop shortcut: %SHORTCUT_NAME%
echo.
echo ADMIN LOGIN CREDENTIALS:
echo • Username: admin
echo • Password: admin
echo • Email: admin@church.local
echo.
echo To start the system:
echo 1. Double-click the desktop shortcut, OR
echo 2. Run startup.bat from the project directory
echo.
echo The system will be available at: http://localhost:8000
echo Admin panel: http://localhost:8000/admin
echo.
echo Press any key to close this installer...
pause >nul
goto :eof

:error_exit
echo.
echo ========================================================
echo    INSTALLATION FAILED
echo ========================================================
echo.
echo Please review the error messages above and try again.
echo If problems persist, please contact technical support.
echo.
echo Press any key to close...
pause >nul
exit /b 1
