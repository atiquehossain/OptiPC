
from __future__ import annotations

APP_NAME = "OptiPC"
APP_VERSION = "1.0"

# Typography
FONT_SIZES = {
    "small": 11,
    "body": 17,
    "label": 14,
    "title": 17,
    "card_title": 20,
    "page_title": 26,
    "metric": 30,
    "hero": 34,
}

# Responsive Widget Font Sizes (logical points, scaled by widget size)
RESPONSIVE_FONT_SIZES = {
    "default": {
        "tiny": 11,
        "small": 13,
        "body": 17,
        "label": 13,
        "title": 17,
        "metric": 28,
        "hero": 34,
    },
    "small": {
        "tiny": 11,
        "small": 13,
        "body": 17,
        "label": 13,
        "title": 17,
        "metric": 28,
        "hero": 34,
    },
    "medium": {
        "tiny": 11,
        "small": 13,
        "body": 17,
        "label": 15,
        "title": 17,
        "metric": 30,
        "hero": 34,
    },
    "large": {
        "tiny": 11,
        "small": 13,
        "body": 17,
        "label": 15,
        "title": 17,
        "metric": 30,
        "hero": 34,
    },
    "extra_large": {
        "tiny": 12,
        "small": 13,
        "body": 17,
        "label": 16,
        "title": 20,
        "metric": 34,
        "hero": 36,
    },
}

# Modern Design System
COLORS = {
    # Primary Colors
    "primary": {
        "50": "#eff6ff",
        "100": "#dbeafe", 
        "200": "#bfdbfe",
        "300": "#93c5fd",
        "400": "#60a5fa",
        "500": "#3b82f6",  # Main primary
        "600": "#2563eb",
        "700": "#1d4ed8",
        "800": "#1e40af",
        "900": "#1e3a8a",
    },
    
    # Gray Scale
    "gray": {
        "50": "#f8fafc",
        "100": "#f1f5f9",
        "200": "#e2e8f0",
        "300": "#cbd5e1",
        "400": "#94a3b8",
        "500": "#64748b",
        "600": "#475569",
        "700": "#334155",
        "800": "#1e293b",
        "900": "#0f172a",
    },
    
    # Semantic Colors
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    "busy": "#6366f1",
}

# Theme Definitions
THEMES = {
    "light": {
        "background": COLORS["gray"]["50"],
        "surface": "#ffffff",
        "card": "#ffffff",
        "border": COLORS["gray"]["200"],
        "text_primary": COLORS["gray"]["800"],
        "text_secondary": COLORS["gray"]["500"],
        "text_muted": COLORS["gray"]["400"],
        "sidebar_bg": COLORS["gray"]["50"],
        "sidebar_button_bg": "transparent",
        "sidebar_button_hover": COLORS["gray"]["100"],
        "sidebar_button_active": COLORS["primary"]["500"],
        "sidebar_button_text": COLORS["gray"]["800"],
        "sidebar_button_text_active": "#ffffff",
        "topbar_bg": "#ffffff",
        "statusbar_bg": COLORS["gray"]["50"],
        "button_primary": COLORS["primary"]["500"],
        "button_primary_hover": COLORS["primary"]["600"],
        "button_secondary": COLORS["gray"]["100"],
        "button_secondary_hover": COLORS["gray"]["200"],
    },
    
    "dark": {
        "background": COLORS["gray"]["900"],
        "surface": COLORS["gray"]["800"],
        "card": COLORS["gray"]["800"],
        "border": COLORS["gray"]["700"],
        "text_primary": COLORS["gray"]["50"],
        "text_secondary": COLORS["gray"]["400"],
        "text_muted": COLORS["gray"]["500"],
        "sidebar_bg": COLORS["gray"]["900"],
        "sidebar_button_bg": "transparent",
        "sidebar_button_hover": COLORS["gray"]["800"],
        "sidebar_button_active": COLORS["primary"]["800"],
        "sidebar_button_text": COLORS["gray"]["200"],
        "sidebar_button_text_active": "#ffffff",
        "topbar_bg": COLORS["gray"]["900"],
        "statusbar_bg": COLORS["gray"]["800"],
        "button_primary": COLORS["primary"]["800"],
        "button_primary_hover": COLORS["primary"]["700"],
        "button_secondary": COLORS["gray"]["700"],
        "button_secondary_hover": COLORS["gray"]["600"],
    },
}

# Status Badge Colors
STATUS_BADGE_COLORS = {
    "info": {"fg": COLORS["info"], "text": "#ffffff"},
    "success": {"fg": COLORS["success"], "text": "#ffffff"},
    "warning": {"fg": COLORS["warning"], "text": "#ffffff"},
    "error": {"fg": COLORS["error"], "text": "#ffffff"},
    "busy": {"fg": COLORS["busy"], "text": "#ffffff"},
}

# UI Component Specifications
UI_SPECS = {
    "sidebar": {
        "width": 280,
        "corner_radius": 0,
        "button_height": 48,
        "button_corner_radius": 14,
        "header_height": 80,
        "footer_height": 60,
    },
    "topbar": {
        "height": 80,
        "corner_radius": 0,
        "theme_switcher_width": 140,
        "theme_switcher_height": 36,
        "theme_switcher_corner_radius": 12,
    },
    "statusbar": {
        "height": 52,
        "corner_radius": 12,
        "progress_height": 6,
        "progress_corner_radius": 3,
    },
    "cards": {
        "corner_radius": 20,
        "header_padding": 20,
        "content_padding": 20,
        "metric_font_size": 32,
    },
    "buttons": {
        "height": 44,
        "corner_radius": 14,
        "font_size": 13,
    },
}

# Navigation Icons
NAVIGATION_ICONS = {
    "Dashboard": "🏠",
    "Cleanup": "🧹",
    "Repair": "🔧",
    "Recovery": "💾",
    "Devices": "💻",
    "Wallpaper": "🖼️",
    "Reports": "📊",
    "Settings": "⚙️",
    "About Developer": "👨‍💻",
}

# Dashboard Icons
DASHBOARD_ICONS = {
    "CPU Usage": "💻",
    "RAM Total": "🧠",
    "Disk Free": "💾",
    "Windows": "🪟",
    "Quick Actions": "⚡",
    "Live CPU Monitor": "🔥",
    "Activity Log": "📋",
    "Quick Cleanup": "🧹",
    "System Info": "📊",
    "Open Settings": "⚙️",
    "CPU Widget": "💻",
    "RAM Widget": "🧠",
    "GPU Widget": "🎮",
    "Partitions Widget": "📁",
    "Storage Widget": "💾",
    "Calendar Widget": "📅",
    "Net Speed Widget": "🌐",
    "Clock Widget": "🕐",
    "Uptime Widget": "⏱️",
    "PC Health Widget": "❤",
    "Top Processes Widget": "📋",
    "Battery Widget": "🔋",
    "Cleanup Widget": "🧹",
    "Disk IO Widget": "💽",
    "Network Quality Widget": "📡",
    "Windows Update Widget": "🔄",
    "Temperature Widget": "🌡️",
    "Quick Actions Widget": "⚡",
    "Timeline Widget": "📈",
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
        "window_bg": "#050506",
        "container": "#1b1b1d",
        "panel": "#29292c",
        "text": "#f5f5f7",
        "muted": "#b8b8bf",
        "accent": "#dfe7f5",
        "button": "#363639",
        "button_hover": "#46464a",
        "progress_track": "#3a3a3f",
        "alpha": 0.96,
        "border": "#4c4c52",
        "edge_highlight": "#ffffff",
        "shadow": "#000000",
        "native_blur": True,
        "blur_alpha": 154,
        "blur_tint": "#1b1b1d",
    },
    "modern_light": {
        "window_bg": "#f7f8fa",
        "container": "#f4f6f8",
        "panel": "#ffffff",
        "text": "#1d1d1f",
        "muted": "#62656b",
        "accent": "#007aff",
        "button": "#eceff3",
        "button_hover": "#dde3ea",
        "progress_track": "#d9dee5",
        "alpha": 0.94,
        "border": "#d6dce3",
        "edge_highlight": "#ffffff",
        "shadow": "#9ca3af",
        "native_blur": True,
        "blur_alpha": 118,
        "blur_tint": "#f4f6f8",
        "cpu_accent": "#5ac8fa",
        "ram_accent": "#30d158",
        "gpu_accent": "#af52de",
        "storage_accent": "#5856d6",
        "calendar_accent": "#ff3b30",
        "clock_accent": "#007aff",
        "runtime_accent": "#8e8e93",
    },
    "modern_dark": {
        "window_bg": "#050506",
        "container": "#1b1b1d",
        "panel": "#29292c",
        "text": "#f5f5f7",
        "muted": "#b8b8bf",
        "accent": "#0a84ff",
        "button": "#363639",
        "button_hover": "#46464a",
        "progress_track": "#3a3a3f",
        "alpha": 0.96,
        "border": "#4c4c52",
        "edge_highlight": "#ffffff",
        "shadow": "#000000",
        "native_blur": True,
        "blur_alpha": 154,
        "blur_tint": "#1b1b1d",
        "cpu_accent": "#64d2ff",
        "ram_accent": "#40dd8e",
        "gpu_accent": "#bf5af2",
        "storage_accent": "#7c7cff",
        "calendar_accent": "#ff453a",
        "clock_accent": "#0a84ff",
        "runtime_accent": "#a8a8ad",
    },
}

# Standard Widget Dimensions
WIDGET_LOGICAL_POINT_SCALE = 1.0
WIDGET_CONTENT_MARGIN = 16
WIDGET_GRID_GAP = 16

DEFAULT_WIDGET_WIDTH = 170
DEFAULT_WIDGET_HEIGHT = 170

WIDGET_SIZE_CLASSES = {
    "small": {"width": 170, "height": 170, "grid_columns": 2, "grid_rows": 2},
    "medium": {"width": 364, "height": 170, "grid_columns": 4, "grid_rows": 2},
    "large": {"width": 364, "height": 376, "grid_columns": 4, "grid_rows": 4},
    "extra_large": {"width": 745, "height": 376, "grid_columns": 8, "grid_rows": 4},
    "default": {"width": DEFAULT_WIDGET_WIDTH, "height": DEFAULT_WIDGET_HEIGHT, "grid_columns": 2, "grid_rows": 2},
}

WIDGET_SIZES = {
    key: {"width": value["width"], "height": value["height"]}
    for key, value in WIDGET_SIZE_CLASSES.items()
}

WIDGET_DEFAULT_SIZE_VERSION = 7
LEGACY_WIDGET_DEFAULT_SIZES = {
    (200, 200),
    (170, 170),
    (280, 210),
    (364, 170),
    (368, 170),
    (364, 376),
    (320, 220),
    (320, 240),
    (400, 220),
    (400, 420),
    (330, 250),
    (380, 280),
    (320, 230),
    (360, 250),
    (340, 230),
    (350, 260),
    (360, 240),
    (340, 240),
    (360, 270),
    (420, 260),
    (745, 376),
}

# Widget resize limits. These keep desktop widgets usable without letting a
# saved accidental drag turn them into oversized empty panels.
WIDGET_SIZE_LIMITS = {
    "small": {"min_width": 150, "min_height": 150, "max_width": 420, "max_height": 360},
    "medium": {"min_width": 150, "min_height": 150, "max_width": 620, "max_height": 380},
    "large": {"min_width": 150, "min_height": 150, "max_width": 760, "max_height": 560},
    "extra_large": {"min_width": 150, "min_height": 150, "max_width": 900, "max_height": 680},
    "default": {"min_width": 150, "min_height": 150, "max_width": 420, "max_height": 360},
}

DEFAULT_APP_SETTINGS = {
    "appearance_mode": "Dark",
    "widget_theme": "modern_dark",
    "widget_color_mode": "automatic",
}
