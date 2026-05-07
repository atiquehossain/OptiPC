from __future__ import annotations

import json
import math
import socket
import subprocess
import threading
import time
import tkinter as tk
import tempfile
import xml.etree.ElementTree as ET
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

import customtkinter as ctk
import psutil

try:
    import GPUtil
except Exception:
    GPUtil = None


def run_hidden_subprocess(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run background probes without flashing a terminal window."""

    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs.setdefault("creationflags", subprocess.CREATE_NO_WINDOW)
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs.setdefault("startupinfo", startupinfo)
        except Exception:
            pass
    return subprocess.run(command, **kwargs)


from config.widget_specs import widget_default_size, widget_spec
from config.widget_style import widget_text_role
from services.cleanup_service import CleanupService
from widgets.base_mini_widget import BaseMiniWidget
from widgets.cpu_usage import CpuUsageSampler, format_cpu_percent
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
        self._scheduled_callbacks: dict[str, Callable[[], None]] = {}
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
        callback_key = f"{id(getattr(callback, '__self__', self))}:{getattr(callback, '__name__', repr(callback))}"
        self._scheduled_callbacks[callback_key] = callback
        if not self._widget_updates_active():
            return

        def run_once() -> None:
            self._scheduled_after_ids.discard(after_id)
            if self._running and self._widget_updates_active():
                callback()

        after_id = self.after(delay_ms, run_once)
        self._scheduled_after_ids.add(after_id)

    def _cancel_scheduled_updates(self) -> None:
        for after_id in list(self._scheduled_after_ids):
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self._scheduled_after_ids.clear()

    def _resume_scheduled_updates(self) -> None:
        if not self._widget_updates_active() or self._scheduled_after_ids:
            return
        for callback in list(self._scheduled_callbacks.values()):
            callback()

    def hide_widget(self) -> None:
        self._cancel_scheduled_updates()
        super().hide_widget()

    def show_widget(self) -> None:
        super().show_widget()
        self._resume_scheduled_updates()

    def ui_after(self, callback: Callable[[], None]) -> None:
        if not self._widget_updates_active():
            return
        try:
            if self.winfo_exists():
                self.after(0, callback)
        except Exception:
            pass

    def destroy_widget(self) -> None:
        self._running = False
        self._cancel_scheduled_updates()
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


class AnalogClockRenderer:
    """Reusable canvas painter for local and world clock widgets."""

    SECOND_HAND_COLOR = "#ff9f0a"

    @staticmethod
    def _point(cx: float, cy: float, radius: float, angle_degrees: float) -> tuple[float, float]:
        radians = math.radians(angle_degrees - 90)
        return cx + math.cos(radians) * radius, cy + math.sin(radians) * radius

    @staticmethod
    def _is_daytime(now: datetime) -> bool:
        return 6 <= int(now.hour) < 18

    @classmethod
    def _palette(cls, theme: dict, now: datetime, *, face_mode: str = "auto") -> dict[str, str]:
        material = str(theme.get("material_mode", "full_color"))
        if face_mode == "dark" or (face_mode == "auto" and not cls._is_daytime(now)):
            return {
                "face": "#2c2c2e" if material != "monochrome" else "#303033",
                "primary": "#f5f5f7",
                "muted": "#d1d1d6",
                "tick": "#b8b8bf",
                "border": "#3a3a3f",
            }
        return {
            "face": "#f5f5f7",
            "primary": "#1d1d1f",
            "muted": "#6e6e73",
            "tick": "#a8a8ad",
            "border": "#d1d1d6",
        }

    @classmethod
    def draw(
        cls,
        canvas: tk.Canvas,
        theme: dict,
        now: datetime,
        bounds: tuple[float, float, float, float],
        *,
        label: str = "",
        face_mode: str = "auto",
        show_second: bool = True,
        show_numbers: bool = True,
        label_inside: bool = False,
    ) -> None:
        x0, y0, x1, y1 = bounds
        width = max(1.0, x1 - x0)
        height = max(1.0, y1 - y0)
        cx = x0 + width / 2.0
        cy = y0 + height / 2.0
        radius = max(10.0, min(width, height) * 0.45)
        palette = cls._palette(theme, now, face_mode=face_mode)

        shadow = theme.get("shadow", "#000000")
        if radius >= 28:
            canvas.create_oval(cx - radius + 2, cy - radius + 3, cx + radius + 2, cy + radius + 3, fill=shadow, outline="")
        canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill=palette["face"],
            outline=palette["border"],
            width=max(1, int(radius * 0.035)),
        )

        major_tick_width = max(1, int(radius * 0.035))
        minor_tick_width = 1
        for tick in range(60):
            is_major = tick % 5 == 0
            outer = radius * 0.91
            inner = radius * (0.76 if is_major else 0.84)
            angle = tick * 6
            x_start, y_start = cls._point(cx, cy, inner, angle)
            x_end, y_end = cls._point(cx, cy, outer, angle)
            canvas.create_line(
                x_start,
                y_start,
                x_end,
                y_end,
                fill=palette["tick"],
                width=major_tick_width if is_major else minor_tick_width,
            )

        if show_numbers:
            number_size = max(6, min(24, int(radius * 0.25)))
            numbers = range(1, 13) if radius >= 42 else (12, 3, 6, 9)
            for number in numbers:
                x_text, y_text = cls._point(cx, cy, radius * 0.62, number * 30)
                canvas.create_text(
                    x_text,
                    y_text,
                    text=str(number),
                    fill=palette["primary"],
                    font=("Segoe UI", number_size, "bold"),
                )

        if label and label_inside:
            label_size = max(6, min(11, int(radius * 0.17)))
            canvas.create_text(
                cx,
                cy - radius * 0.33,
                text=label,
                fill=palette["muted"],
                font=("Segoe UI", label_size, "bold"),
            )

        second = now.second + (now.microsecond / 1_000_000)
        minute = now.minute + (second / 60)
        hour = (now.hour % 12) + (minute / 60)
        hour_angle = hour * 30
        minute_angle = minute * 6
        second_angle = second * 6

        hour_x, hour_y = cls._point(cx, cy, radius * 0.43, hour_angle)
        minute_x, minute_y = cls._point(cx, cy, radius * 0.68, minute_angle)
        canvas.create_line(cx, cy, hour_x, hour_y, fill=palette["primary"], width=max(3, int(radius * 0.10)))
        canvas.create_line(cx, cy, minute_x, minute_y, fill=palette["primary"], width=max(2, int(radius * 0.075)))

        if show_second:
            second_x, second_y = cls._point(cx, cy, radius * 0.86, second_angle)
            tail_x, tail_y = cls._point(cx, cy, radius * -0.20, second_angle)
            canvas.create_line(tail_x, tail_y, second_x, second_y, fill=cls.SECOND_HAND_COLOR, width=max(1, int(radius * 0.025)))

        center_radius = max(2, int(radius * 0.055))
        canvas.create_oval(
            cx - center_radius,
            cy - center_radius,
            cx + center_radius,
            cy + center_radius,
            fill=cls.SECOND_HAND_COLOR,
            outline=palette["primary"],
            width=1,
        )


class AnalogClockWidget(SmartWidgetBase):
    """Single-source local analog clock with smooth hand movement."""

    def __init__(self, parent, x: int = 400, y: int = 40, theme_name: str | None = None):
        super().__init__(parent, None, "clock", x=x, y=y, theme_name=theme_name)
        self.clock_canvas = tk.Canvas(self.body, bg=self.theme["panel"], highlightthickness=0, bd=0)
        self._theme_canvases.append(self.clock_canvas)
        self.clock_canvas.pack(fill="both", expand=True)
        self.clock_canvas.bind("<Configure>", lambda _event: self._draw_clock(), add="+")
        self._bind_widget_chrome(self.clock_canvas)
        self.apply_theme()
        self.update_clock()

    def refresh_theme(self) -> None:
        super().refresh_theme()
        canvas = getattr(self, "clock_canvas", None)
        if canvas is not None:
            canvas.configure(bg=self.theme["panel"])
            self._draw_clock()

    def update_clock(self) -> None:
        if not self._running:
            return
        self._draw_clock()
        now = datetime.now().astimezone()
        self.set_compact_text(now.strftime("%I:%M %p").lstrip("0"))
        self.schedule_update(200, self.update_clock)

    def _draw_clock(self) -> None:
        canvas = getattr(self, "clock_canvas", None)
        if canvas is None:
            return
        canvas.delete("all")
        width = max(int(canvas.winfo_width()), 100)
        height = max(int(canvas.winfo_height()), 100)
        canvas.create_rectangle(0, 0, width, height, fill=self.theme.get("panel", "#1f1f22"), outline="")
        margin = max(6, int(min(width, height) * 0.06))
        AnalogClockRenderer.draw(
            canvas,
            self.theme,
            datetime.now().astimezone(),
            (margin, margin, width - margin, height - margin),
            face_mode="light",
            show_second=True,
            show_numbers=True,
        )


class PCHealthWidget(SmartWidgetBase):
    def __init__(self, parent, x: int = 80, y: int = 80, theme_name: str | None = None):
        super().__init__(parent, None, "pc_health", x=x, y=y, theme_name=theme_name)
        self._cpu_sampler = CpuUsageSampler()
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

    def _update_responsive_layout(self) -> None:
        super()._update_responsive_layout()
        compact = self.widget_is_compact()
        try:
            if compact and self.warning_label.winfo_manager():
                self.warning_label.pack_forget()
            elif not compact and not self.warning_label.winfo_manager():
                self.warning_label.pack(anchor="w", pady=(6, 0))
        except Exception:
            pass

    def update_stats(self) -> None:
        if not self._running:
            return
        cpu = self._cpu_sampler.sample()
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
        compact = self.widget_is_compact()
        self.detail_label.configure(
            text=(
                f"CPU {format_cpu_percent(cpu)} | RAM {memory.percent:.0f}%"
                if compact
                else f"CPU {format_cpu_percent(cpu)} | RAM {memory.percent:.0f}%\nDisk free {100 - disk.percent:.0f}% | Uptime {uptime_hours:.0f}h"
            )
        )
        self.warning_label.configure(text="" if compact else "; ".join(warnings[:2]) if warnings else "No urgent issues detected")
        self.set_compact_text(f"{score} {status} | CPU {format_cpu_percent(cpu)} RAM {memory.percent:.0f}%")
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

    def _update_responsive_layout(self) -> None:
        super()._update_responsive_layout()
        compact = self.widget_is_compact()
        try:
            if compact and self.wear_label.winfo_manager():
                self.wear_label.pack_forget()
            elif not compact and not self.wear_label.winfo_manager():
                self.wear_label.pack(anchor="w", pady=(4, 0))
        except Exception:
            pass

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
            result = run_hidden_subprocess(
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
            result = run_hidden_subprocess(
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
                result = run_hidden_subprocess(
                    ["ping", "-n", "1", "-w", "1200", "1.1.1.1"],
                    capture_output=True,
                    text=True,
                    timeout=4,
                )
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


class BluetoothWidget(SmartWidgetBase):
    """Bluetooth status widget with Apple-style activity rings."""

    _DEVICE_EXCLUDE_TOKENS = (
        "adapter",
        "enumerator",
        "generic access",
        "generic attribute",
        "microsoft bluetooth",
        "protocol",
        "radio",
        "rfcomm",
        "service",
        "transport",
        "wireless bluetooth",
    )
    _AUDIO_TOKENS = (
        "a2dp",
        "airpod",
        "audio",
        "avrcp",
        "buds",
        "ear",
        "hands-free",
        "handsfree",
        "headphone",
        "headset",
        "speaker",
        "sound",
    )

    def __init__(self, parent, x: int = 1200, y: int = 360, theme_name: str | None = None):
        super().__init__(parent, None, "bluetooth", x=x, y=y, theme_name=theme_name)
        self._probe_running = False
        self._last_probe_at = 0.0
        self._bluetooth_snapshot = {
            "available": False,
            "radio_active": False,
            "connected_count": 0,
            "device_count": 0,
            "audio_active": False,
            "devices": [],
            "summary": "Checking Bluetooth",
        }
        self.ring_canvas = tk.Canvas(self.body, bg=self.theme["panel"], highlightthickness=0, bd=0)
        self._theme_canvases.append(self.ring_canvas)
        self.ring_canvas.pack(fill="both", expand=True)
        self.ring_canvas.bind("<Configure>", lambda _event: self._draw_rings(), add="+")
        self._bind_widget_chrome(self.ring_canvas)
        self.apply_theme()
        self.update_stats()

    def refresh_theme(self) -> None:
        super().refresh_theme()
        canvas = getattr(self, "ring_canvas", None)
        if canvas is not None:
            canvas.configure(bg=self.theme["panel"])
            self._draw_rings()

    def _build_context_menu(self) -> None:
        super()._build_context_menu()
        self._context_menu.insert_separator(0)
        self._context_menu.insert_command(0, label="Open Bluetooth Settings", command=self.open_bluetooth_settings)

    def open_bluetooth_settings(self) -> None:
        action_service = getattr(self.master, "action_service", None)
        if action_service is not None:
            action_service.open_target("ms-settings:bluetooth")

    def update_stats(self) -> None:
        if not self._running:
            return
        now = time.time()
        if not self._probe_running and now - self._last_probe_at >= 8:
            self._probe_running = True
            self._last_probe_at = now
            threading.Thread(target=self._probe_bluetooth, daemon=True).start()
        self._draw_rings()
        self.set_compact_text(str(self._bluetooth_snapshot.get("summary") or "Bluetooth"))
        self.schedule_update(1500, self.update_stats)

    def _probe_bluetooth(self) -> None:
        snapshot = self._read_bluetooth_snapshot()
        self.ui_after(lambda: self._show_bluetooth_snapshot(snapshot))

    def _show_bluetooth_snapshot(self, snapshot: dict[str, object]) -> None:
        self._probe_running = False
        self._bluetooth_snapshot = snapshot
        self.set_compact_text(str(snapshot.get("summary") or "Bluetooth"))
        self._draw_rings()

    def _read_bluetooth_snapshot(self) -> dict[str, object]:
        script = r"""
$items = @(Get-PnpDevice -Class Bluetooth -ErrorAction SilentlyContinue |
    Where-Object { $_.FriendlyName } |
    Select-Object FriendlyName, Status, Class, InstanceId)
$radio = @(Get-PnpDevice -Class SoftwareDevice -ErrorAction SilentlyContinue |
    Where-Object { $_.FriendlyName -eq 'Bluetooth' -or $_.InstanceId -like 'SWD\RADIO\BLUETOOTH*' } |
    Select-Object FriendlyName, Status, Class, InstanceId)
$audioEndpoints = @(Get-CimInstance Win32_PnPEntity -ErrorAction SilentlyContinue |
    Where-Object { $_.PNPClass -eq 'AudioEndpoint' } |
    Select-Object Name, Status, PNPDeviceID)
$service = Get-Service bthserv -ErrorAction SilentlyContinue | Select-Object -First 1 Status
[pscustomobject]@{
    Items = $items
    Radio = $radio
    AudioEndpoints = $audioEndpoints
    ServiceStatus = if ($service) { [string]$service.Status } else { $null }
} | ConvertTo-Json -Compress -Depth 4
"""
        try:
            result = run_hidden_subprocess(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=8,
            )
            raw = result.stdout.strip()
            data = json.loads(raw) if raw else {}
            items = data.get("Items", []) if isinstance(data, dict) else []
            radio = data.get("Radio", []) if isinstance(data, dict) else []
            audio_endpoints = data.get("AudioEndpoints", []) if isinstance(data, dict) else []
            if isinstance(items, dict):
                items = [items]
            if isinstance(radio, dict):
                radio = [radio]
            if isinstance(audio_endpoints, dict):
                audio_endpoints = [audio_endpoints]
            entries = [item for item in items if isinstance(item, dict)]
            radio_entries = [item for item in radio if isinstance(item, dict)]
            endpoint_entries = [item for item in audio_endpoints if isinstance(item, dict)]
            service_status = str(data.get("ServiceStatus") or "").lower() if isinstance(data, dict) else ""
            return self._summarize_bluetooth_entries(entries, service_status, radio_entries, endpoint_entries)
        except Exception:
            return {
                "available": False,
                "radio_active": False,
                "connected_count": 0,
                "device_count": 0,
                "audio_active": False,
                "devices": [],
                "summary": "Bluetooth unavailable",
            }

    def _summarize_bluetooth_entries(
        self,
        entries: list[dict],
        service_status: str,
        radio_entries: list[dict] | None = None,
        audio_endpoints: list[dict] | None = None,
    ) -> dict[str, object]:
        radio_entries = radio_entries or []
        audio_endpoints = audio_endpoints or []
        radio_ok = any(str(entry.get("Status") or "").strip().lower() == "ok" for entry in radio_entries)
        device_entries = [entry for entry in entries if self._is_device_candidate(str(entry.get("FriendlyName") or ""))]
        paired_names = self._paired_device_names(device_entries)
        connected_names = self._connected_audio_names(paired_names, audio_endpoints)
        devices = [{"name": name, "icon": self._device_icon_for_name(name), "battery": None} for name in connected_names]
        audio_active = bool(connected_names)
        available = bool(entries) or bool(radio_entries) or service_status == "running"
        radio_active = radio_ok or service_status == "running"
        connected_count = len(connected_names)
        device_count = len(device_entries)
        if radio_active and connected_count:
            summary = f"Bluetooth on | {connected_count} connected"
        elif radio_active:
            summary = "Bluetooth on | no devices connected"
        elif available:
            summary = "Bluetooth idle"
        else:
            summary = "Bluetooth unavailable"
        return {
            "available": available,
            "radio_active": radio_active,
            "connected_count": connected_count,
            "device_count": device_count,
            "audio_active": audio_active,
            "devices": devices,
            "summary": summary,
        }

    def _is_device_candidate(self, name: str) -> bool:
        lower = name.lower().strip()
        return bool(lower) and not any(token in lower for token in self._DEVICE_EXCLUDE_TOKENS)

    @staticmethod
    def _normalize_device_name(name: str) -> str:
        return "".join(char.lower() for char in str(name or "") if char.isalnum())

    def _paired_device_names(self, entries: list[dict]) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()
        for entry in entries:
            instance_id = str(entry.get("InstanceId") or "").upper()
            if not instance_id.startswith("BTHENUM\\DEV_"):
                continue
            name = str(entry.get("FriendlyName") or "").strip()
            normalized = self._normalize_device_name(name)
            if name and normalized and normalized not in seen:
                names.append(name)
                seen.add(normalized)
        return names

    def _connected_audio_names(self, paired_names: list[str], audio_endpoints: list[dict]) -> list[str]:
        connected: list[str] = []
        seen: set[str] = set()
        normalized_pairs = [(name, self._normalize_device_name(name)) for name in paired_names]
        for endpoint in audio_endpoints:
            if str(endpoint.get("Status") or "").strip().lower() != "ok":
                continue
            endpoint_name = str(endpoint.get("Name") or "")
            normalized_endpoint = self._normalize_device_name(endpoint_name)
            for name, normalized_name in normalized_pairs:
                if normalized_name and normalized_name in normalized_endpoint and normalized_name not in seen:
                    connected.append(name)
                    seen.add(normalized_name)
        return connected

    def _device_icon_for_name(self, name: str) -> str:
        lower = str(name or "").lower()
        if "watch" in lower:
            return "watch"
        if any(token in lower for token in self._AUDIO_TOKENS):
            return "headphones"
        if "phone" in lower or "iphone" in lower or "android" in lower:
            return "phone"
        return "headphones"

    def _ring_model(self) -> list[dict[str, object]]:
        snapshot = self._bluetooth_snapshot
        raw_devices = snapshot.get("devices") if isinstance(snapshot, dict) else []
        devices = raw_devices if isinstance(raw_devices, list) else []
        rings: list[dict[str, object]] = []
        for device in devices[:4]:
            if not isinstance(device, dict):
                continue
            battery = device.get("battery")
            has_battery = isinstance(battery, (int, float))
            progress = max(0.0, min(float(battery) / 100.0, 1.0)) if has_battery else 0.0
            rings.append(
                {
                    "icon": str(device.get("icon") or "headphones"),
                    "active": has_battery,
                    "progress": progress,
                }
            )
        while len(rings) < 4:
            rings.append({"icon": "", "active": False, "progress": 0.0})
        return rings

    def _draw_rings(self) -> None:
        canvas = getattr(self, "ring_canvas", None)
        if canvas is None:
            return
        canvas.delete("all")
        width = max(int(canvas.winfo_width()), 120)
        height = max(int(canvas.winfo_height()), 120)
        panel = self.theme.get("panel", "#1f1f22")
        canvas.create_rectangle(0, 0, width, height, fill=panel, outline="")
        cell_w = width / 2.0
        cell_h = height / 2.0
        radius = max(21, min(cell_w, cell_h) * 0.34)
        centers = [
            (cell_w * 0.5, cell_h * 0.5),
            (cell_w * 1.5, cell_h * 0.5),
            (cell_w * 0.5, cell_h * 1.5),
            (cell_w * 1.5, cell_h * 1.5),
        ]
        for center, item in zip(centers, self._ring_model(), strict=False):
            self._draw_ring(canvas, center[0], center[1], radius, item)

    def _draw_ring(self, canvas: tk.Canvas, cx: float, cy: float, radius: float, item: dict[str, object]) -> None:
        active = bool(item.get("active"))
        progress = max(0.0, min(float(item.get("progress") or 0.0), 1.0))
        ring_width = max(5, int(radius * 0.18))
        track = self.theme.get("progress_track", "#3a3a3f")
        inactive = self.theme.get("muted", "#8e8e93")
        active_color = self.widget_accent_color("#30d158")
        track_color = track if active or progress > 0 else inactive
        bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
        canvas.create_oval(*bbox, outline=track_color, width=ring_width)
        if progress > 0:
            color = active_color if active else self._muted_ring_color()
            canvas.create_arc(*bbox, start=92, extent=-max(10, int(progress * 360)), style="arc", outline=color, width=ring_width)
        self._draw_icon(canvas, str(item.get("icon") or ""), cx, cy, radius * 0.55, active)

    def _muted_ring_color(self) -> str:
        mode = str(self.theme.get("material_mode", "full_color"))
        if mode == "monochrome":
            return self.theme.get("muted", "#8e8e93")
        return self.theme.get("muted", "#8e8e93")

    def _draw_icon(self, canvas: tk.Canvas, icon: str, cx: float, cy: float, size: float, active: bool) -> None:
        color = self.theme.get("text", "#ffffff") if active else self.theme.get("muted", "#a8a8ad")
        width = max(2, int(size * 0.12))
        if icon == "phone":
            x0, y0, x1, y1 = cx - size * 0.34, cy - size * 0.52, cx + size * 0.34, cy + size * 0.52
            canvas.create_rectangle(x0, y0, x1, y1, outline=color, width=width)
            canvas.create_line(cx - size * 0.18, y1 - size * 0.14, cx + size * 0.18, y1 - size * 0.14, fill=color, width=width)
        elif icon == "watch":
            x0, y0, x1, y1 = cx - size * 0.38, cy - size * 0.38, cx + size * 0.38, cy + size * 0.38
            canvas.create_rectangle(x0, y0, x1, y1, outline=color, width=width)
            canvas.create_line(cx - size * 0.2, y0, cx - size * 0.2, y0 - size * 0.24, fill=color, width=width)
            canvas.create_line(cx + size * 0.2, y0, cx + size * 0.2, y0 - size * 0.24, fill=color, width=width)
            canvas.create_line(cx - size * 0.2, y1, cx - size * 0.2, y1 + size * 0.24, fill=color, width=width)
            canvas.create_line(cx + size * 0.2, y1, cx + size * 0.2, y1 + size * 0.24, fill=color, width=width)
        elif icon == "headphones":
            canvas.create_arc(cx - size * 0.58, cy - size * 0.48, cx + size * 0.58, cy + size * 0.6, start=20, extent=140, style="arc", outline=color, width=width)
            canvas.create_rectangle(cx - size * 0.62, cy + size * 0.03, cx - size * 0.38, cy + size * 0.48, outline=color, width=width)
            canvas.create_rectangle(cx + size * 0.38, cy + size * 0.03, cx + size * 0.62, cy + size * 0.48, outline=color, width=width)


class WorldClockWidget(SmartWidgetBase):
    """City-based world clock grid with synchronized analog faces."""

    CITY_OPTIONS = {
        "Dhaka": ("DHA", "Asia/Dhaka"),
        "San Francisco": ("SF", "America/Los_Angeles"),
        "New York": ("NYC", "America/New_York"),
        "London": ("LON", "Europe/London"),
        "Tokyo": ("TYO", "Asia/Tokyo"),
        "Paris": ("PAR", "Europe/Paris"),
        "Zurich": ("ZRH", "Europe/Zurich"),
        "Dubai": ("DXB", "Asia/Dubai"),
        "Singapore": ("SIN", "Asia/Singapore"),
        "Sydney": ("SYD", "Australia/Sydney"),
        "Los Angeles": ("LA", "America/Los_Angeles"),
        "Chicago": ("CHI", "America/Chicago"),
        "Toronto": ("TOR", "America/Toronto"),
        "Berlin": ("BER", "Europe/Berlin"),
        "Delhi": ("DEL", "Asia/Kolkata"),
    }
    PRESETS = {
        "Global": ("San Francisco", "New York", "London", "Dhaka"),
        "Apple Reference": ("San Francisco", "New York", "London", "Zurich"),
        "Asia": ("Dhaka", "Tokyo", "Singapore", "Dubai"),
        "Americas": ("San Francisco", "Los Angeles", "Chicago", "New York"),
        "Europe": ("London", "Paris", "Berlin", "Zurich"),
    }
    DEFAULT_CITY_NAMES = PRESETS["Global"]

    def __init__(self, parent, x: int = 400, y: int = 360, theme_name: str | None = None):
        super().__init__(parent, None, "world_clock", x=x, y=y, theme_name=theme_name)
        self._city_names = self._load_city_names()
        self.clock_canvas = tk.Canvas(self.body, bg=self.theme["panel"], highlightthickness=0, bd=0)
        self._theme_canvases.append(self.clock_canvas)
        self.clock_canvas.pack(fill="both", expand=True)
        self.clock_canvas.bind("<Configure>", lambda _event: self._draw_world_clocks(), add="+")
        self._bind_widget_chrome(self.clock_canvas)
        self.apply_theme()
        self.update_clock()

    def refresh_theme(self) -> None:
        super().refresh_theme()
        canvas = getattr(self, "clock_canvas", None)
        if canvas is not None:
            canvas.configure(bg=self.theme["panel"])
            self._draw_world_clocks()

    def _build_context_menu(self) -> None:
        super()._build_context_menu()
        preset_menu = tk.Menu(self._context_menu, tearoff=0)
        for preset_name in self.PRESETS:
            preset_menu.add_command(label=preset_name, command=lambda name=preset_name: self.set_city_preset(name))
        self._city_preset_menu = preset_menu
        self._context_menu.insert_separator(0)
        self._context_menu.insert_command(0, label="Edit Cities...", command=self.open_city_picker)
        self._context_menu.insert_cascade(0, label="City Preset", menu=preset_menu)

    def set_city_preset(self, preset_name: str) -> None:
        names = self.PRESETS.get(preset_name, self.DEFAULT_CITY_NAMES)
        self._city_names = self._normalize_city_names(names)
        self._persist_city_names()
        self._draw_world_clocks()
        self.set_compact_text(" | ".join(self._city_labels()))

    def open_city_picker(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("World Clock Cities")
        dialog.geometry(f"320x310+{self.winfo_rootx() + 24}+{self.winfo_rooty() + 24}")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        try:
            dialog.transient(self)
        except Exception:
            pass

        frame = ctk.CTkFrame(dialog, corner_radius=16, fg_color=self.theme.get("container", self.theme["panel"]))
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        title = ctk.CTkLabel(
            frame,
            text="Choose 4 cities",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme["text"],
        )
        title.pack(anchor="w", padx=14, pady=(14, 8))
        values = sorted(self.CITY_OPTIONS)
        selected_names = list(self._city_names)
        variables: list[tk.StringVar] = []
        for index in range(4):
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=5)
            label = ctk.CTkLabel(row, text=f"Clock {index + 1}", width=70, anchor="w", text_color=self.theme["muted"])
            label.pack(side="left")
            variable = tk.StringVar(value=selected_names[index] if index < len(selected_names) else self.DEFAULT_CITY_NAMES[index])
            variables.append(variable)
            menu = ctk.CTkOptionMenu(
                row,
                values=values,
                variable=variable,
                fg_color=self.theme["button"],
                button_color=self.theme["button"],
                button_hover_color=self.theme["button_hover"],
                text_color=self.theme["text"],
            )
            menu.pack(side="left", fill="x", expand=True)

        action_row = ctk.CTkFrame(frame, fg_color="transparent")
        action_row.pack(fill="x", padx=14, pady=(12, 14))
        action_row.grid_columnconfigure((0, 1), weight=1)

        def save_selection() -> None:
            self._city_names = self._normalize_city_names([variable.get() for variable in variables])
            self._persist_city_names()
            self._draw_world_clocks()
            self.set_compact_text(" | ".join(self._city_labels()))
            dialog.destroy()

        cancel = ctk.CTkButton(
            action_row,
            text="Cancel",
            height=30,
            corner_radius=12,
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text"],
            command=dialog.destroy,
        )
        cancel.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        save = ctk.CTkButton(
            action_row,
            text="Save",
            height=30,
            corner_radius=12,
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text"],
            command=save_selection,
        )
        save.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def update_clock(self) -> None:
        if not self._running:
            return
        self._draw_world_clocks()
        self.set_compact_text(" | ".join(self._city_labels()))
        self.schedule_update(200, self.update_clock)

    def _load_city_names(self) -> tuple[str, str, str, str]:
        state = {}
        try:
            state = self.master.widget_state_service.get_widget_state("world_clock")
        except Exception:
            pass
        saved = state.get("cities") if isinstance(state, dict) else None
        return self._normalize_city_names(saved if isinstance(saved, list) else self.DEFAULT_CITY_NAMES)

    def _persist_city_names(self) -> None:
        service = getattr(self.master, "widget_state_service", None)
        if service is not None and hasattr(service, "set_widget_option"):
            service.set_widget_option("world_clock", "cities", list(self._city_names))

    @classmethod
    def _normalize_city_names(cls, names) -> tuple[str, str, str, str]:
        normalized: list[str] = []
        for name in list(names or []):
            candidate = str(name)
            if candidate in cls.CITY_OPTIONS and candidate not in normalized:
                normalized.append(candidate)
        for fallback in cls.DEFAULT_CITY_NAMES:
            if fallback not in normalized:
                normalized.append(fallback)
            if len(normalized) >= 4:
                break
        return tuple(normalized[:4])  # type: ignore[return-value]

    def _city_labels(self) -> list[str]:
        labels = []
        for city_name in self._city_names:
            label, _zone_name = self.CITY_OPTIONS.get(city_name, ("UTC", "UTC"))
            labels.append(label)
        return labels

    def _city_now(self, city_name: str) -> tuple[str, datetime]:
        label, zone_name = self.CITY_OPTIONS.get(city_name, ("UTC", "UTC"))
        try:
            return label, datetime.now(ZoneInfo(zone_name))
        except Exception:
            return label, datetime.now().astimezone()

    def _draw_world_clocks(self) -> None:
        canvas = getattr(self, "clock_canvas", None)
        if canvas is None:
            return
        canvas.delete("all")
        width = max(int(canvas.winfo_width()), 120)
        height = max(int(canvas.winfo_height()), 98)
        canvas.create_rectangle(0, 0, width, height, fill=self.theme.get("panel", "#1f1f22"), outline="")

        cell_w = width / 2.0
        cell_h = height / 2.0
        gap = max(4, int(min(width, height) * 0.03))
        for index, city_name in enumerate(self._city_names):
            row = index // 2
            column = index % 2
            x0 = column * cell_w + gap
            y0 = row * cell_h + gap
            x1 = (column + 1) * cell_w - gap
            y1 = (row + 1) * cell_h - gap
            label, now = self._city_now(city_name)
            AnalogClockRenderer.draw(
                canvas,
                self.theme,
                now,
                (x0, y0, x1, y1),
                label=label,
                face_mode="auto",
                show_second=True,
                show_numbers=True,
                label_inside=True,
            )


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
                result = run_hidden_subprocess(
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
            result = run_hidden_subprocess(
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
            result = run_hidden_subprocess(
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
        self._cpu_sampler = CpuUsageSampler()
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
        cpu = self._cpu_sampler.sample()
        ram = psutil.virtual_memory().percent
        self.cpu_history.append(cpu)
        self.ram_history.append(ram)
        self.metric_label.configure(text=f"CPU {format_cpu_percent(cpu)} | RAM {ram:.0f}%")
        self.set_compact_text(f"CPU {format_cpu_percent(cpu)} | RAM {ram:.0f}%")
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
