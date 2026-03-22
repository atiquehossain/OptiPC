
from __future__ import annotations

import json
from pathlib import Path

from config.constants import DEFAULT_APP_SETTINGS


class AppSettingsService:
    """Save and load app-level user settings."""

    def __init__(self, settings_file: Path) -> None:
        self.settings_file = settings_file
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        self._settings = self._load()

    def _load(self) -> dict:
        if not self.settings_file.exists():
            return dict(DEFAULT_APP_SETTINGS)
        try:
            data = json.loads(self.settings_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                settings = dict(DEFAULT_APP_SETTINGS)
                settings.update(data)
                return settings
        except Exception:
            pass
        return dict(DEFAULT_APP_SETTINGS)

    def save(self) -> None:
        self.settings_file.write_text(
            json.dumps(self._settings, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_appearance_mode(self) -> str:
        return str(self._settings.get("appearance_mode", DEFAULT_APP_SETTINGS["appearance_mode"]))

    def set_appearance_mode(self, mode: str) -> None:
        self._settings["appearance_mode"] = mode
        self.save()

    def get_widget_theme(self) -> str:
        return str(self._settings.get("widget_theme", DEFAULT_APP_SETTINGS["widget_theme"]))

    def set_widget_theme(self, theme_name: str) -> None:
        self._settings["widget_theme"] = theme_name
        self.save()
