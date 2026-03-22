from __future__ import annotations

import customtkinter as ctk


class MetricCard(ctk.CTkFrame):
    def __init__(self, parent, title: str, value: str) -> None:
        super().__init__(parent, corner_radius=18)
        ctk.CTkLabel(self, text=title, text_color="gray70", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=18, pady=(16, 6))
        ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=18, pady=(0, 18))
