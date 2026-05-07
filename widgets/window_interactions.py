from __future__ import annotations

import ctypes
import re

from config.constants import WIDGET_SIZE_LIMITS


CONTROL_CLASS_NAMES = {
    "CTkButton",
    "CTkCheckBox",
    "CTkComboBox",
    "CTkEntry",
    "CTkOptionMenu",
    "CTkSlider",
    "CTkSwitch",
    "CTkTextbox",
}

GEOMETRY_PATTERN = re.compile(r"(\d+)x(\d+)([+-]\d+)([+-]\d+)")

CURSOR_MAP = {
    None: "arrow",
    "n": "sb_v_double_arrow",
    "s": "sb_v_double_arrow",
    "e": "sb_h_double_arrow",
    "w": "sb_h_double_arrow",
    "ne": "size_ne_sw",
    "sw": "size_ne_sw",
    "nw": "size_nw_se",
    "se": "size_nw_se",
    "move": "fleur",
}


def is_control_widget(widget) -> bool:
    current = widget
    for _ in range(8):
        if current is None:
            return False
        if current.__class__.__name__ in CONTROL_CLASS_NAMES:
            return True
        current = getattr(current, "master", None)
    return False


def cursor_for_direction(direction: str | None) -> str:
    return CURSOR_MAP.get(direction, "arrow")


def set_widget_cursor(widget, cursor: str, *, recursive: bool = False) -> None:
    stack = [widget]
    seen: set[int] = set()
    while stack:
        current = stack.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        try:
            current.configure(cursor=cursor)
        except Exception:
            pass
        if recursive:
            try:
                stack.extend(current.winfo_children())
            except Exception:
                pass


def apply_cursor(window, target, direction: str | None) -> None:
    cursor = cursor_for_direction(direction)
    try:
        window.configure(cursor=cursor)
    except Exception:
        pass
    set_widget_cursor(target, cursor)


def widget_point(window, event) -> tuple[int, int]:
    return event.x_root - window.winfo_rootx(), event.y_root - window.winfo_rooty()


def control_widget_at_event(window, event):
    try:
        hit_widget = window.winfo_containing(event.x_root, event.y_root)
        if is_control_widget(hit_widget):
            return hit_widget
    except Exception:
        pass
    if is_control_widget(event.widget):
        return event.widget
    return None


def start_resize(window, event, direction: str) -> str:
    window._is_resizing = True
    window._resize_dir = direction
    window._resize_start_x = event.x_root
    window._resize_start_y = event.y_root
    window._resize_start_w = window.winfo_width()
    window._resize_start_h = window.winfo_height()
    window._resize_start_win_x = window.winfo_x()
    window._resize_start_win_y = window.winfo_y()
    return "break"


def configure_size_limits(window, size_category: str, default_width: int, default_height: int) -> None:
    limits = WIDGET_SIZE_LIMITS.get(size_category, WIDGET_SIZE_LIMITS["default"])
    min_width = max(int(getattr(window, "MIN_WIDTH", 0) or 0), int(limits["min_width"]))
    min_height = max(int(getattr(window, "MIN_HEIGHT", 0) or 0), int(limits["min_height"]))

    requested_max_width = getattr(window, "MAX_WIDTH", None)
    requested_max_height = getattr(window, "MAX_HEIGHT", None)
    max_width = int(requested_max_width) if requested_max_width is not None else int(limits["max_width"])
    max_height = int(requested_max_height) if requested_max_height is not None else int(limits["max_height"])

    window._default_width = int(default_width)
    window._default_height = int(default_height)
    window.MIN_WIDTH = min_width
    window.MIN_HEIGHT = min_height
    window.MAX_WIDTH = max(min_width, max_width)
    window.MAX_HEIGHT = max(min_height, max_height)


def current_widget_geometry(window) -> tuple[int, int, int, int]:
    try:
        match = GEOMETRY_PATTERN.match(str(window.geometry()))
        if match:
            return (
                int(match.group(3)),
                int(match.group(4)),
                max(1, int(match.group(1))),
                max(1, int(match.group(2))),
            )
    except Exception:
        pass
    return (
        int(window.winfo_x()),
        int(window.winfo_y()),
        max(1, int(window.winfo_width())),
        max(1, int(window.winfo_height())),
    )


def _window_scaling(window=None) -> float:
    if window is None:
        return 1.0
    try:
        scaling = float(window._get_window_scaling())
        if scaling > 0:
            return scaling
    except Exception:
        pass
    return 1.0


def effective_window_size(window, width: int | float, height: int | float) -> tuple[int, int]:
    scale = _window_scaling(window)
    return max(1, int(round(float(width) * scale))), max(1, int(round(float(height) * scale)))


def get_virtual_screen_bounds(window=None) -> tuple[int, int, int, int] | None:
    try:
        user32 = ctypes.windll.user32
        virtual_x = int(user32.GetSystemMetrics(76))
        virtual_y = int(user32.GetSystemMetrics(77))
        virtual_width = int(user32.GetSystemMetrics(78))
        virtual_height = int(user32.GetSystemMetrics(79))
        if virtual_width > 0 and virtual_height > 0:
            scale = _window_scaling(window)
            return (
                int(round(virtual_x / scale)),
                int(round(virtual_y / scale)),
                int(round(virtual_width / scale)),
                int(round(virtual_height / scale)),
            )
    except Exception:
        pass
    if window is not None:
        try:
            return 0, 0, int(window.winfo_screenwidth()), int(window.winfo_screenheight())
        except Exception:
            pass
    return None


def clamp_widget_size(window, width: int | float, height: int | float) -> tuple[int, int]:
    clamped_width = max(int(getattr(window, "MIN_WIDTH", 160)), min(int(width), int(getattr(window, "MAX_WIDTH", width))))
    clamped_height = max(int(getattr(window, "MIN_HEIGHT", 160)), min(int(height), int(getattr(window, "MAX_HEIGHT", height))))
    return clamped_width, clamped_height


def clamp_widget_position(window, x: int | float, y: int | float, width: int | float, height: int | float) -> tuple[int, int]:
    x = int(x)
    y = int(y)
    bounds = get_virtual_screen_bounds(window)
    if bounds is not None:
        virtual_x, virtual_y, virtual_width, virtual_height = bounds
        effective_width, effective_height = effective_window_size(window, width, height)
        max_x = virtual_x + virtual_width - effective_width
        max_y = virtual_y + virtual_height - effective_height
        return max(virtual_x, min(x, max_x)), max(virtual_y, min(y, max_y))
    return x, y


def rectangles_overlap(
    first: tuple[int, int, int, int],
    second: tuple[int, int, int, int],
    *,
    gap: int = 0,
) -> bool:
    first_x, first_y, first_w, first_h = first
    second_x, second_y, second_w, second_h = second
    return not (
        first_x + first_w + gap <= second_x
        or second_x + second_w + gap <= first_x
        or first_y + first_h + gap <= second_y
        or second_y + second_h + gap <= first_y
    )


def find_non_overlapping_position(
    x: int | float,
    y: int | float,
    width: int | float,
    height: int | float,
    obstacles: list[tuple[int, int, int, int]],
    *,
    gap: int = 16,
    margin: int = 12,
    screen_bounds: tuple[int, int, int, int] | None = None,
) -> tuple[int, int]:
    width = int(width)
    height = int(height)
    x = int(x)
    y = int(y)

    bounds = screen_bounds if screen_bounds is not None else get_virtual_screen_bounds()
    if bounds is None:
        return x, y
    screen_x, screen_y, screen_w, screen_h = bounds
    min_x = screen_x + margin
    min_y = screen_y + margin
    max_x = max(min_x, screen_x + screen_w - width - margin)
    max_y = max(min_y, screen_y + screen_h - height - margin)

    def clamp_position(candidate_x: int, candidate_y: int) -> tuple[int, int]:
        return max(min_x, min(candidate_x, max_x)), max(min_y, min(candidate_y, max_y))

    def clear(candidate_x: int, candidate_y: int) -> bool:
        candidate = (candidate_x, candidate_y, width, height)
        return all(not rectangles_overlap(candidate, obstacle, gap=gap) for obstacle in obstacles)

    proposed_x, proposed_y = clamp_position(x, y)
    if clear(proposed_x, proposed_y):
        return proposed_x, proposed_y

    candidates: set[tuple[int, int]] = {(proposed_x, proposed_y)}
    for obs_x, obs_y, obs_w, obs_h in obstacles:
        candidates.update(
            {
                clamp_position(obs_x + obs_w + gap, obs_y),
                clamp_position(obs_x - width - gap, obs_y),
                clamp_position(obs_x, obs_y + obs_h + gap),
                clamp_position(obs_x, obs_y - height - gap),
                clamp_position(obs_x + obs_w + gap, obs_y + obs_h + gap),
                clamp_position(obs_x - width - gap, obs_y + obs_h + gap),
            }
        )

    step_x = max(32, min(width + gap, 360))
    step_y = max(32, min(height + gap, 300))
    current_y = min_y
    while current_y <= max_y:
        current_x = min_x
        while current_x <= max_x:
            candidates.add((current_x, current_y))
            current_x += step_x
        current_y += step_y

    ordered_candidates = sorted(
        candidates,
        key=lambda point: (abs(point[0] - proposed_x) + abs(point[1] - proposed_y), point[1], point[0]),
    )
    for candidate_x, candidate_y in ordered_candidates:
        if clear(candidate_x, candidate_y):
            return candidate_x, candidate_y
    return proposed_x, proposed_y


def clamp_resize_geometry(window, direction: str, x: int | float, y: int | float, width: int | float, height: int | float) -> tuple[int, int, int, int]:
    right = int(x) + int(width)
    bottom = int(y) + int(height)
    clamped_width, clamped_height = clamp_widget_size(window, width, height)
    clamped_x = right - clamped_width if "w" in direction else int(x)
    clamped_y = bottom - clamped_height if "n" in direction else int(y)
    return int(clamped_x), int(clamped_y), int(clamped_width), int(clamped_height)


def bind_drag_target(window, target) -> None:
    def on_motion(event):
        if getattr(window, "_is_resizing", False):
            return None
        try:
            control_widget = control_widget_at_event(window, event)
            if control_widget is not None:
                apply_cursor(window, control_widget, None)
                return None
            x, y = widget_point(window, event)
            apply_cursor(window, event.widget, window.get_resize_direction(x, y) or "move")
        except Exception:
            pass
        return None

    def on_leave(event):
        if not getattr(window, "_is_resizing", False):
            apply_cursor(window, event.widget, None)
        return None

    def on_press(event):
        if control_widget_at_event(window, event) is not None:
            return None
        x, y = widget_point(window, event)
        direction = window.get_resize_direction(x, y)
        if direction:
            return start_resize(window, event, direction)
        window.start_drag(event)
        return None

    def on_drag(event):
        if control_widget_at_event(window, event) is not None:
            return None
        if getattr(window, "_is_resizing", False):
            return window.on_mouse_drag(event)
        window.do_drag(event)
        return None

    def on_release(event):
        if getattr(window, "_is_resizing", False):
            return window.on_mouse_up(event)
        try:
            window._settle_widget_position()
        except Exception:
            pass
        return None

    try:
        target.bind("<Motion>", on_motion, add="+")
        target.bind("<Leave>", on_leave, add="+")
        target.bind("<ButtonPress-1>", on_press, add="+")
        target.bind("<B1-Motion>", on_drag, add="+")
        target.bind("<ButtonRelease-1>", on_release, add="+")
    except Exception:
        pass
