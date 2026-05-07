from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from pages.base_page import BasePage
from services.cleanup_service import CleanupDeleteResult, CleanupScanResult, CleanupService
from services.task_runner import TaskRunner
from widgets.loading_indicator import LoadingIndicator
from widgets.log_box import LogBox


class CleanupPage(BasePage):
    def __init__(self, parent, logger, status_service, system_service, action_service, cleanup_service: CleanupService) -> None:
        super().__init__(parent, logger, status_service, system_service, action_service)
        self.cleanup_service = cleanup_service
        self.category_vars: dict[str, tk.BooleanVar] = {}
        self.category_size_labels: dict[str, ctk.CTkLabel] = {}
        self.category_defs = self.cleanup_service.get_categories()
        self.last_scan: CleanupScanResult | None = None

    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        tools = self.make_card(wrapper, "Cleanup Scanner", "Scan first, then clean selected junk")
        tools.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.action_buttons = []

        self.summary_label = ctk.CTkLabel(
            tools,
            text="No scan yet. Safe categories are selected by default.",
            justify="left",
            wraplength=460,
            text_color="gray75",
        )
        self.summary_label.pack(anchor="w", padx=18, pady=(0, 14))

        primary_actions = ctk.CTkFrame(tools, fg_color="transparent")
        primary_actions.pack(fill="x", padx=18, pady=(0, 10))
        primary_actions.grid_columnconfigure((0, 1), weight=1)

        self._add_action_button(primary_actions, "Scan Junk", self._scan_cleanup, row=0, column=0)
        self._add_action_button(primary_actions, "Clean Selected", self._clean_selected, row=0, column=1)
        self._add_action_button(primary_actions, "Quick Temp Cleanup", self._quick_cleanup, row=1, column=0)
        self._add_action_button(primary_actions, "Clean Safe Defaults", self._deep_cleanup, row=1, column=1)

        selection_actions = ctk.CTkFrame(tools, fg_color="transparent")
        selection_actions.pack(fill="x", padx=18, pady=(0, 10))
        selection_actions.grid_columnconfigure((0, 1, 2), weight=1)

        self._add_action_button(selection_actions, "Select Safe", self._select_defaults, row=0, column=0)
        self._add_action_button(selection_actions, "Select All", self._select_all, row=0, column=1)
        self._add_action_button(selection_actions, "Clear", self._clear_selection, row=0, column=2)

        utility_actions = ctk.CTkFrame(tools, fg_color="transparent")
        utility_actions.pack(fill="x", padx=18, pady=(0, 18))
        utility_actions.grid_columnconfigure((0, 1), weight=1)

        self._add_action_button(utility_actions, "Empty Recycle Bin", self._empty_recycle_bin, row=0, column=0)
        self._add_action_button(utility_actions, "Open Disk Cleanup", self.action_service.open_disk_cleanup, row=0, column=1)

        categories = self.make_card(wrapper, "Cleanup Categories", "Safe is selected automatically; Review and Advanced are opt-in")
        categories.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.category_frame = ctk.CTkScrollableFrame(categories, fg_color="transparent", height=360)
        self.category_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self._build_category_rows()

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
        self.status_service.info("Cleanup page ready", toast=False)
        self._refresh_selected_summary()

    def _add_action_button(self, parent, label: str, command, *, row: int, column: int) -> None:
        button = self.make_action_button(parent, label, command)
        button.grid(row=row, column=column, padx=6, pady=6, sticky="ew")
        self.action_buttons.append(button)

    def _build_category_rows(self) -> None:
        for index, category in enumerate(self.category_defs):
            row = ctk.CTkFrame(self.category_frame, fg_color="transparent")
            row.grid(row=index, column=0, sticky="ew", pady=(0, 12))
            row.grid_columnconfigure(0, weight=1)

            var = tk.BooleanVar(value=category.default_selected)
            self.category_vars[category.key] = var

            header = ctk.CTkFrame(row, fg_color="transparent")
            header.grid(row=0, column=0, sticky="ew")
            header.grid_columnconfigure(0, weight=1)

            checkbox = ctk.CTkCheckBox(
                header,
                text=category.title,
                variable=var,
                command=self._refresh_selected_summary,
            )
            checkbox.grid(row=0, column=0, sticky="w")

            badge = ctk.CTkLabel(
                header,
                text=category.safety,
                width=78,
                corner_radius=12,
                fg_color=self._safety_color(category.safety),
                text_color="#ffffff",
            )
            badge.grid(row=0, column=1, padx=(8, 0), sticky="e")

            ctk.CTkLabel(
                row,
                text=category.description,
                justify="left",
                wraplength=430,
                text_color="gray70",
            ).grid(row=1, column=0, sticky="w", pady=(4, 0))

            size_label = ctk.CTkLabel(row, text="Scan to estimate size", text_color="gray60")
            size_label.grid(row=2, column=0, sticky="w", pady=(2, 0))
            self.category_size_labels[category.key] = size_label

    @staticmethod
    def _safety_color(safety: str) -> str:
        return {
            "Safe": "#10b981",
            "Review": "#f59e0b",
            "Advanced": "#ef4444",
        }.get(safety, "#64748b")

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for button in getattr(self, "action_buttons", []):
            button.configure(state=state)

    def _threadsafe_output(self, message: str) -> None:
        self.after(0, self.logger.write, message)
        self.after(0, self.status_service.busy, message)

    def _selected_keys(self) -> list[str]:
        return [key for key, var in self.category_vars.items() if var.get()]

    def _selected_advanced_categories(self, keys: list[str]) -> list[str]:
        selected = set(keys)
        return [
            category.title
            for category in self.category_defs
            if category.key in selected and category.safety == "Advanced"
        ]

    def _confirm_advanced_cleanup(self, keys: list[str]) -> bool:
        advanced = self._selected_advanced_categories(keys)
        if not advanced:
            return True
        category_text = "\n".join(f"- {title}" for title in advanced)
        return messagebox.askyesno(
            "Confirm Advanced Cleanup",
            (
                "Advanced cleanup can remove system caches that Windows may need "
                "to rebuild later.\n\n"
                f"Selected advanced categories:\n{category_text}\n\n"
                "Continue with cleanup?"
            ),
            parent=self.winfo_toplevel(),
        )

    def _select_defaults(self) -> None:
        defaults = set(self.cleanup_service.get_default_category_keys())
        for key, var in self.category_vars.items():
            var.set(key in defaults)
        self._refresh_selected_summary()

    def _select_all(self) -> None:
        for var in self.category_vars.values():
            var.set(True)
        self._refresh_selected_summary()

    def _clear_selection(self) -> None:
        for var in self.category_vars.values():
            var.set(False)
        self._refresh_selected_summary()

    def _refresh_selected_summary(self) -> None:
        selected = self._selected_keys()
        if self.last_scan is None:
            self.summary_label.configure(text=f"{len(selected)} category(s) selected. Run Scan Junk to preview size.")
            return

        count = self.last_scan.selected_total_count(selected)
        size = self.last_scan.selected_total_size(selected)
        self.summary_label.configure(
            text=(
                f"{len(selected)} category(s) selected. "
                f"Preview: {count} item(s), {self.cleanup_service.format_bytes(size)}."
            )
        )

    def _run_cleanup_task(self, title: str, task_callable) -> None:
        if self.loading_indicator.is_running:
            self.logger.write("Another cleanup task is already running.")
            return

        self.loading_indicator.start(f"{title}...")
        self._set_buttons_enabled(False)
        self.logger.write(f"{title} started.")
        self.status_service.busy(f"{title}...")

        TaskRunner.run(
            task=task_callable,
            on_success=lambda result: self._on_cleanup_success(title, result),
            on_error=self._on_cleanup_error,
            ui_after=self.after,
        )

    def _on_cleanup_success(self, title: str, result) -> None:
        self.loading_indicator.stop(f"{title} completed")
        self._set_buttons_enabled(True)

        if isinstance(result, CleanupScanResult):
            self._on_scan_success(result)
        elif isinstance(result, CleanupDeleteResult):
            self._on_delete_success(result)
        elif isinstance(result, dict):
            removed = result.get("removed", 0)
            failed = result.get("failed", 0)
            skipped = result.get("skipped", 0)
            bytes_freed = result.get("bytes_freed", 0)
            self.logger.write(
                f"{title} completed. Removed: {removed}, Failed: {failed}, "
                f"Skipped: {skipped}, Freed: {self.cleanup_service.format_bytes(bytes_freed)}"
            )
        else:
            self.logger.write(str(result))

        self.status_service.success(f"{title} completed", toast=True)

    def _on_scan_success(self, result: CleanupScanResult) -> None:
        self.last_scan = result
        for key, scan in result.categories.items():
            label = self.category_size_labels.get(key)
            if label is None:
                continue
            label.configure(
                text=(
                    f"{scan.count} item(s) | {self.cleanup_service.format_bytes(scan.size)}"
                    f" | skipped {scan.skipped}"
                )
            )

        self.logger.write(
            f"Scan completed. Found {result.total_count} item(s), "
            f"{self.cleanup_service.format_bytes(result.total_size)} total."
        )
        for scan in result.categories.values():
            if scan.count or scan.skipped or scan.errors:
                self.logger.write(
                    f"- {scan.category.title}: {scan.count} item(s), "
                    f"{self.cleanup_service.format_bytes(scan.size)}, skipped {scan.skipped}"
                )
        self._refresh_selected_summary()

    def _on_delete_success(self, result: CleanupDeleteResult) -> None:
        cleaned_keys = set(result.scanned.categories.keys())
        for key in cleaned_keys:
            label = self.category_size_labels.get(key)
            if label is not None:
                label.configure(text="Cleaned. Scan again to refresh.")
        self.last_scan = None
        self.logger.write(
            f"Cleanup completed. Removed: {result.removed}, Failed: {result.failed}, "
            f"Skipped: {result.skipped}, Freed: {self.cleanup_service.format_bytes(result.bytes_freed)}"
        )
        self.summary_label.configure(
            text=f"Freed {self.cleanup_service.format_bytes(result.bytes_freed)}. Run Scan Junk to preview again."
        )

    def _on_cleanup_error(self, exc: Exception) -> None:
        self.loading_indicator.error("Cleanup failed")
        self._set_buttons_enabled(True)
        self.logger.write(f"Cleanup error: {exc}")
        self.status_service.error("Cleanup error", toast=True)

    def _scan_cleanup(self) -> None:
        self._run_cleanup_task(
            "Cleanup Scan",
            lambda: self.cleanup_service.scan_cleanup(self._threadsafe_output),
        )

    def _clean_selected(self) -> None:
        selected = self._selected_keys()
        if not selected:
            self.logger.write("No cleanup categories selected.")
            self.status_service.warning("Select at least one cleanup category", toast=True)
            return
        if not self._confirm_advanced_cleanup(selected):
            self.logger.write("Advanced cleanup cancelled by user.")
            self.status_service.info("Advanced cleanup cancelled", toast=True)
            return
        self._run_cleanup_task(
            "Selected Cleanup",
            lambda: self.cleanup_service.clean_categories(selected, self._threadsafe_output),
        )

    def _quick_cleanup(self) -> None:
        self._run_cleanup_task(
            "Quick Temp Cleanup",
            lambda: self.cleanup_service.clean_categories(["user_temp"], self._threadsafe_output),
        )

    def _deep_cleanup(self) -> None:
        self._run_cleanup_task(
            "Safe Cleanup",
            lambda: self.cleanup_service.clean_categories(
                self.cleanup_service.get_default_category_keys(),
                self._threadsafe_output,
            ),
        )

    def _empty_recycle_bin(self) -> None:
        message = self.action_service.empty_recycle_bin()
        self.logger.write(message)
        self.status_service.success("Recycle Bin action finished", toast=True)
