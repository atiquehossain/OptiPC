from __future__ import annotations

import customtkinter as ctk

from pages.base_page import BasePage


class SettingsPage(BasePage):
    def __init__(self, parent, logger, status_service, system_service, action_service, appearance_callback) -> None:
        super().__init__(parent, logger, status_service, system_service, action_service)
        self.appearance_callback = appearance_callback

    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        appearance = self.make_card(wrapper, "Appearance", "Adjust app behavior")
        appearance.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(appearance, text="Theme").pack(anchor="w", padx=18, pady=(0, 6))
        mode = ctk.CTkSegmentedButton(appearance, values=["Dark", "Light"], command=self.appearance_callback)
        mode.pack(anchor="w", padx=18, pady=(0, 18))
        mode.set("Dark")

        info = self.make_card(wrapper, "About", "How this app behaves")
        info.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(info, text="The whole app does not run as admin. Only selected actions like repair commands request elevation. Wallpaper and most reports work in normal mode.", justify="left", wraplength=420, text_color="gray75").pack(anchor="w", padx=18, pady=(0, 18))
        self.status_service.set_status("Settings page ready", busy=False)
