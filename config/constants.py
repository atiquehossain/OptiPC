
from __future__ import annotations

APP_NAME = "OptiPC"
APP_VERSION = "1.0"

FONT_SIZES = {
    "small": 11,
    "body": 13,
    "label": 14,
    "title": 16,
    "card_title": 20,
    "page_title": 26,
    "metric": 28,
    "hero": 30,
}

STATUS_BADGE_COLORS = {
    "info": {"fg": "#315b83", "text": "#f3f8ff"},
    "success": {"fg": "#1f6f43", "text": "#effff4"},
    "warning": {"fg": "#8a6a16", "text": "#fff8de"},
    "error": {"fg": "#8b2e2e", "text": "#fff1f1"},
    "busy": {"fg": "#1f4f8b", "text": "#eef6ff"},
}

WIDGET_THEMES = {
    "dark": {
        "window_bg": "#141922",
        "container": "#222831",
        "panel": "#2b313c",
        "text": "#f4f7fb",
        "muted": "#a9b4c2",
        "accent": "#4f9cff",
        "button": "#313a46",
        "button_hover": "#405063",
        "progress_track": "#1f2630",
        "alpha": 1.0,
    },
    "light": {
        "window_bg": "#edf3f9",
        "container": "#ffffff",
        "panel": "#f2f6fb",
        "text": "#102033",
        "muted": "#5f6c7b",
        "accent": "#2f6fed",
        "button": "#dfe7f0",
        "button_hover": "#d2dde8",
        "progress_track": "#d6dee8",
        "alpha": 1.0,
    },
    "glass": {
        "window_bg": "#0e1620",
        "container": "#162433",
        "panel": "#21384d",
        "text": "#edf8ff",
        "muted": "#b8d0e0",
        "accent": "#7dd3fc",
        "button": "#24445d",
        "button_hover": "#315d7d",
        "progress_track": "#183041",
        "alpha": 0.95,
    },
}

DEFAULT_APP_SETTINGS = {
    "appearance_mode": "Dark",
    "widget_theme": "dark",
}
