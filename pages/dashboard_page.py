
from __future__ import annotations

import platform
import customtkinter as ctk

from pages.base_page import BasePage
from widgets.log_box import LogBox
from widgets.metric_card import MetricCard


class DashboardPage(BasePage):
    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1, 2, 3), weight=1)

        metrics = [
            ("CPU Usage", self.system_service.get_cpu_usage()),
            ("RAM Total", self.system_service.get_memory_total()),
            ("Disk Free", self.system_service.get_disk_free()),
            ("Windows", platform.release()),
        ]

        for index, (title, value) in enumerate(metrics):
            card = MetricCard(wrapper, title, value)
            card.grid(row=0, column=index, padx=8, pady=8, sticky="nsew")

        quick_actions = self.make_card(wrapper, "Quick Actions", "Most-used tools")
        quick_actions.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")

        button_frame = ctk.CTkFrame(quick_actions, fg_color="transparent")
        button_frame.pack(fill="x", padx=18, pady=(0, 18))

        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1)

        self.make_action_button(button_frame, "Quick Cleanup", self._quick_cleanup).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "System Info", self._show_system_info).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "Open Settings", self.action_service.open_windows_settings).grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        self.make_action_button(button_frame, "CPU Widget", lambda: self._toggle_widget("toggle_cpu_widget")).grid(row=1, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "RAM Widget", lambda: self._toggle_widget("toggle_ram_widget")).grid(row=1, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "GPU Widget", lambda: self._toggle_widget("toggle_gpu_widget")).grid(row=1, column=2, padx=6, pady=6, sticky="ew")

        self.make_action_button(button_frame, "Partitions Widget", lambda: self._toggle_widget("toggle_partitions_widget")).grid(row=2, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "Storage Widget", lambda: self._toggle_widget("toggle_storage_widget")).grid(row=2, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "Net Speed Widget", lambda: self._toggle_widget("toggle_network_speed_widget")).grid(row=2, column=2, padx=6, pady=6, sticky="ew")

        about_card = self.make_card(wrapper, "Overview", "This is the home page")
        about_card.grid(row=1, column=2, columnspan=2, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(
            about_card,
            text="Use the left sidebar to open features.",
            justify="left",
            text_color="gray75",
        ).pack(anchor="w", padx=18, pady=(0, 18))

        log_card = self.make_card(wrapper, "Activity Log")
        log_card.grid(row=2, column=0, columnspan=4, padx=8, pady=8, sticky="nsew")

        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.logger.bind(log_box.append)
        self.logger.write("Dashboard loaded.")

    def _toggle_widget(self, method_name: str) -> None:
        app = self.winfo_toplevel()
        callback = getattr(app, method_name, None)
        if callable(callback):
            callback()
        else:
            self.logger.write(f"Widget action '{method_name}' is not available.")

    def _quick_cleanup(self) -> None:
        removed, failed = self.system_service.quick_cleanup_temp()
        self.logger.write(f"Quick cleanup completed. Removed: {removed}, Failed: {failed}")

    def _show_system_info(self) -> None:
        self.logger.write(self.system_service.get_system_summary())
