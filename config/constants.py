
from __future__ import annotations

APP_NAME = "OptiPC"
APP_VERSION = "1.0"

# Typography
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

# Responsive Widget Font Sizes (scale with widget size)
RESPONSIVE_FONT_SIZES = {
    "default": {
        "tiny": 9,
        "small": 11,
        "body": 12,
        "label": 13,
        "title": 15,
        "metric": 18,
        "hero": 20,
    },
    "small": {
        "tiny": 9,
        "small": 11,
        "body": 12,
        "label": 13,
        "title": 15,
        "metric": 18,
        "hero": 20,
    },
    "medium": {
        "tiny": 10,
        "small": 12,
        "body": 13,
        "label": 14,
        "title": 16,
        "metric": 22,
        "hero": 24,
    },
    "large": {
        "tiny": 11,
        "small": 13,
        "body": 14,
        "label": 15,
        "title": 18,
        "metric": 26,
        "hero": 28,
    },
    "extra_large": {
        "tiny": 12,
        "small": 14,
        "body": 15,
        "label": 16,
        "title": 20,
        "metric": 30,
        "hero": 32,
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
    "modern_light": {
        "window_bg": "#f5f5f7",
        "container": "rgba(255, 255, 255, 0.72)",
        "panel": "rgba(255, 255, 255, 0.5)",
        "text": "#1d1d1f",
        "muted": "#86868b",
        "accent": "#007aff",
        "button": "rgba(255, 255, 255, 0.8)",
        "button_hover": "rgba(255, 255, 255, 0.9)",
        "progress_track": "rgba(0, 0, 0, 0.1)",
        "alpha": 0.98,
        "border": "rgba(255, 255, 255, 0.2)",
        "shadow": "rgba(0, 0, 0, 0.15)",
        "cpu_accent": "rgba(90, 200, 250, 0.1)",
        "ram_accent": "rgba(48, 209, 88, 0.1)",
        "gpu_accent": "rgba(175, 82, 222, 0.1)",
        "storage_accent": "rgba(88, 86, 214, 0.1)",
        "calendar_accent": "rgba(255, 59, 48, 0.1)",
        "clock_accent": "rgba(0, 122, 255, 0.1)",
        "runtime_accent": "rgba(142, 142, 147, 0.1)",
    },
    "modern_dark": {
        "window_bg": "#000000",
        "container": "rgba(30, 30, 30, 0.72)",
        "panel": "rgba(30, 30, 30, 0.5)",
        "text": "#f5f5f7",
        "muted": "#98989f",
        "accent": "#0a84ff",
        "button": "rgba(60, 60, 60, 0.8)",
        "button_hover": "rgba(80, 80, 80, 0.9)",
        "progress_track": "rgba(255, 255, 255, 0.1)",
        "alpha": 0.98,
        "border": "rgba(255, 255, 255, 0.08)",
        "shadow": "rgba(0, 0, 0, 0.15)",
        "cpu_accent": "rgba(100, 210, 255, 0.1)",
        "ram_accent": "rgba(64, 221, 142, 0.1)",
        "gpu_accent": "rgba(191, 90, 242, 0.1)",
        "storage_accent": "rgba(124, 124, 255, 0.1)",
        "calendar_accent": "rgba(255, 69, 58, 0.1)",
        "clock_accent": "rgba(10, 132, 255, 0.1)",
        "runtime_accent": "rgba(168, 168, 173, 0.1)",
    },
}

# Standard Widget Dimensions
WIDGET_SIZES = {
    "small": {"width": 200, "height": 200},      # Compact widgets (CPU, RAM, GPU, Clock, Uptime)
    "medium": {"width": 320, "height": 220},     # Medium widgets (Network Speed)
    "large": {"width": 400, "height": 220},      # Large widgets (Storage, Partitions)
    "extra_large": {"width": 400, "height": 420}, # Extra large widgets (Calendar)
    "default": {"width": 200, "height": 200},    # Default size for new widgets
}

DEFAULT_APP_SETTINGS = {
    "appearance_mode": "Dark",
    "widget_theme": "modern_dark",
}
