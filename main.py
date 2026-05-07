"""Start OptiPC.

The app runs in normal user mode by default.
Only selected actions (like SFC / DISM / CHKDSK) ask Windows for Administrator permission.
"""

import sys

from app import OptiPCApp


def run_smoke_test() -> int:
    """Start the packaged app, build key pages/widgets, and exit."""
    app = None
    try:
        app = OptiPCApp()
        app.withdraw()
        app.update_idletasks()
        for page_name in ("Dashboard", "Cleanup", "Settings", "Reports"):
            app.show_page(page_name)
            app.update_idletasks()
        for widget_key in ("pc_health", "storage_cleanup", "quick_actions"):
            app._create_or_show_widget(widget_key, show_toast=False)
            app.update_idletasks()
        app.hide_all_widgets()
        app.quit_from_tray()
        return 0
    except Exception as exc:
        print(f"OptiPC smoke test failed: {exc}", file=sys.stderr)
        if app is not None:
            try:
                app.destroy()
            except Exception:
                pass
        return 1


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        raise SystemExit(run_smoke_test())
    app = OptiPCApp()
    app.mainloop()
