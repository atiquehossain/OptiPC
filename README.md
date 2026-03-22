# SmartPC Toolkit (Final ZIP)

A beginner-friendly Windows utility app built with Python + customtkinter.

## What this app can do

- Quick cleanup of TEMP files
- Empty Recycle Bin safely
- Open Windows tools and settings
- Run repair tools (SFC / DISM / CHKDSK) with admin prompt when needed
- Recover deleted files using Microsoft's **Windows File Recovery** (`winfr`)
- Show storage / SSD health information
- Set an image as desktop wallpaper
- Generate text reports
- Show a global status bar and loading animation so users know the app is working

## Important notes

- The app **does not run fully as Administrator**.
- Only admin-required actions try to elevate.
- Recovery uses Microsoft's `winfr` tool. Install **Windows File Recovery** from Microsoft Store if you want to use recovery.
- Storage health information depends on your hardware and Windows drivers. Some fields may show `N/A`.

## Install

Open Terminal / Command Prompt in this folder and run:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## File reading order (best for beginners)

1. `main.py`
2. `app.py`
3. `pages/base_page.py`
4. `services/system_service.py`
5. `pages/dashboard_page.py`
6. `pages/cleanup_page.py`
7. `pages/recovery_page.py`
8. `services/storage_health_service.py`
9. `services/wallpaper_service.py`

## Project structure

- `app.py` = main window and page navigation
- `pages/` = each screen of the app
- `services/` = logic that talks to Windows
- `widgets/` = reusable UI components
- `ui/` = sidebar, top bar, bottom status bar

## Admin behavior

These usually need admin permission:
- SFC / DISM / CHKDSK
- some recovery operations

These usually do **not** need admin:
- cleanup UI
- wallpaper change
- reports
- storage info viewing

## Recovery reminder

For deleted file recovery:
- stop using the source drive as much as possible
- save recovered files to a **different drive**
- SSD recovery is less reliable than HDD recovery if deleted space was already overwritten
