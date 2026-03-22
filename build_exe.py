"""
Script to create standalone executable for OptiPC using PyInstaller
This creates a single .exe file that includes all dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_executable():
    """Create standalone executable using PyInstaller"""
    
    # Get current directory
    current_dir = Path(__file__).parent
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=OptiPC",
        "--onefile",  # Create single .exe file
        "--windowed",  # Hide console window
        "--icon=assets/optipc_icon.ico" if Path("assets/optipc_icon.ico").exists() else "",
        "--add-data=assets;assets",  # Include assets folder
        "--hidden-import=customtkinter",
        "--hidden-import=psutil",
        "--hidden-import=GPUtil",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=threading",
        "--hidden-import=json",
        "--hidden-import=os",
        "--hidden-import=sys",
        "--hidden-import=subprocess",
        "--hidden-import=shutil",
        "--hidden-import=pathlib",
        "--hidden-import=datetime",
        "--clean",  # Clean temporary files
        "main.py"
    ]
    
    # Remove empty icon parameter
    cmd = [arg for arg in cmd if arg]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd, cwd=current_dir)
        print("Executable created successfully!")
        
        # Check if executable was created
        exe_path = current_dir / "dist" / "OptiPC.exe"
        if exe_path.exists():
            print(f"Executable location: {exe_path}")
            print(f"File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("Executable not found!")
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    return True

def create_installer_script():
    """Create a simple installation script"""
    installer_script = """@echo off
echo Installing OptiPC...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python first from https://python.org
    echo Make sure to check "Add to PATH" during installation
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv optipc_env

REM Activate virtual environment
echo Activating environment...
call optipc_env\\Scripts\\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\OptiPC.lnk'); $Shortcut.TargetPath = '%CD%\\optipc_env\\Scripts\\python.exe'; $Shortcut.Arguments = '%CD%\\main.py'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = '%CD%\\assets\\optipc_icon.ico'; $Shortcut.Save()"

echo.
echo Installation complete!
echo You can now run OptiPC from the desktop shortcut or by running main.py
echo.
pause
"""
    
    with open("install.bat", "w") as f:
        f.write(installer_script)
    
    print("Created install.bat for easy installation")

if __name__ == "__main__":
    print("OptiPC Executable Builder")
    print("=" * 40)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create executable
    if create_executable():
        # Create installation script
        create_installer_script()
        
        print("\n" + "=" * 40)
        print("Next Steps:")
        print("1. Test the .exe file in dist/OptiPC.exe")
        print("2. If it works, share the .exe file with your friend")
        print("3. If it still doesn't work, share the install.bat file instead")
        print("\nTip: The .exe file might be large (50-100MB) because it includes Python")
        
    input("\nPress Enter to exit...")
