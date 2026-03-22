
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable

try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover
    pystray = None
    Image = None
    ImageDraw = None


class SystemTrayService:
    """Optional system tray icon using pystray.

    This service is optional. If pystray/Pillow are not available,
    the app still runs normally without tray mode.
    """

    def __init__(self) -> None:
        self.icon = None
        self._thread: threading.Thread | None = None

    @property
    def is_available(self) -> bool:
        return pystray is not None and Image is not None and ImageDraw is not None

    def _create_image(self):
        asset = Path(__file__).resolve().parent.parent / "assets" / "optipc_icon.png"
        if asset.exists() and Image is not None:
            try:
                return Image.open(asset)
            except Exception:
                pass
        image = Image.new("RGB", (64, 64), "#1f6aa5")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((8, 8, 56, 56), radius=10, fill="#1f6aa5", outline="white", width=2)
        draw.text((18, 19), "OP", fill="white")
        return image

    def start(
        self,
        tk_after: Callable[[int, Callable[[], None]], None],
        on_restore: Callable[[], None],
        on_hide_widgets: Callable[[], None],
        on_show_widgets: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> bool:
        if not self.is_available or self.icon is not None:
            return False

        def restore_cb(icon, item):
            tk_after(0, on_restore)

        def hide_widgets_cb(icon, item):
            tk_after(0, on_hide_widgets)

        def show_widgets_cb(icon, item):
            tk_after(0, on_show_widgets)

        def exit_cb(icon, item):
            tk_after(0, on_exit)

        menu = pystray.Menu(
            pystray.MenuItem("Open OptiPC", restore_cb),
            pystray.MenuItem("Show Widgets", show_widgets_cb),
            pystray.MenuItem("Hide Widgets", hide_widgets_cb),
            pystray.MenuItem("Exit", exit_cb),
        )

        self.icon = pystray.Icon("OptiPC", self._create_image(), "OptiPC", menu)

        def runner():
            if self.icon is not None:
                self.icon.run()

        self._thread = threading.Thread(target=runner, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        if self.icon is not None:
            try:
                self.icon.stop()
            except Exception:
                pass
            self.icon = None
