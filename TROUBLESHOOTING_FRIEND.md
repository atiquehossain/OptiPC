# 🔧 OptiPC Troubleshooting Guide

## ❌ "This app can't run on your PC" Error

This error happens when Windows can't run the .exe file properly. Here are the solutions:

---

## 🎯 SOLUTION 1: Use the Installer (Recommended)

**What you need:**
- The OptiPC folder (not just the .exe file)
- Internet connection

**Steps:**
1. **Install Python first:**
   - Go to https://python.org
   - Download Python 3.8 or newer
   - **IMPORTANT:** Check the box "Add Python to PATH" during installation
   - Restart your computer after installation

2. **Run the installer:**
   - Double-click `install_for_friend.bat` in the OptiPC folder
   - Wait for it to finish (it will install everything needed)
   - A desktop shortcut will be created

3. **Run OptiPC:**
   - Double-click the OptiPC shortcut on your desktop
   - Or run `main.py` from the OptiPC folder

---

## 🔧 SOLUTION 2: Manual Installation

1. **Open Command Prompt:**
   - Press Windows key + R
   - Type `cmd` and press Enter

2. **Navigate to OptiPC folder:**
   ```
   cd Desktop\OptiPC
   ```
   (or wherever you saved the folder)

3. **Run these commands:**
   ```
   python -m venv optipc_env
   optipc_env\Scripts\activate
   pip install customtkinter psutil GPUtil pystray Pillow
   python main.py
   ```

---

## 🛡️ SOLUTION 3: Security Issues

**If antivirus blocks OptiPC:**
1. Temporarily disable your antivirus
2. Run OptiPC once
3. Add OptiPC to antivirus exceptions
4. Re-enable antivirus

**If Windows Defender blocks it:**
1. Click "More info" when blocked
2. Click "Run anyway"
3. Or go to Windows Defender settings and add OptiPC as an exception

---

## 💻 SOLUTION 4: System Requirements

**Make sure you have:**
- Windows 10 or Windows 11
- Python 3.8 or newer (for manual installation)
- At least 100MB free disk space

**Not supported:**
- Windows 7, 8, or older
- macOS or Linux
- ARM-based Windows (some features may not work)

---

## 🆘 Still Having Problems?

**Try these steps:**

1. **Restart your computer** after installing Python
2. **Update Windows** to the latest version
3. **Install Visual C++ Redistributable:**
   - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Install and restart

4. **Check Python installation:**
   - Open Command Prompt
   - Type `python --version`
   - If you see an error, Python isn't installed correctly

5. **Run as Administrator:**
   - Right-click on OptiPC
   - Select "Run as administrator"

---

## 📞 Get Help

If you're still stuck:
1. Take a screenshot of the error message
2. Send it to the person who gave you OptiPC
3. Tell them what you tried from this guide

---

## ✅ Success!

Once OptiPC is running:
- It will create a settings folder in your User directory
- Widgets will remember their positions
- All features should work normally

**Enjoy your optimized Windows experience!** 🎉
