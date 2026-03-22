from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from pages.cleanup_page import CleanupPage
from pages.dashboard_page import DashboardPage
from pages.devices_page import DevicesPage
from pages.recovery_page import RecoveryPage
from pages.repair_page import RepairPage
from pages.reports_page import ReportsPage
from pages.settings_page import SettingsPage
from pages.wallpaper_page import WallpaperPage
from services.action_service import ActionService
from services.cleanup_service import CleanupService
from services.log_service import LogService
from services.recovery_service import RecoveryService
from services.status_service import StatusService
from services.system_service import SystemService
from services.wallpaper_service import WallpaperService
from ui.sidebar import Sidebar
from ui.statusbar import StatusBar
from ui.topbar import Topbar
from widgets.network_speed_widget import NetworkSpeedWidget
from widgets.system_widgets import CPUWidget, RAMWidget, GPUWidget, PartitionsWidget, StorageWidget

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class OptiPCApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("OptiPC")
        self.geometry("1320x820")
        self.minsize(1150, 720)

        self.logger = LogService()
        self.status_service = StatusService()
        self.system_service = SystemService()
        self.action_service = ActionService()
        self.cleanup_service = CleanupService()
        self.recovery_service = RecoveryService()
        self.wallpaper_service = WallpaperService()

        self.report_dir = Path.home() / "OptiPCReports"
        self.report_dir.mkdir(parents=True, exist_ok=True)

        self.cpu_widget = None
        self.ram_widget = None
        self.gpu_widget = None
        self.partitions_widget = None
        self.storage_widget = None
        self.network_speed_widget = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray95", "gray12"))
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        self.topbar = Topbar(self.main_area, self.change_theme)
        self.topbar.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))

        self.content = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 8))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.statusbar = StatusBar(self.main_area)
        self.statusbar.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        self.status_service.bind(self.statusbar.set_status)

        self.show_page("Dashboard")

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
            return SettingsPage(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.change_theme)
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
        ctk.set_appearance_mode(mode.lower())

    def toggle_cpu_widget(self) -> None:
        if self.cpu_widget is None or not self.cpu_widget.winfo_exists():
            self.cpu_widget = CPUWidget(self)
            return
        if self.cpu_widget.state() == "withdrawn":
            self.cpu_widget.show_widget()
        else:
            self.cpu_widget.hide_widget()

    def toggle_ram_widget(self) -> None:
        if self.ram_widget is None or not self.ram_widget.winfo_exists():
            self.ram_widget = RAMWidget(self)
            return
        if self.ram_widget.state() == "withdrawn":
            self.ram_widget.show_widget()
        else:
            self.ram_widget.hide_widget()

    def toggle_gpu_widget(self) -> None:
        if self.gpu_widget is None or not self.gpu_widget.winfo_exists():
            self.gpu_widget = GPUWidget(self)
            return
        if self.gpu_widget.state() == "withdrawn":
            self.gpu_widget.show_widget()
        else:
            self.gpu_widget.hide_widget()

    def toggle_partitions_widget(self) -> None:
        if self.partitions_widget is None or not self.partitions_widget.winfo_exists():
            self.partitions_widget = PartitionsWidget(self)
            return
        if self.partitions_widget.state() == "withdrawn":
            self.partitions_widget.show_widget()
        else:
            self.partitions_widget.hide_widget()

    def toggle_storage_widget(self) -> None:
        if self.storage_widget is None or not self.storage_widget.winfo_exists():
            self.storage_widget = StorageWidget(self)
            return
        if self.storage_widget.state() == "withdrawn":
            self.storage_widget.show_widget()
        else:
            self.storage_widget.hide_widget()

    def toggle_network_speed_widget(self) -> None:
        if self.network_speed_widget is None or not self.network_speed_widget.winfo_exists():
            self.network_speed_widget = NetworkSpeedWidget(self)
            return
        if self.network_speed_widget.state() == "withdrawn":
            self.network_speed_widget.show_widget()
        else:
            self.network_speed_widget.hide_widget()


SmartPCToolkitApp = OptiPCApp
