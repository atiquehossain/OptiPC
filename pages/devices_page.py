from __future__ import annotations

import customtkinter as ctk

from pages.base_page import BasePage
from widgets.log_box import LogBox


class DevicesPage(BasePage):
    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        audio = self.make_card(wrapper, "Audio Devices", "Speaker and microphone shortcuts")
        audio.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.make_action_button(audio, "Open Sound Settings", self.action_service.open_sound_settings).pack(fill="x", padx=18, pady=6)
        self.make_action_button(audio, "Open Sound Control Panel", self.action_service.open_sound_panel).pack(fill="x", padx=18, pady=6)

        camera = self.make_card(wrapper, "Camera Tools", "Camera settings and listing")
        camera.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.make_action_button(camera, "List Cameras", self._list_cameras).pack(fill="x", padx=18, pady=6)
        self.make_action_button(camera, "Open Camera Settings", self.action_service.open_camera_settings).pack(fill="x", padx=18, pady=6)
        self.make_action_button(camera, "Open Privacy Settings", self.action_service.open_privacy_settings).pack(fill="x", padx=18, pady=6)

        log_card = self.make_card(wrapper, "Device Output")
        log_card.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.logger.bind(log_box.append)
        self.logger.write("Devices page ready.")
        self.status_service.set_status("Devices page ready", busy=False)

    def _list_cameras(self) -> None:
        self.logger.write(self.action_service.list_cameras())
