"""Start OptiPC.

The app runs in normal user mode by default.
Only selected actions (like SFC / DISM / CHKDSK) ask Windows for Administrator permission.
"""

from app import OptiPCApp


if __name__ == "__main__":
    app = OptiPCApp()
    app.mainloop()
