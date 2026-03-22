from __future__ import annotations

import customtkinter as ctk

from pages.base_page import BasePage
from services.cleanup_service import CleanupService
from services.task_runner import TaskRunner
from widgets.loading_indicator import LoadingIndicator
from widgets.log_box import LogBox


class CleanupPage(BasePage):
    def __init__(self, parent, logger, status_service, system_service, action_service, cleanup_service: CleanupService) -> None:
        super().__init__(parent, logger, status_service, system_service, action_service)
        self.cleanup_service = cleanup_service

    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        tools = self.make_card(wrapper, "Cleanup Tools", "Safe maintenance actions")
        tools.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.action_buttons = []

        actions = [
            ("Quick Temp Cleanup", self._quick_cleanup),
            ("Deep Cleanup", self._deep_cleanup),
            ("Empty Recycle Bin", self._empty_recycle_bin),
            ("Open Disk Cleanup", self.action_service.open_disk_cleanup),
        ]
        for label, command in actions:
            button = self.make_action_button(tools, label, command)
            button.pack(fill="x", padx=18, pady=6)
            self.action_buttons.append(button)

        notes = self.make_card(wrapper, "Notes", "Keep cleanup realistic")
        notes.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(
            notes,
            text=(
                "Cleanup removes junk files and caches, but it does not magically fix every slow PC. "
                "Startup apps, overheating, failing drives, and malware can still be the real cause."
            ),
            justify="left",
            wraplength=420,
            text_color="gray75",
        ).pack(anchor="w", padx=18, pady=(0, 18))

        loading_card = self.make_card(wrapper, "Task Status", "Shows whether the app is busy")
        loading_card.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        self.loading_indicator = LoadingIndicator(loading_card)
        self.loading_indicator.pack(fill="x", padx=18, pady=(0, 18))

        log_card = self.make_card(wrapper, "Cleanup Output")
        log_card.grid(row=2, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.logger.bind(log_box.append)
        self.logger.write("Cleanup page ready.")
        self.status_service.set_status("Cleanup page ready", busy=False)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for button in getattr(self, "action_buttons", []):
            button.configure(state=state)

    def _threadsafe_output(self, message: str) -> None:
        self.after(0, self.logger.write, message)
        self.after(0, self.status_service.set_status, message, True)

    def _run_cleanup_task(self, title: str, task_callable) -> None:
        if self.loading_indicator.is_running:
            self.logger.write("Another cleanup task is already running.")
            return

        self.loading_indicator.start(f"{title}...")
        self._set_buttons_enabled(False)
        self.logger.write(f"{title} started.")
        self.status_service.set_status(f"{title}...", busy=True)

        TaskRunner.run(
            task=task_callable,
            on_success=lambda result: self._on_cleanup_success(title, result),
            on_error=self._on_cleanup_error,
            ui_after=self.after,
        )

    def _on_cleanup_success(self, title: str, result) -> None:
        self.loading_indicator.stop(f"{title} completed")
        self._set_buttons_enabled(True)

        if isinstance(result, dict):
            removed = result.get("removed", 0)
            failed = result.get("failed", 0)
            self.logger.write(f"{title} completed. Removed: {removed}, Failed: {failed}")
        else:
            self.logger.write(str(result))

        self.status_service.set_status(f"{title} completed", busy=False)

    def _on_cleanup_error(self, exc: Exception) -> None:
        self.loading_indicator.error("Cleanup failed")
        self._set_buttons_enabled(True)
        self.logger.write(f"Cleanup error: {exc}")
        self.status_service.set_status("Cleanup error", busy=False)

    def _quick_cleanup(self) -> None:
        self._run_cleanup_task(
            "Quick Cleanup",
            lambda: self.cleanup_service.quick_cleanup(self._threadsafe_output),
        )

    def _deep_cleanup(self) -> None:
        def task():
            result = self.cleanup_service.deep_cleanup(self._threadsafe_output)
            recycle_message = self.action_service.empty_recycle_bin()
            self._threadsafe_output(recycle_message)
            return result

        self._run_cleanup_task("Deep Cleanup", task)

    def _empty_recycle_bin(self) -> None:
        message = self.action_service.empty_recycle_bin()
        self.logger.write(message)
        self.status_service.set_status("Recycle Bin action finished", busy=False)
