from __future__ import annotations

from typing import Callable
import customtkinter as ctk
from config.constants import FONT_SIZES, UI_SPECS, THEMES


class BasePage(ctk.CTkFrame):
    def __init__(self, parent, logger, status_service, system_service, action_service) -> None:
        super().__init__(parent, fg_color="transparent")
        self.logger = logger
        self.status_service = status_service
        self.system_service = system_service
        self.action_service = action_service
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def build(self) -> None:
        raise NotImplementedError

    def make_card(self, parent, title: str, subtitle: str = "") -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent, 
            corner_radius=UI_SPECS["cards"]["corner_radius"], 
            fg_color=(THEMES["light"]["card"], THEMES["dark"]["card"]), 
            border_width=1, 
            border_color=(THEMES["light"]["border"], THEMES["dark"]["border"])
        )
        
        # Header Section
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=UI_SPECS["cards"]["header_padding"], pady=(UI_SPECS["cards"]["header_padding"], 16))
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame, 
            text=title, 
            font=ctk.CTkFont(size=FONT_SIZES["card_title"], weight="bold"),
            text_color=(THEMES["light"]["text_primary"], THEMES["dark"]["text_primary"])
        ).pack(anchor="w")
        
        if subtitle:
            ctk.CTkLabel(
                header_frame, 
                text=subtitle, 
                text_color=(THEMES["light"]["text_secondary"], THEMES["dark"]["text_secondary"]), 
                font=ctk.CTkFont(size=13)
            ).pack(anchor="w", pady=(4, 0))
        
        return card

    def make_action_button(self, parent, text: str, command: Callable[[], None]) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent, 
            text=text, 
            height=UI_SPECS["buttons"]["height"], 
            corner_radius=UI_SPECS["buttons"]["corner_radius"], 
            font=ctk.CTkFont(size=UI_SPECS["buttons"]["font_size"]),
            fg_color=(THEMES["light"]["button_primary"], THEMES["dark"]["button_primary"]),
            hover_color=(THEMES["light"]["button_primary_hover"], THEMES["dark"]["button_primary_hover"]),
            text_color="#ffffff",
            border_width=0,
            command=command
        )
