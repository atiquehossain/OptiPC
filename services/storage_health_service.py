from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import subprocess


@dataclass
class StorageHealthItem:
    device_id: str
    friendly_name: str
    model: str
    serial_number: str
    bus_type: str
    media_type: str
    health_status: str
    operational_status: str
    firmware_version: str
    size_bytes: int
    temperature_c: int | None = None
    temperature_max_c: int | None = None
    wear_percent: int | None = None
    power_on_hours: int | None = None
    read_errors_total: int | None = None
    write_errors_total: int | None = None
    read_errors_uncorrected: int | None = None
    write_errors_uncorrected: int | None = None

    @property
    def size_label(self) -> str:
        return StorageHealthService.format_bytes(self.size_bytes)

    def to_multiline_text(self) -> str:
        return (
            f"Name: {self.friendly_name or 'N/A'}\n"
            f"Model: {self.model or 'N/A'}\n"
            f"Serial: {self.serial_number or 'N/A'}\n"
            f"Bus: {self.bus_type or 'N/A'}\n"
            f"Media: {self.media_type or 'N/A'}\n"
            f"Health: {self.health_status or 'N/A'}\n"
            f"Operational: {self.operational_status or 'N/A'}\n"
            f"Firmware: {self.firmware_version or 'N/A'}\n"
            f"Size: {self.size_label}\n"
            f"Temperature: {self.temperature_c if self.temperature_c is not None else 'N/A'}\n"
            f"Max Temperature: {self.temperature_max_c if self.temperature_max_c is not None else 'N/A'}\n"
            f"Wear: {self.wear_percent if self.wear_percent is not None else 'N/A'}\n"
            f"Power-On Hours: {self.power_on_hours if self.power_on_hours is not None else 'N/A'}\n"
            f"Read Errors Total: {self.read_errors_total if self.read_errors_total is not None else 'N/A'}\n"
            f"Write Errors Total: {self.write_errors_total if self.write_errors_total is not None else 'N/A'}\n"
            f"Read Errors Uncorrected: {self.read_errors_uncorrected if self.read_errors_uncorrected is not None else 'N/A'}\n"
            f"Write Errors Uncorrected: {self.write_errors_uncorrected if self.write_errors_uncorrected is not None else 'N/A'}"
        )


class StorageHealthService:
    @staticmethod
    def format_bytes(size: int) -> str:
        value = float(size)
        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if value < 1024 or unit == "PB":
                return f"{value:.1f} {unit}"
            value /= 1024
        return f"{value:.1f} PB"

    @staticmethod
    def _to_optional_int(value: Any) -> int | None:
        if value in (None, "", "null"):
            return None
        try:
            return int(value)
        except Exception:
            return None

    @staticmethod
    def _run_powershell_json(script: str) -> list[dict[str, Any]]:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
        )
        if result.returncode != 0 and not result.stdout.strip():
            raise RuntimeError(result.stderr.strip() or "PowerShell command failed.")
        raw = result.stdout.strip()
        if not raw:
            return []
        data = json.loads(raw)
        if isinstance(data, dict):
            return [data]
        return data if isinstance(data, list) else []

    def get_storage_health(self) -> list[StorageHealthItem]:
        script = r"""
$ErrorActionPreference = 'SilentlyContinue'
$physical = Get-PhysicalDisk | Select-Object \
    @{Name='DeviceId'; Expression={ "$($_.DeviceId)" }}, FriendlyName, SerialNumber, Model, \
    @{Name='BusType'; Expression={ "$($_.BusType)" }}, \
    @{Name='MediaType'; Expression={ "$($_.MediaType)" }}, \
    @{Name='HealthStatus'; Expression={ "$($_.HealthStatus)" }}, \
    @{Name='OperationalStatus'; Expression={ ($_.OperationalStatus -join ', ') }}, \
    FirmwareVersion, Size
$reliability = Get-PhysicalDisk | Get-StorageReliabilityCounter | Select-Object \
    @{Name='DeviceId'; Expression={ "$($_.DeviceId)" }}, Temperature, TemperatureMax, Wear, PowerOnHours, \
    ReadErrorsTotal, WriteErrorsTotal, ReadErrorsUncorrected, WriteErrorsUncorrected
$wmi = Get-CimInstance Win32_DiskDrive | Select-Object Model, SerialNumber, FirmwareRevision, InterfaceType, MediaType, Size
$relMap = @{}
foreach ($r in $reliability) { $relMap["$($r.DeviceId)"] = $r }
$out = @()
foreach ($d in $physical) {
    $r = $relMap["$($d.DeviceId)"]
    $w = $null
    if ($d.SerialNumber) {
        $w = $wmi | Where-Object { $_.SerialNumber -and $_.SerialNumber.Trim() -eq $d.SerialNumber.Trim() } | Select-Object -First 1
    }
    if (-not $w -and $d.Model) {
        $w = $wmi | Where-Object { $_.Model -and $_.Model.Trim() -eq $d.Model.Trim() } | Select-Object -First 1
    }
    $out += [PSCustomObject]@{
        DeviceId = "$($d.DeviceId)"
        FriendlyName = "$($d.FriendlyName)"
        Model = if ($d.Model) { "$($d.Model)" } elseif ($w) { "$($w.Model)" } else { "" }
        SerialNumber = if ($d.SerialNumber) { "$($d.SerialNumber)" } elseif ($w) { "$($w.SerialNumber)" } else { "" }
        BusType = "$($d.BusType)"
        MediaType = "$($d.MediaType)"
        HealthStatus = "$($d.HealthStatus)"
        OperationalStatus = "$($d.OperationalStatus)"
        FirmwareVersion = if ($d.FirmwareVersion) { "$($d.FirmwareVersion)" } elseif ($w) { "$($w.FirmwareRevision)" } else { "" }
        Size = [Int64]($d.Size)
        Temperature = if ($r) { $r.Temperature } else { $null }
        TemperatureMax = if ($r) { $r.TemperatureMax } else { $null }
        Wear = if ($r) { $r.Wear } else { $null }
        PowerOnHours = if ($r) { $r.PowerOnHours } else { $null }
        ReadErrorsTotal = if ($r) { $r.ReadErrorsTotal } else { $null }
        WriteErrorsTotal = if ($r) { $r.WriteErrorsTotal } else { $null }
        ReadErrorsUncorrected = if ($r) { $r.ReadErrorsUncorrected } else { $null }
        WriteErrorsUncorrected = if ($r) { $r.WriteErrorsUncorrected } else { $null }
    }
}
$out | ConvertTo-Json -Depth 5 -Compress
"""
        rows = self._run_powershell_json(script)
        items: list[StorageHealthItem] = []
        for row in rows:
            items.append(StorageHealthItem(
                device_id=str(row.get("DeviceId") or ""),
                friendly_name=str(row.get("FriendlyName") or ""),
                model=str(row.get("Model") or ""),
                serial_number=str(row.get("SerialNumber") or ""),
                bus_type=str(row.get("BusType") or ""),
                media_type=str(row.get("MediaType") or ""),
                health_status=str(row.get("HealthStatus") or ""),
                operational_status=str(row.get("OperationalStatus") or ""),
                firmware_version=str(row.get("FirmwareVersion") or ""),
                size_bytes=int(row.get("Size") or 0),
                temperature_c=self._to_optional_int(row.get("Temperature")),
                temperature_max_c=self._to_optional_int(row.get("TemperatureMax")),
                wear_percent=self._to_optional_int(row.get("Wear")),
                power_on_hours=self._to_optional_int(row.get("PowerOnHours")),
                read_errors_total=self._to_optional_int(row.get("ReadErrorsTotal")),
                write_errors_total=self._to_optional_int(row.get("WriteErrorsTotal")),
                read_errors_uncorrected=self._to_optional_int(row.get("ReadErrorsUncorrected")),
                write_errors_uncorrected=self._to_optional_int(row.get("WriteErrorsUncorrected")),
            ))
        return items
