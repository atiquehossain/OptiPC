from __future__ import annotations

import getpass
import threading
from tkinter import messagebox

import customtkinter as ctk

from pages.base_page import BasePage
from services.recovery_service import RecoveryRequest, RecoveryService
from widgets.log_box import LogBox


class RecoveryPage(BasePage):
    def __init__(self, parent, logger, status_service, system_service, action_service, recovery_service: RecoveryService) -> None:
        super().__init__(parent, logger, status_service, system_service, action_service)
        self.recovery_service = recovery_service
        self.source_var = ctk.StringVar(value="")
        self.destination_var = ctk.StringVar(value="")
        self.mode_var = ctk.StringVar(value="regular")
        self.filter_var = ctk.StringVar(value=rf"\Users\{getpass.getuser()}\Documents\*")

    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        form = self.make_card(wrapper, "Deleted File Recovery", "Uses Microsoft's Windows File Recovery tool")
        form.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(form, text="Important: recover to a DIFFERENT drive. Stop using the source drive as much as possible.", justify="left", wraplength=460, text_color="orange").pack(anchor="w", padx=18, pady=(0, 18))

        drives = self.recovery_service.list_drives() or ["C:"]
        self.source_combo = ctk.CTkComboBox(form, values=drives, variable=self.source_var, state="readonly", width=240)
        self.destination_combo = ctk.CTkComboBox(form, values=drives, variable=self.destination_var, state="readonly", width=240)
        self.source_var.set(drives[0])
        self.destination_var.set(drives[1] if len(drives) > 1 else drives[0])

        ctk.CTkLabel(form, text="Source drive").pack(anchor="w", padx=18, pady=(0, 4))
        self.source_combo.pack(anchor="w", padx=18, pady=(0, 12))
        ctk.CTkLabel(form, text="Destination drive").pack(anchor="w", padx=18, pady=(0, 4))
        self.destination_combo.pack(anchor="w", padx=18, pady=(0, 12))
        ctk.CTkLabel(form, text="Mode").pack(anchor="w", padx=18, pady=(0, 4))
        mode_switch = ctk.CTkSegmentedButton(form, values=["regular", "extensive"], variable=self.mode_var)
        mode_switch.pack(anchor="w", padx=18, pady=(0, 12))
        mode_switch.set("regular")
        ctk.CTkLabel(form, text="Filter pattern").pack(anchor="w", padx=18, pady=(0, 4))
        ctk.CTkEntry(form, textvariable=self.filter_var, width=460).pack(anchor="w", padx=18, pady=(0, 8))
        ctk.CTkLabel(form, text=r"Example: \Users\YourName\Documents\*.docx", text_color="gray70").pack(anchor="w", padx=18, pady=(0, 18))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 18))
        row.grid_columnconfigure((0, 1, 2), weight=1)
        self.make_action_button(row, "Refresh Drives", self._refresh_drives).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(row, "Preview Command", self._preview_command).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.start_button = self.make_action_button(row, "Start Recovery", self._start_recovery)
        self.start_button.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        help_card = self.make_card(wrapper, "Mode Help", "Which mode should you use?")
        help_card.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(help_card, text="regular = best first try for recently deleted files on healthy NTFS drives.\n\nextensive = broader search for older deletions, formatted drives, or FAT/exFAT media.", justify="left", wraplength=460, text_color="gray75").pack(anchor="w", padx=18, pady=(0, 18))

        log_card = self.make_card(wrapper, "Recovery Output")
        log_card.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        self.log_box = LogBox(log_card)
        self.log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.logger.bind(self.log_box.append)
        self.logger.write("Recovery page loaded.")
        self.status_service.set_status("Recovery page ready", busy=False)

    def _refresh_drives(self) -> None:
        drives = self.recovery_service.list_drives() or ["C:"]
        self.source_combo.configure(values=drives)
        self.destination_combo.configure(values=drives)
        self.source_var.set(drives[0])
        self.destination_var.set(drives[1] if len(drives) > 1 else drives[0])
        self.logger.write(f"Drives detected: {', '.join(drives)}")

    def _create_request(self) -> RecoveryRequest:
        return RecoveryRequest(
            source_drive=self.source_var.get(),
            destination_drive=self.destination_var.get(),
            mode=self.mode_var.get(),
            filter_pattern=self.filter_var.get().strip(),
            auto_confirm=True,
        )

    def _preview_command(self) -> None:
        try:
            request = self._create_request()
            self.logger.write("Command preview:")
            self.logger.write(self.recovery_service.preview_command(request))
        except Exception as exc:
            messagebox.showerror("Invalid recovery request", str(exc))

    def _start_recovery(self) -> None:
        if not self.recovery_service.is_winfr_available():
            messagebox.showerror("Windows File Recovery not found", "Install 'Windows File Recovery' from the Microsoft Store first.")
            return
        try:
            request = self._create_request()
            preview = self.recovery_service.preview_command(request)
        except Exception as exc:
            messagebox.showerror("Invalid recovery request", str(exc))
            return

        if not messagebox.askyesno("Start recovery?", f"Command:\n\n{preview}\n\nContinue?"):
            return

        self.start_button.configure(state="disabled")
        self.status_service.set_status("Recovery in progress...", busy=True)
        self.logger.write("Recovery started...")
        self.logger.write(preview)
        threading.Thread(target=self._run_recovery_thread, args=(request,), daemon=True).start()

    def _run_recovery_thread(self, request: RecoveryRequest) -> None:
        try:
            exit_code = self.recovery_service.run_recovery(request, on_output=lambda line: self.after(0, self.logger.write, line))
            self.after(0, self.logger.write, f"Recovery finished with exit code: {exit_code}")
        except Exception as exc:
            self.after(0, self.logger.write, f"Recovery failed: {exc}")
        finally:
            self.after(0, lambda: self.start_button.configure(state="normal"))
            self.after(0, lambda: self.status_service.set_status("Recovery finished", busy=False))
