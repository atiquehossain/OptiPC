from __future__ import annotations

import re

import customtkinter as ctk

from config.constants import FONT_SIZES, RESPONSIVE_FONT_SIZES

GEOMETRY_PATTERN = re.compile(r"^(\d+)x(\d+)([-+]\d+)([-+]\d+)$")


MIN_FONT_SIZES = {
    "tiny": 8,
    "small": 9,
    "body": 10,
    "label": 10,
    "title": 11,
    "metric": 14,
    "hero": 16,
}

MAX_FONT_SIZES = {
    "tiny": 12,
    "small": 14,
    "body": 17,
    "label": 16,
    "title": 20,
    "metric": 34,
    "hero": 38,
}


def _current_dimension(window, attr_name: str, fallback: int) -> int:
    try:
        match = GEOMETRY_PATTERN.match(str(window.geometry()))
        if match:
            group_index = 1 if attr_name == "winfo_width" else 2
            value = int(match.group(group_index))
            if value > 1:
                return value
    except Exception:
        pass
    try:
        value = int(getattr(window, attr_name)())
    except Exception:
        value = 0
    return value if value > 1 else int(fallback)


def _scale(window) -> float:
    default_width = max(int(getattr(window, "_default_width", 200) or 200), 1)
    default_height = max(int(getattr(window, "_default_height", 200) or 200), 1)
    width = _current_dimension(window, "winfo_width", default_width)
    height = _current_dimension(window, "winfo_height", default_height)
    scale = min(width / default_width, height / default_height)
    return max(0.72, min(scale, 1.25))


def responsive_font_size(window, size_key: str) -> int:
    category = getattr(window, "size_category", "default")
    category_sizes = RESPONSIVE_FONT_SIZES.get(category, RESPONSIVE_FONT_SIZES["default"])
    base_size = category_sizes.get(size_key, FONT_SIZES.get(size_key, 12))
    scaled = int(round(base_size * _scale(window)))
    minimum = MIN_FONT_SIZES.get(size_key, 9)
    maximum = MAX_FONT_SIZES.get(size_key, max(base_size, 12))
    return max(minimum, min(scaled, maximum))


def responsive_spacing(window, default: int, minimum: int = 4) -> int:
    return max(int(minimum), int(round(default * _scale(window))))


def content_wraplength(window, horizontal_padding: int | None = None) -> int:
    default_width = int(getattr(window, "_default_width", 200) or 200)
    width = _current_dimension(window, "winfo_width", default_width)
    if horizontal_padding is None:
        horizontal_padding = int(getattr(window, "PADDING_HORIZONTAL", 12) or 12)
    return max(72, width - (int(horizontal_padding) * 2) - 8)


def tk_font_weight(weight: str) -> str:
    return "bold" if str(weight).lower() in {"bold", "medium", "semibold"} else "normal"


def ensure_label_registry(window) -> list[tuple[ctk.CTkLabel, str, str]]:
    if not hasattr(window, "_responsive_label_specs"):
        window._responsive_label_specs = []
    return window._responsive_label_specs


def configure_label(window, label: ctk.CTkLabel, size_key: str, weight: str) -> None:
    label.configure(
        font=ctk.CTkFont(size=responsive_font_size(window, size_key), weight=tk_font_weight(weight)),
        wraplength=content_wraplength(window),
        justify="center",
    )


def register_label(window, label: ctk.CTkLabel, size_key: str, weight: str) -> ctk.CTkLabel:
    ensure_label_registry(window).append((label, size_key, weight))
    configure_label(window, label, size_key, weight)
    return label


def refresh_labels(window) -> None:
    for label, size_key, weight in list(ensure_label_registry(window)):
        try:
            if label.winfo_exists():
                configure_label(window, label, size_key, weight)
        except Exception:
            pass
