from __future__ import annotations

import customtkinter as ctk

from config.constants import FONT_SIZES, WIDGET_THEMES
from widgets.headerless_edit_mode import HeaderlessEditModeMixin
from widgets.native_window_effects import (
    TRANSPARENT_WINDOW_COLOR,
    apply_native_window_effect,
    apply_rounded_window_region,
    apply_transparent_color_key,
)
from widgets.responsive_layout import (
    refresh_labels,
    register_label,
    responsive_font_size,
    responsive_spacing,
)
from widgets.window_interactions import (
    bind_drag_target,
    clamp_resize_geometry,
    clamp_widget_position,
    clamp_widget_size,
    configure_size_limits,
    current_widget_geometry,
    geometry_root_point,
    logical_size_delta,
    widget_point,
)
from widgets.widget_spec_mixin import WidgetSpecMixin


class BaseMiniWidget(HeaderlessEditModeMixin, WidgetSpecMixin, ctk.CTkToplevel):
    """Base class for floating desktop widgets.

    Design goals:
    - single instance managed by the main app
    - draggable from the title area
    - resizable from every edge and corner
    - themeable using the shared widget themes
    - remembers size and position through the parent app
    """

    RESIZE_BORDER = 10
    MIN_WIDTH = 160
    MIN_HEIGHT = 160

    def __init__(
        self,
        parent,
        title: str | None = None,
        width: int = None,
        height: int = None,
        x: int = 40,
        y: int = 40,
        widget_key: str = "",
        size_category: str | None = None,
    ) -> None:
        title, widget_key, size_category = self._resolve_widget_spec_defaults(title, widget_key, size_category)

        if width is None or height is None:
            width, height = self._resolve_widget_dimensions(width, height)
        configure_size_limits(self, size_category, int(width), int(height))
        if hasattr(parent, "get_widget_initial_geometry") and widget_key:
            geo = parent.get_widget_initial_geometry(widget_key, x=x, y=y, width=width, height=height)
            x = int(geo["x"])
            y = int(geo["y"])
            width = int(geo["width"])
            height = int(geo["height"])
        width, height = clamp_widget_size(self, width, height)

        super().__init__(parent)
        x, y = clamp_widget_position(self, x, y, width, height)

        self._running = True
        self._geometry_save_after_id = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_resizing = False
        self._resize_dir: str | None = None
        self._resize_start_x = 0
        self._resize_start_y = 0
        self._resize_start_w = width
        self._resize_start_h = height
        self._resize_start_win_x = x
        self._resize_start_win_y = y
        
        # Double-click tracking
        self._last_click_time = 0
        self._last_close_click_time = 0
        self._double_click_delay = 300  # milliseconds
        self._close_after_id = None
        self._responsive_label_specs = []
        self._widget_material_active = True
        self._init_headerless_edit_mode()

        self.title(title)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.current_theme_name = self._get_initial_theme_name()
        self.theme = WIDGET_THEMES[self.current_theme_name]

        self.container = ctk.CTkFrame(self, corner_radius=24)
        self.container.pack(fill="both", expand=True, padx=0, pady=0)

        self.topbar = ctk.CTkFrame(self.container, fg_color="transparent")
        self.topbar.pack(fill="x", padx=12, pady=(10, 4))

        self.title_label = ctk.CTkLabel(
            self.topbar,
            text=title,
            font=ctk.CTkFont(size=FONT_SIZES["title"], weight="bold"),
        )
        self.title_label.pack(side="left")

        self.close_button = ctk.CTkButton(
            self.topbar,
            text="X",
            width=28,
            height=28,
            corner_radius=14,
            command=self.on_close_button_click,
        )
        self.close_button.pack(side="right")

        self.body = ctk.CTkFrame(self.container, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        self._install_headerless_edit_mode()

        # Drag functionality with double-click support
        self.topbar.bind("<ButtonPress-1>", self.on_title_click)
        self.topbar.bind("<B1-Motion>", self.on_title_drag)
        self.title_label.bind("<ButtonPress-1>", self.on_title_click)
        self.title_label.bind("<B1-Motion>", self.on_title_drag)

        # Resize functionality - bind only to main window to prevent conflicts
        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<ButtonPress-1>", self.on_mouse_down)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # Prevent child widgets from handling resize events
        self.container.bind("<ButtonPress-1>", self._block_child_resize_events)
        self.body.bind("<ButtonPress-1>", self._block_child_resize_events)
        self._install_window_interactions()

        self.bind("<Configure>", self._on_configure)
        self.protocol("WM_DELETE_WINDOW", self.hide_widget)
        self._install_material_state_bindings()

        # Apply the shared theme only to the base controls here.
        # Child controls do not exist yet, so subclasses call apply_theme()
        # after creating their own widgets.
        self._apply_base_theme()
        self._update_responsive_layout()

        if hasattr(parent, "on_widget_visibility_changed") and widget_key:
            self.after(0, lambda: parent.on_widget_visibility_changed(widget_key, True))

    def _install_window_interactions(self) -> None:
        for target in (self.container, self.body):
            bind_drag_target(self, target)
        self._resize_grips = []

    def _bind_drag_target(self, widget):
        bind_drag_target(self, widget)
        try:
            self.after(0, lambda target=widget: bind_drag_target(self, target))
        except Exception:
            pass
        return widget

    def _get_initial_theme_name(self) -> str:
        if hasattr(self.master, "get_widget_theme_name"):
            return str(self.master.get_widget_theme_name())
        return "dark"

    def _resolved_widget_theme(self) -> dict:
        if hasattr(self.master, "resolve_widget_theme"):
            try:
                return dict(self.master.resolve_widget_theme(self.current_theme_name, active=self._widget_material_active))
            except Exception:
                pass
        return dict(WIDGET_THEMES.get(self.current_theme_name, WIDGET_THEMES["dark"]))

    def _install_material_state_bindings(self) -> None:
        self.bind("<Enter>", lambda _event: self._set_material_active(True), add="+")
        self.bind("<FocusIn>", lambda _event: self._set_material_active(True), add="+")
        self.bind("<Leave>", lambda _event: self._set_material_active(False), add="+")
        self.bind("<FocusOut>", lambda _event: self._set_material_active(False), add="+")

    def _set_material_active(self, active: bool) -> None:
        if self._widget_material_active == bool(active):
            return
        self._widget_material_active = bool(active)
        try:
            if self.winfo_exists():
                self._apply_base_theme()
                self.refresh_theme()
        except Exception:
            pass

    def _apply_base_theme(self) -> None:
        self.theme = self._resolved_widget_theme()
        self.configure(fg_color=TRANSPARENT_WINDOW_COLOR)
        self.attributes("-alpha", self.theme.get("alpha", 1.0))
        apply_transparent_color_key(self)
        self.container.configure(
            fg_color=self.theme.get("container", self.theme["window_bg"]),
            bg_color=TRANSPARENT_WINDOW_COLOR,
            border_width=1,
            border_color=self.theme.get("border", "transparent"),
        )
        self.title_label.configure(text_color=self.theme["text"])
        self.close_button.configure(
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text"],
        )
        self._style_edit_remove_button()
        self.after(0, self._apply_native_glass_effect)
        self.after(0, self._apply_window_shape)

    def _apply_native_glass_effect(self) -> None:
        enabled = bool(self.theme.get("native_blur", self.current_theme_name == "glass"))
        alpha = int(self.theme.get("blur_alpha", 165 if self.current_theme_name == "glass" else 215))
        try:
            apply_native_window_effect(
                self,
                enabled=enabled,
                tint=self.theme.get("blur_tint", self.theme.get("container", self.theme.get("window_bg", "#202020"))),
                alpha=alpha,
            )
        except Exception:
            pass

    def _apply_window_shape(self) -> None:
        apply_rounded_window_region(self, radius=24)

    def apply_theme(self, theme_name: str | None = None) -> None:
        if theme_name is not None:
            self.current_theme_name = theme_name
        self._apply_base_theme()
        self._update_responsive_layout()
        self.refresh_theme()

    def refresh_theme(self) -> None:
        """Override in subclasses to recolor child controls."""

    def get_responsive_font_size(self, size_key: str) -> int:
        """Get font size scaled to the current widget geometry."""
        return responsive_font_size(self, size_key)

    def create_responsive_label(self, parent, text: str, size_key: str = "body", weight: str = "normal") -> ctk.CTkLabel:
        """Create a label with responsive font size."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=self.get_responsive_font_size(size_key), weight=weight),
            justify="center",
        )
        register_label(self, label, size_key, weight)
        return self._bind_drag_target(label)

    def _update_responsive_layout(self) -> None:
        pad_x = responsive_spacing(self, 12, 8)
        top_y = responsive_spacing(self, 10, 6)
        body_bottom = responsive_spacing(self, 12, 8)
        try:
            if not self._pack_headerless_body(padx=pad_x, pady=(top_y, body_bottom)):
                self.topbar.pack_configure(padx=pad_x, pady=(top_y, 4))
                self.body.pack_configure(padx=pad_x, pady=(4, body_bottom))
            self.title_label.configure(
                font=ctk.CTkFont(size=self.get_responsive_font_size("title"), weight="bold"),
                wraplength=max(60, self.winfo_width() - (pad_x * 2) - 42),
            )
        except Exception:
            pass
        refresh_labels(self)

    def create_panel(self, parent):
        panel = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.theme["panel"])
        return self._bind_drag_target(panel)

    def style_textbox(self, textbox) -> None:
        textbox.configure(
            fg_color=self.theme["panel"],
            text_color=self.theme["text"],
            border_width=0,
        )

    def hide_widget(self) -> None:
        if hasattr(self.master, "on_widget_visibility_changed") and self.widget_key:
            self.master.on_widget_visibility_changed(self.widget_key, False)
        self.withdraw()

    def show_widget(self) -> None:
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self._settle_widget_position()
        if hasattr(self.master, "on_widget_visibility_changed") and self.widget_key:
            self.master.on_widget_visibility_changed(self.widget_key, True)
        self._save_geometry_now()

    def destroy_widget(self) -> None:
        self._running = False
        self.destroy()

    def _finish_reset_and_close(self) -> None:
        if hasattr(self.master, "on_widget_visibility_changed") and self.widget_key:
            self.master.on_widget_visibility_changed(self.widget_key, False)
        self.destroy_widget()

    def _on_configure(self, event) -> None:
        # Disable configure handler during resize to prevent layout conflicts
        if event.widget is self:
            self._apply_window_shape()
            self._update_responsive_layout()
        if event.widget is not self or self._is_resizing:
            return
        if self._geometry_save_after_id is not None:
            try:
                self.after_cancel(self._geometry_save_after_id)
            except Exception:
                pass
        self._geometry_save_after_id = self.after(250, self._save_geometry_now)

    def _save_geometry_now(self) -> None:
        self._geometry_save_after_id = None
        if getattr(self, "_suppress_geometry_save", False) or getattr(self, "_edit_mode", False):
            return
        if not self.widget_key or not hasattr(self.master, "save_widget_geometry"):
            return
        try:
            x, y, current_width, current_height = current_widget_geometry(self)
            width, height = clamp_widget_size(self, current_width, current_height)
            self.master.save_widget_geometry(
                self.widget_key,
                x=x,
                y=y,
                width=width,
                height=height,
            )
        except Exception:
            pass

    def _apply_constrained_geometry(self) -> None:
        x, y, current_width, current_height = current_widget_geometry(self)
        width, height = clamp_widget_size(self, current_width, current_height)
        if width != current_width or height != current_height:
            self.geometry(f"{width}x{height}+{x}+{y}")

    def _settle_widget_position(self) -> None:
        if hasattr(self.master, "place_widget_without_overlap"):
            try:
                self.master.place_widget_without_overlap(self)
            except Exception:
                pass

    def start_drag(self, event) -> None:
        if self._is_resizing:
            return
        x, y, _width, _height = current_widget_geometry(self)
        root_x, root_y = geometry_root_point(self, event)
        self._drag_start_x = root_x - x
        self._drag_start_y = root_y - y

    def on_title_click(self, event) -> None:
        """Handle title bar clicks with double-click detection for close and reset."""
        import time
        
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Check for double-click
        if current_time - self._last_click_time < self._double_click_delay:
            # Double-click detected - close and reset widget
            self.reset_and_close()
            return
        
        # Single-click - start drag
        self._last_click_time = current_time
        self.start_drag(event)

    def on_title_drag(self, event) -> None:
        """Handle title bar dragging only when not resizing."""
        # Only drag if we're not currently resizing
        if not self._is_resizing:
            self.do_drag(event)

    def _cancel_pending_close(self) -> None:
        if self._close_after_id is not None:
            try:
                self.after_cancel(self._close_after_id)
            except Exception:
                pass
            self._close_after_id = None

    def _run_single_close(self) -> None:
        self._close_after_id = None
        self.hide_widget()

    def on_close_button_click(self, event=None) -> str:
        """Handle close button clicks with double-click detection for close and reset."""
        import time
        
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Check for double-click
        if current_time - self._last_close_click_time < self._double_click_delay:
            # Double-click detected - close and reset widget
            self._cancel_pending_close()
            self.reset_and_close()
            return "break"
        
        # Single-click - wait briefly so a second click can reset geometry.
        self._last_close_click_time = current_time
        self._cancel_pending_close()
        self._close_after_id = self.after(self._double_click_delay, self._run_single_close)
        return "break"

    def reset_and_close(self) -> None:
        """Close widget and reset to default position/size."""
        # Stop any running operations
        self._running = False
        
        # Cancel any pending geometry saves
        if self._geometry_save_after_id is not None:
            try:
                self.after_cancel(self._geometry_save_after_id)
            except Exception:
                pass
        self._cancel_pending_close()
        
        # Reset to default geometry if widget_key exists
        if self.widget_key and hasattr(self.master, 'reset_widget_geometry'):
            self.master.reset_widget_geometry(self.widget_key)
        
        # Hide the widget
        self.hide_widget()
        
        # Stop the widget completely
        self.after(100, self._finish_reset_and_close)

    def do_drag(self, event) -> None:
        if self._is_resizing:
            return
        self._exit_edit_mode(restore=False)
        root_x, root_y = geometry_root_point(self, event)
        x = root_x - self._drag_start_x
        y = root_y - self._drag_start_y
        self.geometry(f"+{x}+{y}")

    def _block_child_resize_events(self, event) -> None:
        """Allow shared drag/resize bindings to handle child events."""
        return None

    def get_resize_direction(self, x: int, y: int) -> str | None:
        width = self.winfo_width()
        height = self.winfo_height()
        border = self.RESIZE_BORDER

        left = x <= border
        right = x >= width - border
        top = y <= border
        bottom = y >= height - border

        if top and left:
            return "nw"
        if top and right:
            return "ne"
        if bottom and left:
            return "sw"
        if bottom and right:
            return "se"
        if left:
            return "w"
        if right:
            return "e"
        if top:
            return "n"
        if bottom:
            return "s"
        return None

    def apply_cursor(self, direction: str | None) -> None:
        cursor_map = {
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
        self.configure(cursor=cursor_map.get(direction, "arrow"))

    def on_mouse_move(self, event) -> None:
        if self._is_resizing:
            return
        self.apply_cursor(self.get_resize_direction(event.x, event.y))

    def on_mouse_down(self, event) -> None:
        widget_x, widget_y = widget_point(self, event)
        direction = self.get_resize_direction(widget_x, widget_y)
        if not direction:
            return
            
        self._is_resizing = True
        self._resize_dir = direction
        root_x, root_y = geometry_root_point(self, event)
        self._resize_start_x = root_x
        self._resize_start_y = root_y
        x, y, width, height = current_widget_geometry(self)
        self._resize_start_w = width
        self._resize_start_h = height
        self._resize_start_win_x = x
        self._resize_start_win_y = y
        
        # Stop event propagation to prevent conflicts
        return "break"

    def on_mouse_drag(self, event) -> None:
        if not self._is_resizing or not self._resize_dir:
            return

        root_x, root_y = geometry_root_point(self, event)
        dx = root_x - self._resize_start_x
        dy = root_y - self._resize_start_y
        width_delta, height_delta = logical_size_delta(self, dx, dy)

        # Always start from the original start values
        new_x = self._resize_start_win_x
        new_y = self._resize_start_win_y
        new_w = self._resize_start_w
        new_h = self._resize_start_h

        direction = self._resize_dir

        # Calculate new dimensions based on drag direction
        if direction == "e":  # East - resize right edge only
            new_w = max(self.MIN_WIDTH, self._resize_start_w + width_delta)
            
        elif direction == "w":  # West - resize left edge only
            proposed_w = self._resize_start_w - width_delta
            if proposed_w >= self.MIN_WIDTH:
                new_w = proposed_w
                new_x = self._resize_start_win_x + dx
                
        elif direction == "s":  # South - resize bottom edge only
            new_h = max(self.MIN_HEIGHT, self._resize_start_h + height_delta)
            
        elif direction == "n":  # North - resize top edge only
            proposed_h = self._resize_start_h - height_delta
            if proposed_h >= self.MIN_HEIGHT:
                new_h = proposed_h
                new_y = self._resize_start_win_y + dy
                
        elif direction == "ne":  # Northeast - resize right and top
            new_w = max(self.MIN_WIDTH, self._resize_start_w + width_delta)
            proposed_h = self._resize_start_h - height_delta
            if proposed_h >= self.MIN_HEIGHT:
                new_h = proposed_h
                new_y = self._resize_start_win_y + dy
            
        elif direction == "nw":  # Northwest - resize left and top
            proposed_w = self._resize_start_w - width_delta
            proposed_h = self._resize_start_h - height_delta
            if proposed_w >= self.MIN_WIDTH:
                new_w = proposed_w
                new_x = self._resize_start_win_x + dx
            if proposed_h >= self.MIN_HEIGHT:
                new_h = proposed_h
                new_y = self._resize_start_win_y + dy
                
        elif direction == "se":  # Southeast - resize right and bottom
            new_w = max(self.MIN_WIDTH, self._resize_start_w + width_delta)
            new_h = max(self.MIN_HEIGHT, self._resize_start_h + height_delta)
            
        elif direction == "sw":  # Southwest - resize left and bottom
            proposed_w = self._resize_start_w - width_delta
            if proposed_w >= self.MIN_WIDTH:
                new_w = proposed_w
                new_x = self._resize_start_win_x + dx
            new_h = max(self.MIN_HEIGHT, self._resize_start_h + height_delta)

        new_x, new_y, new_w, new_h = clamp_resize_geometry(self, direction, new_x, new_y, new_w, new_h)
        self.geometry(f"{int(new_w)}x{int(new_h)}+{int(new_x)}+{int(new_y)}")
        
        # Stop event propagation during resize
        return "break"

    def on_mouse_up(self, event) -> None:
        self._is_resizing = False
        self._resize_dir = None
        self._settle_widget_position()
        self._save_geometry_now()
        
        # Stop event propagation to prevent conflicts
        return "break"
