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


## New in this build

- system tray mode using `pystray`
- closing the main window minimizes OptiPC to the tray (when tray support is available)
- widget positions, sizes, and visibility are saved automatically
- saved widgets restore on the next app launch
- Settings page includes tray shortcuts

### Tray mode

If `pystray` and `Pillow` are installed, OptiPC creates a tray icon with these actions:
- Open OptiPC
- Show Widgets
- Hide Widgets
- Exit

### Saved widget layout

Widget window state is stored here:

`%USERPROFILE%\OptiPCConfig\widget_state.json`

That file keeps:
- x / y position
- width / height
- visible / hidden state

### Install requirements again

Because tray mode is new, run:

```bat
pip install -r requirements.txt
```


## Theming and constants

This build adds:
- toast notifications for success/error actions
- a status bar badge with levels like INFO, SUCCESS, ERROR, BUSY
- a constants/config layer for common text, font sizes, and widget theme colors
- Settings page controls for widget themes:
  - Dark
  - Light
  - Liquid Glass

The widget theme updates live for already-open widgets.

## Why a constants file is a good idea

Yes — creating a constants/config file is the right move.
It helps you keep:
- app name
- font sizes
- status badge colors
- widget theme colors
- default settings

in one place instead of scattering them across many files.


## Final stability notes

This build fixes the widget theme initialization bug that caused errors like:
- `AttributeError: CPUWidget has no attribute percent_label`
- `AttributeError: NetworkSpeedWidget has no attribute download_frame`

Widget behavior in this build:
- a widget opens only once
- clicking the same widget button again brings it to front and shows a toast saying it is already running
- widgets remember size, position, and visibility
- closing the main window minimizes OptiPC to the system tray when tray support is available

A few realistic notes:
- GPU usage depends on the graphics driver and may show `N/A`
- for Microsoft Store publishing, this project still needs store packaging such as MSIX


## App icon

This build includes app icon files in `assets/`:
- `optipc_icon.png`
- `optipc_icon.ico`

The main window tries to use these automatically on Windows.
