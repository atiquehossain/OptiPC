from __future__ import annotations

import psutil


class CpuUsageSampler:
    """Sample total CPU usage from CPU time deltas.

    psutil.cpu_percent(interval=None) uses process-global cached state. Widgets
    can update on different timers, so each CPU-facing widget keeps its own
    sampler to avoid stale or rounded-away readings.
    """

    def __init__(self) -> None:
        self._last_times = psutil.cpu_times()

    def sample(self) -> float:
        current_times = psutil.cpu_times()
        percent = cpu_percent_from_times(self._last_times, current_times)
        self._last_times = current_times
        return percent


def cpu_percent_from_times(previous, current) -> float:
    previous_values = list(previous)
    current_values = list(current)
    if not previous_values or len(previous_values) != len(current_values):
        return 0.0

    deltas = [max(float(current_value) - float(previous_value), 0.0) for previous_value, current_value in zip(previous_values, current_values)]
    total_delta = sum(deltas)
    idle_delta = 0.0
    fields = getattr(current, "_fields", ())
    for field_name in ("idle", "iowait"):
        if field_name in fields:
            idle_delta += deltas[fields.index(field_name)]

    if total_delta <= 0:
        return 0.0
    busy_delta = max(total_delta - idle_delta, 0.0)
    return max(0.0, min((busy_delta / total_delta) * 100.0, 100.0))


def format_cpu_percent(percent: float) -> str:
    value = max(0.0, min(float(percent), 100.0))
    if 0.0 < value < 9.95:
        return f"{value:.1f}%"
    return f"{value:.0f}%"
