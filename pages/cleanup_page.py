from __future__ import annotations

import customtkinter as ctk

from pages.base_page import BasePage
from services.task_runner import TaskRunner
from widgets.loading_indicator import LoadingIndicator
from widgets.log_box import LogBox


class CleanupPage(BasePage):
    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        tools = self.make_card(wrapper, "Cleanup Tools", "Safe maintenance actions")
        tools.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.action_buttons = []

        actions = [
            ("Quick Temp Cleanup", self._quick_cleanup),
            ("Empty Recycle Bin", self._empty_recycle_bin),
            ("Open Disk Cleanup", self.action_service.open_disk_cleanup),
        ]
        for label, command in actions:
            btn = self.make_action_button(tools, label, command)
            btn.pack(fill="x", padx=18, pady=6)
            self.action_buttons.append(btn)

        notes = self.make_card(wrapper, "Notes", "Keep cleanup realistic")
        notes.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(notes, text="Cleanup can remove junk files, but it does not magically fix every slow PC. Hardware, startup apps, overheating, or malware can still be the real cause.", justify="left", wraplength=420, text_color="gray75").pack(anchor="w", padx=18, pady=(0, 18))

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

    def _quick_cleanup(self) -> None:
        if self.loading_indicator.is_running:
            return
        self.loading_indicator.start("Cleaning temp files...")
        self._set_buttons_enabled(False)
        self.status_service.set_status("Running Quick Cleanup...", busy=True)
        self.logger.write("Cleanup started...")
        TaskRunner.run(self.system_service.quick_cleanup_temp, self._on_cleanup_success, self._on_cleanup_error, self.after)

    def _on_cleanup_success(self, result) -> None:
        removed, failed = result
        self.loading_indicator.stop("Cleanup completed")
        self._set_buttons_enabled(True)
        self.logger.write(f"Temp cleanup completed. Removed: {removed}, Failed: {failed}")
        self.status_service.set_status("Quick Cleanup completed", busy=False)

    def _on_cleanup_error(self, exc: Exception) -> None:
        self.loading_indicator.error("Cleanup failed")
        self._set_buttons_enabled(True)
        self.logger.write(f"Cleanup error: {exc}")
        self.status_service.set_status("Cleanup error", busy=False)

    def _empty_recycle_bin(self) -> None:
        self.logger.write(self.action_service.empty_recycle_bin())
        self.status_service.set_status("Recycle Bin action finished", busy=False)
