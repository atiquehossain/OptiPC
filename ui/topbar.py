from __future__ import annotations

import platform
import socket
import customtkinter as ctk


class Topbar(ctk.CTkFrame):
    def __init__(self, parent, on_theme_change) -> None:
        super().__init__(parent, height=72, corner_radius=0)
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=18, sticky="w")

        self.badge_label = ctk.CTkLabel(
            self,
            text=f"{platform.system()} {platform.release()}  |  {socket.gethostname()}",
            fg_color=("gray85", "gray20"),
            corner_radius=999,
            padx=14,
            pady=7,
        )
        self.badge_label.grid(row=0, column=1, padx=12, pady=18, sticky="e")

        self.theme_switch = ctk.CTkSegmentedButton(self, values=["Dark", "Light"], command=on_theme_change, width=140)
        self.theme_switch.grid(row=0, column=2, padx=(8, 20), pady=18, sticky="e")
        self.theme_switch.set("Dark")

    def set_title(self, title: str) -> None:
        self.title_label.configure(text=title)
