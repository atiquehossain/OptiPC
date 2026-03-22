
from __future__ import annotations

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from pages.base_page import BasePage
from services.wallpaper_service import WallpaperService
from widgets.log_box import LogBox


class WallpaperPage(BasePage):
    def __init__(self, parent, logger, status_service, system_service, action_service, wallpaper_service: WallpaperService, report_dir: Path) -> None:
        super().__init__(parent, logger, status_service, system_service, action_service)
        self.wallpaper_service = wallpaper_service
        self.report_dir = report_dir
        self.image_var = ctk.StringVar(value="")
        self.style_var = ctk.StringVar(value="fill")

    def build(self) -> None:
        wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_columnconfigure((0, 1), weight=1)

        left = self.make_card(wrapper, "Wallpaper Tools", "Choose an image and set it as wallpaper")
        left.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(left, text="Selected image").pack(anchor="w", padx=18, pady=(0, 4))
        ctk.CTkEntry(left, textvariable=self.image_var, width=520).pack(anchor="w", padx=18, pady=(0, 12))

        row1 = ctk.CTkFrame(left, fg_color="transparent")
        row1.pack(fill="x", padx=18, pady=(0, 12))
        row1.grid_columnconfigure((0, 1), weight=1)
        self.make_action_button(row1, "Browse Image", self.choose_image).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(row1, "Show Current Wallpaper", self.show_current_wallpaper).grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        ctk.CTkLabel(left, text="Wallpaper style").pack(anchor="w", padx=18, pady=(0, 4))
        style_switch = ctk.CTkSegmentedButton(left, values=["fill", "fit", "stretch", "center", "tile", "span"], variable=self.style_var)
        style_switch.pack(anchor="w", padx=18, pady=(0, 12))
        style_switch.set("fill")

        row2 = ctk.CTkFrame(left, fg_color="transparent")
        row2.pack(fill="x", padx=18, pady=(0, 18))
        row2.grid_columnconfigure((0, 1, 2), weight=1)
        self.make_action_button(row2, "Set as Wallpaper", self.set_selected_wallpaper).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.make_action_button(row2, "Backup Current", self.backup_current_wallpaper).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.make_action_button(row2, "Restore Backup", self.restore_backup_wallpaper).grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        right = self.make_card(wrapper, "Notes", "Wallpaper feature info")
        right.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(
            right,
            text="Supported image types: JPG, JPEG, PNG, BMP.\nWallpaper changes do not need admin rights.\nUse Backup Current before changing the wallpaper if you want easy restore.",
            justify="left",
            wraplength=420,
            text_color="gray75",
        ).pack(anchor="w", padx=18, pady=(0, 18))

        log_card = self.make_card(wrapper, "Wallpaper Output")
        log_card.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        log_box = LogBox(log_card)
        log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.logger.bind(log_box.append)
        self.logger.write("Wallpaper page loaded.")
        self.status_service.info("Wallpaper page ready", toast=False)

    def choose_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose wallpaper image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")],
        )
        if path:
            self.image_var.set(path)
            self.logger.write(f"Selected image:\n{path}")

    def show_current_wallpaper(self) -> None:
        current = self.wallpaper_service.get_current_wallpaper()
        self.logger.write(f"Current wallpaper:\n{current}" if current else "Could not read current wallpaper.")
        self.status_service.info("Current wallpaper loaded", toast=False)

    def set_selected_wallpaper(self) -> None:
        result = self.wallpaper_service.set_wallpaper(self.image_var.get().strip(), style=self.style_var.get().strip())
        self.logger.write(result.message)
        if result.success:
            self.status_service.success("Wallpaper changed", toast=True)
        else:
            self.status_service.error("Wallpaper action failed", toast=True)

    def backup_current_wallpaper(self) -> None:
        backup_file = self.report_dir / "wallpaper_backup.txt"
        result = self.wallpaper_service.save_current_wallpaper_backup(str(backup_file))
        self.logger.write(result.message)
        if result.success:
            self.status_service.success("Wallpaper backup saved", toast=True)
        else:
            self.status_service.error("Wallpaper backup failed", toast=True)

    def restore_backup_wallpaper(self) -> None:
        backup_file = self.report_dir / "wallpaper_backup.txt"
        result = self.wallpaper_service.restore_wallpaper_from_backup(str(backup_file), style=self.style_var.get().strip())
        self.logger.write(result.message)
        if result.success:
            self.status_service.success("Wallpaper restored", toast=True)
        else:
            self.status_service.error("Wallpaper restore failed", toast=True)
