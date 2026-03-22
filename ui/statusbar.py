
from __future__ import annotations

import customtkinter as ctk

from config.constants import STATUS_BADGE_COLORS


class StatusBar(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent, height=46, corner_radius=10)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.label.grid(row=0, column=0, padx=(12, 8), pady=10, sticky="ew")

        self.badge = ctk.CTkLabel(
            self,
            text="INFO",
            corner_radius=999,
            padx=10,
            pady=4,
        )
        self.badge.grid(row=0, column=1, padx=(0, 8), pady=10, sticky="e")

        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", width=160)
        self.progress.grid(row=0, column=2, padx=12, pady=10, sticky="e")
        self.progress.stop()

        self.set_status("Ready", busy=False, level="info")

    def set_status(self, message: str, busy: bool = False, level: str = "info") -> None:
        self.label.configure(text=message)

        badge_level = "busy" if busy else level
        colors = STATUS_BADGE_COLORS.get(badge_level, STATUS_BADGE_COLORS["info"])
        self.badge.configure(text=badge_level.upper(), fg_color=colors["fg"], text_color=colors["text"])

        if busy:
            self.progress.start()
        else:
            self.progress.stop()
