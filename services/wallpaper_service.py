from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import ctypes
import winreg


@dataclass
class WallpaperResult:
    success: bool
    message: str


class WallpaperService:
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02

    STYLE_MAP = {
        "fill": ("10", "0"),
        "fit": ("6", "0"),
        "stretch": ("2", "0"),
        "tile": ("0", "1"),
        "center": ("0", "0"),
        "span": ("22", "0"),
    }

    def get_current_wallpaper(self) -> str:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
                value, _ = winreg.QueryValueEx(key, "WallPaper")
                return str(value)
        except Exception:
            return ""

    def set_wallpaper_style(self, style: str) -> None:
        style = style.lower().strip()
        wallpaper_style, tile_wallpaper = self.STYLE_MAP.get(style, self.STYLE_MAP["fill"])
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, wallpaper_style)
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, tile_wallpaper)

    def set_wallpaper(self, image_path: str, style: str = "fill") -> WallpaperResult:
        path = Path(image_path).expanduser().resolve()
        if not path.exists():
            return WallpaperResult(False, f"Image not found: {path}")
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp"}:
            return WallpaperResult(False, "Unsupported image type. Use JPG, JPEG, PNG, or BMP.")
        try:
            self.set_wallpaper_style(style)
            result = ctypes.windll.user32.SystemParametersInfoW(
                self.SPI_SETDESKWALLPAPER, 0, str(path), self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )
            if result:
                return WallpaperResult(True, f"Wallpaper set successfully:\n{path}")
            return WallpaperResult(False, "Windows could not set the wallpaper.")
        except Exception as exc:
            return WallpaperResult(False, f"Wallpaper error: {exc}")

    def save_current_wallpaper_backup(self, backup_file: str) -> WallpaperResult:
        try:
            current = self.get_current_wallpaper()
            Path(backup_file).write_text(current, encoding="utf-8")
            return WallpaperResult(True, f"Wallpaper backup saved to:\n{backup_file}")
        except Exception as exc:
            return WallpaperResult(False, f"Backup failed: {exc}")

    def restore_wallpaper_from_backup(self, backup_file: str, style: str = "fill") -> WallpaperResult:
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return WallpaperResult(False, "Backup file not found.")
            saved_path = backup_path.read_text(encoding="utf-8").strip()
            if not saved_path:
                return WallpaperResult(False, "Backup file is empty.")
            return self.set_wallpaper(saved_path, style=style)
        except Exception as exc:
            return WallpaperResult(False, f"Restore failed: {exc}")
