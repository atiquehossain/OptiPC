
from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from config.constants import APP_NAME, UI_SPECS, THEMES, NAVIGATION_ICONS


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_navigate: Callable[[str], None]) -> None:
        super().__init__(
            parent, 
            width=UI_SPECS["sidebar"]["width"], 
            corner_radius=UI_SPECS["sidebar"]["corner_radius"],
            fg_color=(THEMES["light"]["sidebar_bg"], THEMES["dark"]["sidebar_bg"])
        )
        self.on_navigate = on_navigate
        self.buttons: dict[str, ctk.CTkButton] = {}
        self.grid_propagate(False)
        self.grid_rowconfigure(11, weight=1)
        self._build()

    def _build(self) -> None:
        # App Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=UI_SPECS["sidebar"]["header_height"])
        header_frame.grid(row=0, column=0, padx=20, pady=(24, 20), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        # App Icon and Name
        app_name_frame = ctk.CTkFrame(
            header_frame, 
            fg_color=(THEMES["light"]["button_primary"], THEMES["dark"]["button_primary"]), 
            corner_radius=16, 
            height=50
        )
        app_name_frame.grid(row=0, column=0, sticky="ew")
        app_name_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            app_name_frame, 
            text=APP_NAME, 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        ).pack(pady=12)
        
        ctk.CTkLabel(
            self,
            text="System Optimization Suite",
            text_color=(THEMES["light"]["text_secondary"], THEMES["dark"]["text_secondary"]),
            font=ctk.CTkFont(size=12, weight="normal"),
        ).grid(row=1, column=0, padx=20, pady=(0, 24), sticky="w")

        # Navigation Buttons
        names = list(NAVIGATION_ICONS.keys())
        
        for row, name in enumerate(names, start=2):
            button_frame = ctk.CTkFrame(self, fg_color="transparent")
            button_frame.grid(row=row, column=0, padx=16, pady=4, sticky="ew")
            button_frame.grid_columnconfigure(0, weight=1)
            
            button = ctk.CTkButton(
                button_frame,
                text=f" {NAVIGATION_ICONS[name]}  {name}",
                height=UI_SPECS["sidebar"]["button_height"],
                corner_radius=UI_SPECS["sidebar"]["button_corner_radius"],
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=THEMES["light"]["sidebar_button_bg"],
                text_color=THEMES["light"]["sidebar_button_text"],
                hover_color=THEMES["light"]["sidebar_button_hover"],
                border_width=1,
                border_color=THEMES["light"]["border"],
                command=lambda n=name: self.on_navigate(n),
            )
            button.grid(row=0, column=0, sticky="ew")
            self.buttons[name] = button

        # Footer
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=UI_SPECS["sidebar"]["footer_height"])
        footer_frame.grid(row=12, column=0, padx=20, pady=16, sticky="ew")
        footer_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            footer_frame, 
            text="Modern PC Utility", 
            text_color=(THEMES["light"]["text_muted"], THEMES["dark"]["text_muted"]), 
            font=ctk.CTkFont(size=11, weight="normal")
        ).pack(side="bottom")

    def set_active(self, page_name: str) -> None:
        for name, button in self.buttons.items():
            if name == page_name:
                button.configure(
                    fg_color=(THEMES["light"]["sidebar_button_active"], THEMES["dark"]["sidebar_button_active"]),
                    text_color=THEMES["light"]["sidebar_button_text_active"],
                    hover_color=(THEMES["light"]["button_primary_hover"], THEMES["dark"]["button_primary_hover"]),
                    border_color=(THEMES["light"]["sidebar_button_active"], THEMES["dark"]["sidebar_button_active"])
                )
            else:
                button.configure(
                    fg_color=THEMES["light"]["sidebar_button_bg"],
                    text_color=THEMES["light"]["sidebar_button_text"],
                    hover_color=THEMES["light"]["sidebar_button_hover"],
                    border_color=THEMES["light"]["border"]
                )

    def update_theme(self, appearance: str) -> None:
        """Update sidebar theme based on appearance"""
        is_dark = appearance == "dark"
        
        # Update all buttons
        for name, button in self.buttons.items():
            button.configure(
                fg_color=(THEMES["light"]["sidebar_button_bg"], THEMES["dark"]["sidebar_button_bg"])[is_dark],
                text_color=(THEMES["light"]["sidebar_button_text"], THEMES["dark"]["sidebar_button_text"])[is_dark],
                hover_color=(THEMES["light"]["sidebar_button_hover"], THEMES["dark"]["sidebar_button_hover"])[is_dark],
                border_color=(THEMES["light"]["border"], THEMES["dark"]["border"])[is_dark]
            )
        
        # Update sidebar background
        self.configure(
            fg_color=(THEMES["light"]["sidebar_bg"], THEMES["dark"]["sidebar_bg"])[is_dark]
        )
