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
            MetricCard(wrapper, title, value).grid(row=0, column=index, padx=8, pady=8, sticky="nsew")

        quick = self.make_card(wrapper, "Quick Actions", "Most-used tools")
        quick.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        row = ctk.CTkFrame(quick, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 18))
        row.grid_columnconfigure((0, 1, 2), weight=1)
        self.make_action_button(row, "Quick Cleanup", lambda: self.logger.write("Open Cleanup page for full feedback.")).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(row, "System Info", lambda: self.logger.write(self.system_service.get_system_summary())).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(row, "Open Settings", self.action_service.open_windows_settings).grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        about = self.make_card(wrapper, "Overview", "This is the home page")
        about.grid(row=1, column=2, columnspan=2, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(about, text="Use the left sidebar to open cleanup, repair, recovery, wallpaper, reports, and settings.", justify="left", wraplength=460, text_color="gray75").pack(anchor="w", padx=18, pady=(0, 18))

        log_card = self.make_card(wrapper, "Activity Log")
        log_card.grid(row=2, column=0, columnspan=4, padx=8, pady=8, sticky="nsew")
        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.logger.bind(log_box.append)
        self.logger.write("Dashboard loaded.")
        self.status_service.set_status("Dashboard ready", busy=False)
