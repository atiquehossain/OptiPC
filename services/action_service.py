from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable
import ctypes
import subprocess


class SHQUERYRBINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("i64Size", ctypes.c_ulonglong),
        ("i64NumItems", ctypes.c_ulonglong),
    ]


class ActionService:
    """Windows actions, reports, and selected elevated commands."""

    @staticmethod
    def open_target(target: str) -> None:
        subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)

    def open_windows_settings(self) -> None:
        self.open_target("ms-settings:")

    def open_disk_cleanup(self) -> None:
        self.open_target("cleanmgr")

    def open_sound_settings(self) -> None:
        self.open_target("ms-settings:sound")

    def open_camera_settings(self) -> None:
        self.open_target("ms-settings:camera")

    def open_privacy_settings(self) -> None:
        self.open_target("ms-settings:privacy")

    def open_location_settings(self) -> None:
        self.open_target("ms-settings:privacy-location")

    def open_sound_panel(self) -> None:
        self.open_target("mmsys.cpl")

    def open_report_folder(self, folder: Path) -> None:
        self.open_target(str(folder))

    @staticmethod
    def run_command_stream(command: Iterable[str], on_output: Callable[[str], None] | None = None) -> int:
        with subprocess.Popen(
            list(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
        ) as process:
            if process.stdout is not None:
                for line in process.stdout:
                    line = line.rstrip()
                    if line and on_output:
                        on_output(line)
            return process.wait()

    @staticmethod
    def run_elevated_command(command_line: str) -> str:
        """Ask Windows to open an elevated cmd window and run one command."""
        try:
            params = f'/k {command_line}'
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", params, None, 1)
            if result > 32:
                return f"Elevated command started:\n{command_line}"
            return "Administrator prompt was cancelled or failed."
        except Exception as exc:
            return f"Could not start elevated command: {exc}"

    @staticmethod
    def empty_recycle_bin(root_path: str = "") -> str:
        try:
            shell32 = ctypes.windll.shell32
            shell32.SHQueryRecycleBinW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(SHQUERYRBINFO)]
            shell32.SHQueryRecycleBinW.restype = ctypes.c_long
            shell32.SHEmptyRecycleBinW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
            shell32.SHEmptyRecycleBinW.restype = ctypes.c_long

            target = root_path or ""
            label = target if target else "all drives"

            info = SHQUERYRBINFO()
            info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
            query_result = shell32.SHQueryRecycleBinW(target, ctypes.byref(info))
            if query_result != 0:
                return f"Could not read Recycle Bin status for {label}. HRESULT: 0x{query_result & 0xFFFFFFFF:08X}"

            if int(info.i64NumItems) == 0:
                return f"Recycle Bin is already empty on {label}."

            flags = 0x00000001 | 0x00000002 | 0x00000004
            empty_result = shell32.SHEmptyRecycleBinW(None, target, flags)
            if empty_result == 0:
                return f"Recycle Bin emptied on {label}. Removed {int(info.i64NumItems)} item(s)."
            return f"Recycle Bin cleanup failed on {label}. HRESULT: 0x{empty_result & 0xFFFFFFFF:08X}"
        except Exception as exc:
            return f"Recycle Bin cleanup error: {exc}"

    @staticmethod
    def list_cameras() -> str:
        script = (
            "Get-PnpDevice | "
            "Where-Object { $_.Class -eq 'Camera' -or $_.Class -eq 'Image' } | "
            "Sort-Object FriendlyName | "
            "Select-Object FriendlyName, Status | "
            "Format-Table -AutoSize | Out-String -Width 4096"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            shell=False,
        )
        return result.stdout.strip() or result.stderr.strip() or "No camera information found."

    @staticmethod
    def save_network_report(report_dir: Path) -> Path:
        path = report_dir / "network_report.txt"
        result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, shell=False)
        path.write_text(result.stdout or result.stderr, encoding="utf-8", errors="replace")
        return path

    @staticmethod
    def save_battery_report(report_dir: Path) -> Path:
        path = report_dir / "battery_report.html"
        subprocess.run(["powercfg", "/batteryreport", "/output", str(path)], capture_output=True, text=True, shell=False)
        return path

    @staticmethod
    def save_installed_apps_report(report_dir: Path) -> Path:
        path = report_dir / "installed_apps.txt"
        script = r"""
$items = Get-ItemProperty \
'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*', \
'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*', \
'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*' |
Where-Object { $_.DisplayName } |
Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
Sort-Object DisplayName
$items | Format-Table -AutoSize | Out-String -Width 4096
"""
        result = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], capture_output=True, text=True, shell=False)
        path.write_text(result.stdout or result.stderr, encoding="utf-8", errors="replace")
        return path

    @staticmethod
    def save_heavy_process_report(report_dir: Path) -> Path:
        path = report_dir / "heavy_processes.txt"
        script = (
            "Get-Process | Sort-Object CPU -Descending | "
            "Select-Object -First 20 ProcessName, Id, CPU, WS | "
            "Format-Table -AutoSize | Out-String -Width 4096"
        )
        result = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], capture_output=True, text=True, shell=False)
        path.write_text(result.stdout or result.stderr, encoding="utf-8", errors="replace")
        return path
