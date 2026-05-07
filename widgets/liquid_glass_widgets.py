from __future__ import annotations

import psutil
from typing import List
import customtkinter as ctk

from widgets.calendar_responsive import (
    apply_calendar_grid_layout,
    CALENDAR_TODAY_COLOR,
    CALENDAR_BORDER,
    CALENDAR_MUTED_TEXT,
    CALENDAR_SURFACE,
    CALENDAR_TEXT,
    CALENDAR_WEEKDAY_TEXT,
    CALENDAR_WEEKDAY_LABELS,
    calendar_canvas_date_at_point,
    calendar_day_font,
    calendar_month_dates,
    install_calendar_canvas,
    install_calendar_grid,
    redraw_calendar_canvas,
)
from widgets.liquid_glass_widget import LiquidGlassWidget
from config.constants import FONT_SIZES


class LiquidCPUWidget(LiquidGlassWidget):
    """Liquid glass CPU widget with frosted glass appearance."""
    
    def __init__(self, parent, x: int = 40, y: int = 40, theme_name: str = "modern_dark"):
        super().__init__(parent, x=x, y=y, widget_key="cpu", theme_name=theme_name)
        
        # Main CPU percentage display
        self.percent_label = self.create_glass_metric_label(self.body, "0%")
        self.percent_label.pack(pady=(self.SPACING_NORMAL, self.SPACING_TIGHT))
        
        # CPU details with glass styling
        self.detail_label = self.create_glass_label(
            self.body, 
            "Cores: 0", 
            size_key="body", 
            color_key="muted"
        )
        self.detail_label.pack()
        
        # Frequency info
        self.freq_label = self.create_glass_label(
            self.body, 
            "Frequency: N/A", 
            size_key="small", 
            color_key="muted"
        )
        self.freq_label.pack(pady=(self.SPACING_TIGHT, self.SPACING_NORMAL))
        
        # Glass progress bar with CPU accent
        self.progress = self.create_glass_progress_bar(
            self.body, 
            width=140, 
            accent_color=self.widget_accent_color()
        )
        self.progress.pack(fill="x", pady=(self.SPACING_NORMAL, 0))
        
        self.apply_theme()
        self.update_stats()

    def refresh_theme(self) -> None:
        # Update all text colors
        if hasattr(self, 'percent_label'):
            self.percent_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'detail_label'):
            self.detail_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'freq_label'):
            self.freq_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'progress'):
            self.progress.configure(
                progress_color=self.widget_accent_color(),
                fg_color=self.theme["progress_track"]
            )

    def update_stats(self) -> None:
        if not self._running:
            return
            
        percent = psutil.cpu_percent(interval=None)
        logical = psutil.cpu_count(logical=True) or 0
        physical = psutil.cpu_count(logical=False) or logical
        freq = psutil.cpu_freq()
        compact = self.widget_is_compact()
        freq_text = f"{freq.current:.0f} MHz" if compact and freq else f"Frequency: {freq.current:.0f} MHz" if freq else "Frequency: N/A"
        
        self.percent_label.configure(text=f"{percent:.0f}%")
        self.detail_label.configure(text=f"{physical}P / {logical}L cores" if compact else f"Cores: {physical} physical / {logical} logical")
        self.freq_label.configure(text=freq_text)
        if compact and self.freq_label.winfo_manager():
            self.freq_label.pack_forget()
        elif not compact and not self.freq_label.winfo_manager():
            self.freq_label.pack(pady=(self.SPACING_TIGHT, self.SPACING_NORMAL))
        self.progress.set(percent / 100)
        
        self.after(1000, self.update_stats)


class LiquidRAMWidget(LiquidGlassWidget):
    """Liquid glass RAM widget with clean memory display."""
    
    def __init__(self, parent, x: int = 360, y: int = 40, theme_name: str = "modern_dark"):
        super().__init__(parent, x=x, y=y, widget_key="ram", theme_name=theme_name)
        
        # Main memory percentage
        self.percent_label = self.create_glass_metric_label(self.body, "0%")
        self.percent_label.pack(pady=(self.SPACING_NORMAL, self.SPACING_TIGHT))
        
        # Memory usage details
        self.detail_label = self.create_glass_label(
            self.body, 
            "0 GB / 0 GB", 
            size_key="body", 
            color_key="muted"
        )
        self.detail_label.pack()
        
        # Available memory
        self.avail_label = self.create_glass_label(
            self.body, 
            "Available: 0 GB", 
            size_key="small", 
            color_key="muted"
        )
        self.avail_label.pack(pady=(self.SPACING_TIGHT, self.SPACING_NORMAL))
        
        # Glass progress bar with RAM accent
        self.progress = self.create_glass_progress_bar(
            self.body, 
            width=140, 
            accent_color=self.widget_accent_color()
        )
        self.progress.pack(fill="x", pady=(self.SPACING_NORMAL, 0))
        
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
            self.progress.configure(
                progress_color=self.widget_accent_color(),
                fg_color=self.theme["progress_track"]
            )

    def update_stats(self) -> None:
        if not self._running:
            return
            
        mem = psutil.virtual_memory()
        compact = self.widget_is_compact()
        self.percent_label.configure(text=f"{mem.percent:.0f}%")
        separator = "/" if compact else " / "
        self.detail_label.configure(text=f"{self.format_gb(mem.used)}{separator}{self.format_gb(mem.total)}")
        self.avail_label.configure(text=f"Available: {self.format_gb(mem.available)}")
        if compact and self.avail_label.winfo_manager():
            self.avail_label.pack_forget()
        elif not compact and not self.avail_label.winfo_manager():
            self.avail_label.pack(pady=(self.SPACING_TIGHT, self.SPACING_NORMAL))
        self.progress.set(mem.percent / 100)
        
        self.after(1000, self.update_stats)


class LiquidGPUWidget(LiquidGlassWidget):
    """Liquid glass GPU widget with elegant display."""
    
    def __init__(self, parent, x: int = 680, y: int = 40, theme_name: str = "modern_dark"):
        super().__init__(parent, x=x, y=y, widget_key="gpu", theme_name=theme_name)
        
        # GPU name
        self.name_label = self.create_glass_label(
            self.body, 
            "GPU: Detecting...", 
            size_key="label", 
            weight="medium",
            color_key="text"
        )
        self.name_label.pack(anchor="w", pady=(self.SPACING_TIGHT, self.SPACING_NORMAL))
        
        # GPU utilization
        self.percent_label = self.create_glass_metric_label(self.body, "N/A")
        self.percent_label.pack()
        
        # Memory usage
        self.mem_label = self.create_glass_label(
            self.body, 
            "Memory: N/A", 
            size_key="body", 
            color_key="muted"
        )
        self.mem_label.pack(pady=(self.SPACING_TIGHT, self.SPACING_NORMAL))
        
        # Progress bar with GPU accent
        self.progress = self.create_glass_progress_bar(
            self.body, 
            width=140, 
            accent_color=self.widget_accent_color()
        )
        self.progress.pack(fill="x", pady=(self.SPACING_NORMAL, self.SPACING_TIGHT))
        
        # Note label
        self.note_label = self.create_glass_label(
            self.body, 
            "Some systems may not expose GPU usage", 
            size_key="small", 
            color_key="muted"
        )
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
            self.progress.configure(
                progress_color=self.widget_accent_color(),
                fg_color=self.theme["progress_track"]
            )

    def update_stats(self) -> None:
        if not self._running:
            return
            
        try:
            import GPUtil
            compact = self.widget_is_compact()
            if GPUtil is None:
                raise RuntimeError("GPUtil not installed")
            gpus = GPUtil.getGPUs()
            if not gpus:
                raise RuntimeError("No GPU info available")
            gpu = gpus[0]
            load_percent = float(gpu.load) * 100.0
            self.name_label.configure(text=gpu.name if compact else f"GPU: {gpu.name}")
            self.percent_label.configure(text=f"{load_percent:.0f}%")
            self.mem_label.configure(text=f"Memory: {gpu.memoryUsed:.0f} MB / {gpu.memoryTotal:.0f} MB")
            self.progress.set(load_percent / 100.0)
        except Exception:
            self.name_label.configure(text="GPU unavailable" if self.widget_is_compact() else "GPU: Not available")
            self.percent_label.configure(text="N/A")
            self.mem_label.configure(text="Memory: N/A")
            self.progress.set(0)
        if self.widget_is_compact() and self.note_label.winfo_manager():
            self.note_label.pack_forget()
        elif not self.widget_is_compact() and not self.note_label.winfo_manager():
            self.note_label.pack()
        
        self.after(1500, self.update_stats)


class LiquidStorageWidget(LiquidGlassWidget):
    """Liquid glass Storage widget with elegant usage display."""
    
    def __init__(self, parent, x: int = 540, y: int = 250, theme_name: str = "modern_dark"):
        super().__init__(parent, x=x, y=y, widget_key="storage", theme_name=theme_name)
        
        # Main storage usage
        self.usage_label = self.create_glass_metric_label(self.body, "0 GB")
        self.usage_label.pack(pady=(self.SPACING_NORMAL, self.SPACING_TIGHT))
        
        # Total capacity
        self.total_label = self.create_glass_label(
            self.body, 
            "Total: 0 GB", 
            size_key="body", 
            color_key="muted"
        )
        self.total_label.pack()
        
        # Progress bar with storage accent
        self.progress = self.create_glass_progress_bar(
            self.body, 
            width=280, 
            accent_color=self.widget_accent_color()
        )
        self.progress.pack(fill="x", pady=(self.SPACING_NORMAL, self.SPACING_TIGHT))
        
        # Percentage
        self.percent_label = self.create_glass_label(
            self.body, 
            "0% used", 
            size_key="small", 
            color_key="muted"
        )
        self.percent_label.pack()
        
        self.apply_theme()
        self.update_stats()

    @staticmethod
    def format_gb(value_bytes: int) -> str:
        return f"{value_bytes / (1024 ** 3):.0f} GB"

    def refresh_theme(self) -> None:
        if hasattr(self, 'usage_label'):
            self.usage_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'total_label'):
            self.total_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'percent_label'):
            self.percent_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'progress'):
            self.progress.configure(
                progress_color=self.widget_accent_color(),
                fg_color=self.theme["progress_track"]
            )

    def update_stats(self) -> None:
        if not self._running:
            return
            
        try:
            # Get primary drive usage (usually C:)
            import platform
            if platform.system() == "Windows":
                primary_drive = "C:\\"
            else:
                primary_drive = "/"
            
            usage = psutil.disk_usage(primary_drive)
            used_gb = self.format_gb(usage.used)
            total_gb = self.format_gb(usage.total)
            percent = usage.percent
            
            self.usage_label.configure(text=used_gb)
            self.total_label.configure(text=f"Total: {total_gb}")
            self.percent_label.configure(text=f"{percent:.0f}% used")
            self.progress.set(percent / 100)
            
        except Exception:
            self.usage_label.configure(text="N/A")
            self.total_label.configure(text="Total: N/A")
            self.percent_label.configure(text="N/A")
            self.progress.set(0)
        
        self.after(5000, self.update_stats)


class LiquidPartitionsWidget(LiquidGlassWidget):
    """Liquid glass Partitions widget with clean list layout."""
    
    def __init__(self, parent, x: int = 40, y: int = 250, theme_name: str = "modern_dark"):
        super().__init__(parent, x=x, y=y, widget_key="partitions", theme_name=theme_name)
        
        # Scrollable frame for partition list
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.body,
            fg_color="transparent",
            scrollbar_button_color=self.theme["button"],
            scrollbar_button_hover_color=self.theme["button_hover"]
        )
        self.scroll_frame.pack(fill="both", expand=True, pady=(self.SPACING_TIGHT, 0))
        
        # Container for partition items
        self.partitions_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.partitions_container.pack(fill="both", expand=True)
        
        # Store partition widgets for updating
        self.partition_widgets: List[ctk.CTkFrame] = []
        
        self.apply_theme()
        self.update_stats()

    @staticmethod
    def format_gb(value_bytes: int) -> str:
        return f"{value_bytes / (1024 ** 3):.1f} GB"

    def refresh_theme(self) -> None:
        # Update scrollable frame
        if hasattr(self, 'scroll_frame'):
            self.scroll_frame.configure(
                scrollbar_button_color=self.theme["button"],
                scrollbar_button_hover_color=self.theme["button_hover"]
            )
        
        # Update all partition widgets
        for widget in self.partition_widgets:
            self._update_partition_widget_theme(widget)

    def _update_partition_widget_theme(self, widget):
        """Update theme for individual partition widget."""
        try:
            # Update labels in the partition widget
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    if "name" in str(child):
                        child.configure(text_color=self.theme["text"])
                    else:
                        child.configure(text_color=self.theme["muted"])
                elif isinstance(child, ctk.CTkProgressBar):
                    child.configure(
                        progress_color=self.widget_accent_color(),
                        fg_color=self.theme["progress_track"]
                    )
        except Exception:
            pass

    def _create_partition_widget(self, device: str, fstype: str, used: int, total: int, percent: float) -> ctk.CTkFrame:
        """Create a liquid glass partition item."""
        # Main partition frame with glass styling
        partition_frame = self.create_glass_panel(
            self.partitions_container, 
            corner_radius=self.CORNER_RADIUS_MEDIUM
        )
        partition_frame.pack(fill="x", pady=self.SPACING_TIGHT)
        
        # Device name and filesystem
        name_label = self.create_glass_label(
            partition_frame,
            f"{device} ({fstype})",
            size_key="body",
            weight="medium",
            color_key="text"
        )
        name_label.pack(anchor="w", padx=self.SPACING_NORMAL, pady=(self.SPACING_NORMAL, 0))
        
        # Usage details
        usage_text = f"{self.format_gb(used)} / {self.format_gb(total)} ({percent:.0f}%)"
        usage_label = self.create_glass_label(
            partition_frame,
            usage_text,
            size_key="small",
            color_key="muted"
        )
        usage_label.pack(anchor="w", padx=self.SPACING_NORMAL, pady=(self.SPACING_TIGHT, self.SPACING_NORMAL))
        
        # Progress bar
        progress = self.create_glass_progress_bar(
            partition_frame,
            width=300,
            accent_color=self.widget_accent_color()
        )
        progress.set(percent / 100)
        progress.pack(fill="x", padx=self.SPACING_NORMAL, pady=(0, self.SPACING_NORMAL))
        
        return partition_frame

    def update_stats(self) -> None:
        if not self._running:
            return
            
        # Clear existing partition widgets
        for widget in self.partition_widgets:
            widget.destroy()
        self.partition_widgets.clear()
        
        try:
            partitions_added = 0
            for part in psutil.disk_partitions(all=False):
                device = part.device.rstrip("\\")
                opts = part.opts.lower()
                if "cdrom" in opts:
                    continue
                    
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    if partitions_added < 3:  # Limit for clean UI
                        partition_widget = self._create_partition_widget(
                            device, part.fstype, usage.used, usage.total, usage.percent
                        )
                        self.partition_widgets.append(partition_widget)
                        partitions_added += 1
                except Exception:
                    continue
                    
            if partitions_added == 0:
                # No partitions found message
                no_parts_label = self.create_glass_label(
                    self.partitions_container,
                    "No partitions found",
                    size_key="body",
                    color_key="muted"
                )
                no_parts_label.pack(pady=self.SPACING_SECTION)
                self.partition_widgets.append(no_parts_label)
                
        except Exception as exc:
            error_label = self.create_glass_label(
                self.partitions_container,
                f"Error: {str(exc)}",
                size_key="body",
                color_key="muted"
            )
            error_label.pack(pady=self.SPACING_SECTION)
            self.partition_widgets.append(error_label)
        
        self.after(4000, self.update_stats)


class LiquidCalendarWidget(LiquidGlassWidget):
    """Liquid glass Calendar widget with macOS-style design."""
    
    def __init__(self, parent, x: int = 40, y: int = 570, theme_name: str = "modern_dark"):
        super().__init__(parent, x=x, y=y, widget_key="calendar", theme_name=theme_name)
        
        # Current date tracking
        from datetime import datetime
        self.current_date = datetime.now()
        self.display_month = self.current_date.month
        self.display_year = self.current_date.year
        
        # Create UI elements
        self.create_calendar_ui()
        
        # Apply theme after creating all UI elements
        self.apply_theme()
        
        # Update calendar display
        self.update_calendar()
        
        # Update every minute to highlight current time
        self.after(60000, self.update_time)

    def create_calendar_ui(self):
        # Month/Year navigation frame
        nav_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.nav_frame = nav_frame
        nav_frame.pack(fill="x", pady=(self.SPACING_NORMAL, self.SPACING_TIGHT))
        
        # Previous month button
        self.prev_btn = self.create_glass_button(
            nav_frame, 
            "◀", 
            command=self.previous_month,
            width=28,
            height=28
        )
        self.prev_btn.pack(side="left", padx=(0, self.SPACING_TIGHT))
        self.prev_btn.configure(text="<")
        
        # Month/Year label
        self.month_label = self.create_glass_label(
            nav_frame,
            "",
            size_key="title",
            weight="medium",
            color_key="text"
        )
        self.month_label.pack(side="left", expand=True)
        
        # Next month button
        self.next_btn = self.create_glass_button(
            nav_frame, 
            "▶", 
            command=self.next_month,
            width=28,
            height=28
        )
        self.next_btn.pack(side="left", padx=(self.SPACING_TIGHT, 0))
        self.next_btn.configure(text=">")
        
        # Today button
        self.today_btn = self.create_glass_button(
            nav_frame,
            "Today",
            command=self.go_to_today,
            width=60,
            height=28
        )
        self.today_btn.pack(side="right", padx=(self.SPACING_TIGHT, 0))

        # Compact date/agenda surface used by small and medium size classes.
        self.summary_panel = self.create_glass_panel(
            self.body,
            corner_radius=self.CORNER_RADIUS_MEDIUM
        )
        self.summary_panel.grid_columnconfigure(0, weight=1)
        self.summary_panel.grid_columnconfigure(1, weight=1)
        self.summary_weekday_label = self.create_glass_label(
            self.summary_panel,
            "",
            size_key="small",
            weight="medium",
            color_key="muted"
        )
        self.summary_day_label = self.create_glass_label(
            self.summary_panel,
            "",
            size_key="hero",
            weight="bold",
            color_key="text"
        )
        self.summary_month_label = self.create_glass_label(
            self.summary_panel,
            "",
            size_key="title",
            weight="bold",
            color_key="text"
        )
        self.summary_event_label = self.create_glass_label(
            self.summary_panel,
            "",
            size_key="body",
            weight="medium",
            color_key="muted"
        )
         
        # Calendar grid frame with glass styling
        self.calendar_frame = self.create_glass_panel(
            self.body,
            corner_radius=self.CORNER_RADIUS_MEDIUM
        )
        self.calendar_frame.pack(fill="both", expand=True, pady=(self.SPACING_TIGHT, self.SPACING_NORMAL))
        install_calendar_grid(self.calendar_frame)
        
        # Day headers - macOS style (S M T W T F S)
        self.day_labels = []
        for i, day in enumerate(CALENDAR_WEEKDAY_LABELS):
            label = self.create_glass_label(
                self.calendar_frame,
                day,
                size_key="small",
                weight="medium",
                color_key="muted"
            )
            label.grid(row=0, column=i, padx=0, pady=0, sticky="nsew")
            self.day_labels.append(label)
        
        # Day buttons - responsive sizing
        self.day_buttons = []
        for week in range(6):
            week_buttons = []
            for day in range(7):
                btn = ctk.CTkLabel(
                    self.calendar_frame,
                    text="",
                    width=1,
                    height=1,
                    corner_radius=8,
                    fg_color="transparent",
                    font=ctk.CTkFont(size=self.get_responsive_font_size("body"), weight="bold"),
                    text_color=CALENDAR_TEXT,
                )
                self._bind_drag_target(btn)
                btn.bind("<ButtonRelease-1>", lambda _event, w=week, d=day: self.day_clicked(w, d), add="+")
                btn.grid(row=week + 1, column=day, padx=0, pady=0, sticky="nsew")
                week_buttons.append(btn)
            self.day_buttons.append(week_buttons)
        self.calendar_canvas = install_calendar_canvas(
            self,
            self.calendar_frame,
            self._on_calendar_canvas_release,
        )
        
        # Current date/time display
        self.datetime_label = self.create_glass_label(
            self.body,
            "",
            size_key="small",
            color_key="muted"
        )
        self.datetime_label.pack(pady=(self.SPACING_TIGHT, 0))
        self._layout_calendar()

    def _update_responsive_layout(self) -> None:
        super()._update_responsive_layout()
        self._layout_calendar()

    def _layout_calendar(self) -> None:
        if not hasattr(self, "calendar_frame"):
            return
        try:
            if self.nav_frame.winfo_manager():
                self.nav_frame.pack_forget()
            if self.summary_panel.winfo_manager():
                self.summary_panel.pack_forget()
            if getattr(self, "datetime_label", None) is not None and self.datetime_label.winfo_manager():
                self.datetime_label.pack_forget()
            if not self.calendar_frame.winfo_manager():
                self.calendar_frame.pack(fill="both", expand=True, pady=0)
            self.calendar_frame.pack_configure(pady=0)
            self.calendar_frame.configure(fg_color="transparent", border_width=0)
        except Exception:
            pass
        apply_calendar_grid_layout(self, self.calendar_frame, self.day_labels, self.day_buttons)
        if hasattr(self, "calendar_canvas"):
            try:
                self.calendar_canvas.grid(row=0, column=0, rowspan=7, columnspan=7, padx=0, pady=0, sticky="nsew")
                self.calendar_canvas.lift()
            except Exception:
                pass
            redraw_calendar_canvas(self, self.calendar_canvas)

    def _layout_summary_panel(self, size_class: str, margin: int) -> None:
        for label in (
            self.summary_weekday_label,
            self.summary_day_label,
            self.summary_month_label,
            self.summary_event_label,
        ):
            try:
                label.grid_forget()
            except Exception:
                pass

        if size_class == "medium":
            self.summary_panel.grid_columnconfigure(0, weight=0, minsize=120)
            self.summary_panel.grid_columnconfigure(1, weight=1)
            self.summary_day_label.grid(row=0, column=0, rowspan=2, sticky="n", padx=(margin, 10), pady=(margin, 0))
            self.summary_weekday_label.grid(row=0, column=1, sticky="sw", padx=(0, margin), pady=(margin, 0))
            self.summary_month_label.grid(row=1, column=1, sticky="nw", padx=(0, margin), pady=(0, 4))
            self.summary_event_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=margin, pady=(4, margin))
            self.summary_day_label.configure(font=ctk.CTkFont(size=self.get_responsive_font_size("hero"), weight="bold"))
            self.summary_event_label.configure(wraplength=max(180, self.winfo_width() - (margin * 2)))
        else:
            self.summary_panel.grid_columnconfigure(0, weight=1)
            self.summary_weekday_label.grid(row=0, column=0, sticky="ew", padx=margin, pady=(margin, 0))
            self.summary_day_label.grid(row=1, column=0, sticky="ew", padx=margin, pady=(0, 0))
            self.summary_month_label.grid(row=2, column=0, sticky="ew", padx=margin, pady=(0, 2))
            self.summary_event_label.grid(row=3, column=0, sticky="ew", padx=margin, pady=(2, margin))
            self.summary_day_label.configure(font=ctk.CTkFont(size=self.get_responsive_font_size("hero"), weight="bold"))
            self.summary_event_label.configure(wraplength=max(120, self.winfo_width() - (margin * 2)))

    def _update_summary_labels(self) -> None:
        from datetime import datetime

        now = datetime.now()
        try:
            self.summary_weekday_label.configure(text=now.strftime("%A"))
            self.summary_day_label.configure(text=str(now.day))
            self.summary_month_label.configure(text=now.strftime("%B %Y"))
            self.summary_event_label.configure(text="No upcoming events")
        except Exception:
            pass

    def refresh_theme(self) -> None:
        try:
            self.container.configure(fg_color=CALENDAR_SURFACE, border_color=CALENDAR_BORDER)
            self.attributes("-alpha", 0.98)
        except Exception:
            pass
        if hasattr(self, 'month_label'):
            self.month_label.configure(text_color=CALENDAR_TEXT)
        if hasattr(self, 'datetime_label'):
            self.datetime_label.configure(text_color=CALENDAR_MUTED_TEXT)
        if hasattr(self, 'prev_btn'):
            self.prev_btn.configure(
                fg_color=self.theme["button"],
                hover_color=self.theme["button_hover"],
                text_color=self.theme["text"]
            )
        if hasattr(self, 'next_btn'):
            self.next_btn.configure(
                fg_color=self.theme["button"],
                hover_color=self.theme["button_hover"],
                text_color=self.theme["text"]
            )
        if hasattr(self, 'today_btn'):
            self.today_btn.configure(
                fg_color=self.widget_accent_color(),
                hover_color=self.theme["button_hover"],
                text_color=self.widget_on_accent_color()
            )
        
        # Update day labels
        if hasattr(self, 'day_labels'):
            for label in self.day_labels:
                label.configure(text_color=CALENDAR_WEEKDAY_TEXT)
        
        # Update calendar frame
        if hasattr(self, 'calendar_frame'):
            self.calendar_frame.configure(
                fg_color="transparent",
                border_width=0,
                border_color=CALENDAR_BORDER
            )
        if hasattr(self, 'calendar_canvas'):
            self.calendar_canvas.configure(bg=CALENDAR_SURFACE)
        if hasattr(self, 'summary_panel'):
            self.summary_panel.configure(
                fg_color=self.theme["panel"],
                border_color=self.theme.get("border", "transparent")
            )
        for label_name, color_key in (
            ("summary_weekday_label", "muted"),
            ("summary_day_label", "text"),
            ("summary_month_label", "text"),
            ("summary_event_label", "muted"),
        ):
            label = getattr(self, label_name, None)
            if label is not None:
                label.configure(text_color=self.theme.get(color_key, self.theme["text"]))
         
        # Update day buttons with current theme
        self.update_calendar()

    def update_calendar(self):
        import calendar
        from datetime import datetime
        
        month_name = calendar.month_name[self.display_month]
        self.month_label.configure(text=f"{month_name} {self.display_year}")
        self._update_summary_labels()
        self._layout_calendar()
        weeks = calendar_month_dates(self.display_year, self.display_month)
        today = self.current_date.date()
        
        for week in range(6):
            for day in range(7):
                btn = self.day_buttons[week][day]
                day_date = weeks[week][day]
                is_today = day_date == today
                is_current_month = day_date.month == self.display_month
                is_weekend = day_date.weekday() >= 5
                btn._optipc_calendar_date = day_date

                if is_today:
                    fg_color = CALENDAR_TODAY_COLOR
                    text_color = "#111111"
                    bold = True
                elif not is_current_month:
                    fg_color = "transparent"
                    text_color = CALENDAR_MUTED_TEXT
                    bold = True
                elif is_weekend:
                    fg_color = "transparent"
                    text_color = CALENDAR_WEEKDAY_TEXT
                    bold = True
                else:
                    fg_color = "transparent"
                    text_color = CALENDAR_TEXT
                    bold = True

                btn.configure(
                    text=str(day_date.day),
                    fg_color=fg_color,
                    text_color=text_color,
                    font=calendar_day_font(self, self.calendar_frame, bold=bold),
                )

        redraw_calendar_canvas(self, getattr(self, "calendar_canvas", None))
        self.update_time()

    def _on_calendar_canvas_release(self, event) -> None:
        clicked_date = calendar_canvas_date_at_point(
            self.calendar_canvas,
            self,
            self.display_year,
            self.display_month,
            int(event.x),
            int(event.y),
        )
        if clicked_date is None:
            return
        if hasattr(self.master, 'status_service'):
            self.master.status_service.info(
                f"Selected: {clicked_date.strftime('%A, %B %d, %Y')}",
                toast=True
            )

    def update_time(self):
        from datetime import datetime
        
        if not self._running:
            return
        
        now = datetime.now()
        time_str = now.strftime("%A, %B %d, %Y - %I:%M %p")
        self.datetime_label.configure(text=time_str)
        self._update_summary_labels()
        
        # Check if we need to refresh calendar (new day)
        if now.day != self.current_date.day:
            self.current_date = now
            self.update_calendar()
        
        # Schedule next update
        self.after(60000, self.update_time)

    def previous_month(self):
        if self.display_month == 1:
            self.display_month = 12
            self.display_year -= 1
        else:
            self.display_month -= 1
        self.update_calendar()

    def next_month(self):
        if self.display_month == 12:
            self.display_month = 1
            self.display_year += 1
        else:
            self.display_month += 1
        self.update_calendar()

    def go_to_today(self):
        self.display_month = self.current_date.month
        self.display_year = self.current_date.year
        self.update_calendar()

    def day_clicked(self, week, day):
        from datetime import datetime
        
        # Get day number from button
        btn = self.day_buttons[week][day]
        day_text = btn.cget("text")
        
        if day_text:  # Only process if it's a valid day
            saved_date = getattr(btn, "_optipc_calendar_date", None)
            clicked_date = (
                datetime(saved_date.year, saved_date.month, saved_date.day)
                if saved_date is not None
                else datetime(self.display_year, self.display_month, int(day_text))
            )
            
            # Show date selection feedback
            if hasattr(self.master, 'status_service'):
                self.master.status_service.info(
                    f"Selected: {clicked_date.strftime('%A, %B %d, %Y')}", 
                    toast=True
                )


class LiquidClockWidget(LiquidGlassWidget):
    """Liquid glass Clock widget with elegant time display."""
    
    def __init__(self, parent, x: int = 400, y: int = 40, theme_name: str = "modern_dark"):
        super().__init__(parent, x=x, y=y, widget_key="clock", theme_name=theme_name)
        
        # Create UI elements
        self.create_clock_ui()
        self.apply_theme()
        self.update_clock()
        
        # Update every second
        self.after(1000, self.update_clock)

    def create_clock_ui(self):
        # Main time display with liquid glass typography
        self.time_label = self.create_glass_metric_label(self.body, "00:00:00")
        self.time_label.pack(pady=(self.SPACING_SECTION, self.SPACING_NORMAL))
        
        # Date display with accent color
        self.date_label = self.create_glass_label(
            self.body,
            "Loading...",
            size_key="title",
            weight="medium",
            color_key=self.accent_key
        )
        self.date_label.pack(pady=(0, self.SPACING_TIGHT))
        
        # Day of week display
        self.day_label = self.create_glass_label(
            self.body,
            "Loading...",
            size_key="body",
            color_key="muted"
        )
        self.day_label.pack(pady=(0, self.SPACING_SECTION))

    def refresh_theme(self) -> None:
        if hasattr(self, 'time_label'):
            self.time_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'date_label'):
            self.date_label.configure(text_color=self.widget_accent_color())
        if hasattr(self, 'day_label'):
            self.day_label.configure(text_color=self.theme["muted"])

    def update_clock(self):
        from datetime import datetime
        
        if not self._running:
            return
        
        now = datetime.now()
        
        # Update time
        compact = self.widget_is_compact()
        time_str = now.strftime("%I:%M %p") if compact else now.strftime("%I:%M:%S %p")
        self.time_label.configure(text=time_str)
        
        # Update date
        date_str = now.strftime("%b %d, %Y") if compact else now.strftime("%B %d, %Y")
        self.date_label.configure(text=date_str)
        
        # Update day of week
        day_str = now.strftime("%A")
        self.day_label.configure(text=day_str)
        
        # Schedule next update
        self.after(1000, self.update_clock)


class LiquidUptimeWidget(LiquidGlassWidget):
    """Liquid glass PC Uptime widget with minimal, elegant design."""
    
    def __init__(self, parent, x: int = 720, y: int = 40, theme_name: str = "modern_dark"):
        super().__init__(parent, x=x, y=y, widget_key="uptime", theme_name=theme_name)
        
        # Boot time calculation
        from datetime import datetime
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        # Create UI elements
        self.create_uptime_ui()
        self.apply_theme()
        self.update_uptime()
        
        # Update every 30 seconds
        self.after(30000, self.update_uptime)

    def create_uptime_ui(self):
        # Uptime display with large typography
        self.uptime_label = self.create_glass_metric_label(self.body, "Calculating...")
        self.uptime_label.pack(pady=(self.SPACING_SECTION, self.SPACING_NORMAL))
        
        # Boot time display
        self.boot_label = self.create_glass_label(
            self.body,
            "Loading boot time...",
            size_key="body",
            color_key="muted"
        )
        self.boot_label.pack(pady=(0, self.SPACING_SECTION))

    def refresh_theme(self) -> None:
        if hasattr(self, 'uptime_label'):
            self.uptime_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'boot_label'):
            self.boot_label.configure(text_color=self.theme["muted"])

    def format_uptime(self, uptime_seconds):
        """Format uptime into human-readable format"""
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        if days > 0:
            return f"{int(days)}d {int(hours)}h {int(minutes)}m"
        elif hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(minutes)}m {int(seconds)}s"

    def update_uptime(self):
        from datetime import datetime
        
        if not self._running:
            return
        
        # Calculate uptime
        now = datetime.now()
        uptime_seconds = (now - self.boot_time).total_seconds()
        
        # Update uptime display
        compact = self.widget_is_compact()
        uptime_str = self.format_compact_uptime(uptime_seconds) if compact else self.format_uptime(uptime_seconds)
        self.uptime_label.configure(text=uptime_str)
        
        # Update boot time display
        boot_time_str = self.boot_time.strftime("Booted: %I:%M %p")
        boot_date_str = self.boot_time.strftime("%A, %B %d")
        boot_str = f"Since {self.boot_time.strftime('%I:%M %p')}" if compact else f"{boot_time_str}\n{boot_date_str}"
        self.boot_label.configure(text=boot_str)
        
        # Schedule next update
        self.after(30000, self.update_uptime)

    @staticmethod
    def format_compact_uptime(uptime_seconds):
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        if days > 0:
            return f"{days}d {hours}h"
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
