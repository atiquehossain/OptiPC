
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config.constants import (
    DEFAULT_WIDGET_HEIGHT,
    DEFAULT_WIDGET_WIDTH,
    LEGACY_WIDGET_DEFAULT_SIZES,
    WIDGET_DEFAULT_SIZE_VERSION,
    WIDGET_SIZE_CATEGORY_BY_KEY,
    WIDGET_SIZES,
)


class WidgetStateService:
    """Save and load widget window state to a JSON file."""

    def __init__(self, state_file: Path) -> None:
        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state: dict[str, Any] = self._load_from_disk()
        if self._migrate_default_widget_sizes():
            self.save()

    def _load_from_disk(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {"widgets": {}, "main_window": {}, "widget_default_size_version": WIDGET_DEFAULT_SIZE_VERSION}
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("widgets", {})
                data.setdefault("main_window", {})
                return data
        except Exception:
            pass
        return {"widgets": {}, "main_window": {}, "widget_default_size_version": WIDGET_DEFAULT_SIZE_VERSION}

    def _migrate_default_widget_sizes(self) -> bool:
        try:
            current_version = int(self._state.get("widget_default_size_version", 0) or 0)
        except Exception:
            current_version = 0
        if current_version >= WIDGET_DEFAULT_SIZE_VERSION:
            return False

        changed = False
        widgets = self._state.setdefault("widgets", {})
        if isinstance(widgets, dict):
            for key, widget in widgets.items():
                if not isinstance(widget, dict):
                    continue
                try:
                    size = (int(widget.get("width")), int(widget.get("height")))
                except Exception:
                    continue
                if size in LEGACY_WIDGET_DEFAULT_SIZES:
                    category = WIDGET_SIZE_CATEGORY_BY_KEY.get(str(key), "default")
                    target_size = WIDGET_SIZES.get(category, WIDGET_SIZES["default"])
                    widget["width"] = int(target_size.get("width", DEFAULT_WIDGET_WIDTH))
                    widget["height"] = int(target_size.get("height", DEFAULT_WIDGET_HEIGHT))
                    changed = True

        self._state["widget_default_size_version"] = WIDGET_DEFAULT_SIZE_VERSION
        return True if changed else current_version != WIDGET_DEFAULT_SIZE_VERSION

    def save(self) -> None:
        self.state_file.write_text(
            json.dumps(self._state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_widget_state(self, key: str) -> dict[str, Any]:
        return dict(self._state.get("widgets", {}).get(key, {}))

    def get_all_widget_states(self) -> dict[str, dict[str, Any]]:
        widgets = self._state.get("widgets", {})
        if not isinstance(widgets, dict):
            return {}
        return {str(key): dict(value) for key, value in widgets.items() if isinstance(value, dict)}

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
