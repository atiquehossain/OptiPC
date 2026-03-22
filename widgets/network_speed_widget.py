from __future__ import annotations

import time

import customtkinter as ctk
import psutil

from widgets.base_mini_widget import BaseMiniWidget


class NetworkSpeedWidget(BaseMiniWidget):
    """Floating widget that shows live download and upload traffic."""

    def __init__(self, parent, x: int = 980, y: int = 40):
        super().__init__(parent, "Internet Speed", 340, 230, x, y)

        self.download_frame = ctk.CTkFrame(self.body, corner_radius=12)
        self.download_frame.pack(fill="x", pady=(0, 8))

        self.download_title = ctk.CTkLabel(
            self.download_frame,
            text="Download",
            text_color="gray75",
            font=ctk.CTkFont(size=13),
        )
        self.download_title.pack(anchor="w", padx=12, pady=(8, 0))

        self.download_value = ctk.CTkLabel(
            self.download_frame,
            text="0 B/s",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        self.download_value.pack(anchor="w", padx=12, pady=(0, 8))

        self.upload_frame = ctk.CTkFrame(self.body, corner_radius=12)
        self.upload_frame.pack(fill="x", pady=(0, 8))

        self.upload_title = ctk.CTkLabel(
            self.upload_frame,
            text="Upload",
            text_color="gray75",
            font=ctk.CTkFont(size=13),
        )
        self.upload_title.pack(anchor="w", padx=12, pady=(8, 0))

        self.upload_value = ctk.CTkLabel(
            self.upload_frame,
            text="0 B/s",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        self.upload_value.pack(anchor="w", padx=12, pady=(0, 8))

        self.note_label = ctk.CTkLabel(
            self.body,
            text="Live traffic, not ISP max speed",
            text_color="gray65",
            font=ctk.CTkFont(size=11),
        )
        self.note_label.pack(anchor="w", pady=(4, 0))

        counters = psutil.net_io_counters()
        self.last_recv = counters.bytes_recv
        self.last_sent = counters.bytes_sent
        self.last_time = time.time()

        self.update_stats()

    @staticmethod
    def format_speed(bytes_per_second: float) -> str:
        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        value = float(bytes_per_second)
        for unit in units:
            if value < 1024 or unit == "GB/s":
                return f"{value:.0f} {unit}" if unit == "B/s" else f"{value:.2f} {unit}"
            value /= 1024
        return f"{value:.2f} GB/s"

    def update_stats(self) -> None:
        if not self._running:
            return

        current_time = time.time()
        counters = psutil.net_io_counters()
        time_diff = max(current_time - self.last_time, 0.001)

        recv_diff = counters.bytes_recv - self.last_recv
        sent_diff = counters.bytes_sent - self.last_sent

        download_speed = max(recv_diff / time_diff, 0.0)
        upload_speed = max(sent_diff / time_diff, 0.0)

        self.download_value.configure(text=self.format_speed(download_speed))
        self.upload_value.configure(text=self.format_speed(upload_speed))

        self.last_recv = counters.bytes_recv
        self.last_sent = counters.bytes_sent
        self.last_time = current_time

        self.after(1000, self.update_stats)
