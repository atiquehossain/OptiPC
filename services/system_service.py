from __future__ import annotations

import os
import platform
import shutil
import socket
from pathlib import Path

import psutil


class SystemService:
    """Read system info and do safe non-admin cleanup tasks."""

    @staticmethod
    def get_hostname() -> str:
        return socket.gethostname()

    @staticmethod
    def get_os_label() -> str:
        return f"{platform.system()} {platform.release()}"

    @staticmethod
    def get_cpu_usage() -> str:
        return f"{psutil.cpu_percent(interval=0.2)}%"

    @staticmethod
    def format_bytes(size: float) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024 or unit == "TB":
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def get_memory_total() -> str:
        return SystemService.format_bytes(psutil.virtual_memory().total)

    @staticmethod
    def get_memory_used() -> str:
        return SystemService.format_bytes(psutil.virtual_memory().used)

    @staticmethod
    def get_disk_free(drive: str = "C:\\") -> str:
        return SystemService.format_bytes(psutil.disk_usage(drive).free)

    @staticmethod
    def get_disk_total(drive: str = "C:\\") -> str:
        return SystemService.format_bytes(psutil.disk_usage(drive).total)

    @staticmethod
    def get_system_summary() -> str:
        return (
            f"OS: {SystemService.get_os_label()}\n"
            f"PC: {SystemService.get_hostname()}\n"
            f"CPU Usage: {SystemService.get_cpu_usage()}\n"
            f"RAM Used: {SystemService.get_memory_used()} / {SystemService.get_memory_total()}\n"
            f"Disk Free: {SystemService.get_disk_free()} / {SystemService.get_disk_total()}"
        )

    @staticmethod
    def quick_cleanup_temp() -> tuple[int, int]:
        """Clean temporary files safely, skipping locked files and system folders"""
        temp_path = os.getenv("TEMP")
        if not temp_path:
            return 0, 1

        removed = 0
        failed = 0
        skipped_system = 0
        
        try:
            for item in Path(temp_path).glob("*"):
                # Skip system and critical folders
                if item.name.lower() in ['diagnostics', 'microsoft', 'windows']:
                    skipped_system += 1
                    continue
                    
                # Skip files that might be in use by other processes
                try:
                    if item.is_dir():
                        # Try to remove directory, but skip if it contains locked files
                        shutil.rmtree(item, ignore_errors=False)
                    else:
                        # Try to remove file, but skip if in use
                        item.unlink(missing_ok=True)
                    removed += 1
                    
                except (PermissionError, OSError) as e:
                    # File is in use by another process - this is normal
                    failed += 1
                    continue
                except Exception:
                    # Other errors
                    failed += 1
                    continue
                    
        except (PermissionError, OSError) as e:
            # Can't access temp folder itself
            return 0, 1
            
        return removed, failed
