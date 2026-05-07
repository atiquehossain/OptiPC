from __future__ import annotations

import customtkinter as ctk

from config.constants import WIDGET_CONTENT_MARGIN
from widgets.window_interactions import current_widget_geometry


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
    return calendar_size_class(widget) in {"large", "extra_large"}


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
        width = max(104, widget_width - 48)
    elif width > widget_width * 1.25:
        width = max(104, widget_width - 48)
    if height <= 20:
        height = max(68, widget_height - 126)
    elif height > widget_height * 1.25:
        height = max(68, widget_height - 126)
    return width, height


def calendar_cell_metrics(widget, frame) -> tuple[int, int, int]:
    width, height = _frame_size(widget, frame)
    cell_width = max(16, min(44, int((width - 4) / 7)))
    cell_height = max(10, min(28, int((height - 4) / 7)))
    font_size = 8 if cell_height <= 13 else 9 if cell_height <= 16 else 10 if cell_height <= 20 else 11
    return cell_width, cell_height, font_size


def apply_calendar_grid_layout(widget, frame, day_labels, day_buttons) -> None:
    if not frame or not day_labels or not day_buttons:
        return
    install_calendar_grid(frame)
    cell_width, cell_height, font_size = calendar_cell_metrics(widget, frame)
    header_font = ctk.CTkFont(size=max(9, font_size), weight="bold")
    day_font = ctk.CTkFont(size=font_size, weight="bold")
    radius = max(4, min(14, cell_height // 2))

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
