from __future__ import annotations

import customtkinter as ctk


class LogBox(ctk.CTkTextbox):
    """Reusable read-only log area."""

    def __init__(self, parent) -> None:
        super().__init__(parent, height=220, corner_radius=12)
        self.configure(state="disabled")

    def append(self, text: str) -> None:
        self.configure(state="normal")
        self.insert("end", text + "\n")
        self.see("end")
        self.configure(state="disabled")
