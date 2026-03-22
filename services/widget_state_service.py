
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class WidgetStateService:
    """Save and load widget window state to a JSON file."""

    def __init__(self, state_file: Path) -> None:
        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state: dict[str, Any] = self._load_from_disk()

    def _load_from_disk(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {"widgets": {}, "main_window": {}}
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("widgets", {})
                data.setdefault("main_window", {})
                return data
        except Exception:
            pass
        return {"widgets": {}, "main_window": {}}

    def save(self) -> None:
        self.state_file.write_text(
            json.dumps(self._state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_widget_state(self, key: str) -> dict[str, Any]:
        return dict(self._state.get("widgets", {}).get(key, {}))

    def set_widget_visible(self, key: str, visible: bool) -> None:
        widgets = self._state.setdefault("widgets", {})
        widget = widgets.setdefault(key, {})
        widget["visible"] = bool(visible)
        self.save()

    def set_widget_geometry(self, key: str, *, x: int, y: int, width: int, height: int) -> None:
        widgets = self._state.setdefault("widgets", {})
        widget = widgets.setdefault(key, {})
        widget.update({
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
        })
        self.save()

    def reset_widget_geometry(self, key: str) -> None:
        """Remove saved geometry for a widget, forcing it to use defaults."""
        widgets = self._state.setdefault("widgets", {})
        if key in widgets:
            widget = widgets[key]
            # Remove geometry fields but keep visibility state
            widget.pop("x", None)
            widget.pop("y", None)
            widget.pop("width", None)
            widget.pop("height", None)
            # If widget is now empty, remove it entirely
            if not widget:
                widgets.pop(key, None)
            self.save()

    def get_main_window_state(self) -> dict[str, Any]:
        return dict(self._state.get("main_window", {}))

    def set_main_window_geometry(self, *, x: int, y: int, width: int, height: int) -> None:
        self._state["main_window"] = {
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
        }
        self.save()
