from __future__ import annotations

import customtkinter as ctk

from pages.base_page import BasePage
from widgets.log_box import LogBox


class RepairPage(BasePage):
    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        tools = self.make_card(wrapper, "Repair Tools", "Admin will be requested only for these tools")
        tools.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        buttons = [
            ("Run SFC", lambda: self._run_admin("sfc /scannow")),
            ("Run DISM", lambda: self._run_admin("DISM /Online /Cleanup-Image /RestoreHealth")),
            ("Run CHKDSK Scan", lambda: self._run_admin("chkdsk C: /scan")),
        ]
        for label, command in buttons:
            self.make_action_button(tools, label, command).pack(fill="x", padx=18, pady=6)

        info = self.make_card(wrapper, "Important", "Why these are special")
        info.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(info, text="The app itself runs in normal mode. Only these commands ask Windows for Administrator permission when needed. A separate command window may open.", justify="left", wraplength=420, text_color="gray75").pack(anchor="w", padx=18, pady=(0, 18))

        log_card = self.make_card(wrapper, "Repair Output")
        log_card.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.logger.bind(log_box.append)
        self.logger.write("Repair page ready.")
        self.status_service.set_status("Repair page ready", busy=False)

    def _run_admin(self, command: str) -> None:
        self.logger.write(self.action_service.run_elevated_command(command))
        self.status_service.set_status("Admin command launched", busy=False)
