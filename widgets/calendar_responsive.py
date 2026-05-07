from __future__ import annotations

import calendar
import tkinter as tk
from datetime import date, timedelta
from typing import Any

import customtkinter as ctk

from config.constants import WIDGET_CONTENT_MARGIN
from widgets.window_interactions import current_widget_geometry

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
    top = max(10, int(height * 0.075))
    bottom = max(8, int(height * 0.05))
    usable_width = max(70, width - left - right)
    cell_width = usable_width / 7
    header_y = top
    grid_top = header_y + max(20, int(height * 0.155))
    row_height = max(15, (height - grid_top - bottom) / 6)
    header_size = max(8, min(12, int(row_height * 0.78)))
    day_size = max(9, min(13, int(row_height * 0.78)))

    return {
        "width": float(width),
        "height": float(height),
        "left": float(left),
        "right": float(right),
        "top": float(top),
        "bottom": float(bottom),
        "cell_width": float(cell_width),
        "header_y": float(header_y),
        "grid_top": float(grid_top),
        "row_height": float(row_height),
        "header_size": float(header_size),
        "day_size": float(day_size),
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
    try:
        widget._bind_drag_target(canvas)
    except Exception:
        pass
    canvas.grid(row=0, column=0, rowspan=7, columnspan=7, padx=0, pady=0, sticky="nsew")
    canvas.bind("<Configure>", lambda _event: redraw_calendar_canvas(widget, canvas), add="+")
    if click_handler is not None:
        canvas.bind("<ButtonRelease-1>", click_handler, add="+")
    try:
        canvas.lift()
    except Exception:
        pass
    return canvas


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


def draw_calendar_canvas(canvas: Any, widget, year: int, month: int, current_day: date) -> None:
    weeks = calendar_month_dates(year, month)
    metrics = _calendar_canvas_metrics(canvas, widget)

    canvas.delete("all")
    canvas.configure(bg=CALENDAR_SURFACE, highlightthickness=0, bd=0)

    left = metrics["left"]
    cell_width = metrics["cell_width"]
    header_y = metrics["header_y"]
    grid_top = metrics["grid_top"]
    row_height = metrics["row_height"]
    header_size = int(metrics["header_size"])
    day_size = int(metrics["day_size"])
    header_font = ("Segoe UI", header_size, "bold")
    day_font = ("Segoe UI", day_size, "bold")

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
