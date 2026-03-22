from __future__ import annotations

import customtkinter as ctk


class LoadingIndicator(ctk.CTkFrame):
    """Small animated progress box that tells the user the app is busy."""

    def __init__(self, parent) -> None:
        super().__init__(parent, corner_radius=12)
        self.label = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=14, weight="bold"))
        self.label.pack(anchor="w", padx=14, pady=(12, 8))

        self.progress = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=14, pady=(0, 12))
        self.progress.stop()

        self.is_running = False

    def start(self, message: str = "Working...") -> None:
        self.label.configure(text=message)
        self.progress.start()
        self.is_running = True

    def stop(self, message: str = "Done") -> None:
        self.progress.stop()
        self.label.configure(text=message)
        self.is_running = False

    def error(self, message: str = "Error") -> None:
        self.progress.stop()
        self.label.configure(text=message)
        self.is_running = False
