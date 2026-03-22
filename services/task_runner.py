from __future__ import annotations

import threading
from typing import Any, Callable


class TaskRunner:
    """Run a function in a background thread so the UI stays responsive."""

    @staticmethod
    def run(
        task: Callable[[], Any],
        on_success: Callable[[Any], None],
        on_error: Callable[[Exception], None],
        ui_after: Callable[..., str],
    ) -> None:
        def worker() -> None:
            try:
                result = task()
                ui_after(0, on_success, result)
            except Exception as exc:
                ui_after(0, on_error, exc)

        threading.Thread(target=worker, daemon=True).start()
