from __future__ import annotations

import customtkinter as ctk

from widgets.responsive_layout import responsive_font_size
from widgets.window_interactions import control_widget_at_event, current_widget_geometry


class HeaderlessEditModeMixin:
    """Apple-style headerless widget chrome with long-press removal mode."""

    EDIT_LONG_PRESS_MS = 650
    EDIT_DRAG_CANCEL_PX = 8
    EDIT_JIGGLE_MS = 120
    EDIT_JIGGLE_OFFSETS = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))

    def _init_headerless_edit_mode(self) -> None:
        self._headerless_widgets = True
        self._edit_mode = False
        self._edit_press_after_id = None
        self._edit_jiggle_after_id = None
        self._edit_press_root: tuple[int, int] | None = None
        self._edit_base_position: tuple[int, int] | None = None
        self._edit_jiggle_index = 0
        self._suppress_geometry_save = False

    def _install_headerless_edit_mode(self) -> None:
        try:
            self.topbar.pack_forget()
        except Exception:
            pass

        self.edit_remove_button = ctk.CTkButton(
            self.container,
            text="-",
            width=30,
            height=30,
            corner_radius=15,
            command=self._remove_widget_from_edit_mode,
        )
        self.edit_remove_button.place_forget()
        self._style_edit_remove_button()
        try:
            self.bind_all("<ButtonPress-1>", self._on_global_edit_press, add="+")
            self.bind_all("<ButtonRelease-1>", self._on_global_edit_release, add="+")
        except Exception:
            pass
        try:
            self.bind("<Escape>", lambda _event: self._exit_edit_mode())
        except Exception:
            pass

    def _style_edit_remove_button(self) -> None:
        button = getattr(self, "edit_remove_button", None)
        if button is None:
            return
        theme = getattr(self, "theme", {}) or {}
        try:
            button.configure(
                fg_color=theme.get("button", "#3a3a3a"),
                hover_color=theme.get("button_hover", "#4a4a4a"),
                text_color=theme.get("text", "#ffffff"),
                font=ctk.CTkFont(size=responsive_font_size(self, "title"), weight="bold"),
            )
        except Exception:
            pass

    def _pack_headerless_body(self, *, padx: int, pady: tuple[int, int]) -> bool:
        if not getattr(self, "_headerless_widgets", False):
            return False
        try:
            self.topbar.pack_forget()
            self.body.pack_configure(padx=padx, pady=pady)
        except Exception:
            pass
        return True

    def _on_edit_press(self, event) -> None:
        if getattr(self, "_edit_mode", False) or getattr(self, "_is_resizing", False):
            return
        self._cancel_edit_press()
        self._edit_press_root = (int(event.x_root), int(event.y_root))
        self._edit_press_after_id = self.after(self.EDIT_LONG_PRESS_MS, self._enter_edit_mode)

    def _on_edit_drag(self, event) -> None:
        if self._edit_press_after_id is None or self._edit_press_root is None:
            return
        start_x, start_y = self._edit_press_root
        if abs(int(event.x_root) - start_x) > self.EDIT_DRAG_CANCEL_PX or abs(int(event.y_root) - start_y) > self.EDIT_DRAG_CANCEL_PX:
            self._cancel_edit_press()

    def _on_edit_release(self, _event=None) -> None:
        self._cancel_edit_press()

    def _on_global_edit_press(self, event) -> None:
        if getattr(self, "_edit_mode", False) and self._event_is_inside_remove_button(event):
            self._remove_widget_from_edit_mode()
            return
        if not self._event_is_inside_widget(event):
            return
        try:
            control = control_widget_at_event(self, event)
            if control is not None and self._contains_widget(control):
                return
        except Exception:
            pass
        self._on_edit_press(event)

    def _on_global_edit_release(self, event) -> None:
        if self._edit_press_after_id is not None:
            self._on_edit_release(event)

    def _event_is_inside_widget(self, event) -> bool:
        try:
            if not self.winfo_exists() or self.state() == "withdrawn":
                return False
            left = int(self.winfo_rootx())
            top = int(self.winfo_rooty())
            right = left + max(1, int(self.winfo_width()))
            bottom = top + max(1, int(self.winfo_height()))
            return left <= int(event.x_root) <= right and top <= int(event.y_root) <= bottom
        except Exception:
            return False

    def _event_is_inside_remove_button(self, event) -> bool:
        try:
            left = int(self.winfo_rootx())
            top = int(self.winfo_rooty())
            right = left + max(1, int(self.winfo_width()))
            x = int(event.x_root)
            y = int(event.y_root)
            return right - 70 <= x <= right and top <= y <= top + 70
        except Exception:
            return False

    def _contains_widget(self, widget) -> bool:
        current = widget
        for _ in range(12):
            if current is None:
                return False
            if current is self:
                return True
            current = getattr(current, "master", None)
        return False

    def _cancel_edit_press(self) -> None:
        if self._edit_press_after_id is not None:
            try:
                self.after_cancel(self._edit_press_after_id)
            except Exception:
                pass
        self._edit_press_after_id = None
        self._edit_press_root = None

    def _enter_edit_mode(self) -> None:
        self._edit_press_after_id = None
        if getattr(self, "_edit_mode", False) or not getattr(self, "_running", True):
            return
        x, y, _width, _height = current_widget_geometry(self)
        self._edit_base_position = (x, y)
        self._edit_jiggle_index = 0
        self._edit_mode = True
        try:
            self.edit_remove_button.place(relx=1.0, x=-10, y=10, anchor="ne")
            self.edit_remove_button.lift()
        except Exception:
            pass
        self._run_edit_jiggle()

    def _run_edit_jiggle(self) -> None:
        if not getattr(self, "_edit_mode", False):
            return
        base = self._edit_base_position
        if base is None:
            x, y, _width, _height = current_widget_geometry(self)
            base = (x, y)
            self._edit_base_position = base
        offset_x, offset_y = self.EDIT_JIGGLE_OFFSETS[self._edit_jiggle_index % len(self.EDIT_JIGGLE_OFFSETS)]
        self._edit_jiggle_index += 1
        try:
            self._suppress_geometry_save = True
            self.geometry(f"+{base[0] + offset_x}+{base[1] + offset_y}")
        finally:
            self._suppress_geometry_save = False
        self._edit_jiggle_after_id = self.after(self.EDIT_JIGGLE_MS, self._run_edit_jiggle)

    def _exit_edit_mode(self, *, restore: bool = True) -> None:
        self._cancel_edit_press()
        if self._edit_jiggle_after_id is not None:
            try:
                self.after_cancel(self._edit_jiggle_after_id)
            except Exception:
                pass
        self._edit_jiggle_after_id = None
        was_editing = getattr(self, "_edit_mode", False)
        self._edit_mode = False
        try:
            self.edit_remove_button.place_forget()
        except Exception:
            pass
        if was_editing and restore and self._edit_base_position is not None:
            x, y = self._edit_base_position
            try:
                self._suppress_geometry_save = True
                self.geometry(f"+{x}+{y}")
            finally:
                self._suppress_geometry_save = False
        self._edit_base_position = None

    def _remove_widget_from_edit_mode(self) -> str:
        self._exit_edit_mode(restore=True)
        self.hide_widget()
        return "break"
