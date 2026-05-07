from __future__ import annotations

import json
import socket
import subprocess
import threading
import time
import tkinter as tk
import tempfile
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path
from typing import Callable

import customtkinter as ctk
import psutil

try:
    import GPUtil
except Exception:
    GPUtil = None

from config.widget_specs import widget_default_size, widget_spec
from config.widget_style import widget_text_role
from services.cleanup_service import CleanupService
from widgets.base_mini_widget import BaseMiniWidget
from widgets.responsive_layout import register_label, responsive_font_size, tk_font_weight
from widgets.window_interactions import current_widget_geometry, is_control_widget, set_widget_cursor


class SmartWidgetBase(BaseMiniWidget):
    def __init__(
        self,
        parent,
        title: str | None,
        widget_key: str,
        *,
        width: int | None = None,
        height: int | None = None,
        x: int = 80,
        y: int = 80,
        theme_name: str | None = None,
        size_category: str | None = None,
    ) -> None:
        spec = widget_spec(widget_key)
        category = size_category or spec.size_category
        resolved_title = title or spec.title
        size = widget_default_size(widget_key, category)
        width = int(width if width is not None else size["width"])
        height = int(height if height is not None else size["height"])
        self._theme_labels: list[tuple[ctk.CTkLabel, str, str, str]] = []
        self._theme_panels: list[ctk.CTkFrame] = []
        self._theme_buttons: list[ctk.CTkButton] = []
        self._theme_progress: list[ctk.CTkProgressBar] = []
        self._theme_canvases: list[tk.Canvas] = []
        self._toolbar_buttons: list[ctk.CTkButton] = []
        self._default_width = width
        self._default_height = height
        self._compact_height = 92
        self._expanded_geometry: str | None = None
        self._is_compact = False
        self._latest_compact_text = ""
        self._scheduled_after_ids: set[str] = set()
        self.MIN_WIDTH = max(150, int(width * 0.82))
        self.MIN_HEIGHT = max(150, int(height * 0.84))
        self.MAX_WIDTH = max(width + 120, int(width * 1.45))
        self.MAX_HEIGHT = max(height + 90, int(height * 1.35))
        super().__init__(
            parent,
            resolved_title,
            width=width,
            height=height,
            x=x,
            y=y,
            widget_key=widget_key,
            size_category=category,
        )
        if theme_name:
            self.current_theme_name = theme_name
        self._install_widget_chrome()

    def label(
        self,
        parent,
        text: str,
        *,
        role: str = "body",
        size_key: str | None = None,
        weight: str | None = None,
        color: str | None = None,
    ) -> ctk.CTkLabel:
        text_role = widget_text_role(role)
        resolved_size_key = size_key or text_role.size_key
        resolved_weight = weight or text_role.weight
        resolved_color = color or text_role.color_key
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=responsive_font_size(self, resolved_size_key), weight=tk_font_weight(resolved_weight)),
            text_color=self.theme.get(resolved_color, self.theme["text"]),
            wraplength=max(90, self._default_width - 36),
            justify="left",
            anchor="w",
        )
        register_label(self, label, resolved_size_key, resolved_weight)
        self._theme_labels.append((label, resolved_color, resolved_size_key, resolved_weight))
        self._bind_widget_chrome(label)
        return label

    def panel(self, parent) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(parent, corner_radius=14, fg_color=self.theme["panel"])
        self._theme_panels.append(panel)
        self._bind_widget_chrome(panel)
        return panel

    def button(self, parent, text: str, command: Callable[[], None]) -> ctk.CTkButton:
        button = ctk.CTkButton(
            parent,
            text=text,
            height=30,
            corner_radius=12,
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text"],
            command=command,
        )
        self._theme_buttons.append(button)
        self._bind_widget_chrome(button)
        return button

    def progress(self, parent) -> ctk.CTkProgressBar:
        progress = ctk.CTkProgressBar(
            parent,
            height=8,
            corner_radius=4,
            progress_color=self.widget_accent_color(),
            fg_color=self.theme["progress_track"],
        )
        progress.set(0)
        self._theme_progress.append(progress)
        self._bind_widget_chrome(progress)
        return progress

    def canvas(self, parent, *, height: int = 56) -> tk.Canvas:
        canvas = tk.Canvas(parent, height=height, bg=self.theme["panel"], highlightthickness=0, bd=0)
        self._theme_canvases.append(canvas)
        self._bind_widget_chrome(canvas)
        return canvas

    def _install_widget_chrome(self) -> None:
        self.compact_label = ctk.CTkLabel(
            self.topbar,
            text="",
            font=ctk.CTkFont(size=responsive_font_size(self, "tiny")),
            text_color=self.theme.get("muted", self.theme["text"]),
        )
        self.compact_label.pack(side="left", padx=(8, 0))

        self.menu_button = ctk.CTkButton(
            self.topbar,
            text="...",
            width=28,
            height=28,
            corner_radius=14,
            command=self._show_menu_from_button,
        )
        self.menu_button.pack(side="right", padx=(4, 0))

        self.compact_button = ctk.CTkButton(
            self.topbar,
            text="-",
            width=28,
            height=28,
            corner_radius=14,
            command=self.toggle_compact,
        )
        self.compact_button.pack(side="right", padx=(4, 0))
        self._toolbar_buttons.extend([self.menu_button, self.compact_button])
        self._context_menu = tk.Menu(self, tearoff=0)

        for widget in (self, self.container, self.topbar, self.title_label, self.body, self.close_button):
            self._bind_widget_chrome(widget)
        self.refresh_theme()

    def _bind_widget_chrome(self, widget) -> None:
        try:
            if is_control_widget(widget):
                set_widget_cursor(widget, "arrow", recursive=True)
            else:
                self._bind_drag_target(widget)
            widget.bind("<Button-3>", self._show_context_menu, add="+")
            widget.bind("<Enter>", self._on_hover_enter, add="+")
            widget.bind("<Leave>", self._on_hover_leave, add="+")
        except Exception:
            pass

    def _on_hover_enter(self, _event=None) -> None:
        self._set_widget_border(active=True)

    def _on_hover_leave(self, _event=None) -> None:
        pointer_x = self.winfo_pointerx()
        pointer_y = self.winfo_pointery()
        left = self.winfo_rootx()
        top = self.winfo_rooty()
        if left <= pointer_x <= left + self.winfo_width() and top <= pointer_y <= top + self.winfo_height():
            return
        self._set_widget_border(active=False)

    def _set_widget_border(self, *, active: bool) -> None:
        color = self.widget_accent_color() if active else self.theme.get("border", self.theme.get("progress_track", self.theme["button"]))
        try:
            self.container.configure(border_width=1, border_color=color)
        except Exception:
            pass

    def _show_menu_from_button(self) -> None:
        self._build_context_menu()
        x = self.menu_button.winfo_rootx()
        y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
        self._context_menu.tk_popup(x, y)

    def _show_context_menu(self, event) -> str:
        self._build_context_menu()
        self._context_menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def _build_context_menu(self) -> None:
        self._context_menu.delete(0, "end")
        self._context_menu.add_command(
            label="Expand" if self._is_compact else "Compact",
            command=self.toggle_compact,
        )
        self._context_menu.add_command(label="Reset Size", command=self.reset_widget_size)
        self._context_menu.add_command(label="Bring to Front", command=self.bring_to_front)
        self._context_menu.add_separator()
        self._context_menu.add_command(label="Hide Widget", command=self.hide_widget)

    def bring_to_front(self) -> None:
        self.deiconify()
        self.lift()
        try:
            self.focus_force()
        except Exception:
            pass

    def reset_widget_size(self) -> None:
        self._is_compact = False
        self.body.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.compact_button.configure(text="-")
        self.geometry(f"{self._default_width}x{self._default_height}+{self.winfo_x()}+{self.winfo_y()}")
        self.after(0, self._apply_constrained_geometry)

    def toggle_compact(self) -> None:
        if self._is_compact:
            self.expand_widget()
        else:
            self.compact_widget()

    def compact_widget(self) -> None:
        if self._is_compact:
            return
        self._expanded_geometry = self.geometry()
        self.body.pack_forget()
        self._is_compact = True
        self.compact_label.configure(text=self._latest_compact_text)
        self.minsize(self.MIN_WIDTH, self._compact_height)
        self.compact_button.configure(text="+")
        width = max(self.winfo_width(), self.MIN_WIDTH)
        self.geometry(f"{width}x{self._compact_height}+{self.winfo_x()}+{self.winfo_y()}")

    def expand_widget(self) -> None:
        if not self._is_compact:
            return
        self._is_compact = False
        self.body.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        self.compact_label.configure(text="")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.compact_button.configure(text="-")
        if self._expanded_geometry:
            self.geometry(self._expanded_geometry)
        self.after(0, self._apply_constrained_geometry)

    def set_compact_text(self, text: str) -> None:
        clean_text = " ".join(str(text).split())
        if len(clean_text) > 42:
            clean_text = clean_text[:39] + "..."
        self._latest_compact_text = clean_text
        self.compact_label.configure(text=clean_text if self._is_compact else "")

    def _update_responsive_layout(self) -> None:
        super()._update_responsive_layout()
        wraplength = max(80, self.winfo_width() - 36)
        try:
            self.compact_label.configure(
                wraplength=max(80, self.winfo_width() - 140),
                font=ctk.CTkFont(size=responsive_font_size(self, "tiny")),
            )
        except Exception:
            pass
        for label, _color, size_key, weight in self._theme_labels:
            try:
                label.configure(
                    wraplength=wraplength,
                    font=ctk.CTkFont(size=responsive_font_size(self, size_key), weight=tk_font_weight(weight)),
                )
            except Exception:
                pass

    def schedule_update(self, delay_ms: int, callback: Callable[[], None]) -> None:
        if not self._running:
            return

        def run_once() -> None:
            self._scheduled_after_ids.discard(after_id)
            if self._running:
                callback()

        after_id = self.after(delay_ms, run_once)
        self._scheduled_after_ids.add(after_id)

    def ui_after(self, callback: Callable[[], None]) -> None:
        if not self._running:
            return
        try:
            if self.winfo_exists():
                self.after(0, callback)
        except Exception:
            pass

    def destroy_widget(self) -> None:
        self._running = False
        for after_id in list(self._scheduled_after_ids):
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self._scheduled_after_ids.clear()
        super().destroy_widget()

    def refresh_theme(self) -> None:
        self.container.configure(
            fg_color=self.theme.get("container", self.theme["panel"]),
            border_width=1,
            border_color=self.theme.get("border", self.theme.get("progress_track", self.theme["button"])),
        )
        self.compact_label.configure(text_color=self.theme.get("muted", self.theme["text"]))
        for button in self._toolbar_buttons:
            button.configure(
                fg_color=self.theme["button"],
                hover_color=self.theme["button_hover"],
                text_color=self.theme["text"],
            )
        for panel in self._theme_panels:
            panel.configure(fg_color=self.theme["panel"])
        for label, color, _size_key, _weight in self._theme_labels:
            label.configure(text_color=self.theme.get(color, self.theme["text"]))
        for button in self._theme_buttons:
            button.configure(
                fg_color=self.theme["button"],
                hover_color=self.theme["button_hover"],
                text_color=self.theme["text"],
            )
        for progress in self._theme_progress:
            progress.configure(progress_color=self.widget_accent_color(), fg_color=self.theme["progress_track"])
        for canvas in self._theme_canvases:
            canvas.configure(bg=self.theme["panel"])

    def set_status(self, message: str, level: str = "info") -> None:
        status = getattr(self.master, "status_service", None)
        if status is None:
            return
        callback = getattr(status, level, status.info)
        callback(message, toast=True)

    @staticmethod
    def format_bytes(size: float) -> str:
        value = float(size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if value < 1024 or unit == "TB":
                return f"{value:.1f} {unit}"
            value /= 1024
        return f"{value:.1f} TB"

    @staticmethod
    def format_speed(bytes_per_second: float) -> str:
        return f"{SmartWidgetBase.format_bytes(bytes_per_second)}/s"

    @staticmethod
    def format_seconds(seconds: float | int | None) -> str:
        if seconds is None or seconds < 0:
            return "Calculating"
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def draw_sparkline(self, canvas: tk.Canvas, values: list[float] | deque[float], *, maximum: float = 100.0) -> None:
        canvas.delete("all")
        width = max(canvas.winfo_width(), 120)
        height = max(canvas.winfo_height(), 40)
        canvas.create_rectangle(0, 0, width, height, fill=self.theme["panel"], outline="")
        values = list(values)
        if len(values) < 2:
            return
        step = width / max(len(values) - 1, 1)
        points = []
        for index, value in enumerate(values):
            normalized = max(0.0, min(float(value) / maximum, 1.0))
            points.extend([index * step, height - (normalized * (height - 8)) - 4])
        canvas.create_line(points, fill=self.widget_accent_color(), width=2, smooth=True)
        canvas.create_line(0, height - 1, width, height - 1, fill=self.theme.get("border", self.theme["progress_track"]))


class PCHealthWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 80, y: int = 80, theme_name: str | None = None):
        super().__init__(parent, None, "pc_health", x=x, y=y, theme_name=theme_name)
        self.score_label = self.label(self.body, "0", role="hero")
        self.score_label.pack(anchor="w")
        self.status_label = self.label(self.body, "Checking system health", role="caption")
        self.status_label.pack(anchor="w", pady=(0, 10))
        self.health_progress = self.progress(self.body)
        self.health_progress.pack(fill="x", pady=(0, 12))
        self.detail_label = self.label(self.body, "", role="caption")
        self.detail_label.pack(anchor="w")
        self.warning_label = self.label(self.body, "", role="tiny")
        self.warning_label.pack(anchor="w", pady=(6, 0))
        self.apply_theme()
        self.update_stats()

    def update_stats(self) -> None:
        if not self._running:
            return
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        try:
            disk = psutil.disk_usage("C:\\")
        except Exception:
            disk = psutil.disk_usage("/")
        battery = psutil.sensors_battery()
        uptime_hours = max((time.time() - psutil.boot_time()) / 3600, 0)

        checks: list[tuple[float, float]] = [
            (max(0.0, 100.0 - cpu), 0.25),
            (max(0.0, 100.0 - memory.percent), 0.25),
            (max(0.0, 100.0 - disk.percent), 0.25),
            (100.0 if uptime_hours < 72 else 80.0 if uptime_hours < 168 else 60.0, 0.15),
        ]
        warnings: list[str] = []
        if cpu >= 85:
            warnings.append("CPU is under heavy load")
        if memory.percent >= 85:
            warnings.append("RAM pressure is high")
        if disk.percent >= 90:
            warnings.append("System drive is almost full")
        if uptime_hours >= 168:
            warnings.append("Restart recommended")

        if battery is not None:
            battery_score = 100.0
            if not battery.power_plugged and battery.percent < 25:
                battery_score = float(battery.percent)
                warnings.append("Battery is low")
            checks.append((battery_score, 0.10))

        weight_total = sum(weight for _, weight in checks) or 1.0
        score = max(0, min(100, int(sum(value * weight for value, weight in checks) / weight_total)))
        status = "Healthy" if score >= 75 else "Needs attention" if score >= 50 else "Under pressure"

        self.score_label.configure(text=str(score))
        self.status_label.configure(text=status)
        self.health_progress.set(score / 100)
        self.detail_label.configure(
            text=(
                f"CPU {cpu:.0f}% | RAM {memory.percent:.0f}%\n"
                f"Disk free {100 - disk.percent:.0f}% | Uptime {uptime_hours:.0f}h"
            )
        )
        self.warning_label.configure(text="; ".join(warnings[:2]) if warnings else "No urgent issues detected")
        self.set_compact_text(f"{score} {status} | CPU {cpu:.0f}% RAM {memory.percent:.0f}%")
        self.schedule_update(2000, self.update_stats)


class TopProcessesWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 430, y: int = 80, theme_name: str | None = None):
        super().__init__(parent, None, "top_processes", x=x, y=y, theme_name=theme_name)
        self.rows: list[ctk.CTkLabel] = []
        self._tracked_processes: dict[int, psutil.Process] = {}
        self.summary_label = self.label(self.body, "Ranking by sampled CPU, then RAM", role="tiny")
        self.summary_label.pack(anchor="w", pady=(0, 8))
        for _ in range(2):
            row = self.label(self.body, "", role="body")
            row.pack(anchor="w", fill="x", pady=2)
            self.rows.append(row)
        self.task_manager_button = self.button(self.body, "Open Task Manager", lambda: self.master.action_service.open_target("taskmgr"))
        self.task_manager_button.pack(fill="x", pady=(10, 0))
        self.apply_theme()
        self._seed_process_cpu_samples()
        for row in self.rows:
            row.configure(text="Sampling CPU usage...")
        self.set_compact_text("Sampling CPU usage")
        self.schedule_update(900, self.update_stats)

    @staticmethod
    def _shorten_process_name(name: str, limit: int) -> str:
        clean_name = " ".join(str(name).split()) or "Unknown"
        if len(clean_name) <= limit:
            return clean_name
        return clean_name[: max(1, limit - 3)].rstrip() + "..."

    def _format_process_row(self, name: str, cpu: float, memory: float) -> str:
        _x, _y, width, _height = current_widget_geometry(self)
        if width < 310:
            return f"{self._shorten_process_name(name, 14)}  CPU {cpu:.0f}%"
        if width < 370:
            return f"{self._shorten_process_name(name, 16)}  CPU {cpu:.0f}%  RAM {memory:.1f}%"
        return f"{self._shorten_process_name(name, 22)}  CPU {cpu:.1f}%  RAM {memory:.1f}%"

    def _update_responsive_layout(self) -> None:
        super()._update_responsive_layout()
        compact_height = self.winfo_height() < 230
        try:
            if compact_height and self.summary_label.winfo_manager():
                self.summary_label.pack_forget()
            elif not compact_height and not self.summary_label.winfo_manager():
                self.summary_label.pack(anchor="w", before=self.rows[0], pady=(0, 8))
            self.task_manager_button.pack_configure(pady=(6 if compact_height else 10, 0))
        except Exception:
            pass

    def _seed_process_cpu_samples(self) -> None:
        for proc in psutil.process_iter(["pid"]):
            try:
                pid = int(proc.info.get("pid") or 0)
                self._tracked_processes[pid] = proc
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def update_stats(self) -> None:
        if not self._running:
            return
        processes = []
        seen_pids: set[int] = set()
        for proc in psutil.process_iter(["pid", "name", "memory_percent"]):
            try:
                info = proc.info
                pid = int(info.get("pid") or 0)
                seen_pids.add(pid)
                tracked = self._tracked_processes.get(pid)
                if tracked is None:
                    tracked = proc
                    self._tracked_processes[pid] = tracked
                cpu = max(float(tracked.cpu_percent(interval=None) or 0), 0.0)
                memory = max(float(info.get("memory_percent") or 0), 0.0)
                processes.append((cpu, memory, pid, info.get("name") or "Unknown"))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self._tracked_processes = {pid: proc for pid, proc in self._tracked_processes.items() if pid in seen_pids}
        processes.sort(key=lambda item: (item[0], item[1]), reverse=True)
        for index, row in enumerate(self.rows):
            if index >= len(processes):
                row.configure(text="")
                continue
            cpu, memory, pid, name = processes[index]
            row.configure(text=self._format_process_row(name, cpu, memory))
        if processes:
            top_cpu, top_memory, _pid, top_name = processes[0]
            self.set_compact_text(f"{top_name[:18]} CPU {top_cpu:.0f}% RAM {top_memory:.1f}%")
        else:
            self.set_compact_text("No process data")
        self.schedule_update(3000, self.update_stats)


class BatteryHealthWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 830, y: int = 80, theme_name: str | None = None):
        super().__init__(parent, None, "battery_health", x=x, y=y, theme_name=theme_name)
        self.percent_label = self.label(self.body, "N/A", role="hero")
        self.percent_label.pack(anchor="w")
        self.status_label = self.label(self.body, "Battery information unavailable", role="caption")
        self.status_label.pack(anchor="w", pady=(0, 10))
        self.battery_progress = self.progress(self.body)
        self.battery_progress.pack(fill="x", pady=(0, 12))
        self.detail_label = self.label(self.body, "", role="caption")
        self.detail_label.pack(anchor="w")
        self.wear_label = self.label(self.body, "Wear: checking", role="caption")
        self.wear_label.pack(anchor="w", pady=(4, 0))
        self._wear_checked = False
        self._battery_wear_text = "Wear: unavailable"
        self.apply_theme()
        self._refresh_battery_wear()
        self.update_stats()

    def update_stats(self) -> None:
        if not self._running:
            return
        battery = psutil.sensors_battery()
        if battery is None:
            self.percent_label.configure(text="N/A")
            self.status_label.configure(text="No battery detected")
            self.battery_progress.set(0)
            self.detail_label.configure(text="Desktop PCs often do not expose battery data.")
            self.wear_label.configure(text="Wear: N/A")
            self.set_compact_text("Battery N/A")
        else:
            status = "Plugged in" if battery.power_plugged else "On battery"
            self.percent_label.configure(text=f"{battery.percent:.0f}%")
            self.status_label.configure(text=status)
            self.battery_progress.set(float(battery.percent) / 100)
            self.detail_label.configure(text=f"Time remaining: {self.format_seconds(battery.secsleft)}")
            self.wear_label.configure(text=self._battery_wear_text)
            self.set_compact_text(f"{battery.percent:.0f}% {status} | {self._battery_wear_text}")
        self.schedule_update(5000, self.update_stats)

    def _refresh_battery_wear(self) -> None:
        if self._wear_checked:
            return
        self._wear_checked = True

        def worker() -> None:
            text = self._read_battery_wear()
            self.ui_after(lambda: self._set_battery_wear(text))

        threading.Thread(target=worker, daemon=True).start()

    def _set_battery_wear(self, text: str) -> None:
        self._battery_wear_text = text
        self.wear_label.configure(text=text)

    @staticmethod
    def _read_battery_wear() -> str:
        cim_text = BatteryHealthWidget._read_battery_wear_from_cim()
        if cim_text:
            return cim_text
        report_text = BatteryHealthWidget._read_battery_wear_from_powercfg()
        if report_text:
            return report_text
        return "Wear: unavailable"

    @staticmethod
    def _read_battery_wear_from_cim() -> str | None:
        script = r"""
$full = Get-CimInstance -Namespace root\wmi -ClassName BatteryFullChargedCapacity -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullChargedCapacity
$design = Get-CimInstance -Namespace root\wmi -ClassName BatteryStaticData -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty DesignedCapacity
if ($full -and $design -and [double]$design -gt 0) {
    $wear = [math]::Max(0, [math]::Min(100, [math]::Round((1 - ([double]$full / [double]$design)) * 100, 1)))
    [pscustomobject]@{ Full = [double]$full; Design = [double]$design; Wear = $wear } | ConvertTo-Json -Compress
}
"""
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=12,
            )
            data = json.loads(result.stdout.strip()) if result.stdout.strip() else {}
            wear = data.get("Wear")
            full = data.get("Full")
            design = data.get("Design")
            if wear is None or full is None or design is None:
                return None
            return f"Wear: {float(wear):.1f}% | {float(full):.0f}/{float(design):.0f} mWh"
        except Exception:
            return None

    @staticmethod
    def _read_battery_wear_from_powercfg() -> str | None:
        report_path = Path(tempfile.gettempdir()) / "optipc_battery_report.xml"
        try:
            result = subprocess.run(
                ["powercfg", "/batteryreport", "/xml", "/output", str(report_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
            if result.returncode != 0 or not report_path.exists():
                return None
            root = ET.parse(report_path).getroot()
            values: dict[str, float] = {}
            for element in root.iter():
                tag = element.tag.split("}", 1)[-1].lower()
                if tag not in {"designcapacity", "fullchargecapacity"}:
                    continue
                number = BatteryHealthWidget._numeric_text(element.text)
                if number is not None:
                    values[tag] = number
            design = values.get("designcapacity")
            full = values.get("fullchargecapacity")
            if not design or not full:
                return None
            wear = max(0.0, min(100.0, round((1 - (full / design)) * 100, 1)))
            return f"Wear: {wear:.1f}% | {full:.0f}/{design:.0f} mWh"
        except Exception:
            return None

    @staticmethod
    def _numeric_text(value: str | None) -> float | None:
        if not value:
            return None
        cleaned = "".join(char for char in value if char.isdigit() or char == ".")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None


class StorageCleanupWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 80, y: int = 360, theme_name: str | None = None):
        super().__init__(parent, None, "storage_cleanup", x=x, y=y, theme_name=theme_name)
        self.size_label = self.label(self.body, "Scan to estimate", role="metric")
        self.size_label.pack(anchor="w")
        self.detail_label = self.label(self.body, "Safe cleanup categories only", role="caption")
        self.detail_label.pack(anchor="w", pady=(0, 12))
        actions = ctk.CTkFrame(self.body, fg_color="transparent")
        actions.pack(fill="x")
        actions.grid_columnconfigure((0, 1), weight=1)
        self.button(actions, "Scan", self.scan).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self.button(actions, "Clean Safe", self.clean_safe).grid(row=0, column=1, padx=(6, 0), sticky="ew")
        self.apply_theme()
        self.set_compact_text("Safe categories only")

    @property
    def cleanup_service(self) -> CleanupService:
        return getattr(self.master, "cleanup_service", CleanupService())

    def _run(self, work: Callable[[], object], done: Callable[[object], None]) -> None:
        self.detail_label.configure(text="Working...")
        self.set_compact_text("Working...")

        def worker() -> None:
            try:
                result = work()
                self.ui_after(lambda: done(result))
            except Exception as exc:
                message = f"Error: {exc}"
                self.ui_after(lambda: self.detail_label.configure(text=message))

        threading.Thread(target=worker, daemon=True).start()

    def scan(self) -> None:
        keys = self.cleanup_service.get_default_category_keys()
        self._run(lambda: self.cleanup_service.scan_cleanup(keys=keys), self._show_scan)

    def _show_scan(self, result) -> None:
        self.size_label.configure(text=self.cleanup_service.format_bytes(result.total_size))
        self.detail_label.configure(text=f"{result.total_count} safe item(s) found")
        self.set_compact_text(f"{self.cleanup_service.format_bytes(result.total_size)} preview")

    def clean_safe(self) -> None:
        keys = self.cleanup_service.get_default_category_keys()
        self._run(lambda: self.cleanup_service.clean_categories(keys), self._show_clean)

    def _show_clean(self, result) -> None:
        self.size_label.configure(text=self.cleanup_service.format_bytes(result.bytes_freed))
        self.detail_label.configure(text=f"Removed {result.removed}; failed {result.failed}; skipped {result.skipped}")
        self.set_compact_text(f"Freed {self.cleanup_service.format_bytes(result.bytes_freed)}")
        self.set_status("Safe cleanup finished", "success")


class DiskIOWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 460, y: int = 360, theme_name: str | None = None):
        super().__init__(parent, None, "disk_io", x=x, y=y, theme_name=theme_name)
        self.read_label = self.label(self.body, "Read 0 B/s", role="title")
        self.read_label.pack(anchor="w")
        self.write_label = self.label(self.body, "Write 0 B/s", role="title")
        self.write_label.pack(anchor="w", pady=(2, 10))
        self.history = deque([0.0] * 40, maxlen=40)
        self.chart = self.canvas(self.body)
        self.chart.pack(fill="both", expand=True)
        counters = psutil.disk_io_counters() or None
        self._last_read = counters.read_bytes if counters else 0
        self._last_write = counters.write_bytes if counters else 0
        self._last_time = time.time()
        self.apply_theme()
        self.update_stats()

    def update_stats(self) -> None:
        if not self._running:
            return
        counters = psutil.disk_io_counters()
        now = time.time()
        elapsed = max(now - self._last_time, 0.001)
        if counters is not None:
            read_speed = max((counters.read_bytes - self._last_read) / elapsed, 0)
            write_speed = max((counters.write_bytes - self._last_write) / elapsed, 0)
            self._last_read = counters.read_bytes
            self._last_write = counters.write_bytes
        else:
            read_speed = write_speed = 0
        self._last_time = now
        self.read_label.configure(text=f"Read  {self.format_speed(read_speed)}")
        self.write_label.configure(text=f"Write {self.format_speed(write_speed)}")
        self.set_compact_text(f"R {self.format_speed(read_speed)} | W {self.format_speed(write_speed)}")
        self.history.append(max(read_speed, write_speed))
        self.draw_sparkline(self.chart, self.history, maximum=max(max(self.history), 1024))
        self.schedule_update(1000, self.update_stats)


class NetworkQualityWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 820, y: int = 360, theme_name: str | None = None):
        super().__init__(parent, None, "network_quality", x=x, y=y, theme_name=theme_name)
        self.speed_label = self.label(self.body, "0 B/s down | 0 B/s up", role="title")
        self.speed_label.pack(anchor="w")
        self.ip_label = self.label(self.body, f"IP: {self._local_ip()}", role="caption")
        self.ip_label.pack(anchor="w", pady=(4, 8))
        self.ping_label = self.label(self.body, "Ping: not tested", role="caption")
        self.ping_label.pack(anchor="w", pady=(0, 10))
        self.button(self.body, "Test Ping", self.test_ping).pack(fill="x")
        counters = psutil.net_io_counters()
        self._last_recv = counters.bytes_recv
        self._last_sent = counters.bytes_sent
        self._last_time = time.time()
        self.apply_theme()
        self.update_stats()

    @staticmethod
    def _local_ip() -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("8.8.8.8", 80))
                return sock.getsockname()[0]
        except Exception:
            return "Unavailable"

    def update_stats(self) -> None:
        if not self._running:
            return
        counters = psutil.net_io_counters()
        now = time.time()
        elapsed = max(now - self._last_time, 0.001)
        down = max((counters.bytes_recv - self._last_recv) / elapsed, 0)
        up = max((counters.bytes_sent - self._last_sent) / elapsed, 0)
        self._last_recv = counters.bytes_recv
        self._last_sent = counters.bytes_sent
        self._last_time = now
        self.speed_label.configure(text=f"{self.format_speed(down)} down | {self.format_speed(up)} up")
        self.set_compact_text(f"Down {self.format_speed(down)} | Up {self.format_speed(up)}")
        self.schedule_update(1000, self.update_stats)

    def test_ping(self) -> None:
        self.ping_label.configure(text="Ping: testing...")

        def worker() -> None:
            try:
                result = subprocess.run(["ping", "-n", "1", "-w", "1200", "1.1.1.1"], capture_output=True, text=True, timeout=4)
                text = result.stdout or result.stderr
                label = "Ping: failed"
                for token in ("Average =", "time="):
                    if token in text:
                        label = "Ping: " + text.split(token, 1)[1].split()[0].strip()
                        if token == "Average =":
                            label = "Ping: " + text.split(token, 1)[1].splitlines()[0].strip()
                        break
            except Exception as exc:
                label = f"Ping: {exc}"
            self.ui_after(lambda: self._show_ping(label))

        threading.Thread(target=worker, daemon=True).start()

    def _show_ping(self, label: str) -> None:
        self.ping_label.configure(text=label)
        self.set_compact_text(label)


class WindowsUpdateWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 80, y: int = 640, theme_name: str | None = None):
        super().__init__(parent, None, "windows_update", x=x, y=y, theme_name=theme_name)
        self.status_label = self.label(self.body, "Refresh to check pending and installed updates", role="caption")
        self.status_label.pack(anchor="w", pady=(0, 12))
        self.update_label = self.label(self.body, "Last update: unknown", role="title")
        self.update_label.pack(anchor="w", pady=(0, 12))
        actions = ctk.CTkFrame(self.body, fg_color="transparent")
        actions.pack(fill="x")
        actions.grid_columnconfigure((0, 1), weight=1)
        self.button(actions, "Refresh", self.refresh_update).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self.button(actions, "Open Update", lambda: self.master.action_service.open_target("ms-settings:windowsupdate")).grid(row=0, column=1, padx=(6, 0), sticky="ew")
        self.apply_theme()
        self.set_compact_text("Update status unknown")

    def refresh_update(self) -> None:
        self.status_label.configure(text="Checking pending and installed updates...")
        self.set_compact_text("Checking updates...")

        def worker() -> None:
            script = r"""
$latest = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1 HotFixID,InstalledOn,Description
$pendingCount = $null
$pendingTitle = $null
try {
    $searcher = (New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher()
    $result = $searcher.Search("IsInstalled=0 and Type='Software'")
    $pendingCount = $result.Updates.Count
    if ($pendingCount -gt 0) {
        $pendingTitle = $result.Updates.Item(0).Title
    }
} catch {
    $pendingCount = $null
}
[pscustomobject]@{
    HotFixID = $latest.HotFixID
    InstalledOn = $latest.InstalledOn
    Description = $latest.Description
    PendingCount = $pendingCount
    PendingTitle = $pendingTitle
} | ConvertTo-Json -Compress
"""
            try:
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=30,
                )
                data = json.loads(result.stdout.strip()) if result.stdout.strip() else {}
                hotfix = data.get("HotFixID") or "Unknown"
                installed = str(data.get("InstalledOn") or "Unknown").split("T")[0]
                pending = data.get("PendingCount")
                if pending is None:
                    label = f"{hotfix} | {installed}"
                    status = "Pending update check unavailable"
                else:
                    label = f"{pending} pending | {hotfix}"
                    if int(pending) > 0:
                        title = str(data.get("PendingTitle") or "Pending update")
                        status = f"Pending: {title[:54]}"
                    else:
                        status = f"No pending updates | Last installed {installed}"
            except Exception as exc:
                label = "Last update: unavailable"
                status = str(exc)
            self.ui_after(lambda: self._show_update(label, status))

        threading.Thread(target=worker, daemon=True).start()

    def _show_update(self, label: str, status: str) -> None:
        self.update_label.configure(text=label)
        self.status_label.configure(text=status)
        self.set_compact_text(label)


class TemperatureWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 460, y: int = 640, theme_name: str | None = None):
        super().__init__(parent, None, "temperature", x=x, y=y, theme_name=theme_name)
        self._fallback_temps: list[tuple[str, float]] = []
        self._fallback_probe_running = False
        self._fallback_last_probe = 0.0
        self.temp_label = self.label(self.body, "N/A", role="hero")
        self.temp_label.pack(anchor="w")
        self.detail_label = self.label(self.body, "Sensor support varies by hardware", role="caption")
        self.detail_label.pack(anchor="w", pady=(0, 12))
        self.temp_progress = self.progress(self.body)
        self.temp_progress.pack(fill="x")
        self.apply_theme()
        self.update_stats()

    def update_stats(self) -> None:
        if not self._running:
            return
        temps = self._collect_live_temperatures() + self._fallback_temps
        if not temps:
            self.temp_label.configure(text="N/A")
            self.detail_label.configure(text="Checking fallback sensors..." if self._fallback_probe_running else "No exposed sensors; hardware support required")
            self.temp_progress.set(0)
            self.set_compact_text("Temperature N/A")
            self._maybe_probe_fallback_temperatures()
        else:
            label, temp = max(temps, key=lambda item: item[1])
            self.temp_label.configure(text=f"{temp:.0f} C")
            self.detail_label.configure(text=label[:42])
            self.temp_progress.set(min(temp / 100, 1))
            self.set_compact_text(f"{temp:.0f} C | {label[:22]}")
        self.schedule_update(4000, self.update_stats)

    def _collect_live_temperatures(self) -> list[tuple[str, float]]:
        temps: list[tuple[str, float]] = []
        try:
            sensors = getattr(psutil, "sensors_temperatures", lambda: {})()
            for name, entries in sensors.items():
                for entry in entries:
                    if entry.current is not None:
                        temps.append((getattr(entry, "label", "") or name, float(entry.current)))
        except Exception:
            pass
        try:
            if GPUtil is not None:
                for gpu in GPUtil.getGPUs():
                    if getattr(gpu, "temperature", None) is not None:
                        temps.append((gpu.name, float(gpu.temperature)))
        except Exception:
            pass
        return self._plausible_temperatures(temps)

    def _maybe_probe_fallback_temperatures(self) -> None:
        now = time.time()
        if self._fallback_probe_running or now - self._fallback_last_probe < 30:
            return
        self._fallback_probe_running = True
        self._fallback_last_probe = now

        def worker() -> None:
            temps = self._collect_fallback_temperatures()
            self.ui_after(lambda: self._set_fallback_temperatures(temps))

        threading.Thread(target=worker, daemon=True).start()

    def _set_fallback_temperatures(self, temps: list[tuple[str, float]]) -> None:
        self._fallback_probe_running = False
        self._fallback_temps = temps

    def _collect_fallback_temperatures(self) -> list[tuple[str, float]]:
        temps = self._nvidia_smi_temperatures() + self._acpi_temperatures()
        return self._plausible_temperatures(temps)

    @staticmethod
    def _nvidia_smi_temperatures() -> list[tuple[str, float]]:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,temperature.gpu", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=3,
            )
            temps: list[tuple[str, float]] = []
            for line in result.stdout.splitlines():
                parts = [part.strip() for part in line.split(",")]
                if len(parts) >= 2:
                    temps.append((parts[0], float(parts[1])))
            return temps
        except Exception:
            return []

    @staticmethod
    def _acpi_temperatures() -> list[tuple[str, float]]:
        script = r"""
Get-CimInstance -Namespace root\wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue |
ForEach-Object {
    [pscustomobject]@{
        Name = $_.InstanceName
        Celsius = [math]::Round(($_.CurrentTemperature / 10) - 273.15, 1)
    }
} | ConvertTo-Json -Compress
"""
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=6,
            )
            raw = result.stdout.strip()
            if not raw:
                return []
            data = json.loads(raw)
            entries = data if isinstance(data, list) else [data]
            temps = []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                value = entry.get("Celsius")
                name = entry.get("Name") or "ACPI thermal zone"
                if value is not None:
                    temps.append((str(name), float(value)))
            return temps
        except Exception:
            return []

    @staticmethod
    def _plausible_temperatures(temps: list[tuple[str, float]]) -> list[tuple[str, float]]:
        return [(label, value) for label, value in temps if -20.0 <= value <= 125.0]


class QuickActionsWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 820, y: int = 640, theme_name: str | None = None):
        super().__init__(parent, None, "quick_actions", x=x, y=y, theme_name=theme_name)
        grid = ctk.CTkFrame(self.body, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1), weight=1)
        actions = [
            ("Cleanup", self._open_cleanup),
            ("Safe Clean", self._safe_clean),
            ("Settings", lambda: self.master.action_service.open_windows_settings()),
            ("Task Manager", lambda: self.master.action_service.open_target("taskmgr")),
            ("Reports", lambda: self.master.action_service.open_report_folder(getattr(self.master, "report_dir", Path.home()))),
            ("Repair", self._open_repair),
        ]
        for index, (label, command) in enumerate(actions):
            self.button(grid, label, command).grid(row=index // 2, column=index % 2, padx=5, pady=5, sticky="ew")
        self.status_label = self.label(self.body, "Ready", role="caption")
        self.status_label.pack(anchor="w", pady=(8, 0))
        self.apply_theme()
        self.set_compact_text("6 shortcuts ready")

    def _open_cleanup(self) -> None:
        if hasattr(self.master, "restore_from_tray"):
            self.master.restore_from_tray()
        if hasattr(self.master, "show_page"):
            self.master.show_page("Cleanup")

    def _open_repair(self) -> None:
        if hasattr(self.master, "restore_from_tray"):
            self.master.restore_from_tray()
        if hasattr(self.master, "show_page"):
            self.master.show_page("Repair")

    def _safe_clean(self) -> None:
        self.status_label.configure(text="Cleaning safe junk...")

        def worker() -> None:
            try:
                service = getattr(self.master, "cleanup_service", CleanupService())
                result = service.clean_categories(service.get_default_category_keys())
                text = f"Freed {service.format_bytes(result.bytes_freed)}"
                self.ui_after(lambda: self._show_safe_clean(text))
            except Exception as exc:
                message = f"Error: {exc}"
                self.ui_after(lambda: self._show_safe_clean(message))

        threading.Thread(target=worker, daemon=True).start()

    def _show_safe_clean(self, text: str) -> None:
        self.status_label.configure(text=text)
        self.set_compact_text(text)


class PerformanceTimelineWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 1200, y: int = 80, theme_name: str | None = None):
        super().__init__(parent, None, "performance_timeline", x=x, y=y, theme_name=theme_name)
        self.metric_label = self.label(self.body, "CPU 0% | RAM 0%", role="title")
        self.metric_label.pack(anchor="w", pady=(0, 8))
        self.cpu_history = deque([0.0] * 50, maxlen=50)
        self.ram_history = deque([0.0] * 50, maxlen=50)
        self.chart = self.canvas(self.body, height=130)
        self.chart.pack(fill="both", expand=True)
        self.legend_label = self.label(self.body, "Blue: CPU | Gray: RAM", role="tiny")
        self.legend_label.pack(anchor="w", pady=(6, 0))
        self.apply_theme()
        self.update_stats()

    def update_stats(self) -> None:
        if not self._running:
            return
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        self.cpu_history.append(cpu)
        self.ram_history.append(ram)
        self.metric_label.configure(text=f"CPU {cpu:.0f}% | RAM {ram:.0f}%")
        self.set_compact_text(f"CPU {cpu:.0f}% | RAM {ram:.0f}%")
        self._draw_timeline()
        self.schedule_update(1000, self.update_stats)

    def _draw_timeline(self) -> None:
        canvas = self.chart
        canvas.delete("all")
        width = max(canvas.winfo_width(), 180)
        height = max(canvas.winfo_height(), 80)
        canvas.create_rectangle(0, 0, width, height, fill=self.theme["panel"], outline="")
        self._draw_line(canvas, list(self.ram_history), width, height, self.theme.get("muted", "#94a3b8"))
        self._draw_line(canvas, list(self.cpu_history), width, height, self.widget_accent_color())
        canvas.create_line(0, height - 1, width, height - 1, fill=self.theme.get("border", self.theme["progress_track"]))

    @staticmethod
    def _draw_line(canvas: tk.Canvas, values: list[float], width: int, height: int, color: str) -> None:
        if len(values) < 2:
            return
        step = width / max(len(values) - 1, 1)
        points = []
        for index, value in enumerate(values):
            normalized = max(0.0, min(value / 100.0, 1.0))
            points.extend([index * step, height - (normalized * (height - 8)) - 4])
        canvas.create_line(points, fill=color, width=2, smooth=True)
