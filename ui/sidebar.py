
from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from config.constants import APP_NAME, FONT_SIZES


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_navigate: Callable[[str], None]) -> None:
        super().__init__(parent, width=250, corner_radius=0)
        self.on_navigate = on_navigate
        self.buttons: dict[str, ctk.CTkButton] = {}
        self.grid_propagate(False)
        self.grid_rowconfigure(11, weight=1)
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text=APP_NAME, font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, padx=24, pady=(28, 10), sticky="w"
        )
        ctk.CTkLabel(
            self,
            text="Windows Utility Dashboard",
            text_color="gray70",
            font=ctk.CTkFont(size=FONT_SIZES["body"]),
        ).grid(row=1, column=0, padx=24, pady=(0, 20), sticky="w")

        names = ["Dashboard", "Cleanup", "Repair", "Recovery", "Devices", "Wallpaper", "Reports", "Settings"]
        for row, name in enumerate(names, start=2):
            button = ctk.CTkButton(
                self,
                text=name,
                height=42,
                corner_radius=12,
                anchor="w",
                command=lambda n=name: self.on_navigate(n),
            )
            button.grid(row=row, column=0, padx=18, pady=6, sticky="ew")
            self.buttons[name] = button

        ctk.CTkLabel(self, text="structured themed build", text_color="gray60", font=ctk.CTkFont(size=12)).grid(
            row=12, column=0, padx=24, pady=20, sticky="sw"
        )

    def set_active(self, page_name: str) -> None:
        for name, button in self.buttons.items():
            if name == page_name:
                button.configure(fg_color=("#1f6aa5", "#1f6aa5"))
            else:
                button.configure(fg_color=("gray75", "gray25"))
