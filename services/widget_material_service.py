from __future__ import annotations

from functools import lru_cache
from pathlib import Path


ACCENT_KEYS = (
    "cpu_accent",
    "ram_accent",
    "gpu_accent",
    "storage_accent",
    "calendar_accent",
    "clock_accent",
    "runtime_accent",
    "bluetooth_accent",
)

WIDGET_COLOR_MODE_LABELS = {
    "automatic": "Automatic",
    "full_color": "Full Color",
    "monochrome": "Monochrome",
    "tinted": "Tinted",
}

WIDGET_COLOR_MODE_VALUES = {label: key for key, label in WIDGET_COLOR_MODE_LABELS.items()}


def normalize_widget_color_mode(value: str | None) -> str:
    text = str(value or "").strip()
    if text in WIDGET_COLOR_MODE_LABELS:
        return text
    key = text.lower().replace(" ", "_").replace("-", "_")
    return key if key in WIDGET_COLOR_MODE_LABELS else "automatic"


def widget_color_mode_label(value: str | None) -> str:
    return WIDGET_COLOR_MODE_LABELS[normalize_widget_color_mode(value)]


def widget_color_mode_value(label: str | None) -> str:
    return WIDGET_COLOR_MODE_VALUES.get(str(label or "").strip(), normalize_widget_color_mode(label))


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    value = str(color or "#808080").strip().lstrip("#")
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    if len(value) != 6:
        value = "808080"
    try:
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
    except Exception:
        return 128, 128, 128


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(int(channel), 255)) for channel in rgb))


def mix_hex(color: str, other: str, ratio: float) -> str:
    ratio = max(0.0, min(float(ratio), 1.0))
    red, green, blue = _hex_to_rgb(color)
    other_red, other_green, other_blue = _hex_to_rgb(other)
    return _rgb_to_hex(
        (
            round(red * (1.0 - ratio) + other_red * ratio),
            round(green * (1.0 - ratio) + other_green * ratio),
            round(blue * (1.0 - ratio) + other_blue * ratio),
        )
    )


def _relative_luminance(color: str) -> float:
    red, green, blue = (channel / 255 for channel in _hex_to_rgb(color))
    return (0.2126 * red) + (0.7152 * green) + (0.0722 * blue)


@lru_cache(maxsize=8)
def wallpaper_dominant_color(wallpaper_path: str | None) -> str:
    path = Path(str(wallpaper_path or ""))
    if not path.exists() or not path.is_file():
        return "#5a8fd8"
    try:
        from PIL import Image, ImageStat

        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((80, 80))
            stat = ImageStat.Stat(image)
            red, green, blue = (int(channel) for channel in stat.mean[:3])
            return _rgb_to_hex((red, green, blue))
    except Exception:
        return "#5a8fd8"


def _base_material(base_theme: dict, *, appearance: str) -> dict:
    theme = dict(base_theme)
    dark = str(appearance).lower() != "light"
    if dark:
        theme.update(
            {
                "window_bg": "#050506",
                "container": "#1b1b1d",
                "panel": "#29292c",
                "button": "#363639",
                "button_hover": "#46464a",
                "progress_track": "#3a3a3f",
                "text": "#f5f5f7",
                "muted": "#b8b8bf",
                "border": "#4c4c52",
                "edge_highlight": "#ffffff",
                "shadow": "#000000",
                "alpha": 0.96,
                "native_blur": True,
                "blur_alpha": 154,
                "blur_tint": "#1b1b1d",
            }
        )
    else:
        theme.update(
            {
                "window_bg": "#f7f8fa",
                "container": "#f4f6f8",
                "panel": "#ffffff",
                "button": "#eceff3",
                "button_hover": "#dde3ea",
                "progress_track": "#d9dee5",
                "text": "#1d1d1f",
                "muted": "#62656b",
                "border": "#d6dce3",
                "edge_highlight": "#ffffff",
                "shadow": "#9ca3af",
                "alpha": 0.94,
                "native_blur": True,
                "blur_alpha": 118,
                "blur_tint": "#f4f6f8",
            }
        )
    return theme


def _apply_monochrome(theme: dict, *, appearance: str) -> dict:
    dark = str(appearance).lower() != "light"
    accent = "#dedee3" if dark else "#59616d"
    theme.update(
        {
            "accent": accent,
            "calendar_accent": accent,
            "clock_accent": accent,
            "runtime_accent": "#b6b6bd" if dark else "#6f7784",
            "material_mode": "monochrome",
        }
    )
    for key in ACCENT_KEYS:
        theme[key] = accent
    return theme


def _apply_tint(theme: dict, tint: str, *, appearance: str) -> dict:
    dark = str(appearance).lower() != "light"
    readable_tint = mix_hex(tint, "#ffffff" if dark else "#000000", 0.24 if dark else 0.18)
    theme.update(
        {
            "container": mix_hex(theme["container"], tint, 0.22 if dark else 0.14),
            "panel": mix_hex(theme["panel"], tint, 0.18 if dark else 0.10),
            "button": mix_hex(theme["button"], tint, 0.22 if dark else 0.12),
            "button_hover": mix_hex(theme["button_hover"], tint, 0.26 if dark else 0.16),
            "progress_track": mix_hex(theme["progress_track"], tint, 0.16 if dark else 0.10),
            "accent": readable_tint,
            "border": mix_hex(theme["border"], tint, 0.36 if dark else 0.24),
            "blur_tint": mix_hex(theme.get("blur_tint", theme["container"]), tint, 0.24 if dark else 0.18),
            "material_mode": "tinted",
            "wallpaper_tint": tint,
        }
    )
    for key in ACCENT_KEYS:
        theme[key] = readable_tint
    return theme


def resolve_widget_material_theme(
    base_theme: dict,
    *,
    mode: str = "automatic",
    appearance: str = "Dark",
    wallpaper_path: str | None = None,
    active: bool = True,
) -> dict:
    resolved_mode = normalize_widget_color_mode(mode)
    theme = _base_material(base_theme, appearance=appearance)

    if resolved_mode == "automatic":
        resolved_mode = "full_color" if active else "monochrome"

    if resolved_mode == "monochrome":
        return _apply_monochrome(theme, appearance=appearance)
    if resolved_mode == "tinted":
        return _apply_tint(theme, wallpaper_dominant_color(wallpaper_path), appearance=appearance)

    theme["material_mode"] = "full_color"
    theme["wallpaper_tint"] = wallpaper_dominant_color(wallpaper_path)
    if _relative_luminance(theme.get("accent", "#7dd3fc")) < 0.25 and str(appearance).lower() != "light":
        theme["accent"] = mix_hex(theme["accent"], "#ffffff", 0.35)
    return theme
