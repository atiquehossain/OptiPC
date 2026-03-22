from __future__ import annotations

from typing import Callable, Optional


class StatusService:
    """Shared bottom status bar messages for the whole app."""

    def __init__(self) -> None:
        self._callback: Optional[Callable[[str, bool], None]] = None

    def bind(self, callback: Callable[[str, bool], None]) -> None:
        self._callback = callback

    def set_status(self, message: str, busy: bool = False) -> None:
        if self._callback:
            self._callback(message, busy)
