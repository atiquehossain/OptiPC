from __future__ import annotations

import calendar
import platform
import psutil
from datetime import datetime
from typing import List

import customtkinter as ctk

try:
    import GPUtil
except Exception:
    GPUtil = None

from widgets.base_mini_widget import BaseMiniWidget
from config.constants import FONT_SIZES


class CPUWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 40, y: int = 40):
        super().__init__(parent, "CPU Usage", size_category="small", x=x, y=y, widget_key="cpu")
        self.percent_label = self.create_responsive_label(self.body, "0%", "metric", "bold")
        self.percent_label.pack(pady=(4, 2))
        self.detail_label = self.create_responsive_label(self.body, "Cores: 0", "body")
        self.detail_label.pack()
        self.freq_label = self.create_responsive_label(self.body, "Frequency: N/A", "small")
        self.freq_label.pack(pady=(2, 2))
        self.progress = ctk.CTkProgressBar(self.body, width=180)
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
        super().__init__(parent, "RAM Usage", size_category="small", x=x, y=y, widget_key="ram")
        self.percent_label = self.create_responsive_label(self.body, "0%", "metric", "bold")
        self.percent_label.pack(pady=(6, 2))
        self.detail_label = self.create_responsive_label(self.body, "0 GB / 0 GB", "body")
        self.detail_label.pack()
        self.avail_label = self.create_responsive_label(self.body, "Available: 0 GB", "small")
        self.avail_label.pack(pady=(2, 2))
        self.progress = ctk.CTkProgressBar(self.body, width=180)
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
        super().__init__(parent, "GPU Usage", size_category="small", x=x, y=y, widget_key="gpu")
        self.name_label = self.create_responsive_label(self.body, "GPU: Detecting...", "label", "bold")
        self.name_label.pack(anchor="w", pady=(4, 6))
        self.percent_label = self.create_responsive_label(self.body, "N/A", "metric", "bold")
        self.percent_label.pack()
        self.mem_label = self.create_responsive_label(self.body, "Memory: N/A", "body")
        self.mem_label.pack(pady=(4, 6))
        self.progress = ctk.CTkProgressBar(self.body, width=180)
        self.progress.pack(fill="x", padx=4, pady=(8, 4))
        self.progress.set(0)
        self.note_label = self.create_responsive_label(self.body, "Some systems may not expose GPU usage", "small")
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
        super().__init__(parent, "Drive Partitions", size_category="large", x=x, y=y, widget_key="partitions")
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
        super().__init__(parent, "SSD / HDD Summary", size_category="large", x=x, y=y, widget_key="storage")
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


class CalendarWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 40, y: int = 570):
        super().__init__(parent, "Calendar", size_category="extra_large", x=x, y=y, widget_key="calendar")
        
        # Current date tracking
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
        # Month/Year navigation
        nav_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(8, 4))
        
        # Previous month button
        self.prev_btn = ctk.CTkButton(
            nav_frame, 
            text="◀", 
            width=30, 
            height=30,
            command=self.previous_month
        )
        self.prev_btn.pack(side="left", padx=(0, 8))
        
        # Month/Year label
        self.month_label = self.create_responsive_label(
            nav_frame,
            "",
            "title",
            "bold"
        )
        self.month_label.pack(side="left", expand=True)
        
        # Next month button
        self.next_btn = ctk.CTkButton(
            nav_frame, 
            text="▶", 
            width=30, 
            height=30,
            command=self.next_month
        )
        self.next_btn.pack(side="left", padx=(8, 0))
        
        # Today button
        self.today_btn = ctk.CTkButton(
            nav_frame,
            text="Today",
            width=60,
            height=30,
            command=self.go_to_today
        )
        self.today_btn.pack(side="right", padx=(8, 0))
        
        # Calendar grid frame
        self.calendar_frame = ctk.CTkFrame(self.body, corner_radius=12)
        self.calendar_frame.pack(fill="both", expand=True, padx=4, pady=(8, 12))
        
        # Day headers
        self.day_labels = []
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            label = self.create_responsive_label(
                self.calendar_frame,
                day,
                "small",
                "bold"
            )
            label.configure(width=40, height=25)
            label.grid(row=0, column=i, padx=2, pady=2)
            self.day_labels.append(label)
        
        # Day buttons (6 weeks x 7 days)
        self.day_buttons = []
        for week in range(6):
            week_buttons = []
            for day in range(7):
                btn = ctk.CTkButton(
                    self.calendar_frame,
                    text="",
                    width=40,
                    height=35,
                    corner_radius=8,
                    font=ctk.CTkFont(size=self.get_responsive_font_size("body")),
                    text_color="#ffffff",  # Force white text initially
                    command=lambda w=week, d=day: self.day_clicked(w, d)
                )
                btn.grid(row=week + 1, column=day, padx=2, pady=2)
                week_buttons.append(btn)
            self.day_buttons.append(week_buttons)
        
        # Current date/time display
        self.datetime_label = self.create_responsive_label(
            self.body,
            "",
            "small"
        )
        self.datetime_label.pack(pady=(4, 8))

    def refresh_theme(self) -> None:
        if hasattr(self, 'month_label'):
            self.month_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'datetime_label'):
            self.datetime_label.configure(text_color=self.theme["muted"])
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
                fg_color=self.theme["accent"],
                hover_color=self.theme.get("button_hover", "#343638"),
                text_color=self.theme["text"]
            )
        if hasattr(self, 'day_labels'):
            for label in self.day_labels:
                label.configure(text_color=self.theme["muted"])
        
        # Update day buttons with current theme
        self.update_calendar()

    def update_calendar(self):
        # Update month/year label
        month_name = calendar.month_name[self.display_month]
        self.month_label.configure(text=f"{month_name} {self.display_year}")
        
        # Get calendar data
        cal = calendar.monthcalendar(self.display_year, self.display_month)
        
        # Clear and update day buttons
        for week in range(6):
            for day in range(7):
                btn = self.day_buttons[week][day]
                
                if week < len(cal) and day < len(cal[week]) and cal[week][day] != 0:
                    day_num = cal[week][day]
                    btn.configure(text=str(day_num))
                    
                    # Check if this is today
                    is_today = (self.display_year == self.current_date.year and 
                               self.display_month == self.current_date.month and 
                               day_num == self.current_date.day)
                    
                    # Check if this is weekend
                    is_weekend = day == 0 or day == 6
                    
                    # Apply styling based on conditions
                    if is_today:
                        btn.configure(
                            fg_color=self.theme.get("accent", "#1f6aa5"),
                            hover_color=self.theme.get("button_hover", "#343638"),
                            text_color="white",
                            font=ctk.CTkFont(size=self.get_responsive_font_size("body"), weight="bold")
                        )
                    elif is_weekend:
                        btn.configure(
                            fg_color=self.theme.get("panel", "#212121"),
                            hover_color=self.theme.get("button_hover", "#343638"),
                            text_color=self.theme.get("accent", "#1f6aa5"),
                            font=ctk.CTkFont(size=self.get_responsive_font_size("body"))
                        )
                    else:
                        btn.configure(
                            fg_color=self.theme.get("panel", "#212121"),
                            hover_color=self.theme.get("button_hover", "#343638"),
                            text_color=self.theme.get("text", "#ffffff"),
                            font=ctk.CTkFont(size=self.get_responsive_font_size("body"))
                        )
                else:
                    btn.configure(
                        text="",
                        fg_color=self.theme.get("window_bg", "#141922"),
                        hover_color=self.theme.get("window_bg", "#141922"),
                        text_color=self.theme.get("text", "#ffffff")
                    )
        
        # Update current time display
        self.update_time()

    def update_time(self):
        if not self._running:
            return
        
        now = datetime.now()
        time_str = now.strftime("%A, %B %d, %Y - %I:%M %p")
        self.datetime_label.configure(text=time_str)
        
        # Check if we need to refresh the calendar (new day)
        if now.day != self.current_date.day:
            self.current_date = now
            self.update_calendar()
        
        # Schedule next update
        self.after(60000, self.update_time)  # Update every minute

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
        # Get the day number from the button
        btn = self.day_buttons[week][day]
        day_text = btn.cget("text")
        
        if day_text:  # Only process if it's a valid day
            day_num = int(day_text)
            clicked_date = datetime(self.display_year, self.display_month, day_num)
            
            # You could add functionality here, like:
            # - Adding events to a calendar
            # - Opening a date picker
            # - Showing date details
            
            # For now, just show a toast or update the display
            if hasattr(self.master, 'status_service'):
                self.master.status_service.info(
                    f"Selected: {clicked_date.strftime('%A, %B %d, %Y')}", 
                    toast=True
                )


class ClockWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 400, y: int = 40):
        super().__init__(parent, "Clock", size_category="small", x=x, y=y, widget_key="clock")
        
        # Create UI elements
        self.create_clock_ui()
        self.apply_theme()
        self.update_clock()
        
        # Update every second
        self.after(1000, self.update_clock)

    def create_clock_ui(self):
        # Main time display
        self.time_label = self.create_responsive_label(
            self.body,
            "00:00:00",
            "hero",
            "bold"
        )
        self.time_label.pack(pady=(20, 10))
        
        # Date display
        self.date_label = self.create_responsive_label(
            self.body,
            "Loading...",
            "title"
        )
        self.date_label.pack(pady=(0, 10))
        
        # Day of week display
        self.day_label = self.create_responsive_label(
            self.body,
            "Loading...",
            "body"
        )
        self.day_label.pack(pady=(0, 20))

    def refresh_theme(self) -> None:
        if hasattr(self, 'time_label'):
            self.time_label.configure(text_color=self.theme["text"])
        if hasattr(self, 'date_label'):
            self.date_label.configure(text_color=self.theme["accent"])
        if hasattr(self, 'day_label'):
            self.day_label.configure(text_color=self.theme["muted"])

    def update_clock(self):
        if not self._running:
            return
        
        now = datetime.now()
        
        # Update time
        time_str = now.strftime("%I:%M:%S %p")
        self.time_label.configure(text=time_str)
        
        # Update date
        date_str = now.strftime("%B %d, %Y")
        self.date_label.configure(text=date_str)
        
        # Update day of week
        day_str = now.strftime("%A")
        self.day_label.configure(text=day_str)
        
        # Schedule next update
        self.after(1000, self.update_clock)


class UptimeWidget(BaseMiniWidget):
    def __init__(self, parent, x: int = 720, y: int = 40):
        super().__init__(parent, "PC Uptime", size_category="small", x=x, y=y, widget_key="uptime")
        
        # Boot time calculation
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        # Create UI elements
        self.create_uptime_ui()
        self.apply_theme()
        self.update_uptime()
        
        # Update every 30 seconds
        self.after(30000, self.update_uptime)

    def create_uptime_ui(self):
        # Uptime display
        self.uptime_label = self.create_responsive_label(
            self.body,
            "Calculating...",
            "title",
            "bold"
        )
        self.uptime_label.pack(pady=(20, 10))
        
        # Boot time display
        self.boot_label = self.create_responsive_label(
            self.body,
            "Loading boot time...",
            "body"
        )
        self.boot_label.pack(pady=(0, 20))

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
        if not self._running:
            return
        
        # Calculate uptime
        now = datetime.now()
        uptime_seconds = (now - self.boot_time).total_seconds()
        
        # Update uptime display
        uptime_str = self.format_uptime(uptime_seconds)
        self.uptime_label.configure(text=uptime_str)
        
        # Update boot time display
        boot_time_str = self.boot_time.strftime("Booted: %I:%M %p")
        boot_date_str = self.boot_time.strftime("%A, %B %d")
        boot_str = f"{boot_time_str}\n{boot_date_str}"
        self.boot_label.configure(text=boot_str)
        
        # Schedule next update
        self.after(30000, self.update_uptime)
