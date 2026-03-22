from __future__ import annotations

import platform
from typing import List

import customtkinter as ctk
import psutil

try:
    import GPUtil
except Exception:
    GPUtil = None

from widgets.base_mini_widget import BaseMiniWidget
from config.constants import FONT_SIZES


class CPUWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 40, y: int = 40):
        super().__init__(parent, "CPU Usage", 300, 190, x, y, widget_key="cpu")
        self.percent_label = ctk.CTkLabel(self.body, text="0%", font=ctk.CTkFont(size=FONT_SIZES["hero"], weight="bold"))
        self.percent_label.pack(pady=(4, 2))
        self.detail_label = ctk.CTkLabel(self.body, text="Cores: 0", font=ctk.CTkFont(size=FONT_SIZES["body"]))
        self.detail_label.pack()
        self.freq_label = ctk.CTkLabel(self.body, text="Frequency: N/A", font=ctk.CTkFont(size=FONT_SIZES["small"]))
        self.freq_label.pack(pady=(2, 2))
        self.progress = ctk.CTkProgressBar(self.body, width=220)
        self.progress.pack(fill="x", padx=4, pady=(12, 6))
        self.progress.set(0)
        self.apply_theme()
        self.update_stats()

    def refresh_theme(self) -> None:
        if hasattr(self, 'percent_label'):
            self.percent_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'detail_label'):
            self.detail_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'freq_label'):
            self.freq_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'progress'):
            self.progress.configure(progress_color=self.theme["accent"], fg_color=self.theme["progress_track"])

    def update_stats(self) -> None:
        if not self._running:
            return
        percent = psutil.cpu_percent(interval=None)
        logical = psutil.cpu_count(logical=True) or 0
        physical = psutil.cpu_count(logical=False) or logical
        freq = psutil.cpu_freq()
        freq_text = f"Frequency: {freq.current:.0f} MHz" if freq else "Frequency: N/A"
        self.percent_label.configure(text=f"{percent:.0f}%")
        self.detail_label.configure(text=f"Cores: {physical} physical / {logical} logical")
        self.freq_label.configure(text=freq_text)
        self.progress.set(percent / 100)
        self.after(1000, self.update_stats)


class RAMWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 360, y: int = 40):
        super().__init__(parent, "RAM Usage", 300, 180, x, y, widget_key="ram")
        self.percent_label = ctk.CTkLabel(self.body, text="0%", font=ctk.CTkFont(size=FONT_SIZES["hero"], weight="bold"))
        self.percent_label.pack(pady=(6, 2))
        self.detail_label = ctk.CTkLabel(self.body, text="0 GB / 0 GB", font=ctk.CTkFont(size=FONT_SIZES["body"]))
        self.detail_label.pack()
        self.avail_label = ctk.CTkLabel(self.body, text="Available: 0 GB", font=ctk.CTkFont(size=FONT_SIZES["small"]))
        self.avail_label.pack(pady=(2, 2))
        self.progress = ctk.CTkProgressBar(self.body, width=220)
        self.progress.pack(fill="x", padx=4, pady=(12, 6))
        self.progress.set(0)
        self.apply_theme()
        self.update_stats()

    @staticmethod
    def format_gb(value_bytes: int) -> str:
        return f"{value_bytes / (1024 ** 3):.1f} GB"

    def refresh_theme(self) -> None:
        if hasattr(self, 'percent_label'):
            self.percent_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'detail_label'):
            self.detail_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'avail_label'):
            self.avail_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'progress'):
            self.progress.configure(progress_color=self.theme["accent"], fg_color=self.theme["progress_track"])

    def update_stats(self) -> None:
        if not self._running:
            return
        mem = psutil.virtual_memory()
        self.percent_label.configure(text=f"{mem.percent:.0f}%")
        self.detail_label.configure(text=f"{self.format_gb(mem.used)} / {self.format_gb(mem.total)}")
        self.avail_label.configure(text=f"Available: {self.format_gb(mem.available)}")
        self.progress.set(mem.percent / 100)
        self.after(1000, self.update_stats)


class GPUWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 680, y: int = 40):
        super().__init__(parent, "GPU Usage", 320, 190, x, y, widget_key="gpu")
        self.name_label = ctk.CTkLabel(self.body, text="GPU: Detecting...", font=ctk.CTkFont(size=FONT_SIZES["label"], weight="bold"), wraplength=280, justify="left")
        self.name_label.pack(anchor="w", pady=(4, 6))
        self.percent_label = ctk.CTkLabel(self.body, text="N/A", font=ctk.CTkFont(size=FONT_SIZES["metric"], weight="bold"))
        self.percent_label.pack()
        self.mem_label = ctk.CTkLabel(self.body, text="Memory: N/A", font=ctk.CTkFont(size=FONT_SIZES["body"]))
        self.mem_label.pack(pady=(4, 6))
        self.progress = ctk.CTkProgressBar(self.body, width=220)
        self.progress.pack(fill="x", padx=4, pady=(8, 4))
        self.progress.set(0)
        self.note_label = ctk.CTkLabel(self.body, text="Some systems may not expose GPU usage", font=ctk.CTkFont(size=FONT_SIZES["small"]))
        self.note_label.pack()
        self.apply_theme()
        self.update_stats()

    def refresh_theme(self) -> None:
        if hasattr(self, 'name_label'):
            self.name_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'percent_label'):
            self.percent_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'mem_label'):
            self.mem_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'note_label'):
            self.note_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'progress'):
            self.progress.configure(progress_color=self.theme["accent"], fg_color=self.theme["progress_track"])

    def update_stats(self) -> None:
        if not self._running:
            return
        try:
            if GPUtil is None:
                raise RuntimeError("GPUtil not installed")
            gpus = GPUtil.getGPUs()
            if not gpus:
                raise RuntimeError("No GPU info available")
            gpu = gpus[0]
            load_percent = float(gpu.load) * 100.0
            self.name_label.configure(text=f"GPU: {gpu.name}")
            self.percent_label.configure(text=f"{load_percent:.0f}%")
            self.mem_label.configure(text=f"Memory: {gpu.memoryUsed:.0f} MB / {gpu.memoryTotal:.0f} MB")
            self.progress.set(load_percent / 100.0)
        except Exception:
            self.name_label.configure(text="GPU: Not available")
            self.percent_label.configure(text="N/A")
            self.mem_label.configure(text="Memory: N/A")
            self.progress.set(0)
        self.after(1500, self.update_stats)


class PartitionsWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 40, y: int = 250):
        super().__init__(parent, "Drive Partitions", 460, 300, x, y, widget_key="partitions")
        self.text = ctk.CTkTextbox(self.body, height=230, corner_radius=12)
        self.text.pack(fill="both", expand=True)
        self.apply_theme()
        self.update_stats()

    @staticmethod
    def format_gb(value_bytes: int) -> str:
        return f"{value_bytes / (1024 ** 3):.1f} GB"

    def refresh_theme(self) -> None:
        if hasattr(self, 'text'):
            self.style_textbox(self.text)

    def update_stats(self) -> None:
        if not self._running:
            return
        lines: List[str] = []
        for part in psutil.disk_partitions(all=False):
            device = part.device.rstrip("\\")
            opts = part.opts.lower()
            if "cdrom" in opts:
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                free_percent = 100.0 - usage.percent
                lines.append(
                    f"{device}  ({part.fstype})\n"
                    f"  Total: {self.format_gb(usage.total)}\n"
                    f"  Free : {self.format_gb(usage.free)} ({free_percent:.1f}%)\n"
                    f"  Used : {usage.percent:.1f}%\n"
                )
            except Exception:
                lines.append(f"{device}\n  Could not read usage.\n")
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", "\n".join(lines) if lines else "No partitions found.")
        self.text.configure(state="disabled")
        self.after(4000, self.update_stats)


class StorageWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 540, y: int = 250):
        super().__init__(parent, "SSD / HDD Summary", 470, 300, x, y, widget_key="storage")
        self.text = ctk.CTkTextbox(self.body, height=230, corner_radius=12)
        self.text.pack(fill="both", expand=True)
        self.apply_theme()
        self.update_stats()

    def refresh_theme(self) -> None:
        if hasattr(self, 'text'):
            self.style_textbox(self.text)

    def update_stats(self) -> None:
        if not self._running:
            return
        lines: List[str] = []
        try:
            for part in psutil.disk_partitions(all=False):
                device = part.device.rstrip("\\")
                opts = part.opts.lower()
                if "cdrom" in opts:
                    continue
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    lines.append(
                        f"Partition: {device}\n"
                        f"  File System: {part.fstype}\n"
                        f"  Mount: {part.mountpoint}\n"
                        f"  Total: {usage.total / (1024**3):.1f} GB\n"
                        f"  Free:  {usage.free / (1024**3):.1f} GB\n"
                        f"  Used:  {usage.percent:.1f}%\n"
                    )
                except Exception:
                    lines.append(f"Partition: {device}\n  Usage info unavailable.\n")
            lines.insert(0, f"OS: {platform.system()}\n")
        except Exception as exc:
            lines = [f"Storage info error: {exc}"]
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", "\n".join(lines))
        self.text.configure(state="disabled")
        self.after(5000, self.update_stats)
