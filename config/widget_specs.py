from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from config.constants import DEFAULT_WIDGET_HEIGHT, DEFAULT_WIDGET_WIDTH, WIDGET_SIZES


@dataclass(frozen=True)
class WidgetSpec:
    """Single source of truth for a desktop widget's default presentation."""

    key: str
    title: str
    size_category: str = "default"
    accent_key: str = "accent"
    content_style: str = "standard"

    @property
    def size(self) -> dict[str, int]:
        size = WIDGET_SIZES.get(self.size_category, WIDGET_SIZES["default"])
        return {
            "width": int(size.get("width", DEFAULT_WIDGET_WIDTH)),
            "height": int(size.get("height", DEFAULT_WIDGET_HEIGHT)),
        }


_WIDGET_SPECS: dict[str, WidgetSpec] = {
    "cpu": WidgetSpec("cpu", "CPU", "small", "cpu_accent", "metric"),
    "ram": WidgetSpec("ram", "Memory", "small", "ram_accent", "metric"),
    "gpu": WidgetSpec("gpu", "GPU", "small", "gpu_accent", "metric"),
    "clock": WidgetSpec("clock", "Clock", "small", "clock_accent", "clock"),
    "uptime": WidgetSpec("uptime", "Uptime", "small", "runtime_accent", "metric"),
    "pc_health": WidgetSpec("pc_health", "PC Health", "small", "accent", "metric"),
    "battery_health": WidgetSpec("battery_health", "Battery", "small", "accent", "metric"),
    "temperature": WidgetSpec("temperature", "Temperature", "small", "accent", "metric"),
    "network_speed": WidgetSpec("network_speed", "Internet Speed", "small", "accent", "metric_pair"),
    "storage_cleanup": WidgetSpec("storage_cleanup", "Storage Cleanup", "small", "storage_accent", "action"),
    "disk_io": WidgetSpec("disk_io", "Disk I/O", "small", "storage_accent", "chart"),
    "network_quality": WidgetSpec("network_quality", "Network Quality", "small", "accent", "action"),
    "windows_update": WidgetSpec("windows_update", "Windows Update", "small", "runtime_accent", "action"),
    "bluetooth": WidgetSpec("bluetooth", "Bluetooth", "small", "bluetooth_accent", "rings"),
    "storage": WidgetSpec("storage", "Storage", "small", "storage_accent", "meter"),
    "partitions": WidgetSpec("partitions", "Partitions", "small", "storage_accent", "list"),
    "calendar": WidgetSpec("calendar", "Calendar", "small", "calendar_accent", "calendar"),
    "top_processes": WidgetSpec("top_processes", "Top Processes", "small", "accent", "list"),
    "quick_actions": WidgetSpec("quick_actions", "Quick Actions", "small", "accent", "actions"),
    "performance_timeline": WidgetSpec("performance_timeline", "Performance Timeline", "small", "accent", "chart"),
}

WIDGET_SPECS = MappingProxyType(_WIDGET_SPECS)
KNOWN_WIDGET_KEYS = frozenset(_WIDGET_SPECS)


def has_widget_spec(key: str | None) -> bool:
    return str(key or "") in WIDGET_SPECS


def widget_spec(key: str | None) -> WidgetSpec:
    normalized_key = str(key or "").strip()
    if normalized_key in WIDGET_SPECS:
        return WIDGET_SPECS[normalized_key]
    if not normalized_key:
        return WidgetSpec("", "Widget")
    return WidgetSpec(normalized_key, normalized_key.replace("_", " ").title())


def widget_title(key: str | None, fallback: str | None = None) -> str:
    spec = widget_spec(key)
    if spec.key or fallback is None:
        return spec.title
    return fallback


def widget_size_category(key: str | None, fallback: str = "default") -> str:
    spec = widget_spec(key)
    return spec.size_category if spec.key else fallback


def widget_accent_key(key: str | None, fallback: str = "accent") -> str:
    spec = widget_spec(key)
    return spec.accent_key if spec.key else fallback


def widget_default_size(key: str | None, size_category: str | None = None) -> dict[str, int]:
    category = size_category or widget_size_category(key)
    size = WIDGET_SIZES.get(category, WIDGET_SIZES["default"])
    return {
        "width": int(size.get("width", DEFAULT_WIDGET_WIDTH)),
        "height": int(size.get("height", DEFAULT_WIDGET_HEIGHT)),
    }
