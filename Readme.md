# Church Management System - Windows Installation Guide

## Quick Start

### For First-Time Installation

1. **Download the project files** to a folder on your computer (e.g., `C:\ChurchManagement\`)

2. **Run the installer**:
   - Double-click `installer.bat`
   - Follow the on-screen instructions
   - The installer will automatically:
     - Download and install Python if needed
     - Create a virtual environment
     - Install all required dependencies
     - Create a desktop shortcut

3. **Start the application**:
   - Double-click the desktop shortcut "Church Management System", OR
   - Double-click `startup.bat` in the project folder

4. **Access the system**:
   - Your web browser will automatically open to `http://localhost:8000`
   - If it doesn't open automatically, manually navigate to that URL

5. **Admin Access**:
   - Admin panel: `http://localhost:8000/admin`
   - Username: `admin`
   - Password: `admin`
   - Email: `admin@church.local`

## What the Scripts Do

### installer.bat
- **Checks for Python**: Downloads and installs Python 3.11.7 if not present
- **Creates Virtual Environment**: Isolates project dependencies
- **Installs Dependencies**: Downloads all required Python packages
- **Creates Desktop Shortcut**: For easy access to the application
- **Creates Admin User**: Automatically sets up admin/admin superuser account
- **Database Setup**: Runs migrations and prepares the database
- **Error Handling**: Provides clear error messages and solutions

### startup.bat
- **Activates Environment**: Ensures correct Python environment is used
- **Checks Server Status**: Detects if Django server is already running
- **Starts Server**: Launches Django development server in background
- **Opens Browser**: Automatically navigates to the application
- **Auto-closes**: Exits after successfully launching the application

## System Requirements

- **Operating System**: Windows 7 or later
- **Internet Connection**: Required for initial installation only
- **Disk Space**: Approximately 500MB for Python and dependencies
- **RAM**: Minimum 2GB recommended
- **Browser**: Any modern web browser (Chrome, Firefox, Edge, Safari)

## Troubleshooting

### Common Issues and Solutions

#### "Python not found" error
- **Solution**: Run `installer.bat` as Administrator
- **Alternative**: Manually install Python from https://python.org and ensure "Add to PATH" is checked

#### "Virtual environment creation failed"
- **Solution**: Delete the `venv` folder and run `installer.bat` again
- **Check**: Ensure you have write permissions in the project directory

#### "Dependencies installation failed"
- **Cause**: Usually internet connectivity issues
- **Solution**: Check internet connection and run `installer.bat` again
- **Alternative**: Try running from a different network

#### "Server won't start" or "Port 8000 in use"
- **Solution**: 
  1. Open Task Manager
  2. End any `python.exe` processes
  3. Run `startup.bat` again
- **Alternative**: Restart your computer

#### "Browser doesn't open automatically"
- **Solution**: Manually open your browser and go to `http://localhost:8000`
- **Check**: Ensure you have a default browser set in Windows

#### "Page not loading" in browser
- **Wait**: Server may still be starting (wait 30-60 seconds)
- **Check**: Look for error messages in any open command windows
- **Restart**: Close all windows and run `startup.bat` again

#### "Can't log in to admin panel"
- **Default Credentials**:
  - URL: `http://localhost:8000/admin`
  - Username: `admin`
  - Password: `admin`
- **Reset Admin User**: Run `setup.bat` and choose option 5 to recreate the admin user
- **Manual Creation**: Use `python manage.py createsuperuser` in the virtual environment

### Advanced Troubleshooting

#### Manual Server Start
If the automatic startup fails, you can start the server manually:

1. Open Command Prompt in the project directory
2. Run these commands:
   ```batch
   venv\Scripts\activate
   python manage.py runserver
   ```
3. Open browser to `http://localhost:8000`

#### Checking Installation
To verify your installation:

1. Open Command Prompt in project directory
2. Run: `venv\Scripts\activate`
3. Run: `python --version` (should show Python 3.11.x)
4. Run: `pip list` (should show Django and other packages)

#### Reinstalling
If you need to completely reinstall:

1. Delete the `venv` folder
2. Run `installer.bat` again

## File Structure

```
ChurchManagement/
├── installer.bat          # Installation script
├── startup.bat           # Application launcher
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
├── venv/                # Virtual environment (created by installer)
├── core/                # Django project settings
├── reports/             # Reports module
├── congregation/        # Congregation management
├── accounts/           # Financial accounts
├── web/                # Web interface
└── templates/          # HTML templates
```

## Security Notes

- The application runs locally on your computer only
- No data is sent to external servers (except during installation)
- The development server is not suitable for production use
- For production deployment, consult a Django deployment guide

## Support

If you encounter issues not covered in this guide:

1. Check that all files are in the same directory
2. Ensure you have administrator privileges
3. Try running the installer as Administrator
4. Check Windows Event Viewer for system errors
5. Contact your system administrator or technical support

## Updates

To update the system:
1. Download new project files
2. Replace old files (keep the `venv` folder)
3. Run `installer.bat` to update dependencies if needed

---

**Note**: This installation is designed for development and testing purposes. For production use in a church environment, consider proper web hosting and security measures.
