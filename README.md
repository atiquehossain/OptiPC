# OptiPC

[![Download OptiPC](https://img.shields.io/badge/Download-OptiPC-blue?style=for-the-badge)](builds/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)

**OptiPC is your all-in-one Windows toolkit that makes computer maintenance easy!** 

Think of OptiPC as a friendly dashboard that puts all the important Windows tools in one place. Instead of searching through complicated Windows settings, you can clean up your computer, fix problems, and monitor performance with just a few clicks. It's perfect for both beginners who want to keep their PC running smoothly and advanced users who want quick access to system tools.

---

## 🎯 **Quick Download - Ready to Run!**

| Your System | 📦 Download | 📏 Size |
|-------------|---------------|----------|
| **Most PCs** (64-bit) | [OptiPC_x64_Release.zip](builds/OptiPC_x64_Release.zip) | ~20MB |
| **Older PCs** (32-bit) | [OptiPC_x86_Release.zip](builds/OptiPC_x86_Release.zip) | ~18MB |
| **ARM Devices** | [OptiPC_arm64_Release.zip](builds/OptiPC_arm64_Release.zip) | ~19MB |

**🚀 How to run:**
1. Download the ZIP file for your system
2. Extract all files to a folder  
3. Double-click `OptiPC_[version].exe`
4. **That's it!** No installation required!

---

![OptiPC Dashboard](assets/optipc_icon.png)

##  What OptiPC Can Do For You

### ** Main Dashboard - Your Command Center**
The dashboard is like your PC's control panel. From here you can:
- Launch useful tools with one click
- See live updates about your computer's performance
- Switch between different color themes to match your style
- Open floating widgets that stay on your desktop

### ** System Cleanup - Keep Your PC Fast**
Over time, computers collect junk files that slow them down. OptiPC helps you clean up safely:
- **Quick Temp Cleanup**: Removes temporary files that programs leave behind (like browser cache and installation leftovers)
- **Deep Cleanup**: Thorough cleaning that finds and removes more system junk
- **Empty Recycle Bin**: Safely deletes files you've already thrown away
- **Live Progress**: Watch the cleanup happen in real-time, so you know what's being cleaned

### **🔧 System Repair - Fix Windows Problems**
When Windows acts weird or crashes, OptiPC has the right tools:
- **SFC (System File Checker)**: Finds and fixes damaged Windows files that can cause errors
- **DISM**: Repairs the core Windows system itself (more powerful than SFC)
- **CHKDSK**: Checks your hard drive for errors and fixes them to prevent data loss

### ** Data Recovery - Get Your Files Back**
Accidentally deleted something important? OptiPC helps:
- Uses Windows' built-in file recovery tools
- Simple interface that guides you through the recovery process
- No annoying popups - just clear status messages

### ** Device Management - Control Your Hardware**
Quickly access important device settings:
- **Sound Settings**: Adjust volume and audio devices
- **Camera Privacy**: Control which apps can use your camera
- **Privacy Settings**: Manage app permissions and personal data
- **Location Settings**: Control location tracking for apps

### ** Personalization - Make It Yours**
Customize how your computer looks and feels:
- **Wallpaper Tools**: Change your desktop background easily
- **Multiple Themes**: Choose from Dark, Light, or Liquid Glass themes
- **Live Theme Switching**: Change themes instantly without restarting

### ** System Reports - Know Your PC**
Get detailed information about your computer's health:
- **Battery Report**: See how much power you're using and battery condition
- **Network Analysis**: Check your internet connection speed and status
- **Installed Apps**: See all programs on your computer
- **Heavy Processes**: Find apps that are using too much memory or CPU
- **Storage Health**: Check how much space you have left on each drive

### **Desktop Widgets - Live System Monitoring**
These are small windows that stay on your desktop showing live information:
- **CPU Monitor**: Shows how hard your processor is working (useful for gamers and professionals)
- **RAM Monitor**: Displays memory usage (helps you know if you need more RAM)
- **GPU Monitor**: Shows graphics card performance (great for gamers and video editors)
- **Partitions**: View your disk drives and how they're organized
- **Storage**: See how much space is left on each drive
- **Network Speed**: Watch your internet download/upload speeds in real-time
- **Calendar**: Interactive calendar with current date/time display and month navigation
- **Clock**: Large digital clock with date and day display
- **PC Uptime**: Shows how long your computer has been running since boot

### ** Advanced Features**
- **System Tray Mode**: Minimize OptiPC to the system tray so it runs in the background
- **Smart Widgets**: Your widgets remember where you put them and how big they are
- **Helpful Notifications**: Get friendly messages when actions complete (no annoying alerts)
- **Resizable Widgets**: Make widgets bigger or smaller by dragging their edges

## 🚀 Quick Start - Download & Run (No Installation Required!)

### **For Users Who Want to Run OptiPC Immediately**

If you just want to use OptiPC without installing Python or dealing with command lines:

#### **Step 1: Choose Your Version**
| Your Computer | Download This File |
|---------------|-------------------|
| Most modern PCs (64-bit) | [OptiPC_x64_Release.zip](builds/OptiPC_x64_Release.zip) |
| Older PCs (32-bit) | [OptiPC_x86_Release.zip](builds/OptiPC_x86_Release.zip) |
| ARM devices (Surface Pro X) | [OptiPC_arm64_Release.zip](builds/OptiPC_arm64_Release.zip) |

*Not sure? 99% of computers use the **64-bit version**.*

#### **Step 2: Download & Extract**
1. Click the appropriate download link above
2. Save the ZIP file to your Desktop or Downloads folder  
3. Right-click the ZIP file → "Extract All..." or "Extract here"
4. Open the extracted folder

#### **Step 3: Run OptiPC**
1. Double-click `OptiPC_[your_version].exe`
2. **That's it!** No installation needed - fully portable!

#### **What's Included in Each Download?**
```
OptiPC_[version]_Release/
├── OptiPC_[version].exe     # The main program (run this!)
├── README.md                 # Full documentation  
├── README_FRIEND.md           # Quick start guide
├── TROUBLESHOOTING_FRIEND.md # Help if something goes wrong
└── INSTALL.txt              # Installation instructions
```

#### **First Time Setup**
- **Widgets**: Click Dashboard → CPU/RAM/GPU buttons to open desktop widgets
- **Themes**: Go to Settings → Choose Dark/Light/Liquid Glass themes  
- **System Tray**: Close main window to minimize to system tray
- **Resize Widgets**: Drag edges of any widget to make it bigger/smaller

#### **Security Note**
- Windows may show a security warning (this is normal for new programs)
- Click "More info" → "Run anyway" to continue
- OptiPC is 100% safe and open source

---

## How to Install OptiPC (Developer Version)

### What You Need First
- **Windows 10 or Windows 11** (most modern computers have this)
- **Python 3.8 or newer** (don't worry if you're not sure - we'll help you check)

### Step-by-Step Installation

**Step 1: Get the OptiPC files**
- Download the OptiPC folder from GitHub
- Save it somewhere you can find it easily (like your Desktop or Downloads folder)

**Step 2: Open Command Prompt**
- Press the Windows key
- Type "cmd" and press Enter
- A black window will open - this is Command Prompt

**Step 3: Navigate to OptiPC folder**
- In the black window, type: `cd Desktop\OptiPC` (if you saved it to Desktop)
- Or `cd Downloads\OptiPC` (if you saved it to Downloads)
- Press Enter

**Step 4: Create a virtual environment**
This keeps OptiPC separate from other programs on your computer:
```
python -m venv .venv
```
- Press Enter
- Wait for it to finish (you'll see a new folder called ".venv")

**Step 5: Activate the virtual environment**
```
.venv\Scripts\activate
```
- Press Enter
- You should see `(.venv)` at the beginning of your line

**Step 6: Install the needed programs**
```
pip install -r requirements.txt
```
- Press Enter
- This downloads all the tools OptiPC needs to work
- Wait for it to finish (might take a few minutes)

**Step 7: Start OptiPC!**
```
python main.py
```
- Press Enter
- The OptiPC window should open!

##  How to Use OptiPC

### **Getting Started - First Time**
When you first open OptiPC, you'll see:
- **Left sidebar**: Different pages you can visit (Dashboard, Cleanup, Repair, etc.)
- **Main area**: The tools for that page
- **Top bar**: Settings and theme options

**Try this first:**
1. Click on **Dashboard** (it's probably already selected)
2. Click the **CPU** button to open your first widget
3. Drag the widget around your desktop - it stays on top!
4. Try the **RAM** and **Network Speed** widgets too

### **System Tray Mode - Keep OptiPC Running**
Want OptiPC to stay open even when you close the main window?
- If you have the extra packages installed, closing OptiPC will minimize it to the system tray (the area near the clock)
- Right-click the tray icon to:
  - Open OptiPC again
  - Show or hide all your widgets
  - Completely exit the program

### **Managing Your Widgets**
Your widgets are smart - they remember:
- **Where you put them** on your desktop
- **How big** you made them
- **Whether they were visible or hidden**

**To resize widgets:**
- Move your mouse to the edges or corners
- When the cursor changes, click and drag

**To change themes:**
- Go to the Settings page
- Choose Dark, Light, or Liquid Glass
- All your widgets update instantly!

##  How OptiPC Works (Simple Explanation)

### **The Main Parts**
```
OptiPC/
├── main.py                 # The start button - opens the whole program
├── services/               # The "engine room" - does all the hard work
│   ├── cleanup_service.py  # Handles cleaning up your computer
│   └── ...                 # Other service files for different tasks
├── widgets/                # The floating windows you see on desktop
│   ├── base_mini_widget.py # The basic blueprint for all widgets
│   └── ...                 # Individual widget files
├── assets/                 # Pictures and icons
├── requirements.txt        # Shopping list of programs OptiPC needs
└── README.md              # This file you're reading!
```

### **How It All Works Together**
- **Services Layer**: Like workers that do specific jobs (cleaning, repairing, etc.)
- **Widget System**: Creates those floating windows that show live information
- **Settings Manager**: Remembers your preferences and widget positions
- **Theme Engine**: Changes colors and styles without restarting

##  Personalizing OptiPC

### **Choose Your Look**
OptiPC comes with three beautiful themes:
- **Dark Theme**: Easy on the eyes, great for nighttime use
- **Light Theme**: Clean and bright, good for daytime
- **Liquid Glass**: Modern and stylish with glass-like effects

**How to change themes:**
1. Click the **Settings** page
2. Choose your preferred theme
3. All open widgets change instantly!

### **Where Your Settings Are Saved**
- **Widget Positions**: `%USERPROFILE%\OptiPCConfig\widget_state.json`
  - This is a special folder in your User folder
  - Don't delete this file unless you want to reset widget positions
- **App Settings**: Saved in Windows registry (automatic)

##  Troubleshooting - Common Problems

### **"GPU shows N/A"**
- This is normal! GPU monitoring depends on your graphics card driver
- Some graphics cards don't report usage information
- Don't worry - everything else still works perfectly

### **"Widgets don't open or show errors"**
- This was fixed in the latest version
- Make sure you installed all requirements with `pip install -r requirements.txt`
- Try restarting OptiPC

### **"System tray icon doesn't appear"**
- You need two extra packages for tray mode: `pystray` and `Pillow`
- Install them with: `pip install pystray Pillow`
- Restart OptiPC and try again

### **"Python command not found"**
- Python might not be installed or not added to your PATH
- Download Python from python.org and check "Add to PATH" during installation
- Or restart your computer after installing Python

##  What's Coming Next

### **Future Updates We're Working On**
- **Advanced Storage Page**: See all your drives with detailed information cards
- **More Monitoring Tools**: Additional system performance metrics
- **Automatic Maintenance**: Schedule cleanups and repairs automatically
- **Microsoft Store**: Easy installation from Windows Store

### **Want to Help?**
We love suggestions and improvements!
- Found a bug? Tell us about it
- Have an idea for a new feature? We'd love to hear it
- Good at programming? We welcome contributions!

##  Legal Stuff

This project is open source and free to use. It's licensed under the MIT License, which means:
- You can use it for personal or commercial projects
- You can modify it to fit your needs
- You just need to keep the original copyright notice

##  Thank You To

- **CustomTkinter**: For the beautiful modern interface framework
- **Python Community**: For all the amazing libraries that make system monitoring possible
- **Windows Documentation**: For helping us understand Windows internals
- **Beta Testers**: For finding bugs and suggesting improvements

---

##  You're Ready to Go!

**OptiPC is your friendly Windows assistant - keeping your computer clean, fast, and running smoothly.**

Whether you're a complete beginner who just wants to keep their PC in good shape, or an advanced user who wants quick access to powerful tools, OptiPC has something for everyone.

**Happy computing! **

---

*Still have questions? Feel free to ask in our GitHub discussions or check out our troubleshooting section above.*
