from __future__ import annotations

import customtkinter as ctk
from config.constants import FONT_SIZES, WIDGET_THEMES, WIDGET_SIZES
from widgets.native_window_effects import (
    TRANSPARENT_WINDOW_COLOR,
    apply_rounded_window_region,
    apply_transparent_color_key,
)
from widgets.responsive_layout import (
    refresh_labels,
    register_label,
    responsive_font_size,
    responsive_spacing,
    tk_font_weight,
)
from widgets.window_interactions import (
    bind_drag_target,
    clamp_resize_geometry,
    clamp_widget_position,
    clamp_widget_size,
    configure_size_limits,
)


class ModernWidgetCard(ctk.CTkFrame):
    """Modern-style widget card with frosted glass appearance and rounded corners."""
    
    def __init__(
        self,
        parent,
        theme_name: str = "modern_dark",
        corner_radius: int = 24,
        width: int = 280,
        height: int = 180,
        **kwargs
    ):
        self.theme_name = theme_name
        self.theme = WIDGET_THEMES.get(theme_name, WIDGET_THEMES["modern_dark"])
        
        # Remove fg_color from kwargs if present to avoid conflicts
        if "fg_color" in kwargs:
            kwargs.pop("fg_color")
            
        super().__init__(
            parent,
            corner_radius=corner_radius,
            width=width,
            height=height,
            fg_color=self.theme["container"],
            bg_color=TRANSPARENT_WINDOW_COLOR,
            border_width=1,
            border_color=self.theme.get("border", "transparent"),
            **kwargs
        )
        
        # Apply frosted glass effect with shadow
        self._apply_apple_styling()
    
    def _apply_apple_styling(self):
        """Apply Modern-specific styling including shadow effects."""
        # Note: True shadow and blur effects would require platform-specific APIs
        # For now, we simulate with border and transparency
        self.configure(
            fg_color=self.theme["container"],
            bg_color=TRANSPARENT_WINDOW_COLOR,
            border_color=self.theme.get("border", "transparent")
        )


class ModernMiniWidget(ctk.CTkToplevel):
    """Modern-style base widget with frosted glass appearance and premium feel."""
    
    RESIZE_BORDER = 10
    MIN_WIDTH = 160
    MIN_HEIGHT = 160
    
    # Modern design tokens
    SPACING_TIGHT = 8
    SPACING_NORMAL = 12
    SPACING_SECTION = 20
    PADDING_HORIZONTAL = 20
    PADDING_VERTICAL = 16
    CORNER_RADIUS_LARGE = 24
    CORNER_RADIUS_MEDIUM = 20
    CORNER_RADIUS_SMALL = 16
    
    def __init__(
        self,
        parent,
        title: str,
        width: int = None,
        height: int = None,
        x: int = 40,
        y: int = 40,
        widget_key: str = "",
        theme_name: str = "modern_dark",
        size_category: str = "default",
    ) -> None:
        # Use standard size if dimensions not provided
        if width is None or height is None:
            size = WIDGET_SIZES.get(size_category, WIDGET_SIZES["default"])
            width = width if width is not None else size["width"]
            height = height if height is not None else size["height"]
        self.widget_key = widget_key
        self.size_category = size_category
        self.theme_name = theme_name
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

        self.title(title)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.current_theme_name = theme_name
        self.theme = WIDGET_THEMES[self.current_theme_name]

        # Main frosted glass container
        self.container = ModernWidgetCard(
            self,
            theme_name=self.current_theme_name,
            corner_radius=self.CORNER_RADIUS_LARGE
        )
        self.container.pack(fill="both", expand=True, padx=0, pady=0)

        # Title bar with Modern-style spacing
        self.topbar = ctk.CTkFrame(self.container, fg_color="transparent")
        self.topbar.pack(fill="x", padx=self.PADDING_HORIZONTAL, pady=(self.PADDING_VERTICAL, self.SPACING_TIGHT))

        # Title with Modern typography
        self.title_label = ctk.CTkLabel(
            self.topbar,
            text=title,
            font=ctk.CTkFont(size=FONT_SIZES["label"], weight="bold"),
            text_color=self.theme["muted"]
        )
        self.title_label.pack(side="left")

        # Close button with Modern styling
        self.close_button = ctk.CTkButton(
            self.topbar,
            text="X",
            width=24,
            height=24,
            corner_radius=12,
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text"],
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.on_close_button_click,
        )
        self.close_button.pack(side="right")

        # Main content area with generous padding
        self.body = ctk.CTkFrame(self.container, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=self.PADDING_HORIZONTAL, pady=(self.SPACING_TIGHT, self.PADDING_VERTICAL))

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

        # Apply Modern theme
        self._apply_base_theme()
        self._update_responsive_layout()

        if hasattr(parent, "on_widget_visibility_changed") and widget_key:
            self.after(0, lambda: parent.on_widget_visibility_changed(widget_key, True))

    def _install_window_interactions(self) -> None:
        for target in (self.container, self.topbar, self.title_label, self.body):
            bind_drag_target(self, target)
        self._resize_grips = []

    def _bind_drag_target(self, widget):
        bind_drag_target(self, widget)
        return widget

    def _get_initial_theme_name(self) -> str:
        if hasattr(self.master, "get_widget_theme_name"):
            return str(self.master.get_widget_theme_name())
        return "modern_dark"

    def _apply_base_theme(self) -> None:
        self.theme = WIDGET_THEMES.get(self.current_theme_name, WIDGET_THEMES["modern_dark"])
        self.configure(fg_color=TRANSPARENT_WINDOW_COLOR)
        self.attributes("-alpha", self.theme.get("alpha", 0.98))
        apply_transparent_color_key(self)
        
        # Update container styling
        if hasattr(self, 'container'):
            self.container.configure(
                fg_color=self.theme.get("container", self.theme["window_bg"]),
                bg_color=TRANSPARENT_WINDOW_COLOR,
                border_color=self.theme.get("border", "transparent")
            )
        
        # Update text colors
        if hasattr(self, 'title_label'):
            self.title_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'close_button'):
            self.close_button.configure(
                fg_color=self.theme["button"],
                hover_color=self.theme["button_hover"],
                text_color=self.theme["text"]
            )
        self.after(0, self._apply_window_shape)

    def _apply_window_shape(self) -> None:
        apply_rounded_window_region(self, radius=self.CORNER_RADIUS_LARGE)

    def apply_theme(self, theme_name: str | None = None) -> None:
        if theme_name is not None:
            self.current_theme_name = theme_name
        self._apply_base_theme()
        self._update_responsive_layout()
        self.refresh_theme()

    def refresh_theme(self) -> None:
        """Override in subclasses to recolor child controls."""

    def get_responsive_font_size(self, size_key: str) -> int:
        """Get font size that scales with the current widget geometry."""
        return responsive_font_size(self, size_key)

    def create_apple_label(self, parent, text: str, size_key: str = "body", weight: str = "normal", color_key: str = "text") -> ctk.CTkLabel:
        """Create an Modern-style label with proper typography."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=self.get_responsive_font_size(size_key), weight=tk_font_weight(weight)),
            text_color=self.theme.get(color_key, self.theme["text"]),
            justify="center",
        )
        register_label(self, label, size_key, weight)
        return self._bind_drag_target(label)

    def create_apple_panel(self, parent, corner_radius: int = None) -> ctk.CTkFrame:
        if corner_radius is None:
            corner_radius = self.CORNER_RADIUS_MEDIUM
            
        return self._bind_drag_target(ctk.CTkFrame(
            parent,
            corner_radius=corner_radius,
            fg_color=self.theme["panel"],
            border_width=1,
            border_color=self.theme.get("border", "transparent")
        ))

    def create_apple_progress_bar(self, parent, width: int = 200, accent_color: str = None) -> ctk.CTkProgressBar:
        """Create an Modern-style progress bar with rounded corners."""
        if accent_color is None:
            accent_color = self.theme["accent"]
            
        progress = ctk.CTkProgressBar(
            parent,
            width=width,
            height=8,
            corner_radius=4,
            progress_color=accent_color,
            fg_color=self.theme["progress_track"],
            border_width=0
        )
        progress.set(0)
        return self._bind_drag_target(progress)

    def create_apple_metric_label(self, parent, text: str = "0%") -> ctk.CTkLabel:
        """Create a large Modern-style metric label."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=self.get_responsive_font_size("metric"), weight="bold"),
            text_color=self.theme["text"],
            justify="center",
        )
        register_label(self, label, "metric", "bold")
        return self._bind_drag_target(label)

    def _update_responsive_layout(self) -> None:
        pad_x = responsive_spacing(self, self.PADDING_HORIZONTAL, 12)
        top_y = responsive_spacing(self, self.PADDING_VERTICAL, 10)
        spacing_tight = responsive_spacing(self, self.SPACING_TIGHT, 5)
        body_bottom = responsive_spacing(self, self.PADDING_VERTICAL, 10)
        try:
            self.topbar.pack_configure(padx=pad_x, pady=(top_y, spacing_tight))
            self.body.pack_configure(padx=pad_x, pady=(spacing_tight, body_bottom))
            self.title_label.configure(
                font=ctk.CTkFont(size=self.get_responsive_font_size("label"), weight="bold"),
                wraplength=max(60, self.winfo_width() - (pad_x * 2) - 40),
            )
        except Exception:
            pass
        refresh_labels(self)

    def create_apple_button(
        self,
        parent,
        text: str,
        command=None,
        width: int = None,
        height: int = 30,
        corner_radius: int | None = None,
    ) -> ctk.CTkButton:
        """Create an Modern-style button with subtle styling."""
        if corner_radius is None:
            corner_radius = self.CORNER_RADIUS_SMALL
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=corner_radius,
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text"],
            font=ctk.CTkFont(size=self.get_responsive_font_size("body"), weight="bold"),
            border_width=0
        )

    def hide_widget(self) -> None:
        if hasattr(self.master, "on_widget_visibility_changed") and self.widget_key:
            self.master.on_widget_visibility_changed(self.widget_key, False)
        self.withdraw()

    def show_widget(self) -> None:
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
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
        if event.widget is self:
            self._apply_window_shape()
            self._update_responsive_layout()
        if event.widget is not self:
            return
        if self._geometry_save_after_id is not None:
            try:
                self.after_cancel(self._geometry_save_after_id)
            except Exception:
                pass
        self._geometry_save_after_id = self.after(250, self._save_geometry_now)

    def _save_geometry_now(self) -> None:
        self._geometry_save_after_id = None
        if not self.widget_key or not hasattr(self.master, "save_widget_geometry"):
            return
        try:
            width, height = clamp_widget_size(self, self.winfo_width(), self.winfo_height())
            self.master.save_widget_geometry(
                self.widget_key,
                x=self.winfo_x(),
                y=self.winfo_y(),
                width=width,
                height=height,
            )
        except Exception:
            pass

    def _apply_constrained_geometry(self) -> None:
        width, height = clamp_widget_size(self, self.winfo_width(), self.winfo_height())
        if width != self.winfo_width() or height != self.winfo_height():
            self.geometry(f"{width}x{height}+{self.winfo_x()}+{self.winfo_y()}")

    def start_drag(self, event) -> None:
        if self._is_resizing:
            return
        self._drag_start_x = event.x_root - self.winfo_x()
        self._drag_start_y = event.y_root - self.winfo_y()

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
        x = event.x_root - self._drag_start_x
        y = event.y_root - self._drag_start_y
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
        # Convert window coordinates to widget-relative coordinates
        widget_x = event.x_root - self.winfo_rootx()
        widget_y = event.y_root - self.winfo_rooty()
        
        direction = self.get_resize_direction(widget_x, widget_y)
        if not direction:
            return
            
        self._is_resizing = True
        self._resize_dir = direction
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._resize_start_w = self.winfo_width()
        self._resize_start_h = self.winfo_height()
        self._resize_start_win_x = self.winfo_x()
        self._resize_start_win_y = self.winfo_y()
        
        # Stop event propagation to prevent conflicts
        return "break"

    def on_mouse_drag(self, event) -> None:
        if not self._is_resizing or not self._resize_dir:
            return

        dx = event.x_root - self._resize_start_x
        dy = event.y_root - self._resize_start_y

        new_x = self._resize_start_win_x
        new_y = self._resize_start_win_y
        new_w = self._resize_start_w
        new_h = self._resize_start_h

        direction = self._resize_dir

        # Handle each direction separately to prevent auto-incrementing
        if direction == "e":  # East - resize right edge only
            new_w = max(self.MIN_WIDTH, self._resize_start_w + dx)
            
        elif direction == "w":  # West - resize left edge only
            proposed_w = self._resize_start_w - dx
            if proposed_w >= self.MIN_WIDTH:
                new_w = proposed_w
                new_x = self._resize_start_win_x + dx
                
        elif direction == "s":  # South - resize bottom edge only
            new_h = max(self.MIN_HEIGHT, self._resize_start_h + dy)
            
        elif direction == "n":  # North - resize top edge only
            proposed_h = self._resize_start_h - dy
            if proposed_h >= self.MIN_HEIGHT:
                new_h = proposed_h
                new_y = self._resize_start_win_y + dy
                
        elif direction == "ne":  # Northeast - resize right and bottom
            new_w = max(self.MIN_WIDTH, self._resize_start_w + dx)
            new_h = max(self.MIN_HEIGHT, self._resize_start_h + dy)
            
        elif direction == "nw":  # Northwest - resize left and top
            proposed_w = self._resize_start_w - dx
            proposed_h = self._resize_start_h - dy
            if proposed_w >= self.MIN_WIDTH:
                new_w = proposed_w
                new_x = self._resize_start_win_x + dx
            if proposed_h >= self.MIN_HEIGHT:
                new_h = proposed_h
                new_y = self._resize_start_win_y + dy
                
        elif direction == "se":  # Southeast - resize right and bottom
            new_w = max(self.MIN_WIDTH, self._resize_start_w + dx)
            new_h = max(self.MIN_HEIGHT, self._resize_start_h + dy)
            
        elif direction == "sw":  # Southwest - resize left and bottom
            proposed_w = self._resize_start_w - dx
            if proposed_w >= self.MIN_WIDTH:
                new_w = proposed_w
                new_x = self._resize_start_win_x + dx
            new_h = max(self.MIN_HEIGHT, self._resize_start_h + dy)

        new_x, new_y, new_w, new_h = clamp_resize_geometry(self, direction, new_x, new_y, new_w, new_h)
        self.geometry(f"{int(new_w)}x{int(new_h)}+{int(new_x)}+{int(new_y)}")
        
        # Stop event propagation during resize
        return "break"

    def on_mouse_up(self, event) -> None:
        self._is_resizing = False
        self._resize_dir = None
        
        # Stop event propagation to prevent conflicts
        return "break"
