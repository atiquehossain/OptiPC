from __future__ import annotations

import calendar
import tkinter as tk
from datetime import date, timedelta
from typing import Any

import customtkinter as ctk

from config.constants import WIDGET_CONTENT_MARGIN
from widgets.window_interactions import apply_cursor, current_widget_geometry, start_resize, widget_point

CALENDAR_WEEKDAY_LABELS = ("M", "T", "W", "T", "F", "S", "S")
CALENDAR_SURFACE = "#2c2828"
CALENDAR_BORDER = "#474141"
CALENDAR_TEXT = "#ebe7e4"
CALENDAR_WEEKDAY_TEXT = "#a7a0a0"
CALENDAR_MUTED_TEXT = "#706b6b"
CALENDAR_TODAY_COLOR = "#ff453a"
CALENDAR_TODAY_HOVER = "#ff6961"


def widget_logical_size(widget) -> tuple[int, int]:
    try:
        _x, _y, width, height = current_widget_geometry(widget)
        return max(1, int(width)), max(1, int(height))
    except Exception:
        pass
    try:
        width = int(widget.winfo_width())
        height = int(widget.winfo_height())
    except Exception:
        width = height = 0
    if width <= 1:
        width = int(getattr(widget, "_default_width", 170) or 170)
    if height <= 1:
        height = int(getattr(widget, "_default_height", 170) or 170)
    return max(1, width), max(1, height)


def calendar_size_class(widget) -> str:
    width, height = widget_logical_size(widget)
    if height <= 220:
        return "small" if width <= 240 else "medium"
    if width >= 620 and height >= 320:
        return "extra_large"
    return "large"


def calendar_uses_month_grid(widget) -> bool:
    return True


def widget_content_margin(widget) -> int:
    size_class = calendar_size_class(widget)
    if size_class == "small":
        return 10
    if size_class == "medium":
        return 12
    return WIDGET_CONTENT_MARGIN


def install_calendar_grid(frame) -> None:
    for column in range(7):
        frame.grid_columnconfigure(column, weight=1, uniform="calendar_day")
    for row in range(7):
        frame.grid_rowconfigure(row, weight=1, uniform="calendar_week")
    try:
        frame.grid_propagate(False)
    except Exception:
        pass


def _frame_size(widget, frame) -> tuple[int, int]:
    widget_width, widget_height = widget_logical_size(widget)
    try:
        width = int(frame.winfo_width())
        height = int(frame.winfo_height())
    except Exception:
        width = height = 0
    if width <= 20:
        width = max(124, widget_width - 18)
    elif width > widget_width * 1.25:
        width = max(124, widget_width - 18)
    if height <= 20:
        height = max(124, widget_height - 18)
    elif height > widget_height * 1.25:
        height = max(124, widget_height - 18)
    return width, height


def calendar_cell_metrics(widget, frame) -> tuple[int, int, int]:
    width, height = _frame_size(widget, frame)
    cell_width = max(14, min(48, int((width - 4) / 7)))
    cell_height = max(14, min(32, int((height - 4) / 7)))
    font_size = 11 if cell_height <= 15 else 12 if cell_height <= 18 else 13 if cell_height <= 22 else 15
    return cell_width, cell_height, font_size


def apply_calendar_grid_layout(widget, frame, day_labels, day_buttons) -> None:
    if not frame or not day_labels or not day_buttons:
        return
    install_calendar_grid(frame)
    cell_width, cell_height, font_size = calendar_cell_metrics(widget, frame)
    header_font = ctk.CTkFont(size=max(9, font_size), weight="bold")
    day_font = ctk.CTkFont(size=font_size, weight="bold")
    radius = max(6, min(20, min(cell_width, cell_height) // 2))

    for column, label in enumerate(day_labels):
        try:
            label.configure(width=cell_width, height=cell_height, font=header_font)
            label.grid_configure(row=0, column=column, padx=0, pady=0, sticky="nsew")
        except Exception:
            pass

    for week, row in enumerate(day_buttons):
        for day, button in enumerate(row):
            try:
                button.configure(width=cell_width, height=cell_height, corner_radius=radius, font=day_font)
                button.grid_configure(row=week + 1, column=day, padx=0, pady=0, sticky="nsew")
            except Exception:
                pass


def apply_calendar_footer_visibility(widget, label, *, pady: tuple[int, int] = (4, 0)) -> None:
    if label is None:
        return
    try:
        if int(widget.winfo_height()) < 300:
            label.pack_forget()
        elif not label.winfo_manager():
            label.pack(pady=pady)
    except Exception:
        pass


def calendar_day_font(widget, frame, *, bold: bool = True) -> ctk.CTkFont:
    _cell_width, cell_height, font_size = calendar_cell_metrics(widget, frame)
    if not bold and cell_height <= 16:
        font_size = max(8, font_size - 1)
    return ctk.CTkFont(size=font_size, weight="bold" if bold else "normal")


def calendar_month_dates(year: int, month: int) -> list[list[date]]:
    weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(year, month)
    while len(weeks) < 6:
        start = weeks[-1][-1] + timedelta(days=1)
        weeks.append([start + timedelta(days=offset) for offset in range(7)])
    return weeks[:6]


def _calendar_canvas_current_day(widget) -> date:
    current_day = getattr(widget, "current_date", date.today())
    if hasattr(current_day, "date"):
        current_day = current_day.date()
    return current_day


def _calendar_canvas_metrics(canvas: Any, widget) -> dict[str, float]:
    try:
        width = int(canvas.winfo_width())
        height = int(canvas.winfo_height())
    except Exception:
        width = height = 0
    if width <= 20 or height <= 20:
        widget_width, widget_height = widget_logical_size(widget)
        width = max(124, widget_width - 18)
        height = max(124, widget_height - 18)

    left = max(8, int(width * 0.055))
    right = max(8, int(width * 0.055))
    top = max(8, int(height * 0.06))
    bottom = max(8, int(height * 0.05))
    usable_width = max(70, width - left - right)
    cell_width = usable_width / 7
    nav_height = max(22, min(36, int(height * 0.16)))
    nav_y = top + nav_height / 2
    header_y = top + nav_height + max(12, int(height * 0.055))
    grid_top = header_y + max(16, int(height * 0.105))
    row_height = max(15, (height - grid_top - bottom) / 6)
    header_size = max(8, min(12, int(row_height * 0.78)))
    day_size = max(9, min(13, int(row_height * 0.78)))
    nav_size = max(9, min(14, int(nav_height * 0.5)))
    nav_button_radius = max(10, min(17, nav_height * 0.46))

    return {
        "width": float(width),
        "height": float(height),
        "left": float(left),
        "right": float(right),
        "top": float(top),
        "bottom": float(bottom),
        "cell_width": float(cell_width),
        "nav_height": float(nav_height),
        "nav_y": float(nav_y),
        "nav_button_radius": float(nav_button_radius),
        "header_y": float(header_y),
        "grid_top": float(grid_top),
        "row_height": float(row_height),
        "header_size": float(header_size),
        "day_size": float(day_size),
        "nav_size": float(nav_size),
    }


def install_calendar_canvas(widget, frame, click_handler=None):
    canvas = tk.Canvas(
        frame,
        bg=CALENDAR_SURFACE,
        highlightthickness=0,
        borderwidth=0,
        bd=0,
        relief="flat",
        takefocus=0,
    )
    canvas.grid(row=0, column=0, rowspan=7, columnspan=7, padx=0, pady=0, sticky="nsew")
    canvas.bind("<Configure>", lambda _event: redraw_calendar_canvas(widget, canvas), add="+")
    _bind_calendar_canvas_interactions(widget, canvas, click_handler)
    try:
        canvas.lift()
    except Exception:
        pass
    return canvas


def _bind_calendar_canvas_interactions(widget, canvas, click_handler=None) -> None:
    def on_motion(event):
        if getattr(widget, "_is_resizing", False):
            return None
        try:
            x, y = widget_point(widget, event)
            apply_cursor(widget, event.widget, widget.get_resize_direction(x, y) or "move")
        except Exception:
            pass
        return None

    def on_leave(event):
        if not getattr(widget, "_is_resizing", False):
            apply_cursor(widget, event.widget, None)
        return None

    def on_press(event):
        try:
            x, y = widget_point(widget, event)
            direction = widget.get_resize_direction(x, y)
        except Exception:
            direction = None
        widget._calendar_canvas_press_root = (int(event.x_root), int(event.y_root))
        widget._calendar_canvas_dragged = False
        if direction:
            widget._calendar_canvas_mode = "resize"
            return start_resize(widget, event, direction)
        edit_press = getattr(widget, "_on_edit_press", None)
        if callable(edit_press):
            edit_press(event)
        widget._calendar_canvas_mode = "drag"
        widget.start_drag(event)
        widget._is_dragging_widget = True
        return "break"

    def on_drag(event):
        mode = getattr(widget, "_calendar_canvas_mode", "")
        if mode == "resize" or getattr(widget, "_is_resizing", False):
            return widget.on_mouse_drag(event)
        edit_drag = getattr(widget, "_on_edit_drag", None)
        if callable(edit_drag):
            edit_drag(event)
        start_root = getattr(widget, "_calendar_canvas_press_root", None)
        if start_root is not None:
            dx = abs(int(event.x_root) - int(start_root[0]))
            dy = abs(int(event.y_root) - int(start_root[1]))
            if dx > 3 or dy > 3:
                widget._calendar_canvas_dragged = True
        widget.do_drag(event)
        widget._is_dragging_widget = True
        return "break"

    def on_release(event):
        mode = getattr(widget, "_calendar_canvas_mode", "")
        widget._calendar_canvas_mode = ""
        if mode == "resize" or getattr(widget, "_is_resizing", False):
            return widget.on_mouse_up(event)
        edit_release = getattr(widget, "_on_edit_release", None)
        if callable(edit_release):
            edit_release(event)
        widget._is_dragging_widget = False
        if getattr(widget, "_calendar_canvas_dragged", False):
            save_now = getattr(widget, "_save_geometry_now", None)
            if callable(save_now):
                save_now()
            return "break"
        if callable(click_handler):
            click_handler(event)
        return "break"

    canvas.bind("<Motion>", on_motion, add="+")
    canvas.bind("<Leave>", on_leave, add="+")
    canvas.bind("<ButtonPress-1>", on_press, add="+")
    canvas.bind("<B1-Motion>", on_drag, add="+")
    canvas.bind("<ButtonRelease-1>", on_release, add="+")


def redraw_calendar_canvas(widget, canvas=None) -> None:
    canvas = canvas or getattr(widget, "calendar_canvas", None)
    if canvas is None:
        return
    draw_calendar_canvas(
        canvas,
        widget,
        int(getattr(widget, "display_year", date.today().year)),
        int(getattr(widget, "display_month", date.today().month)),
        _calendar_canvas_current_day(widget),
    )


def calendar_canvas_date_at_point(canvas: Any, widget, year: int, month: int, x: int, y: int) -> date | None:
    metrics = _calendar_canvas_metrics(canvas, widget)
    left = metrics["left"]
    cell_width = metrics["cell_width"]
    grid_top = metrics["grid_top"]
    row_height = metrics["row_height"]
    if x < left or x > left + cell_width * 7 or y < grid_top:
        return None
    column = int((x - left) // cell_width)
    row = int((y - grid_top) // row_height)
    if not (0 <= row < 6 and 0 <= column < 7):
        return None
    return calendar_month_dates(year, month)[row][column]


def calendar_canvas_nav_action_at_point(canvas: Any, widget, x: int, y: int) -> str | None:
    metrics = _calendar_canvas_metrics(canvas, widget)
    top = metrics["top"]
    nav_height = metrics["nav_height"]
    if y < top or y > top + nav_height:
        return None
    radius = metrics["nav_button_radius"]
    if x <= metrics["left"] + radius * 2.4:
        return "previous"
    if x >= metrics["width"] - metrics["right"] - radius * 2.4:
        return "next"
    return None


def _create_round_rect(canvas: Any, left: float, top: float, right: float, bottom: float, radius: float, **kwargs) -> None:
    radius = max(1, min(float(radius), (right - left) / 2, (bottom - top) / 2))
    canvas.create_rectangle(left + radius, top, right - radius, bottom, **kwargs)
    canvas.create_rectangle(left, top + radius, right, bottom - radius, **kwargs)
    canvas.create_oval(left, top, left + radius * 2, top + radius * 2, **kwargs)
    canvas.create_oval(right - radius * 2, top, right, top + radius * 2, **kwargs)
    canvas.create_oval(left, bottom - radius * 2, left + radius * 2, bottom, **kwargs)
    canvas.create_oval(right - radius * 2, bottom - radius * 2, right, bottom, **kwargs)


def draw_calendar_canvas(canvas: Any, widget, year: int, month: int, current_day: date) -> None:
    weeks = calendar_month_dates(year, month)
    metrics = _calendar_canvas_metrics(canvas, widget)

    canvas.delete("all")
    canvas.configure(bg=CALENDAR_SURFACE, highlightthickness=0, bd=0)

    width = metrics["width"]
    height = metrics["height"]
    left = metrics["left"]
    right = metrics["right"]
    cell_width = metrics["cell_width"]
    nav_y = metrics["nav_y"]
    nav_radius = metrics["nav_button_radius"]
    header_y = metrics["header_y"]
    grid_top = metrics["grid_top"]
    row_height = metrics["row_height"]
    nav_size = int(metrics["nav_size"])
    header_size = int(metrics["header_size"])
    day_size = int(metrics["day_size"])
    canvas.create_rectangle(0, 0, width, height, fill=CALENDAR_SURFACE, outline=CALENDAR_SURFACE)

    nav_font = ("Segoe UI", nav_size, "bold")
    header_font = ("Segoe UI", header_size, "bold")
    day_font = ("Segoe UI", day_size, "bold")
    month_font = ("Segoe UI", max(9, min(13, nav_size)), "bold")
    nav_button_fill = "#3b3737"
    month_name = calendar.month_name[int(month)]
    prev_x = left + nav_radius
    next_x = width - right - nav_radius
    _create_round_rect(
        canvas,
        prev_x - nav_radius,
        nav_y - nav_radius,
        prev_x + nav_radius,
        nav_y + nav_radius,
        nav_radius,
        fill=nav_button_fill,
        outline=nav_button_fill,
    )
    _create_round_rect(
        canvas,
        next_x - nav_radius,
        nav_y - nav_radius,
        next_x + nav_radius,
        nav_y + nav_radius,
        nav_radius,
        fill=nav_button_fill,
        outline=nav_button_fill,
    )
    canvas.create_text(prev_x, nav_y - 1, text="<", fill=CALENDAR_TEXT, font=nav_font, anchor="center")
    canvas.create_text(next_x, nav_y - 1, text=">", fill=CALENDAR_TEXT, font=nav_font, anchor="center")
    canvas.create_text(width / 2, nav_y - 1, text=f"{month_name} {year}", fill=CALENDAR_TEXT, font=month_font, anchor="center")

    for col, label in enumerate(CALENDAR_WEEKDAY_LABELS):
        x = left + (col + 0.5) * cell_width
        canvas.create_text(x, header_y, text=label, fill=CALENDAR_WEEKDAY_TEXT, font=header_font, anchor="center")

    for row, week in enumerate(weeks):
        y = grid_top + (row + 0.5) * row_height
        for col, day in enumerate(week):
            x = left + (col + 0.5) * cell_width
            is_today = day == current_day
            is_current_month = day.month == month
            is_weekend = day.weekday() >= 5
            if is_today:
                radius = max(8, min(cell_width, row_height) * 0.43)
                canvas.create_oval(
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                    fill=CALENDAR_TODAY_COLOR,
                    outline=CALENDAR_TODAY_COLOR,
                )
                fill = "#111111"
            elif not is_current_month:
                fill = CALENDAR_MUTED_TEXT
            elif is_weekend:
                fill = CALENDAR_WEEKDAY_TEXT
            else:
                fill = CALENDAR_TEXT
            canvas.create_text(x, y, text=str(day.day), fill=fill, font=day_font, anchor="center")
