from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Callable


class CleanupService:
    """Performs cleanup tasks and streams live progress messages."""

    def _remove_children(self, folder: Path, on_output: Callable[[str], None]) -> tuple[int, int]:
        removed = 0
        failed = 0

        if not str(folder) or not folder.exists():
            on_output(f"Skipping missing folder: {folder}")
            return removed, failed

        on_output(f"Scanning: {folder}")

        for item in folder.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink(missing_ok=True)
                removed += 1
                on_output(f"Removed: {item}")
            except Exception as exc:
                failed += 1
                on_output(f"Failed: {item} ({exc})")

        return removed, failed

    def _remove_pattern(self, folder: Path, pattern: str, on_output: Callable[[str], None]) -> tuple[int, int]:
        removed = 0
        failed = 0

        if not str(folder) or not folder.exists():
            on_output(f"Skipping missing folder: {folder}")
            return removed, failed

        on_output(f"Searching for {pattern} in {folder}")

        for item in folder.glob(pattern):
            try:
                item.unlink(missing_ok=True)
                removed += 1
                on_output(f"Removed: {item}")
            except Exception as exc:
                failed += 1
                on_output(f"Failed: {item} ({exc})")

        return removed, failed

    def quick_cleanup(self, on_output: Callable[[str], None]) -> dict:
        total_removed = 0
        total_failed = 0

        temp_dir = os.getenv("TEMP")
        if not temp_dir:
            raise RuntimeError("TEMP environment variable not found.")

        on_output("Starting quick cleanup...")
        removed, failed = self._remove_children(Path(temp_dir), on_output)
        total_removed += removed
        total_failed += failed

        on_output("Quick cleanup finished.")
        return {"removed": total_removed, "failed": total_failed}

    def deep_cleanup(self, on_output: Callable[[str], None]) -> dict:
        total_removed = 0
        total_failed = 0

        on_output("Starting deep cleanup...")

        folders = [
            Path(os.getenv("TEMP", "")),
            Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Temp",
            Path(os.getenv("APPDATA", "")) / "Microsoft" / "Windows" / "Recent",
        ]

        for folder in folders:
            removed, failed = self._remove_children(folder, on_output)
            total_removed += removed
            total_failed += failed

        temp_dir = Path(os.getenv("TEMP", ""))
        windows_temp = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Temp"
        for folder in [temp_dir, windows_temp]:
            for pattern in ("*.log", "*.tmp"):
                removed, failed = self._remove_pattern(folder, pattern, on_output)
                total_removed += removed
                total_failed += failed

        thumb_dir = Path(os.getenv("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Explorer"
        removed, failed = self._remove_pattern(thumb_dir, "thumbcache_*.db", on_output)
        total_removed += removed
        total_failed += failed

        on_output("Deep cleanup finished.")
        return {"removed": total_removed, "failed": total_failed}
