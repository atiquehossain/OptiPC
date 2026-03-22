from __future__ import annotations

from typing import Callable, Optional


class LogService:
    """Simple logger that writes text into the current page's log box."""

    def __init__(self) -> None:
        self._callback: Optional[Callable[[str], None]] = None

    def bind(self, callback: Callable[[str], None]) -> None:
        self._callback = callback

    def write(self, message: str) -> None:
        if self._callback:
            self._callback(message)
