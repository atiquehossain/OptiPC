
from __future__ import annotations

import platform
import socket
import customtkinter as ctk

from config.constants import FONT_SIZES, UI_SPECS, THEMES


class Topbar(ctk.CTkFrame):
    def __init__(self, parent, on_theme_change) -> None:
        super().__init__(
            parent, 
            height=UI_SPECS["topbar"]["height"], 
            corner_radius=UI_SPECS["topbar"]["corner_radius"], 
            fg_color=(THEMES["light"]["topbar_bg"], THEMES["dark"]["topbar_bg"])
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        # Title Section
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=24, pady=20, sticky="w")
        
        self.title_label = ctk.CTkLabel(
            title_frame, 
            text="Dashboard", 
            font=ctk.CTkFont(size=FONT_SIZES["page_title"], weight="bold"),
            text_color=(THEMES["light"]["text_primary"], THEMES["dark"]["text_primary"])
        )
        self.title_label.pack(side="left")
        
        # Subtitle/Breadcrumb
        self.subtitle_label = ctk.CTkLabel(
            title_frame,
            text="System Overview",
            text_color=(THEMES["light"]["text_secondary"], THEMES["dark"]["text_secondary"]),
            font=ctk.CTkFont(size=12)
        )
        self.subtitle_label.pack(side="left", padx=(12, 0))

        # System Info Badge
        self.badge_label = ctk.CTkLabel(
            self,
            text=f"{platform.system()} {platform.release()}  |  {socket.gethostname()}",
            fg_color=(THEMES["light"]["button_secondary"], THEMES["dark"]["button_secondary"]),
            text_color=(THEMES["light"]["text_secondary"], THEMES["dark"]["text_secondary"]),
            corner_radius=20,
            padx=16,
            pady=8,
            font=ctk.CTkFont(size=11, weight="normal")
        )
        self.badge_label.grid(row=0, column=1, padx=12, pady=20, sticky="e")

        # Theme Switcher
        theme_frame = ctk.CTkFrame(
            self, 
            fg_color=(THEMES["light"]["button_secondary"], THEMES["dark"]["button_secondary"]), 
            corner_radius=16
        )
        theme_frame.grid(row=0, column=2, padx=(12, 24), pady=20, sticky="e")
        
        self.theme_switch = ctk.CTkSegmentedButton(
            theme_frame, 
            values=["🌙 Dark", "☀️ Light"], 
            command=on_theme_change, 
            width=UI_SPECS["topbar"]["theme_switcher_width"],
            height=UI_SPECS["topbar"]["theme_switcher_height"],
            fg_color=(THEMES["light"]["button_secondary"], THEMES["dark"]["button_secondary"]),
            selected_color=(THEMES["light"]["button_primary"], THEMES["dark"]["button_primary"]),
            selected_hover_color=(THEMES["light"]["button_primary_hover"], THEMES["dark"]["button_primary_hover"]),
            unselected_color=(THEMES["light"]["button_secondary"], THEMES["dark"]["button_secondary"]),
            unselected_hover_color=(THEMES["light"]["button_secondary_hover"], THEMES["dark"]["button_secondary_hover"]),
            text_color=(THEMES["light"]["text_secondary"], THEMES["dark"]["text_secondary"]),
            font=ctk.CTkFont(size=11),
            corner_radius=UI_SPECS["topbar"]["theme_switcher_corner_radius"]
        )
        self.theme_switch.pack(padx=8, pady=6)

    def set_title(self, title: str, subtitle: str = "") -> None:
        self.title_label.configure(text=title)
        if subtitle:
            self.subtitle_label.configure(text=subtitle)
        else:
            # Set default subtitle based on page
            subtitle_map = {
                "Dashboard": "System Overview",
                "Cleanup": "System Cleaning Tools",
                "Repair": "System Repair Utilities",
                "Recovery": "System Recovery Options",
                "Devices": "Device Management",
                "Wallpaper": "Wallpaper Customization",
                "Reports": "System Reports",
                "Settings": "Application Settings"
            }
            self.subtitle_label.configure(text=subtitle_map.get(title, ""))
