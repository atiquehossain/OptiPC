# 🚀 OptiPC - Installation Guide for Your Friend

## 📦 Option 1: Easy Install (Recommended)

**What you need:**
- Windows 10 or Windows 11
- Internet connection

**Step 1: Get Python**
1. Go to https://python.org
2. Click "Downloads"
3. Download the latest Python version
4. **IMPORTANT:** During installation, check the box that says "Add Python to PATH"
5. Complete the installation

**Step 2: Install OptiPC**
1. Download the OptiPC folder
2. Right-click inside the folder and choose "Open in Terminal" or "Open PowerShell here"
3. Type these commands one by one:
   ```
   python -m venv optipc_env
   optipc_env\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

## 🎯 Option 2: Quick Install (Using install.bat)

1. Download the OptiPC folder
2. Double-click the `install.bat` file
3. Follow the on-screen instructions
4. A desktop shortcut will be created automatically

## 🔧 Option 3: Standalone EXE (If Available)

If your friend sent you a single `OptiPC.exe` file:

1. **If it works:** Great! Just run the .exe file
2. **If you get an error:**
   - Try right-clicking and "Run as administrator"
   - Temporarily disable your antivirus
   - Install [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

## ❌ Common Problems & Solutions

### "This app can't run on your PC"
**Solution:** Use Option 1 or 2 above - the standalone .exe might not work on all computers

### "Python command not found"
**Solution:** Install Python first (Step 1 in Option 1) and make sure to check "Add to PATH"

### "pip command not found"
**Solution:** Restart your computer after installing Python, then try again

### Antivirus blocks the program
**Solution:** Add OptiPC to your antivirus exceptions or temporarily disable it

## 🎉 Once Installed

- **Desktop Shortcut:** Look for OptiPC on your desktop
- **Start Menu:** You can also run it by double-clicking `main.py` in the OptiPC folder
- **First Run:** Windows might ask for permission - click "Yes" to allow it

## 🆘 Still Having Problems?

1. Make sure you have Windows 10 or 11
2. Try the "Easy Install" option first
3. Restart your computer after installing Python
4. Ask your friend to send the entire OptiPC folder, not just the .exe file

---

**Need help?** Contact the person who sent you OptiPC!
