"""Start SmartPC Toolkit.

This app runs in normal user mode by default.
Only selected actions (like SFC / DISM / CHKDSK) try to run elevated.
"""

from app import SmartPCToolkitApp


if __name__ == "__main__":
    app = SmartPCToolkitApp()
    app.mainloop()
