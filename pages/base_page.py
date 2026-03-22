from __future__ import annotations

from typing import Callable
import customtkinter as ctk


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
        card = ctk.CTkFrame(parent, corner_radius=18)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=18, pady=(16, 4))
        if subtitle:
            ctk.CTkLabel(card, text=subtitle, text_color="gray70", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=18, pady=(0, 12))
        return card

    def make_action_button(self, parent, text: str, command: Callable[[], None]) -> ctk.CTkButton:
        return ctk.CTkButton(parent, text=text, height=40, corner_radius=12, command=command)
