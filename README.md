# OptiPC

OptiPC is a beginner-friendly Windows utility dashboard built with Python and CustomTkinter.

## Features

- Dashboard with quick actions
- Cleanup page with:
  - Quick Temp Cleanup
  - Deep Cleanup
  - Empty Recycle Bin
- Repair page for SFC, DISM, and CHKDSK
- Recovery page for Windows File Recovery
- Devices page with sound, camera, privacy, and location shortcuts
- Wallpaper tools
- Reports page with battery, network, installed apps, heavy process, and storage health reports
- Floating desktop widgets:
  - CPU
  - RAM
  - GPU
  - Partitions
  - Storage
  - Network Speed

## What changed in this build

- Network Speed widget now uses the same resizable widget base as the other widgets
- Widgets resize from all edges and corners
- Deep Cleanup was added back
- Devices page now includes Location Settings
- Recovery page no longer uses success/error popups
- Cleanup now streams live progress into the output box
- Code structure is cleaner:
  - `services/cleanup_service.py` handles cleanup logic
  - `widgets/base_mini_widget.py` handles shared widget behavior

## Run the project

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Suggested next upgrades

- System tray mode so widgets can stay alive in the background
- Save widget positions and sizes between launches
- Add toast notifications
- Add a dedicated Storage page with device cards
