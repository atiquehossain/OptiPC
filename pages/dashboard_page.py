from __future__ import annotations

import platform

import customtkinter as ctk
import psutil

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

        quick_actions = self.make_card(wrapper, "Quick Actions", "Most-used tools and desktop widgets")
        quick_actions.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")

        button_frame = ctk.CTkFrame(quick_actions, fg_color="transparent")
        button_frame.pack(fill="x", padx=18, pady=(0, 18))
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1)

        self.make_action_button(button_frame, "Quick Cleanup", self._quick_cleanup).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "System Info", self._show_system_info).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "Open Settings", self.action_service.open_windows_settings).grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        self.make_action_button(button_frame, "CPU Widget", lambda: self._open_widget("toggle_cpu_widget", "CPU Widget")).grid(row=1, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "RAM Widget", lambda: self._open_widget("toggle_ram_widget", "RAM Widget")).grid(row=1, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "GPU Widget", lambda: self._open_widget("toggle_gpu_widget", "GPU Widget")).grid(row=1, column=2, padx=6, pady=6, sticky="ew")

        self.make_action_button(button_frame, "Partitions Widget", lambda: self._open_widget("toggle_partitions_widget", "Partitions Widget")).grid(row=2, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "Storage Widget", lambda: self._open_widget("toggle_storage_widget", "Storage Widget")).grid(row=2, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, "Net Speed Widget", lambda: self._open_widget("toggle_network_speed_widget", "Net Speed Widget")).grid(row=2, column=2, padx=6, pady=6, sticky="ew")

        live_card = self.make_card(wrapper, "Live CPU Overview", "Updates automatically while the Dashboard is open")
        live_card.grid(row=1, column=2, columnspan=2, padx=8, pady=8, sticky="nsew")

        self.cpu_live_value = ctk.CTkLabel(live_card, text="0%", font=ctk.CTkFont(size=34, weight="bold"))
        self.cpu_live_value.pack(anchor="w", padx=18, pady=(0, 0))
        self.cpu_live_detail = ctk.CTkLabel(live_card, text="Loading CPU details...", text_color="gray75", justify="left")
        self.cpu_live_detail.pack(anchor="w", padx=18, pady=(0, 10))
        self.cpu_live_progress = ctk.CTkProgressBar(live_card)
        self.cpu_live_progress.pack(fill="x", padx=18, pady=(0, 18))
        self.cpu_live_progress.set(0)
        self.after(100, self._update_live_cpu)

        log_card = self.make_card(wrapper, "Activity Log")
        log_card.grid(row=2, column=0, columnspan=4, padx=8, pady=8, sticky="nsew")

        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.logger.bind(log_box.append)
        self.logger.write("Dashboard loaded.")
        self.status_service.info("Dashboard ready", toast=False)

    def _update_live_cpu(self) -> None:
        if not self.winfo_exists():
            return
        percent = psutil.cpu_percent(interval=None)
        logical = psutil.cpu_count(logical=True) or 0
        physical = psutil.cpu_count(logical=False) or logical
        freq = psutil.cpu_freq()
        freq_text = f"{freq.current:.0f} MHz" if freq else "N/A"
        self.cpu_live_value.configure(text=f"{percent:.0f}%")
        self.cpu_live_detail.configure(text=f"Physical cores: {physical}\nLogical cores: {logical}\nFrequency: {freq_text}")
        self.cpu_live_progress.set(percent / 100)
        self.after(1000, self._update_live_cpu)

    def _open_widget(self, method_name: str, widget_name: str) -> None:
        app = self.winfo_toplevel()
        callback = getattr(app, method_name, None)
        if callable(callback):
            callback()
        else:
            self.logger.write(f"{widget_name} is not available.")
            self.status_service.error(f"{widget_name} is not available", toast=True)

    def _quick_cleanup(self) -> None:
        removed, failed = self.system_service.quick_cleanup_temp()
        self.logger.write(f"Quick cleanup completed. Removed: {removed}, Failed: {failed}")
        self.status_service.success("Quick cleanup finished", toast=True)

    def _show_system_info(self) -> None:
        self.logger.write(self.system_service.get_system_summary())
        self.status_service.info("System info written to the log", toast=False)
