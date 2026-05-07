"""Start OptiPC.

The app runs in normal user mode by default.
Only selected actions (like SFC / DISM / CHKDSK) ask Windows for Administrator permission.
"""

import sys
from pathlib import Path

from app import OptiPCApp


def _snapshot_config_files() -> dict[Path, bytes | None]:
    config_dir = Path.home() / "OptiPCConfig"
    paths = [config_dir / "widget_state.json", config_dir / "app_settings.json"]
    return {path: path.read_bytes() if path.exists() else None for path in paths}


def _restore_config_files(snapshot: dict[Path, bytes | None]) -> None:
    for path, data in snapshot.items():
        try:
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        except Exception:
            pass


def run_smoke_test() -> int:
    """Start the packaged app, build key pages/widgets, and exit."""
    app = None
    config_snapshot = _snapshot_config_files()
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
    finally:
        _restore_config_files(config_snapshot)


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        raise SystemExit(run_smoke_test())
    app = OptiPCApp()
    app.mainloop()
