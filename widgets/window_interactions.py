from __future__ import annotations

import ctypes

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


def clamp_widget_size(window, width: int | float, height: int | float) -> tuple[int, int]:
    clamped_width = max(int(getattr(window, "MIN_WIDTH", 160)), min(int(width), int(getattr(window, "MAX_WIDTH", width))))
    clamped_height = max(int(getattr(window, "MIN_HEIGHT", 160)), min(int(height), int(getattr(window, "MAX_HEIGHT", height))))
    return clamped_width, clamped_height


def clamp_widget_position(window, x: int | float, y: int | float, width: int | float, height: int | float) -> tuple[int, int]:
    x = int(x)
    y = int(y)
    try:
        user32 = ctypes.windll.user32
        virtual_x = int(user32.GetSystemMetrics(76))
        virtual_y = int(user32.GetSystemMetrics(77))
        virtual_width = int(user32.GetSystemMetrics(78))
        virtual_height = int(user32.GetSystemMetrics(79))
        if virtual_width > 0 and virtual_height > 0:
            max_x = virtual_x + virtual_width - int(width)
            max_y = virtual_y + virtual_height - int(height)
            return max(virtual_x, min(x, max_x)), max(virtual_y, min(y, max_y))
    except Exception:
        pass
    return x, y


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
        return None

    try:
        target.bind("<Motion>", on_motion, add="+")
        target.bind("<Leave>", on_leave, add="+")
        target.bind("<ButtonPress-1>", on_press, add="+")
        target.bind("<B1-Motion>", on_drag, add="+")
        target.bind("<ButtonRelease-1>", on_release, add="+")
    except Exception:
        pass
