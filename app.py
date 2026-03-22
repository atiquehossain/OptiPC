
from __future__ import annotations

from pathlib import Path
from tkinter import PhotoImage

import customtkinter as ctk

from config.constants import APP_NAME, THEMES
from pages.cleanup_page import CleanupPage
from pages.dashboard_page import DashboardPage
from pages.devices_page import DevicesPage
from pages.recovery_page import RecoveryPage
from pages.repair_page import RepairPage
from pages.reports_page import ReportsPage
from pages.settings_page import SettingsPage
from pages.wallpaper_page import WallpaperPage
from services.action_service import ActionService
from services.app_settings_service import AppSettingsService
from services.cleanup_service import CleanupService
from services.log_service import LogService
from services.recovery_service import RecoveryService
from services.status_service import StatusService
from services.system_service import SystemService
from services.wallpaper_service import WallpaperService
from services.widget_state_service import WidgetStateService
from services.system_tray_service import SystemTrayService
from ui.sidebar import Sidebar
from ui.statusbar import StatusBar
from ui.topbar import Topbar
from widgets.network_speed_widget import NetworkSpeedWidget
from widgets.system_widgets import CPUWidget, RAMWidget, GPUWidget, PartitionsWidget, StorageWidget, CalendarWidget, ClockWidget, UptimeWidget
from widgets.modern_system_widgets import (
    ModernCPUWidget, ModernRAMWidget, ModernGPUWidget, ModernPartitionsWidget, 
    ModernStorageWidget, ModernCalendarWidget, ModernClockWidget, ModernUptimeWidget
)
from widgets.liquid_glass_widgets import (
    LiquidCPUWidget, LiquidRAMWidget, LiquidGPUWidget, LiquidPartitionsWidget, 
    LiquidStorageWidget, LiquidCalendarWidget, LiquidClockWidget, LiquidUptimeWidget
)
from widgets.toast import ToastManager


class OptiPCApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self._icon_photo = None
        self._set_window_icon()

        self.logger = LogService()
        self.status_service = StatusService()
        self.system_service = SystemService()
        self.action_service = ActionService()
        self.cleanup_service = CleanupService()
        self.recovery_service = RecoveryService()
        self.wallpaper_service = WallpaperService()

        self.report_dir = Path.home() / "OptiPCReports"
        self.report_dir.mkdir(parents=True, exist_ok=True)

        self.config_dir = Path.home() / "OptiPCConfig"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.widget_state_service = WidgetStateService(self.config_dir / "widget_state.json")
        self.app_settings = AppSettingsService(self.config_dir / "app_settings.json")
        self.tray_service = SystemTrayService()

        # Apply saved appearance before building UI
        ctk.set_appearance_mode(self.app_settings.get_appearance_mode().lower())
        ctk.set_default_color_theme("blue")
        
        # Modern color scheme
        self.configure(fg_color=(THEMES["light"]["background"], THEMES["dark"]["background"]))

        self._main_geometry_after_id = None

        self.widgets: dict[str, object] = {
            "cpu": None,
            "ram": None,
            "gpu": None,
            "partitions": None,
            "storage": None,
            "network_speed": None,
        }

        # Backward-compatible attributes used by older code paths
        self.cpu_widget = None
        self.ram_widget = None
        self.gpu_widget = None
        self.partitions_widget = None
        self.storage_widget = None
        self.network_speed_widget = None

        self._apply_saved_main_geometry()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color=(THEMES["light"]["background"], THEMES["dark"]["background"]))
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        self.topbar = Topbar(self.main_area, self.change_theme)
        self.topbar.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        self.topbar.theme_switch.set("🌙 Dark" if self.app_settings.get_appearance_mode() == "Dark" else "☀️ Light")

        self.content = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 8))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.statusbar = StatusBar(self.main_area)
        self.statusbar.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        self.status_service.bind(self.statusbar.set_status)

        self.toast_manager = ToastManager(self)
        self.status_service.bind_toast(self.toast_manager.show)

        self.protocol("WM_DELETE_WINDOW", self.on_close_clicked)
        self.bind("<Configure>", self._on_main_configure)

        self.show_page("Dashboard")
        self._start_tray_if_available()
        self.after(700, self.restore_visible_widgets_on_startup)

    def _set_window_icon(self) -> None:
        assets = Path(__file__).resolve().parent / "assets"
        ico_path = assets / "optipc_icon.ico"
        png_path = assets / "optipc_icon.png"
        try:
            if ico_path.exists():
                self.iconbitmap(default=str(ico_path))
        except Exception:
            pass
        try:
            if png_path.exists():
                self._icon_photo = PhotoImage(file=str(png_path))
                self.iconphoto(True, self._icon_photo)
        except Exception:
            pass

    def _apply_saved_main_geometry(self) -> None:
        state = self.widget_state_service.get_main_window_state()
        width = int(state.get("width", 1320))
        height = int(state.get("height", 820))
        x = int(state.get("x", 80))
        y = int(state.get("y", 60))
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(1150, 720)

    def _on_main_configure(self, event) -> None:
        if event.widget is not self:
            return
        if self._main_geometry_after_id is not None:
            try:
                self.after_cancel(self._main_geometry_after_id)
            except Exception:
                pass
        self._main_geometry_after_id = self.after(300, self._save_main_geometry)

    def _save_main_geometry(self) -> None:
        self._main_geometry_after_id = None
        self.widget_state_service.set_main_window_geometry(
            x=self.winfo_x(),
            y=self.winfo_y(),
            width=self.winfo_width(),
            height=self.winfo_height(),
        )

    def _widget_builders(self) -> dict[str, type]:
        """Get widget builders based on current theme style."""
        theme_name = self.get_widget_theme_name()
        
        # Use liquid glass widgets for modern themes
        if theme_name.startswith("modern_"):
            return {
                "cpu": LiquidCPUWidget,
                "ram": LiquidRAMWidget,
                "gpu": LiquidGPUWidget,
                "partitions": LiquidPartitionsWidget,
                "storage": LiquidStorageWidget,
                "network_speed": NetworkSpeedWidget,  # Keep original for now
                "calendar": LiquidCalendarWidget,
                "clock": LiquidClockWidget,
                "uptime": LiquidUptimeWidget,
            }
        else:
            # Use original widgets for other themes
            return {
                "cpu": CPUWidget,
                "ram": RAMWidget,
                "gpu": GPUWidget,
                "partitions": PartitionsWidget,
                "storage": StorageWidget,
                "network_speed": NetworkSpeedWidget,
                "calendar": CalendarWidget,
                "clock": ClockWidget,
                "uptime": UptimeWidget,
            }

    def get_widget_theme_name(self) -> str:
        return self.app_settings.get_widget_theme()

    def apply_widget_theme_to_open_widgets(self) -> None:
        theme_name = self.get_widget_theme_name()
        for key in self._widget_builders():
            widget = self._get_widget_ref(key)
            if widget is not None and widget.winfo_exists() and hasattr(widget, "apply_theme"):
                try:
                    widget.apply_theme(theme_name)
                except Exception:
                    pass

    def get_widget_initial_geometry(self, key: str, *, x: int, y: int, width: int, height: int) -> dict[str, int]:
        state = self.widget_state_service.get_widget_state(key)
        return {
            "x": int(state.get("x", x)),
            "y": int(state.get("y", y)),
            "width": int(state.get("width", width)),
            "height": int(state.get("height", height)),
        }

    def save_widget_geometry(self, key: str, *, x: int, y: int, width: int, height: int) -> None:
        self.widget_state_service.set_widget_geometry(key, x=x, y=y, width=width, height=height)

    def reset_widget_geometry(self, key: str) -> None:
        """Reset widget geometry to default values."""
        self.widget_state_service.reset_widget_geometry(key)

    def on_widget_visibility_changed(self, key: str, visible: bool) -> None:
        self.widget_state_service.set_widget_visible(key, visible)

    def _set_widget_ref(self, key: str, widget) -> None:
        self.widgets[key] = widget
        attr_map = {
            "cpu": "cpu_widget",
            "ram": "ram_widget",
            "gpu": "gpu_widget",
            "partitions": "partitions_widget",
            "storage": "storage_widget",
            "network_speed": "network_speed_widget",
            "calendar": "calendar_widget",
            "clock": "clock_widget",
            "uptime": "uptime_widget",
        }
        setattr(self, attr_map[key], widget)

    def _get_widget_ref(self, key: str):
        widget = self.widgets.get(key)
        if widget is None:
            attr_map = {
                "cpu": "cpu_widget",
                "ram": "ram_widget",
                "gpu": "gpu_widget",
                "partitions": "partitions_widget",
                "storage": "storage_widget",
                "network_speed": "network_speed_widget",
                "calendar": "calendar_widget",
                "clock": "clock_widget",
                "uptime": "uptime_widget",
            }
            widget = getattr(self, attr_map[key], None)
            self.widgets[key] = widget
        return widget

    def _create_or_show_widget(self, key: str, show_toast: bool = False) -> None:
        widget = self._get_widget_ref(key)
        title = key.replace("_", " ").title()
        if widget is None or not widget.winfo_exists():
            widget_class = self._widget_builders()[key]
            theme_name = self.get_widget_theme_name()
            
            # Pass theme_name to Modern widgets
            if theme_name.startswith("modern_"):
                widget = widget_class(self, theme_name=theme_name)
            else:
                widget = widget_class(self)
                
            self._set_widget_ref(key, widget)
            self.status_service.info(f"{title} widget opened", toast=show_toast)
            return
        if widget.state() == "withdrawn":
            widget.show_widget()
            self.status_service.info(f"{title} widget shown", toast=False)
        else:
            try:
                widget.show_widget()
                widget.focus_force()
            except Exception:
                pass
            self.status_service.warning(f"{title} widget is already running", toast=True)

    def _toggle_widget(self, key: str) -> None:
        self._create_or_show_widget(key, show_toast=False)

    def restore_visible_widgets_on_startup(self) -> None:
        for key in self._widget_builders():
            state = self.widget_state_service.get_widget_state(key)
            if state.get("visible", False):
                self._create_or_show_widget(key, show_toast=False)

    def show_all_saved_widgets(self) -> None:
        for key in self._widget_builders():
            state = self.widget_state_service.get_widget_state(key)
            if state.get("visible", False):
                widget = self._get_widget_ref(key)
                if widget is None or not widget.winfo_exists():
                    self._create_or_show_widget(key, show_toast=False)
                else:
                    widget.show_widget()
        self.status_service.success("Saved widgets restored", toast=True)

    def hide_all_widgets(self) -> None:
        for key in self._widget_builders():
            widget = self._get_widget_ref(key)
            if widget is not None and widget.winfo_exists():
                widget.hide_widget()
        self.status_service.info("All widgets hidden", toast=False)

    def _start_tray_if_available(self) -> None:
        started = self.tray_service.start(
            tk_after=self.after,
            on_restore=self.restore_from_tray,
            on_hide_widgets=self.hide_all_widgets,
            on_show_widgets=self.show_all_saved_widgets,
            on_exit=self.quit_from_tray,
        )
        if started:
            self.status_service.info("System tray mode ready", toast=False)
        else:
            self.status_service.warning("Tray mode unavailable (install requirements)", toast=False)

    def minimize_to_tray(self) -> None:
        self.withdraw()
        self.status_service.info("OptiPC minimized to tray", toast=True)

    def restore_from_tray(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()
        self.status_service.info("OptiPC restored", toast=False)

    def on_close_clicked(self) -> None:
        if self.tray_service.is_available:
            self.minimize_to_tray()
        else:
            self.quit_from_tray()

    def quit_from_tray(self) -> None:
        self.tray_service.stop()
        try:
            self._save_main_geometry()
        except Exception:
            pass
        for key in list(self._widget_builders().keys()):
            widget = self._get_widget_ref(key)
            if widget is not None and widget.winfo_exists():
                try:
                    widget.destroy_widget()
                except Exception:
                    pass
        self.destroy()

    def _build_page(self, page_name: str):
        if page_name == "Dashboard":
            return DashboardPage(self.content, self.logger, self.status_service, self.system_service, self.action_service)
        if page_name == "Cleanup":
            return CleanupPage(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.cleanup_service)
        if page_name == "Repair":
            return RepairPage(self.content, self.logger, self.status_service, self.system_service, self.action_service)
        if page_name == "Recovery":
            return RecoveryPage(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.recovery_service)
        if page_name == "Devices":
            return DevicesPage(self.content, self.logger, self.status_service, self.system_service, self.action_service)
        if page_name == "Wallpaper":
            return WallpaperPage(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.wallpaper_service, self.report_dir)
        if page_name == "Reports":
            return ReportsPage(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.report_dir)
        if page_name == "Settings":
            widget_theme_label = {
                "dark": "Dark",
                "light": "Light",
                "glass": "Liquid Glass",
                "modern_dark": "Modern Dark",
                "modern_light": "Modern Light",
            }.get(self.app_settings.get_widget_theme(), "Dark")
            return SettingsPage(
                self.content,
                self.logger,
                self.status_service,
                self.system_service,
                self.action_service,
                self.change_theme,
                self.change_widget_theme,
                self.app_settings.get_appearance_mode(),
                widget_theme_label,
            )
        raise ValueError(f"Unknown page: {page_name}")

    def show_page(self, page_name: str) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

        page = self._build_page(page_name)
        page.grid(row=0, column=0, sticky="nsew")
        page.build()

        self.sidebar.set_active(page_name)
        self.topbar.set_title(page_name)

    def change_theme(self, mode: str) -> None:
        # Extract the actual mode from the themed string
        actual_mode = "Dark" if "🌙" in mode else "Light"
        ctk.set_appearance_mode(actual_mode.lower())
        self.app_settings.set_appearance_mode(actual_mode)
        self.topbar.theme_switch.set(mode)
        self.status_service.success(f"App theme changed to {actual_mode}", toast=True)

    def change_widget_theme(self, label: str) -> None:
        label_map = {
            "Dark": "dark",
            "Light": "light",
            "Liquid Glass": "glass",
            "Modern Dark": "modern_dark",
            "Modern Light": "modern_light",
        }
        theme_name = label_map.get(label, "dark")
        self.app_settings.set_widget_theme(theme_name)
        self.apply_widget_theme_to_open_widgets()
        self.status_service.success(f"Widget theme changed to {label}", toast=True)

    # Backward-compatible toggle methods used by the Dashboard buttons
    def toggle_cpu_widget(self) -> None:
        self._toggle_widget("cpu")

    def toggle_ram_widget(self) -> None:
        self._toggle_widget("ram")

    def toggle_gpu_widget(self) -> None:
        self._toggle_widget("gpu")

    def toggle_partitions_widget(self) -> None:
        self._toggle_widget("partitions")

    def toggle_storage_widget(self) -> None:
        self._toggle_widget("storage")

    def toggle_network_speed_widget(self) -> None:
        self._toggle_widget("network_speed")

    def toggle_calendar_widget(self) -> None:
        self._toggle_widget("calendar")

    def toggle_clock_widget(self) -> None:
        self._toggle_widget("clock")

    def toggle_uptime_widget(self) -> None:
        self._toggle_widget("uptime")


SmartPCToolkitApp = OptiPCApp
