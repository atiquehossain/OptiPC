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
from services.log_service import LogService
from services.recovery_service import RecoveryService
from services.status_service import StatusService
from services.system_service import SystemService
from services.wallpaper_service import WallpaperService
from ui.sidebar import Sidebar
from ui.statusbar import StatusBar
from ui.topbar import Topbar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SmartPCToolkitApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("SmartPC Toolkit")
        self.geometry("1320x820")
        self.minsize(1150, 720)

        self.logger = LogService()
        self.status_service = StatusService()
        self.system_service = SystemService()
        self.action_service = ActionService()
        self.recovery_service = RecoveryService()
        self.wallpaper_service = WallpaperService()
        self.report_dir = Path.home() / "SmartPCReports"
        self.report_dir.mkdir(parents=True, exist_ok=True)

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

        self.pages = self._create_pages()
        self.show_page("Dashboard")

    def _create_pages(self):
        return {
            "Dashboard": DashboardPage(self.content, self.logger, self.status_service, self.system_service, self.action_service),
            "Cleanup": CleanupPage(self.content, self.logger, self.status_service, self.system_service, self.action_service),
            "Repair": RepairPage(self.content, self.logger, self.status_service, self.system_service, self.action_service),
            "Recovery": RecoveryPage(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.recovery_service),
            "Devices": DevicesPage(self.content, self.logger, self.status_service, self.system_service, self.action_service),
            "Wallpaper": WallpaperPage(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.wallpaper_service, self.report_dir),
            "Reports": ReportsPage(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.report_dir),
            "Settings": SettingsPage(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.change_theme),
        }

    def show_page(self, page_name: str) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()
        page = self.pages[page_name]
        # Recreate the page instance each time so page log boxes and widgets are fresh
        page_class = page.__class__
        if page_name == "Recovery":
            page = page_class(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.recovery_service)
        elif page_name == "Wallpaper":
            page = page_class(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.wallpaper_service, self.report_dir)
        elif page_name == "Reports":
            page = page_class(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.report_dir)
        elif page_name == "Settings":
            page = page_class(self.content, self.logger, self.status_service, self.system_service, self.action_service, self.change_theme)
        else:
            page = page_class(self.content, self.logger, self.status_service, self.system_service, self.action_service)
        self.pages[page_name] = page
        page.grid(row=0, column=0, sticky="nsew")
        page.build()
        self.sidebar.set_active(page_name)
        self.topbar.set_title(page_name)

    def change_theme(self, mode: str) -> None:
        ctk.set_appearance_mode(mode.lower())
