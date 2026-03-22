from __future__ import annotations

from pages.base_page import BasePage
from services.storage_health_service import StorageHealthService
from services.task_runner import TaskRunner
from widgets.loading_indicator import LoadingIndicator
from widgets.log_box import LogBox
import customtkinter as ctk


class ReportsPage(BasePage):
    def __init__(self, parent, logger, status_service, system_service, action_service, report_dir) -> None:
        super().__init__(parent, logger, status_service, system_service, action_service)
        self.report_dir = report_dir
        self.storage_health_service = StorageHealthService()

    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        report_card = self.make_card(wrapper, "Reports", "Generate diagnostics and exports")
        report_card.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        actions = [
            ("Battery Report", self._battery_report),
            ("Network Report", self._network_report),
            ("Installed Apps Report", self._installed_apps_report),
            ("Heavy Process Report", self._heavy_process_report),
            ("Storage Health", self.show_storage_health),
        ]
        for label, command in actions:
            self.make_action_button(report_card, label, command).pack(fill="x", padx=18, pady=6)

        output_card = self.make_card(wrapper, "Output Folder", "Reports are saved here")
        output_card.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(output_card, text=str(self.report_dir), justify="left", text_color="gray75", wraplength=420).pack(anchor="w", padx=18, pady=(0, 18))
        self.make_action_button(output_card, "Open Output Folder", lambda: self.action_service.open_report_folder(self.report_dir)).pack(fill="x", padx=18, pady=(0, 18))

        loading_card = self.make_card(wrapper, "Task Status", "Long reports show activity here")
        loading_card.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        self.loading_indicator = LoadingIndicator(loading_card)
        self.loading_indicator.pack(fill="x", padx=18, pady=(0, 18))

        log_card = self.make_card(wrapper, "Report Output")
        log_card.grid(row=2, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.logger.bind(log_box.append)
        self.logger.write("Reports page ready.")
        self.status_service.set_status("Reports page ready", busy=False)

    def _run_report_task(self, name: str, task) -> None:
        if self.loading_indicator.is_running:
            self.logger.write("Another report is already running.")
            return
        self.loading_indicator.start(f"Generating {name}...")
        self.status_service.set_status(f"Generating {name}...", busy=True)
        TaskRunner.run(task, lambda result: self._on_report_success(name, result), self._on_report_error, self.after)

    def _on_report_success(self, name: str, result) -> None:
        self.loading_indicator.stop(f"{name} completed")
        self.status_service.set_status(f"{name} completed", busy=False)
        if isinstance(result, str):
            self.logger.write(result)
        else:
            self.logger.write(f"{name} saved to:\n{result}")

    def _on_report_error(self, exc: Exception) -> None:
        self.loading_indicator.error("Report failed")
        self.status_service.set_status("Report error", busy=False)
        self.logger.write(f"Report error: {exc}")

    def _battery_report(self) -> None:
        self._run_report_task("Battery Report", lambda: self.action_service.save_battery_report(self.report_dir))

    def _network_report(self) -> None:
        self._run_report_task("Network Report", lambda: self.action_service.save_network_report(self.report_dir))

    def _installed_apps_report(self) -> None:
        self._run_report_task("Installed Apps Report", lambda: self.action_service.save_installed_apps_report(self.report_dir))

    def _heavy_process_report(self) -> None:
        self._run_report_task("Heavy Process Report", lambda: self.action_service.save_heavy_process_report(self.report_dir))

    def show_storage_health(self) -> None:
        self._run_report_task("Storage Health", self._get_storage_text)

    def _get_storage_text(self) -> str:
        disks = self.storage_health_service.get_storage_health()
        if not disks:
            return "No disk health information found."
        parts = ["===== STORAGE HEALTH ====="]
        for disk in disks:
            parts.append(disk.to_multiline_text())
            parts.append("-" * 50)
        return "\n".join(parts)
