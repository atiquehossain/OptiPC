from __future__ import annotations

import platform

import customtkinter as ctk
import psutil

from pages.base_page import BasePage
from widgets.log_box import LogBox
from widgets.metric_card import MetricCard
from config.constants import DASHBOARD_ICONS, THEMES, UI_SPECS
from services.cleanup_service import CleanupService


class DashboardPage(BasePage):
    def __init__(
        self,
        parent,
        logger,
        status_service,
        system_service,
        action_service,
        cleanup_service: CleanupService | None = None,
    ) -> None:
        super().__init__(parent, logger, status_service, system_service, action_service)
        self.cleanup_service = cleanup_service

    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1, uniform="dashboard")

        # System Metrics Cards
        metrics = [
            (DASHBOARD_ICONS["CPU Usage"], self.system_service.get_cpu_usage()),
            (DASHBOARD_ICONS["RAM Total"], self.system_service.get_memory_total()),
            (DASHBOARD_ICONS["Disk Free"], self.system_service.get_disk_free()),
            (DASHBOARD_ICONS["Windows"], platform.release()),
        ]
        
        metric_titles = ["CPU Usage", "RAM Total", "Disk Free", "Windows"]

        metrics_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        metrics_frame.grid(row=0, column=0, columnspan=2, padx=8, pady=(8, 14), sticky="ew")
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="metrics")

        for index, (icon, value) in enumerate(metrics):
            card = MetricCard(metrics_frame, f"{icon} {metric_titles[index]}", value)
            card.grid(row=0, column=index, padx=8, pady=0, sticky="nsew")

        # Quick Actions Section
        quick_actions = self.make_card(wrapper, f"{DASHBOARD_ICONS['Quick Actions']} Quick Actions", "Most-used tools and desktop widgets")
        quick_actions.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

        button_frame = ctk.CTkFrame(quick_actions, fg_color="transparent")
        button_frame.pack(fill="x", padx=UI_SPECS["cards"]["content_padding"], pady=(0, UI_SPECS["cards"]["content_padding"]))
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1, uniform="actions")

        # System Tools Row
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Quick Cleanup']} Cleanup", self._quick_cleanup).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['System Info']} Info", self._show_system_info).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Open Settings']} Settings", self.action_service.open_windows_settings).grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        # System Widgets Row 1
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['CPU Widget']} CPU", lambda: self._open_widget("toggle_cpu_widget", "CPU Widget")).grid(row=1, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['RAM Widget']} RAM", lambda: self._open_widget("toggle_ram_widget", "RAM Widget")).grid(row=1, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['GPU Widget']} GPU", lambda: self._open_widget("toggle_gpu_widget", "GPU Widget")).grid(row=1, column=2, padx=6, pady=6, sticky="ew")

        # System Widgets Row 2
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Partitions Widget']} Partitions", lambda: self._open_widget("toggle_partitions_widget", "Partitions Widget")).grid(row=2, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Storage Widget']} Storage", lambda: self._open_widget("toggle_storage_widget", "Storage Widget")).grid(row=2, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Calendar Widget']} Calendar", lambda: self._open_widget("toggle_calendar_widget", "Calendar Widget")).grid(row=2, column=2, padx=6, pady=6, sticky="ew")

        # System Widgets Row 3
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Net Speed Widget']} Net Speed", lambda: self._open_widget("toggle_network_speed_widget", "Net Speed Widget")).grid(row=3, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Clock Widget']} Clock", lambda: self._open_widget("toggle_clock_widget", "Clock Widget")).grid(row=3, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Uptime Widget']} Uptime", lambda: self._open_widget("toggle_uptime_widget", "Uptime Widget")).grid(row=3, column=2, padx=6, pady=6, sticky="ew")

        # Smart Widgets Row 1
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['PC Health Widget']} PC Health", lambda: self._open_widget("toggle_pc_health_widget", "PC Health Widget")).grid(row=4, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Top Processes Widget']} Processes", lambda: self._open_widget("toggle_top_processes_widget", "Top Processes Widget")).grid(row=4, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Battery Widget']} Battery", lambda: self._open_widget("toggle_battery_health_widget", "Battery Widget")).grid(row=4, column=2, padx=6, pady=6, sticky="ew")

        # Smart Widgets Row 2
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Cleanup Widget']} Cleanup", lambda: self._open_widget("toggle_storage_cleanup_widget", "Cleanup Widget")).grid(row=5, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Disk IO Widget']} Disk I/O", lambda: self._open_widget("toggle_disk_io_widget", "Disk I/O Widget")).grid(row=5, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Network Quality Widget']} Net Quality", lambda: self._open_widget("toggle_network_quality_widget", "Network Quality Widget")).grid(row=5, column=2, padx=6, pady=6, sticky="ew")

        # Smart Widgets Row 3
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Windows Update Widget']} Update", lambda: self._open_widget("toggle_windows_update_widget", "Windows Update Widget")).grid(row=6, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Temperature Widget']} Temp", lambda: self._open_widget("toggle_temperature_widget", "Temperature Widget")).grid(row=6, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Quick Actions Widget']} Actions", lambda: self._open_widget("toggle_quick_actions_widget", "Quick Actions Widget")).grid(row=6, column=2, padx=6, pady=6, sticky="ew")

        # Smart Widgets Row 4
        self.make_action_button(button_frame, f"{DASHBOARD_ICONS['Timeline Widget']} Timeline", lambda: self._open_widget("toggle_performance_timeline_widget", "Timeline Widget")).grid(row=7, column=0, padx=6, pady=6, sticky="ew")
        # Live CPU Monitor
        live_card = self.make_card(wrapper, f"{DASHBOARD_ICONS['Live CPU Monitor']} Live CPU Monitor", "Real-time CPU performance monitoring")
        live_card.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")

        # CPU Display Frame
        cpu_frame = ctk.CTkFrame(live_card, fg_color="transparent")
        cpu_frame.pack(fill="x", padx=UI_SPECS["cards"]["content_padding"], pady=(0, UI_SPECS["cards"]["content_padding"]))
        cpu_frame.grid_columnconfigure(0, weight=1)
        
        # CPU Value with better styling
        self.cpu_live_value = ctk.CTkLabel(
            cpu_frame, 
            text="0%", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=(THEMES["light"]["text_primary"], THEMES["dark"]["text_primary"])
        )
        self.cpu_live_value.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # CPU Details
        self.cpu_live_detail = ctk.CTkLabel(
            cpu_frame, 
            text="Loading CPU details...", 
            text_color=(THEMES["light"]["text_secondary"], THEMES["dark"]["text_secondary"]), 
            justify="left",
            font=ctk.CTkFont(size=11)
        )
        self.cpu_live_detail.grid(row=1, column=0, sticky="w", pady=(0, 12))
        
        # CPU Progress Bar
        self.cpu_live_progress = ctk.CTkProgressBar(
            cpu_frame,
            height=8,
            corner_radius=4,
            progress_color=(THEMES["light"]["button_primary"], THEMES["dark"]["button_primary"])
        )
        self.cpu_live_progress.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.cpu_live_progress.set(0)
        
        self.after(100, self._update_live_cpu)

        # Activity Log
        log_card = self.make_card(wrapper, f"{DASHBOARD_ICONS['Activity Log']} Activity Log", "Recent system activities and events")
        log_card.grid(row=2, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")

        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=UI_SPECS["cards"]["content_padding"], pady=(0, UI_SPECS["cards"]["content_padding"]))
        self.logger.bind(log_box.append)
        self.logger.write("🚀 Dashboard loaded successfully.")
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
        if self.cleanup_service is not None:
            result = self.cleanup_service.quick_cleanup(self.logger.write)
            self.logger.write(
                "Quick cleanup completed. "
                f"Removed: {result['removed']}, Failed: {result['failed']}, "
                f"Skipped: {result['skipped']}, "
                f"Freed: {self.cleanup_service.format_bytes(result['bytes_freed'])}"
            )
        else:
            removed, failed = self.system_service.quick_cleanup_temp()
            self.logger.write(f"Quick cleanup completed. Removed: {removed}, Failed: {failed}")
        self.status_service.success("Quick cleanup finished", toast=True)

    def _show_system_info(self) -> None:
        self.logger.write(self.system_service.get_system_summary())
        self.status_service.info("System info written to the log", toast=False)
