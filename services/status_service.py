
from __future__ import annotations

from typing import Callable, Optional


class StatusService:
    """Shared bottom status bar + optional toast notifications for the whole app."""

    def __init__(self) -> None:
        self._status_callback: Optional[Callable[[str, bool, str], None]] = None
        self._toast_callback: Optional[Callable[[str, str], None]] = None

    def bind(self, callback: Callable[[str, bool, str], None]) -> None:
        self._status_callback = callback

    def bind_toast(self, callback: Callable[[str, str], None]) -> None:
        self._toast_callback = callback

    def set_status(self, message: str, busy: bool = False, level: str = "info", toast: bool = False) -> None:
        if self._status_callback:
            self._status_callback(message, busy, level)
        if toast and self._toast_callback:
            self._toast_callback(message, level)

    def info(self, message: str, toast: bool = False) -> None:
        self.set_status(message, busy=False, level="info", toast=toast)

    def success(self, message: str, toast: bool = True) -> None:
        self.set_status(message, busy=False, level="success", toast=toast)

    def warning(self, message: str, toast: bool = True) -> None:
        self.set_status(message, busy=False, level="warning", toast=toast)

    def error(self, message: str, toast: bool = True) -> None:
        self.set_status(message, busy=False, level="error", toast=toast)

    def busy(self, message: str) -> None:
        self.set_status(message, busy=True, level="busy", toast=False)
