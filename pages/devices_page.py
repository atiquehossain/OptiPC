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
        self.make_action_button(audio, "Open Sound Settings", self._open_sound_settings).pack(fill="x", padx=18, pady=6)
        self.make_action_button(audio, "Open Sound Control Panel", self._open_sound_panel).pack(fill="x", padx=18, pady=6)

        camera = self.make_card(wrapper, "Camera and Location", "Camera listing and privacy/location shortcuts")
        camera.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.make_action_button(camera, "List Cameras", self._list_cameras).pack(fill="x", padx=18, pady=6)
        self.make_action_button(camera, "Open Camera Settings", self._open_camera_settings).pack(fill="x", padx=18, pady=6)
        self.make_action_button(camera, "Open Privacy Settings", self._open_privacy_settings).pack(fill="x", padx=18, pady=6)
        self.make_action_button(camera, "Open Location Settings", self._open_location_settings).pack(fill="x", padx=18, pady=6)

        log_card = self.make_card(wrapper, "Device Output")
        log_card.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.logger.bind(log_box.append)
        self.logger.write("Devices page ready.")
        self.status_service.info("Devices page ready", toast=False)

    def _open_sound_settings(self) -> None:
        try:
            self.logger.write("Opening Sound Settings...")
            success = self.action_service.open_sound_settings()
            if success:
                self.status_service.success("Sound Settings opened", toast=True)
            else:
                self.status_service.error("Failed to open Sound Settings", toast=True)
        except Exception as e:
            self.logger.write(f"Failed to open Sound Settings: {e}")
            self.status_service.error("Failed to open Sound Settings", toast=True)

    def _open_sound_panel(self) -> None:
        try:
            self.logger.write("Opening Sound Control Panel...")
            success = self.action_service.open_sound_panel()
            if success:
                self.status_service.success("Sound Control Panel opened", toast=True)
            else:
                self.status_service.error("Failed to open Sound Control Panel", toast=True)
        except Exception as e:
            self.logger.write(f"Failed to open Sound Control Panel: {e}")
            self.status_service.error("Failed to open Sound Control Panel", toast=True)

    def _list_cameras(self) -> None:
        try:
            self.logger.write("Listing cameras...")
            cameras = self.action_service.list_cameras()
            self.logger.write(cameras)
            if cameras and cameras.strip():
                self.status_service.success("Camera list updated", toast=True)
            else:
                self.status_service.warning("No cameras found", toast=True)
        except Exception as e:
            self.logger.write(f"Failed to list cameras: {e}")
            self.status_service.error("Failed to list cameras", toast=True)

    def _open_camera_settings(self) -> None:
        try:
            self.logger.write("Opening Camera Settings...")
            success = self.action_service.open_camera_settings()
            if success:
                self.status_service.success("Camera Settings opened", toast=True)
            else:
                self.status_service.error("Failed to open Camera Settings", toast=True)
        except Exception as e:
            self.logger.write(f"Failed to open Camera Settings: {e}")
            self.status_service.error("Failed to open Camera Settings", toast=True)

    def _open_privacy_settings(self) -> None:
        try:
            self.logger.write("Opening Privacy Settings...")
            success = self.action_service.open_privacy_settings()
            if success:
                self.status_service.success("Privacy Settings opened", toast=True)
            else:
                self.status_service.error("Failed to open Privacy Settings", toast=True)
        except Exception as e:
            self.logger.write(f"Failed to open Privacy Settings: {e}")
            self.status_service.error("Failed to open Privacy Settings", toast=True)

    def _open_location_settings(self) -> None:
        try:
            self.logger.write("Opening Location Settings...")
            success = self.action_service.open_location_settings()
            if success:
                self.status_service.success("Location Settings opened", toast=True)
            else:
                self.status_service.error("Failed to open Location Settings", toast=True)
        except Exception as e:
            self.logger.write(f"Failed to open Location Settings: {e}")
            self.status_service.error("Failed to open Location Settings", toast=True)
