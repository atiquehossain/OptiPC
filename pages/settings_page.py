
from __future__ import annotations

import customtkinter as ctk

from pages.base_page import BasePage


class SettingsPage(BasePage):
    def __init__(
        self,
        parent,
        logger,
        status_service,
        system_service,
        action_service,
        appearance_callback,
        widget_theme_callback,
        current_appearance: str,
        current_widget_theme_label: str,
    ) -> None:
        super().__init__(parent, logger, status_service, system_service, action_service)
        self.appearance_callback = appearance_callback
        self.widget_theme_callback = widget_theme_callback
        self.current_appearance = current_appearance
        self.current_widget_theme_label = current_widget_theme_label

    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        appearance = self.make_card(wrapper, "Appearance", "Adjust app behavior and widget style")
        appearance.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(appearance, text="App theme").pack(anchor="w", padx=18, pady=(0, 6))
        app_mode = ctk.CTkSegmentedButton(appearance, values=["Dark", "Light"], command=self._change_app_theme)
        app_mode.pack(anchor="w", padx=18, pady=(0, 18))
        app_mode.set(self.current_appearance)

        ctk.CTkLabel(appearance, text="Widget theme").pack(anchor="w", padx=18, pady=(0, 6))
        widget_mode = ctk.CTkSegmentedButton(
            appearance,
            values=["Dark", "Light", "Liquid Glass"],
            command=self._change_widget_theme,
        )
        widget_mode.pack(anchor="w", padx=18, pady=(0, 18))
        widget_mode.set(self.current_widget_theme_label)

        ctk.CTkLabel(
            appearance,
            text="Widgets update live. Try switching between Dark, Light, and Liquid Glass while widgets are open.",
            justify="left",
            wraplength=420,
            text_color="gray75",
        ).pack(anchor="w", padx=18, pady=(0, 18))

        tray = self.make_card(wrapper, "Tray and Widgets", "Background mode and saved layout")
        tray.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(
            tray,
            text="Close button minimizes OptiPC to the system tray when tray support is available. Widget positions, sizes, and visibility are saved automatically.",
            justify="left",
            wraplength=420,
            text_color="gray75",
        ).pack(anchor="w", padx=18, pady=(0, 12))

        buttons = ctk.CTkFrame(tray, fg_color="transparent")
        buttons.pack(fill="x", padx=18, pady=(0, 18))
        buttons.grid_columnconfigure((0, 1), weight=1)

        self.make_action_button(buttons, "Minimize to Tray", self._minimize_to_tray).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(buttons, "Restore Saved Widgets", self._restore_saved_widgets).grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        self.make_action_button(tray, "Open Startup Apps Settings", self._open_startup_apps).pack(fill="x", padx=18, pady=(0, 12))

        info = self.make_card(wrapper, "About Structure", "Why this build is easier to maintain")
        info.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(
            info,
            text="This build centralizes colors, text labels, and font sizes in a constants/config layer. That makes theme updates and UI cleanup much easier.",
            justify="left",
            wraplength=900,
            text_color="gray75",
        ).pack(anchor="w", padx=18, pady=(0, 18))

        self.status_service.info("Settings page ready", toast=False)

    def _change_app_theme(self, value: str) -> None:
        self.appearance_callback(value)

    def _change_widget_theme(self, value: str) -> None:
        self.widget_theme_callback(value)

    def _minimize_to_tray(self) -> None:
        app = self.winfo_toplevel()
        if hasattr(app, "minimize_to_tray"):
            app.minimize_to_tray()

    def _restore_saved_widgets(self) -> None:
        app = self.winfo_toplevel()
        if hasattr(app, "show_all_saved_widgets"):
            app.show_all_saved_widgets()


    def _open_startup_apps(self) -> None:
        self.action_service.open_target("ms-settings:startupapps")
        self.status_service.info("Opened Startup Apps Settings", toast=False)
