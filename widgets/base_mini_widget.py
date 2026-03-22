from __future__ import annotations

import customtkinter as ctk

from config.constants import FONT_SIZES, WIDGET_THEMES, WIDGET_SIZES, RESPONSIVE_FONT_SIZES


class BaseMiniWidget(ctk.CTkToplevel):
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
        title: str,
        width: int = None,
        height: int = None,
        x: int = 40,
        y: int = 40,
        widget_key: str = "",
        size_category: str = "default",
    ) -> None:
        # Use standard size if dimensions not provided
        if width is None or height is None:
            size = WIDGET_SIZES.get(size_category, WIDGET_SIZES["default"])
            width = width if width is not None else size["width"]
            height = height if height is not None else size["height"]
        self.widget_key = widget_key
        self.size_category = size_category
        if hasattr(parent, "get_widget_initial_geometry") and widget_key:
            geo = parent.get_widget_initial_geometry(widget_key, x=x, y=y, width=width, height=height)
            x = int(geo["x"])
            y = int(geo["y"])
            width = int(geo["width"])
            height = int(geo["height"])

        super().__init__(parent)

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
        self._double_click_delay = 300  # milliseconds

        self.title(title)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.current_theme_name = self._get_initial_theme_name()
        self.theme = WIDGET_THEMES[self.current_theme_name]

        self.container = ctk.CTkFrame(self, corner_radius=24)
        self.container.pack(fill="both", expand=True, padx=4, pady=4)

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
            text="×",
            width=28,
            height=28,
            corner_radius=14,
            command=self.hide_widget,
        )
        self.close_button.pack(side="right")
        
        # Add double-click support to close button
        self.close_button.bind("<ButtonPress-1>", self.on_close_button_click)

        self.body = ctk.CTkFrame(self.container, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=12, pady=(4, 12))

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

        self.bind("<Configure>", self._on_configure)
        self.protocol("WM_DELETE_WINDOW", self.hide_widget)

        # Apply the shared theme only to the base controls here.
        # Child controls do not exist yet, so subclasses call apply_theme()
        # after creating their own widgets.
        self._apply_base_theme()

        if hasattr(parent, "on_widget_visibility_changed") and widget_key:
            self.after(0, lambda: parent.on_widget_visibility_changed(widget_key, True))

    def _get_initial_theme_name(self) -> str:
        if hasattr(self.master, "get_widget_theme_name"):
            return str(self.master.get_widget_theme_name())
        return "dark"

    def _apply_base_theme(self) -> None:
        self.theme = WIDGET_THEMES.get(self.current_theme_name, WIDGET_THEMES["dark"])
        self.configure(fg_color=self.theme["window_bg"])
        self.attributes("-alpha", self.theme.get("alpha", 1.0))
        self.container.configure(fg_color="transparent")
        self.title_label.configure(text_color=self.theme["text"])
        self.close_button.configure(
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text"],
        )

    def apply_theme(self, theme_name: str | None = None) -> None:
        if theme_name is not None:
            self.current_theme_name = theme_name
        self._apply_base_theme()
        self.refresh_theme()

    def refresh_theme(self) -> None:
        """Override in subclasses to recolor child controls."""

    def get_responsive_font_size(self, size_key: str) -> int:
        """Get fixed font size instead of responsive scaling."""
        # Disable responsive scaling - return fixed sizes
        fixed_sizes = {
            "tiny": 9,
            "small": 11,
            "body": 12,
            "label": 13,
            "title": 15,
            "metric": 18,
            "hero": 20,
        }
        return fixed_sizes.get(size_key, FONT_SIZES.get(size_key, 12))

    def create_responsive_label(self, parent, text: str, size_key: str = "body", weight: str = "normal") -> ctk.CTkLabel:
        """Create a label with responsive font size."""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=self.get_responsive_font_size(size_key), weight=weight)
        )

    def create_panel(self, parent):
        return ctk.CTkFrame(parent, corner_radius=12, fg_color=self.theme["panel"])

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
        if hasattr(self.master, "on_widget_visibility_changed") and self.widget_key:
            self.master.on_widget_visibility_changed(self.widget_key, True)
        self._save_geometry_now()

    def destroy_widget(self) -> None:
        self._running = False
        self.destroy()

    def _on_configure(self, event) -> None:
        # Disable configure handler during resize to prevent layout conflicts
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
        if not self.widget_key or not hasattr(self.master, "save_widget_geometry"):
            return
        try:
            self.master.save_widget_geometry(
                self.widget_key,
                x=self.winfo_x(),
                y=self.winfo_y(),
                width=self.winfo_width(),
                height=self.winfo_height(),
            )
        except Exception:
            pass

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

    def on_close_button_click(self, event) -> None:
        """Handle close button clicks with double-click detection for close and reset."""
        import time
        
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Check for double-click
        if current_time - self._last_click_time < self._double_click_delay:
            # Double-click detected - close and reset widget
            self.reset_and_close()
            return
        
        # Single-click - update time and let normal close proceed
        self._last_click_time = current_time

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
        
        # Reset to default geometry if widget_key exists
        if self.widget_key and hasattr(self.master, 'reset_widget_geometry'):
            self.master.reset_widget_geometry(self.widget_key)
        
        # Hide the widget
        self.hide_widget()
        
        # Stop the widget completely
        self.after(100, self.destroy_widget)

    def do_drag(self, event) -> None:
        if self._is_resizing:
            return
        x = event.x_root - self._drag_start_x
        y = event.y_root - self._drag_start_y
        self.geometry(f"+{x}+{y}")

    def _block_child_resize_events(self, event) -> None:
        """Prevent child widgets from handling resize events."""
        # Check if this is a resize attempt (near edges)
        if self.get_resize_direction(event.x, event.y):
            # Stop the event from propagating to prevent conflicts
            return "break"
        # Allow normal click events to pass through
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

        # Always start from the original start values
        new_x = self._resize_start_win_x
        new_y = self._resize_start_win_y
        new_w = self._resize_start_w
        new_h = self._resize_start_h

        direction = self._resize_dir

        # Calculate new dimensions based on drag direction
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

        self.geometry(f"{int(new_w)}x{int(new_h)}+{int(new_x)}+{int(new_y)}")
        
        # Stop event propagation during resize
        return "break"

    def on_mouse_up(self, event) -> None:
        self._is_resizing = False
        self._resize_dir = None
        
        # Stop event propagation to prevent conflicts
        return "break"
