from __future__ import annotations

import customtkinter as ctk
from config.constants import UI_SPECS, THEMES


class MetricCard(ctk.CTkFrame):
    def __init__(self, parent, title: str, value: str) -> None:
        super().__init__(
            parent, 
            corner_radius=UI_SPECS["cards"]["corner_radius"], 
            fg_color=(THEMES["light"]["card"], THEMES["dark"]["card"]), 
            border_width=1, 
            border_color=(THEMES["light"]["border"], THEMES["dark"]["border"])
        )
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=UI_SPECS["cards"]["header_padding"], pady=(UI_SPECS["cards"]["header_padding"], 12))
        header_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            header_frame, 
            text=title, 
            text_color=(THEMES["light"]["text_secondary"], THEMES["dark"]["text_secondary"]), 
            font=ctk.CTkFont(size=12, weight="normal")
        )
        self.title_label.pack(anchor="w")
        
        # Value
        self.value_label = ctk.CTkLabel(
            self, 
            text=value, 
            font=ctk.CTkFont(size=UI_SPECS["cards"]["metric_font_size"], weight="bold"),
            text_color=(THEMES["light"]["text_primary"], THEMES["dark"]["text_primary"])
        )
        self.value_label.pack(anchor="w", padx=UI_SPECS["cards"]["content_padding"], pady=(0, UI_SPECS["cards"]["content_padding"]))
        
        # Add subtle gradient effect
        self._add_gradient_overlay()

    def _add_gradient_overlay(self) -> None:
        """Add a subtle gradient overlay effect"""
        gradient_frame = ctk.CTkFrame(
            self, 
            fg_color=(THEMES["light"]["background"], THEMES["dark"]["background"]), 
            corner_radius=UI_SPECS["cards"]["corner_radius"]
        )
        gradient_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        gradient_frame.lower()  # Send to background
        
    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)
        
    def set_title(self, title: str) -> None:
        self.title_label.configure(text=title)
