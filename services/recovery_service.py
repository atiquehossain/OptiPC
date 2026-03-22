from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import shutil
import subprocess

import psutil


@dataclass(frozen=True)
class RecoveryRequest:
    source_drive: str
    destination_drive: str
    mode: str
    filter_pattern: str
    auto_confirm: bool = True


class RecoveryService:
    SUPPORTED_MODES = {
        "regular": "/regular",
        "extensive": "/extensive",
    }

    def list_drives(self) -> list[str]:
        drives: list[str] = []
        for partition in psutil.disk_partitions(all=False):
            device = partition.device.rstrip("\\")
            options = partition.opts.lower()
            if "cdrom" in options:
                continue
            if len(device) == 2 and device[1] == ":" and device not in drives:
                drives.append(device)
        return sorted(drives)

    def is_winfr_available(self) -> bool:
        if shutil.which("winfr"):
            return True
        try:
            result = subprocess.run(["winfr", "/?"], capture_output=True, text=True, timeout=5, shell=False)
            return result.returncode in (0, 1)
        except Exception:
            return False

    @staticmethod
    def normalize_drive(drive: str) -> str:
        cleaned = drive.strip().rstrip("\\/")
        if len(cleaned) >= 2:
            return cleaned[:2].upper()
        return cleaned.upper()

    def validate_request(self, request: RecoveryRequest) -> None:
        source = self.normalize_drive(request.source_drive)
        destination = self.normalize_drive(request.destination_drive)

        if source == destination:
            raise ValueError("Source drive and destination drive must be different.")
        drives = self.list_drives()
        if source not in drives:
            raise ValueError(f"Source drive {source} was not found.")
        if destination not in drives:
            raise ValueError(f"Destination drive {destination} was not found.")
        if request.mode not in self.SUPPORTED_MODES:
            raise ValueError("Unsupported mode. Use regular or extensive.")
        if not request.filter_pattern.strip():
            raise ValueError("Please enter a file or folder filter pattern.")

    def build_command(self, request: RecoveryRequest) -> list[str]:
        self.validate_request(request)
        command = [
            "winfr",
            self.normalize_drive(request.source_drive),
            self.normalize_drive(request.destination_drive),
            self.SUPPORTED_MODES[request.mode],
            "/n",
            request.filter_pattern,
        ]
        if request.auto_confirm:
            command.append("/a")
        return command

    def preview_command(self, request: RecoveryRequest) -> str:
        return subprocess.list2cmdline(self.build_command(request))

    def run_recovery(self, request: RecoveryRequest, on_output: Callable[[str], None] | None = None) -> int:
        command = self.build_command(request)
        with subprocess.Popen(
            command,
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
                    cleaned = line.rstrip()
                    if cleaned and on_output:
                        on_output(cleaned)
            return process.wait()
