from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable


OutputCallback = Callable[[str], None]


@dataclass(frozen=True)
class CleanupCategory:
    key: str
    title: str
    description: str
    safety: str
    default_selected: bool
    roots: tuple[Path, ...]


@dataclass
class CleanupItem:
    path: Path
    size: int
    is_dir: bool


@dataclass
class CleanupCategoryScan:
    category: CleanupCategory
    items: list[CleanupItem] = field(default_factory=list)
    skipped: int = 0
    missing: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def size(self) -> int:
        return sum(item.size for item in self.items)


@dataclass
class CleanupScanResult:
    categories: dict[str, CleanupCategoryScan]

    @property
    def total_count(self) -> int:
        return sum(category.count for category in self.categories.values())

    @property
    def total_size(self) -> int:
        return sum(category.size for category in self.categories.values())

    def selected_total_size(self, keys: Iterable[str]) -> int:
        return sum(self.categories[key].size for key in keys if key in self.categories)

    def selected_total_count(self, keys: Iterable[str]) -> int:
        return sum(self.categories[key].count for key in keys if key in self.categories)


@dataclass
class CleanupDeleteResult:
    scanned: CleanupScanResult
    removed: int = 0
    failed: int = 0
    skipped: int = 0
    bytes_freed: int = 0


class CleanupService:
    """Scan and remove known safe junk data with size estimates."""

    SKIP_NAMES = {"diagnostics", "microsoft", "windows"}

    @staticmethod
    def format_bytes(size: int | float) -> str:
        value = float(size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if value < 1024 or unit == "TB":
                return f"{value:.1f} {unit}"
            value /= 1024
        return f"{value:.1f} TB"

    @staticmethod
    def _env_path(name: str, *parts: str) -> Path | None:
        value = os.getenv(name)
        if not value:
            return None
        return Path(value).joinpath(*parts)

    @staticmethod
    def _existing(paths: Iterable[Path | None]) -> tuple[Path, ...]:
        return tuple(path for path in paths if path is not None)

    @staticmethod
    def _glob_existing(base: Path | None, pattern: str) -> list[Path]:
        if base is None or not base.exists():
            return []
        try:
            return list(base.glob(pattern))
        except (PermissionError, OSError):
            return []

    def get_categories(self) -> list[CleanupCategory]:
        local = self._env_path("LOCALAPPDATA")
        roaming = self._env_path("APPDATA")
        user_profile = self._env_path("USERPROFILE")
        system_root = self._env_path("SystemRoot") or Path(r"C:\Windows")
        program_data = self._env_path("ProgramData") or Path(r"C:\ProgramData")

        chrome_roots = self._browser_cache_roots(local, "Google", "Chrome")
        edge_roots = self._browser_cache_roots(local, "Microsoft", "Edge")
        firefox_roots = self._firefox_cache_roots(roaming)

        return [
            CleanupCategory(
                key="user_temp",
                title="User Temp Files",
                description="Temporary files created by apps in your profile.",
                safety="Safe",
                default_selected=True,
                roots=self._existing([self._env_path("TEMP")]),
            ),
            CleanupCategory(
                key="browser_caches",
                title="Browser Caches",
                description="Chrome, Edge, and Firefox cache files that browsers can rebuild.",
                safety="Safe",
                default_selected=True,
                roots=tuple(chrome_roots + edge_roots + firefox_roots),
            ),
            CleanupCategory(
                key="thumbnail_shader_caches",
                title="Thumbnail and Shader Caches",
                description="Explorer thumbnails and graphics shader caches.",
                safety="Safe",
                default_selected=True,
                roots=self._existing([
                    self._env_path("LOCALAPPDATA", "Microsoft", "Windows", "Explorer"),
                    self._env_path("LOCALAPPDATA", "D3DSCache"),
                    self._env_path("LOCALAPPDATA", "NVIDIA", "DXCache"),
                    self._env_path("LOCALAPPDATA", "NVIDIA", "GLCache"),
                    self._env_path("LOCALAPPDATA", "AMD", "DxCache"),
                    self._env_path("LOCALAPPDATA", "Intel", "ShaderCache"),
                ]),
            ),
            CleanupCategory(
                key="package_caches",
                title="Package Manager Caches",
                description="Pip, npm, Yarn, pnpm, and NuGet download caches.",
                safety="Safe",
                default_selected=True,
                roots=self._existing([
                    self._env_path("LOCALAPPDATA", "pip", "Cache"),
                    self._env_path("APPDATA", "npm-cache"),
                    self._env_path("LOCALAPPDATA", "npm-cache"),
                    self._env_path("LOCALAPPDATA", "Yarn", "Cache"),
                    self._env_path("LOCALAPPDATA", "pnpm-store"),
                    self._env_path("LOCALAPPDATA", "NuGet", "v3-cache"),
                    self._env_path("LOCALAPPDATA", "NuGet", "http-cache"),
                ]),
            ),
            CleanupCategory(
                key="windows_temp",
                title="Windows Temp Files",
                description="System temporary files. Some locked/admin files may be skipped.",
                safety="Advanced",
                default_selected=False,
                roots=self._existing([system_root / "Temp"]),
            ),
            CleanupCategory(
                key="windows_update_cache",
                title="Windows Update Cache",
                description="Downloaded Windows Update files that Windows can fetch again.",
                safety="Advanced",
                default_selected=False,
                roots=self._existing([
                    system_root / "SoftwareDistribution" / "Download",
                    program_data / "Microsoft" / "Windows" / "DeliveryOptimization" / "Cache",
                ]),
            ),
            CleanupCategory(
                key="crash_reports",
                title="Crash Reports and Dumps",
                description="Crash dumps and Windows Error Reporting data. Useful only for debugging.",
                safety="Review",
                default_selected=False,
                roots=self._existing([
                    self._env_path("LOCALAPPDATA", "CrashDumps"),
                    self._env_path("LOCALAPPDATA", "Microsoft", "Windows", "WER", "ReportArchive"),
                    self._env_path("LOCALAPPDATA", "Microsoft", "Windows", "WER", "ReportQueue"),
                    program_data / "Microsoft" / "Windows" / "WER" / "ReportArchive",
                    program_data / "Microsoft" / "Windows" / "WER" / "ReportQueue",
                    system_root / "Minidump",
                ]),
            ),
            CleanupCategory(
                key="recent_items",
                title="Recent Items Shortcuts",
                description="Recent file shortcuts. Small size, mostly privacy cleanup.",
                safety="Review",
                default_selected=False,
                roots=self._existing([
                    self._env_path("APPDATA", "Microsoft", "Windows", "Recent"),
                    self._env_path("APPDATA", "Microsoft", "Windows", "Recent", "AutomaticDestinations"),
                    self._env_path("APPDATA", "Microsoft", "Windows", "Recent", "CustomDestinations"),
                ]),
            ),
            CleanupCategory(
                key="installer_leftovers",
                title="Installer Leftovers",
                description="Common setup leftovers in temp folders. Does not touch Windows Installer or ProgramData package caches.",
                safety="Review",
                default_selected=False,
                roots=self._installer_leftover_roots(user_profile),
            ),
        ]

    def _browser_cache_roots(self, local: Path | None, vendor: str, browser: str) -> list[Path]:
        base = None if local is None else local / vendor / browser / "User Data"
        roots: list[Path] = []
        for profile in self._glob_existing(base, "*"):
            roots.extend([
                profile / "Cache",
                profile / "Cache" / "Cache_Data",
                profile / "Code Cache",
                profile / "GPUCache",
                profile / "GrShaderCache",
                profile / "ShaderCache",
                profile / "Service Worker" / "CacheStorage",
            ])
        return roots

    def _firefox_cache_roots(self, roaming: Path | None) -> list[Path]:
        base = None if roaming is None else roaming / "Mozilla" / "Firefox" / "Profiles"
        return [profile / "cache2" for profile in self._glob_existing(base, "*")]

    def _installer_leftover_roots(self, user_profile: Path | None) -> tuple[Path, ...]:
        temp_dir = self._env_path("TEMP")
        candidates = [
            temp_dir / "is-*" if temp_dir else None,
            temp_dir / "Install*" if temp_dir else None,
            temp_dir / "Setup*" if temp_dir else None,
            user_profile / "AppData" / "Local" / "Downloaded Installations" if user_profile else None,
        ]
        roots: list[Path] = []
        for candidate in candidates:
            if candidate is None:
                continue
            if any(char in str(candidate) for char in "*?[]"):
                roots.extend(self._glob_existing(candidate.parent, candidate.name))
            else:
                roots.append(candidate)
        return tuple(roots)

    def get_default_category_keys(self) -> list[str]:
        return [category.key for category in self.get_categories() if category.default_selected]

    def scan_cleanup(
        self,
        on_output: OutputCallback | None = None,
        keys: Iterable[str] | None = None,
    ) -> CleanupScanResult:
        selected = set(keys) if keys is not None else None
        categories = {}
        for category in self.get_categories():
            if selected is not None and category.key not in selected:
                continue
            if on_output:
                on_output(f"Scanning {category.title}...")
            categories[category.key] = self._scan_category(category)
        return CleanupScanResult(categories)

    def clean_categories(self, keys: Iterable[str], on_output: OutputCallback | None = None) -> CleanupDeleteResult:
        selected = set(keys)
        all_scan = self.scan_cleanup(on_output, selected)
        result = CleanupDeleteResult(scanned=all_scan)

        for key in selected:
            scan = all_scan.categories.get(key)
            if scan is None:
                continue
            if on_output:
                on_output(
                    f"Cleaning {scan.category.title}: "
                    f"{scan.count} item(s), {self.format_bytes(scan.size)}"
                )
            for item in scan.items:
                freed = self._delete_item(item, on_output)
                if freed is None:
                    result.failed += 1
                else:
                    result.removed += 1
                    result.bytes_freed += freed
            result.skipped += scan.skipped

        return result

    def quick_cleanup(self, on_output: OutputCallback) -> dict:
        result = self.clean_categories(["user_temp"], on_output)
        return {
            "removed": result.removed,
            "failed": result.failed,
            "skipped": result.skipped,
            "bytes_freed": result.bytes_freed,
        }

    def deep_cleanup(self, on_output: OutputCallback) -> dict:
        result = self.clean_categories(self.get_default_category_keys(), on_output)
        return {
            "removed": result.removed,
            "failed": result.failed,
            "skipped": result.skipped,
            "bytes_freed": result.bytes_freed,
        }

    def _scan_category(self, category: CleanupCategory) -> CleanupCategoryScan:
        scan = CleanupCategoryScan(category=category)
        seen: set[Path] = set()

        for root in self._dedupe_nested_roots(category.roots):
            try:
                resolved_root = root.expanduser()
                if not resolved_root.exists():
                    scan.missing += 1
                    continue
                if resolved_root.is_file() or resolved_root.is_symlink():
                    self._add_scan_item(resolved_root, scan, seen)
                    continue
                for child in resolved_root.iterdir():
                    if self._should_skip_child(child):
                        scan.skipped += 1
                        continue
                    self._add_scan_item(child, scan, seen)
            except (PermissionError, OSError) as exc:
                scan.skipped += 1
                scan.errors.append(f"{root}: {exc}")

        return scan

    def _dedupe_nested_roots(self, roots: Iterable[Path]) -> list[Path]:
        existing: list[tuple[Path, Path]] = []
        missing: list[Path] = []

        for root in roots:
            expanded = root.expanduser()
            if not expanded.exists():
                missing.append(expanded)
                continue
            try:
                resolved = expanded.resolve(strict=False)
            except (PermissionError, OSError):
                resolved = expanded.absolute()
            existing.append((expanded, resolved))

        existing.sort(key=lambda pair: len(pair[1].parts))
        kept: list[tuple[Path, Path]] = []
        for expanded, resolved in existing:
            if any(self._is_same_or_child(resolved, kept_resolved) for _, kept_resolved in kept):
                continue
            kept.append((expanded, resolved))

        return [expanded for expanded, _ in kept] + missing

    @staticmethod
    def _is_same_or_child(path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def _add_scan_item(self, path: Path, scan: CleanupCategoryScan, seen: set[Path]) -> None:
        try:
            resolved = path.resolve(strict=False)
            if resolved in seen:
                return
            seen.add(resolved)
            size, skipped = self._measure_path(path)
            scan.skipped += skipped
            scan.items.append(CleanupItem(path=path, size=size, is_dir=path.is_dir() and not path.is_symlink()))
        except (PermissionError, OSError) as exc:
            scan.skipped += 1
            scan.errors.append(f"{path}: {exc}")

    def _should_skip_child(self, path: Path) -> bool:
        return path.name.lower() in self.SKIP_NAMES

    def _measure_path(self, path: Path) -> tuple[int, int]:
        try:
            if path.is_symlink() or path.is_file():
                return path.stat().st_size, 0
            if not path.is_dir():
                return 0, 0
        except (PermissionError, OSError):
            return 0, 1

        total = 0
        skipped = 0
        stack = [path]

        while stack:
            current = stack.pop()
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        try:
                            if entry.is_symlink():
                                total += entry.stat(follow_symlinks=False).st_size
                            elif entry.is_dir(follow_symlinks=False):
                                stack.append(Path(entry.path))
                            elif entry.is_file(follow_symlinks=False):
                                total += entry.stat(follow_symlinks=False).st_size
                        except (PermissionError, OSError):
                            skipped += 1
            except (PermissionError, OSError):
                skipped += 1

        return total, skipped

    def _delete_item(self, item: CleanupItem, on_output: OutputCallback | None = None) -> int | None:
        try:
            size = item.size
            if item.path.is_dir() and not item.path.is_symlink():
                shutil.rmtree(item.path, ignore_errors=False)
            else:
                item.path.unlink(missing_ok=True)
            if on_output:
                on_output(f"Removed: {item.path.name} ({self.format_bytes(size)})")
            return size
        except (PermissionError, OSError) as exc:
            if on_output:
                on_output(f"Skipped locked or protected item: {item.path.name} ({exc})")
            return None
        except Exception as exc:
            if on_output:
                on_output(f"Failed: {item.path.name} ({exc})")
            return None
