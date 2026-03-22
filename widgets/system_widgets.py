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


class CPUWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 40, y: int = 40):
        super().__init__(parent, "CPU Usage", 280, 150, x, y)
        self.percent_label = ctk.CTkLabel(self.body, text="0%", font=ctk.CTkFont(size=30, weight="bold"))
        self.percent_label.pack(pady=(6, 2))
        self.detail_label = ctk.CTkLabel(self.body, text="Cores: 0", text_color="gray75", font=ctk.CTkFont(size=13))
        self.detail_label.pack()
        self.progress = ctk.CTkProgressBar(self.body, width=220)
        self.progress.pack(fill="x", padx=4, pady=(12, 6))
        self.progress.set(0)
        self.update_stats()

    def update_stats(self) -> None:
        if not self._running:
            return
        percent = psutil.cpu_percent(interval=None)
        cores = psutil.cpu_count(logical=True) or 0
        self.percent_label.configure(text=f"{percent:.0f}%")
        self.detail_label.configure(text=f"Cores: {cores}")
        self.progress.set(percent / 100)
        self.after(1000, self.update_stats)


class RAMWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 340, y: int = 40):
        super().__init__(parent, "RAM Usage", 280, 150, x, y)
        self.percent_label = ctk.CTkLabel(self.body, text="0%", font=ctk.CTkFont(size=30, weight="bold"))
        self.percent_label.pack(pady=(6, 2))
        self.detail_label = ctk.CTkLabel(self.body, text="0 GB / 0 GB", text_color="gray75", font=ctk.CTkFont(size=13))
        self.detail_label.pack()
        self.progress = ctk.CTkProgressBar(self.body, width=220)
        self.progress.pack(fill="x", padx=4, pady=(12, 6))
        self.progress.set(0)
        self.update_stats()

    @staticmethod
    def format_gb(value_bytes: int) -> str:
        return f"{value_bytes / (1024 ** 3):.1f} GB"

    def update_stats(self) -> None:
        if not self._running:
            return
        mem = psutil.virtual_memory()
        self.percent_label.configure(text=f"{mem.percent:.0f}%")
        self.detail_label.configure(text=f"{self.format_gb(mem.used)} / {self.format_gb(mem.total)}")
        self.progress.set(mem.percent / 100)
        self.after(1000, self.update_stats)


class GPUWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 640, y: int = 40):
        super().__init__(parent, "GPU Usage", 300, 170, x, y)
        self.name_label = ctk.CTkLabel(self.body, text="GPU: Detecting...", font=ctk.CTkFont(size=14, weight="bold"), wraplength=250, justify="left")
        self.name_label.pack(anchor="w", pady=(4, 6))
        self.percent_label = ctk.CTkLabel(self.body, text="N/A", font=ctk.CTkFont(size=28, weight="bold"))
        self.percent_label.pack()
        self.mem_label = ctk.CTkLabel(self.body, text="Memory: N/A", text_color="gray75", font=ctk.CTkFont(size=13))
        self.mem_label.pack(pady=(4, 6))
        self.progress = ctk.CTkProgressBar(self.body, width=220)
        self.progress.pack(fill="x", padx=4, pady=(8, 4))
        self.progress.set(0)
        self.note_label = ctk.CTkLabel(self.body, text="Some systems may not expose GPU usage", text_color="gray65", font=ctk.CTkFont(size=11))
        self.note_label.pack()
        self.update_stats()

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
    def __init__(self, parent, x: int = 40, y: int = 230):
        super().__init__(parent, "Drive Partitions", 430, 280, x, y)
        self.text = ctk.CTkTextbox(self.body, height=210, corner_radius=12)
        self.text.pack(fill="both", expand=True)
        self.text.configure(state="disabled")
        self.update_stats()

    @staticmethod
    def format_gb(value_bytes: int) -> str:
        return f"{value_bytes / (1024 ** 3):.1f} GB"

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
    def __init__(self, parent, x: int = 500, y: int = 230):
        super().__init__(parent, "SSD / HDD Summary", 440, 280, x, y)
        self.text = ctk.CTkTextbox(self.body, height=210, corner_radius=12)
        self.text.pack(fill="both", expand=True)
        self.text.configure(state="disabled")
        self.update_stats()

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
