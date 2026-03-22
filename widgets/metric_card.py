from __future__ import annotations

import customtkinter as ctk


class MetricCard(ctk.CTkFrame):
    def __init__(self, parent, title: str, value: str) -> None:
        super().__init__(parent, corner_radius=18)
        self.title_label = ctk.CTkLabel(self, text=title, text_color="gray70", font=ctk.CTkFont(size=13))
        self.title_label.pack(anchor="w", padx=18, pady=(16, 6))
        self.value_label = ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=28, weight="bold"))
        self.value_label.pack(anchor="w", padx=18, pady=(0, 18))

    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)
