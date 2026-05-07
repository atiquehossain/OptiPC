from __future__ import annotations


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


def is_control_widget(widget) -> bool:
    return widget.__class__.__name__ in CONTROL_CLASS_NAMES


def widget_point(window, event) -> tuple[int, int]:
    return event.x_root - window.winfo_rootx(), event.y_root - window.winfo_rooty()


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


def bind_drag_target(window, target) -> None:
    def on_motion(event):
        if is_control_widget(event.widget) or getattr(window, "_is_resizing", False):
            return None
        x, y = widget_point(window, event)
        try:
            window.apply_cursor(window.get_resize_direction(x, y))
        except Exception:
            pass
        return None

    def on_press(event):
        if is_control_widget(event.widget):
            return None
        x, y = widget_point(window, event)
        direction = window.get_resize_direction(x, y)
        if direction:
            return start_resize(window, event, direction)
        window.start_drag(event)
        return None

    def on_drag(event):
        if is_control_widget(event.widget):
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
        target.bind("<ButtonPress-1>", on_press, add="+")
        target.bind("<B1-Motion>", on_drag, add="+")
        target.bind("<ButtonRelease-1>", on_release, add="+")
    except Exception:
        pass
