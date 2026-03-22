from __future__ import annotations

import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent, height=46, corner_radius=10)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.label.grid(row=0, column=0, padx=12, pady=10, sticky="ew")

        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", width=180)
        self.progress.grid(row=0, column=1, padx=12, pady=10, sticky="e")
        self.progress.stop()

    def set_status(self, message: str, busy: bool = False) -> None:
        self.label.configure(text=message)
        if busy:
            self.progress.start()
        else:
            self.progress.stop()
