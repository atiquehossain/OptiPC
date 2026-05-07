
from __future__ import annotations

from pathlib import Path
from tkinter import PhotoImage

import customtkinter as ctk

from config.constants import APP_NAME, THEMES, WIDGET_THEMES
from config.widget_specs import widget_title
from pages.about_developer_page import AboutDeveloperPage
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
from services.widget_material_service import (
    normalize_widget_color_mode,
    resolve_widget_material_theme,
    widget_color_mode_label,
    widget_color_mode_value,
)
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
from widgets.smart_widgets import (
    BatteryHealthWidget,
    DiskIOWidget,
    NetworkQualityWidget,
    PCHealthWidget,
    PerformanceTimelineWidget,
    QuickActionsWidget,
    StorageCleanupWidget,
    TemperatureWidget,
    TopProcessesWidget,
    WindowsUpdateWidget,
)
from widgets.toast import ToastManager
from widgets.window_interactions import (
    current_widget_geometry,
    effective_window_size,
    find_non_overlapping_position,
    get_virtual_screen_bounds,
)


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
        self._wallpaper_path_cache: str | None = None

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
        smart_widgets = {
            "pc_health": PCHealthWidget,
            "top_processes": TopProcessesWidget,
            "battery_health": BatteryHealthWidget,
            "storage_cleanup": StorageCleanupWidget,
            "disk_io": DiskIOWidget,
            "network_quality": NetworkQualityWidget,
            "windows_update": WindowsUpdateWidget,
            "temperature": TemperatureWidget,
            "quick_actions": QuickActionsWidget,
            "performance_timeline": PerformanceTimelineWidget,
        }
        
        # Use liquid glass widgets for the Liquid Glass and modern themes.
        if self._uses_liquid_widget_style(theme_name):
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
                **smart_widgets,
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
                **smart_widgets,
            }

    @staticmethod
    def _uses_liquid_widget_style(theme_name: str) -> bool:
        return theme_name == "glass" or theme_name.startswith("modern_")

    def get_widget_theme_name(self) -> str:
        return self.app_settings.get_widget_theme()

    def get_widget_color_mode(self) -> str:
        return normalize_widget_color_mode(self.app_settings.get_widget_color_mode())

    def _current_wallpaper_path(self) -> str:
        if self._wallpaper_path_cache is not None:
            return self._wallpaper_path_cache
        try:
            current = self.wallpaper_service.get_current_wallpaper()
            if current:
                self._wallpaper_path_cache = current
        except Exception:
            pass
        if self._wallpaper_path_cache is None:
            self._wallpaper_path_cache = ""
        return self._wallpaper_path_cache

    def resolve_widget_theme(self, theme_name: str, *, active: bool = True) -> dict:
        base_theme = WIDGET_THEMES.get(theme_name, WIDGET_THEMES["modern_dark"])
        return resolve_widget_material_theme(
            base_theme,
            mode=self.get_widget_color_mode(),
            appearance=self.app_settings.get_appearance_mode(),
            wallpaper_path=self._current_wallpaper_path(),
            active=active,
        )

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
        geometry = {
            "x": int(state.get("x", x)),
            "y": int(state.get("y", y)),
            "width": int(state.get("width", width)),
            "height": int(state.get("height", height)),
        }
        geometry["x"], geometry["y"] = self._non_overlapping_widget_position(
            key,
            geometry["x"],
            geometry["y"],
            geometry["width"],
            geometry["height"],
        )
        return geometry

    def _visible_widget_rects(self, exclude_key: str | None = None) -> list[tuple[int, int, int, int]]:
        seen: set[tuple[int, int, int, int]] = set()
        live_keys: set[str] = set()
        rects: list[tuple[int, int, int, int]] = []
        for key, widget in self.widgets.items():
            if key == exclude_key or widget is None:
                continue
            try:
                saved_visible = self.widget_state_service.get_widget_state(key).get("visible", False)
                if not widget.winfo_exists() or (widget.state() == "withdrawn" and not saved_visible):
                    continue
                rect = self._widget_window_rect(widget)
                if rect not in seen:
                    rects.append(rect)
                    seen.add(rect)
                live_keys.add(key)
            except Exception:
                continue
        for key, state in self.widget_state_service.get_all_widget_states().items():
            if key == exclude_key or key in live_keys or not state.get("visible", False):
                continue
            try:
                rect = (
                    int(state["x"]),
                    int(state["y"]),
                    *self._effective_widget_size(max(1, int(state["width"])), max(1, int(state["height"]))),
                )
            except Exception:
                continue
            if rect not in seen:
                rects.append(rect)
                seen.add(rect)
        return rects

    @staticmethod
    def _widget_window_rect(widget) -> tuple[int, int, int, int]:
        x, y, width, height = current_widget_geometry(widget)
        effective_width, effective_height = effective_window_size(widget, width, height)
        return x, y, effective_width, effective_height

    def _effective_widget_size(self, width: int, height: int) -> tuple[int, int]:
        return effective_window_size(self, width, height)

    def _non_overlapping_widget_position(
        self,
        key: str,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> tuple[int, int]:
        obstacles = self._visible_widget_rects(exclude_key=key)
        if not obstacles:
            return int(x), int(y)
        effective_width, effective_height = self._effective_widget_size(int(width), int(height))
        return find_non_overlapping_position(
            int(x),
            int(y),
            effective_width,
            effective_height,
            obstacles,
            gap=18,
            margin=12,
            screen_bounds=get_virtual_screen_bounds(self),
        )

    def place_widget_without_overlap(self, widget) -> None:
        key = getattr(widget, "widget_key", "")
        if not key:
            return
        try:
            current_x, current_y, width, height = current_widget_geometry(widget)
            x, y = self._non_overlapping_widget_position(key, current_x, current_y, width, height)
            if x != current_x or y != current_y:
                widget.geometry(f"{width}x{height}+{x}+{y}")
                save_now = getattr(widget, "_save_geometry_now", None)
                if callable(save_now):
                    widget.after(0, save_now)
        except Exception:
            pass

    def save_widget_geometry(self, key: str, *, x: int, y: int, width: int, height: int) -> None:
        self.widget_state_service.set_widget_geometry(key, x=x, y=y, width=width, height=height)

    def reset_widget_geometry(self, key: str) -> None:
        """Reset widget geometry to default values."""
        self.widget_state_service.reset_widget_geometry(key)

    def on_widget_visibility_changed(self, key: str, visible: bool) -> None:
        self.widget_state_service.set_widget_visible(key, visible)

    def _set_widget_ref(self, key: str, widget) -> None:
        self.widgets[key] = widget
        setattr(self, f"{key}_widget", widget)

    def _get_widget_ref(self, key: str):
        widget = self.widgets.get(key)
        if widget is None:
            widget = getattr(self, f"{key}_widget", None)
            self.widgets[key] = widget
        return widget

    def _create_or_show_widget(self, key: str, show_toast: bool = False) -> None:
        widget = self._get_widget_ref(key)
        title = widget_title(key)
        if widget is None or not widget.winfo_exists():
            widget_class = self._widget_builders()[key]
            theme_name = self.get_widget_theme_name()
            
            # Liquid and smart widgets accept an explicit theme. Original base
            # widgets read the current theme from the parent.
            if self._uses_liquid_widget_style(theme_name) and key not in {
                "network_speed",
            }:
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
        self.after(250, self._settle_visible_widgets)

    def _settle_visible_widgets(self) -> None:
        for key in self._widget_builders():
            widget = self._get_widget_ref(key)
            if widget is None:
                continue
            try:
                if widget.winfo_exists() and widget.state() != "withdrawn":
                    self.place_widget_without_overlap(widget)
            except Exception:
                continue

    def show_all_saved_widgets(self) -> None:
        for key in self._widget_builders():
            state = self.widget_state_service.get_widget_state(key)
            if state.get("visible", False):
                widget = self._get_widget_ref(key)
                if widget is None or not widget.winfo_exists():
                    self._create_or_show_widget(key, show_toast=False)
                else:
                    widget.show_widget()
        self.after(250, self._settle_visible_widgets)
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
            return DashboardPage(
                self.content,
                self.logger,
                self.status_service,
                self.system_service,
                self.action_service,
                self.cleanup_service,
            )
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
        if page_name == "About Developer":
            return AboutDeveloperPage(self.content, self.logger, self.status_service, self.system_service, self.action_service)
        if page_name == "Settings":
            widget_theme_label = {
                "dark": "Dark",
                "light": "Light",
                "glass": "Liquid Glass",
                "modern_dark": "Modern Dark",
                "modern_light": "Modern Light",
            }.get(self.app_settings.get_widget_theme(), "Dark")
            widget_color_mode = widget_color_mode_label(self.app_settings.get_widget_color_mode())
            return SettingsPage(
                self.content,
                self.logger,
                self.status_service,
                self.system_service,
                self.action_service,
                self.change_theme,
                self.change_widget_theme,
                self.change_widget_color_mode,
                self.app_settings.get_appearance_mode(),
                widget_theme_label,
                widget_color_mode,
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
        mode_text = str(mode).lower()
        actual_mode = "Dark" if "dark" in mode_text else "Light"
        display_mode = "🌙 Dark" if actual_mode == "Dark" else "☀️ Light"
        ctk.set_appearance_mode(actual_mode.lower())
        self.app_settings.set_appearance_mode(actual_mode)
        self.topbar.theme_switch.set(display_mode)
        self.sidebar.update_theme(actual_mode.lower())
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

    def change_widget_color_mode(self, label: str) -> None:
        mode = widget_color_mode_value(label)
        self.app_settings.set_widget_color_mode(mode)
        self._wallpaper_path_cache = None
        self.apply_widget_theme_to_open_widgets()
        self.status_service.success(f"Widget color changed to {label}", toast=True)

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

    def toggle_pc_health_widget(self) -> None:
        self._toggle_widget("pc_health")

    def toggle_top_processes_widget(self) -> None:
        self._toggle_widget("top_processes")

    def toggle_battery_health_widget(self) -> None:
        self._toggle_widget("battery_health")

    def toggle_storage_cleanup_widget(self) -> None:
        self._toggle_widget("storage_cleanup")

    def toggle_disk_io_widget(self) -> None:
        self._toggle_widget("disk_io")

    def toggle_network_quality_widget(self) -> None:
        self._toggle_widget("network_quality")

    def toggle_windows_update_widget(self) -> None:
        self._toggle_widget("windows_update")

    def toggle_temperature_widget(self) -> None:
        self._toggle_widget("temperature")

    def toggle_quick_actions_widget(self) -> None:
        self._toggle_widget("quick_actions")

    def toggle_performance_timeline_widget(self) -> None:
        self._toggle_widget("performance_timeline")


SmartPCToolkitApp = OptiPCApp
