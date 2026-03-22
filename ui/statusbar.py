
from __future__ import annotations

import customtkinter as ctk

from config.constants import STATUS_BADGE_COLORS, UI_SPECS, THEMES


class StatusBar(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(
            parent, 
            height=UI_SPECS["statusbar"]["height"], 
            corner_radius=UI_SPECS["statusbar"]["corner_radius"], 
            fg_color=(THEMES["light"]["statusbar_bg"], THEMES["dark"]["statusbar_bg"])
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        # Status Message
        self.label = ctk.CTkLabel(
            self, 
            text="Ready", 
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=(THEMES["light"]["text_secondary"], THEMES["dark"]["text_secondary"])
        )
        self.label.grid(row=0, column=0, padx=(16, 12), pady=12, sticky="ew")

        # Status Badge
        self.badge = ctk.CTkLabel(
            self,
            text="INFO",
            corner_radius=12,
            padx=12,
            pady=6,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#ffffff"
        )
        self.badge.grid(row=0, column=1, padx=(0, 12), pady=12, sticky="e")

        # Progress Indicator
        self.progress = ctk.CTkProgressBar(
            self, 
            mode="indeterminate", 
            width=140,
            height=UI_SPECS["statusbar"]["progress_height"],
            corner_radius=UI_SPECS["statusbar"]["progress_corner_radius"],
            progress_color=(THEMES["light"]["button_primary"], THEMES["dark"]["button_primary"])
        )
        self.progress.grid(row=0, column=2, padx=16, pady=12, sticky="e")
        self.progress.stop()

        self.set_status("Ready", busy=False, level="info")

    def set_status(self, message: str, busy: bool = False, level: str = "info") -> None:
        self.label.configure(text=message)

        badge_level = "busy" if busy else level
        colors = STATUS_BADGE_COLORS.get(badge_level, STATUS_BADGE_COLORS["info"])
        self.badge.configure(
            text=badge_level.upper(), 
            fg_color=colors["fg"], 
            text_color=colors["text"]
        )

        if busy:
            self.progress.start()
        else:
            self.progress.stop()
