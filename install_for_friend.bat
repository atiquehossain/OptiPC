@echo off
title OptiPC Installation
color 0A

echo ========================================
echo           OptiPC Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python first:
    echo 1. Go to https://python.org
    echo 2. Click "Downloads"
    echo 3. Download and install Python
    echo 4. IMPORTANT: Check "Add Python to PATH"
    echo.
    echo After installing Python, run this file again.
    echo.
    pause
    exit /b 1
)

echo Python found! Continuing installation...
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv optipc_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating environment...
call optipc_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate environment
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing required packages...
pip install customtkinter psutil GPUtil pystray Pillow
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

REM Create desktop shortcut
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\OptiPC.lnk
set TARGET=%CD%\optipc_env\Scripts\python.exe
set ARGS=%CD%\main.py
set WORKDIR=%CD%
set ICON=%CD%\assets\optipc_icon.ico

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%TARGET%'; $Shortcut.Arguments = '%ARGS%'; $Shortcut.WorkingDirectory = '%WORKDIR%'; $Shortcut.IconLocation = '%ICON%'; $Shortcut.Save()"

echo.
echo ========================================
echo        INSTALLATION COMPLETE!
echo ========================================
echo.
echo OptiPC has been installed successfully!
echo.
echo You can now:
echo 1. Double-click the OptiPC shortcut on your desktop
echo 2. Or run main.py from this folder
echo.
echo The shortcut will automatically use the correct Python environment.
echo.
pause
