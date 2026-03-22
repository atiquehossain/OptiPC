from __future__ import annotations

import time

import customtkinter as ctk
import psutil

from widgets.base_mini_widget import BaseMiniWidget
from config.constants import FONT_SIZES


class NetworkSpeedWidget(BaseMiniWidget):
    """Floating widget that shows live download and upload speed."""

    def __init__(self, parent, x: int = 1020, y: int = 40):
        super().__init__(parent, "Internet Speed", size_category="medium", x=x, y=y, widget_key="network_speed")

        self.download_frame = self.create_panel(self.body)
        self.download_frame.pack(fill="x", pady=(0, 8))

        self.download_title = ctk.CTkLabel(
            self.download_frame,
            text="Download",
            font=ctk.CTkFont(size=FONT_SIZES["body"]),
        )
        self.download_title.pack(anchor="w", padx=12, pady=(8, 0))

        self.download_value = ctk.CTkLabel(
            self.download_frame,
            text="0 B/s",
            font=ctk.CTkFont(size=FONT_SIZES["page_title"], weight="bold"),
        )
        self.download_value.pack(anchor="w", padx=12, pady=(0, 8))

        self.upload_frame = self.create_panel(self.body)
        self.upload_frame.pack(fill="x", pady=(0, 8))

        self.upload_title = ctk.CTkLabel(
            self.upload_frame,
            text="Upload",
            font=ctk.CTkFont(size=FONT_SIZES["body"]),
        )
        self.upload_title.pack(anchor="w", padx=12, pady=(8, 0))

        self.upload_value = ctk.CTkLabel(
            self.upload_frame,
            text="0 B/s",
            font=ctk.CTkFont(size=FONT_SIZES["page_title"], weight="bold"),
        )
        self.upload_value.pack(anchor="w", padx=12, pady=(0, 8))

        self.note_label = ctk.CTkLabel(
            self.body,
            text="Live traffic, not ISP max speed",
            font=ctk.CTkFont(size=FONT_SIZES["small"]),
        )
        self.note_label.pack(anchor="w", pady=(4, 0))

        counters = psutil.net_io_counters()
        self.last_recv = counters.bytes_recv
        self.last_sent = counters.bytes_sent
        self.last_time = time.time()

        self.apply_theme()
        self.update_stats()

    def refresh_theme(self) -> None:
        if hasattr(self, 'download_frame'):
            self.download_frame.configure(fg_color=self.theme["panel"])
        if hasattr(self, 'upload_frame'):
            self.upload_frame.configure(fg_color=self.theme["panel"])
        for label_name in ("download_title", "upload_title", "note_label"):
            label = getattr(self, label_name, None)
            if label is not None:
                label.configure(text_color=self.theme["muted"])
        for label_name in ("download_value", "upload_value"):
            label = getattr(self, label_name, None)
            if label is not None:
                label.configure(text_color=self.theme["text"])

    @staticmethod
    def format_speed(bytes_per_second: float) -> str:
        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        value = float(bytes_per_second)
        for unit in units:
            if value < 1024 or unit == "GB/s":
                if unit == "B/s":
                    return f"{value:.0f} {unit}"
                return f"{value:.2f} {unit}"
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
