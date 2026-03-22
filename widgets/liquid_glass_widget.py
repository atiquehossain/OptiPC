from __future__ import annotations

import customtkinter as ctk
from config.constants import WIDGET_THEMES


class GlassWidgetCard(ctk.CTkFrame):
    """Liquid glass widget card with backdrop blur and premium Apple-style effects."""
    
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
            fg_color=self.theme["container"],  # Semi-transparent background
            border_width=1,
            border_color=self.theme.get("border", "transparent"),
            **kwargs
        )
        
        # Apply liquid glass styling
        self._apply_liquid_glass_effect()
    
    def _apply_liquid_glass_effect(self):
        """Apply liquid glass effects including blur simulation and highlights."""
        # The main glass effect comes from the semi-transparent background
        # and subtle border. In a real implementation, we'd use platform-specific
        # blur APIs, but for cross-platform compatibility, we simulate it.
        
        # Set up the glass appearance
        self.configure(
            fg_color=self.theme["container"],  # Semi-transparent
            border_color=self.theme.get("border", "transparent")
        )
        
        # Store original bindings for hover effects
        self._original_enter = None
        self._original_leave = None
        self._setup_liquid_interactions()
    
    def _setup_liquid_interactions(self):
        """Set up liquid glass hover and interaction effects."""
        # Store original bindings if they exist
        if self.bind("<Enter>"):
            self._original_enter = self.bind("<Enter>")
        if self.bind("<Leave>"):
            self._original_leave = self.bind("<Leave>")
        
        # Apply liquid hover effects
        self.bind("<Enter>", self._on_liquid_enter)
        self.bind("<Leave>", self._on_liquid_leave)
    
    def _on_liquid_enter(self, event=None):
        """Liquid glass hover enter effect."""
        # Slight brighten and scale effect
        try:
            current_bg = self.cget("fg_color")
            # Simulate slight brighten by reducing opacity effect
            self.configure(fg_color=current_bg)
            
            # Subtle scale effect would require canvas or other methods
            # For now, we'll use border highlight
            self.configure(border_color=self.theme.get("accent", self.theme.get("border", "transparent")))
        except Exception:
            pass
        
        # Call original enter binding if it existed
        if self._original_enter:
            try:
                self._original_enter(event)
            except Exception:
                pass
    
    def _on_liquid_leave(self, event=None):
        """Liquid glass hover leave effect."""
        try:
            # Restore original appearance
            self.configure(
                fg_color=self.theme["container"],
                border_color=self.theme.get("border", "transparent")
            )
        except Exception:
            pass
        
        # Call original leave binding if it existed
        if self._original_leave:
            try:
                self._original_leave(event)
            except Exception:
                pass
    
    def update_theme(self, theme_name: str):
        """Update the glass theme."""
        self.theme_name = theme_name
        self.theme = WIDGET_THEMES.get(theme_name, WIDGET_THEMES["modern_dark"])
        self._apply_liquid_glass_effect()


class LiquidGlassWidget(ctk.CTkToplevel):
    """Base widget with liquid glass material design."""
    
    RESIZE_BORDER = 10
    MIN_WIDTH = 160
    MIN_HEIGHT = 160
    
    # Liquid glass design tokens
    SPACING_TIGHT = 8
    SPACING_NORMAL = 12
    SPACING_SECTION = 20
    PADDING_HORIZONTAL = 20
    PADDING_VERTICAL = 16
    CORNER_RADIUS_LARGE = 26
    CORNER_RADIUS_MEDIUM = 22
    CORNER_RADIUS_SMALL = 18
    
    def __init__(
        self,
        parent,
        title: str,
        width: int = 170,
        height: int = 170,
        x: int = 40,
        y: int = 40,
        widget_key: str = "",
        theme_name: str = "modern_dark",
    ) -> None:
        self.widget_key = widget_key
        self.theme_name = theme_name
        
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

        self.title(title)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.current_theme_name = theme_name
        self.theme = WIDGET_THEMES[self.current_theme_name]

        # Main liquid glass container
        self.container = GlassWidgetCard(
            self,
            theme_name=self.current_theme_name,
            corner_radius=self.CORNER_RADIUS_LARGE
        )
        self.container.pack(fill="both", expand=True, padx=6, pady=6)

        # Title bar with glass styling
        self.topbar = ctk.CTkFrame(self.container, fg_color="transparent")
        self.topbar.pack(fill="x", padx=self.PADDING_HORIZONTAL, pady=(self.PADDING_VERTICAL, self.SPACING_TIGHT))

        # Title with glass typography
        self.title_label = ctk.CTkLabel(
            self.topbar,
            text=title,
            font=ctk.CTkFont(size=14, weight="medium"),
            text_color=self.theme["muted"]
        )
        self.title_label.pack(side="left")

        # Glass-style close button
        self.close_button = ctk.CTkButton(
            self.topbar,
            text="×",
            width=24,
            height=24,
            corner_radius=12,
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text"],
            font=ctk.CTkFont(size=16, weight="medium"),
            command=self.hide_widget,
        )
        self.close_button.pack(side="right")

        # Main content area with glass spacing
        self.body = ctk.CTkFrame(self.container, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=self.PADDING_HORIZONTAL, pady=(self.SPACING_TIGHT, self.PADDING_VERTICAL))

        # Drag functionality
        self.topbar.bind("<ButtonPress-1>", self.start_drag)
        self.topbar.bind("<B1-Motion>", self.do_drag)
        self.title_label.bind("<ButtonPress-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.do_drag)

        # Resize functionality
        for widget in (self, self.container, self.body):
            widget.bind("<Motion>", self.on_mouse_move)
            widget.bind("<ButtonPress-1>", self.on_mouse_down)
            widget.bind("<B1-Motion>", self.on_mouse_drag)
            widget.bind("<ButtonRelease-1>", self.on_mouse_up)

        self.bind("<Configure>", self._on_configure)
        self.protocol("WM_DELETE_WINDOW", self.hide_widget)

        # Apply liquid glass theme
        self._apply_base_theme()

        if hasattr(parent, "on_widget_visibility_changed") and widget_key:
            self.after(0, lambda: parent.on_widget_visibility_changed(widget_key, True))

    def _get_initial_theme_name(self) -> str:
        if hasattr(self.master, "get_widget_theme_name"):
            return str(self.master.get_widget_theme_name())
        return "modern_dark"

    def _apply_base_theme(self) -> None:
        self.theme = WIDGET_THEMES.get(self.current_theme_name, WIDGET_THEMES["modern_dark"])
        self.configure(fg_color=self.theme["window_bg"])
        self.attributes("-alpha", self.theme.get("alpha", 0.98))
        
        # Update glass container
        if hasattr(self, 'container'):
            self.container.update_theme(self.current_theme_name)
        
        # Update text colors
        if hasattr(self, 'title_label'):
            self.title_label.configure(text_color=self.theme["muted"])
        if hasattr(self, 'close_button'):
            self.close_button.configure(
                fg_color=self.theme["button"],
                hover_color=self.theme["button_hover"],
                text_color=self.theme["text"]
            )

    def apply_theme(self, theme_name: str | None = None) -> None:
        if theme_name is not None:
            self.current_theme_name = theme_name
        self._apply_base_theme()
        self.refresh_theme()

    def refresh_theme(self) -> None:
        """Override in subclasses to recolor child controls."""

    def create_glass_panel(self, parent, corner_radius: int = None, accent_tint: str = None) -> ctk.CTkFrame:
        """Create a glass panel with optional accent tint."""
        if corner_radius is None:
            corner_radius = self.CORNER_RADIUS_MEDIUM
            
        # Apply subtle accent tint if specified
        fg_color = self.theme["panel"]
        if accent_tint and accent_tint in self.theme:
            # Mix the accent color with the panel color at low opacity
            fg_color = self.theme[accent_tint]
            
        return ctk.CTkFrame(
            parent,
            corner_radius=corner_radius,
            fg_color=fg_color,
            border_width=1,
            border_color=self.theme.get("border", "transparent")
        )

    def create_glass_progress_bar(self, parent, width: int = 200, accent_color: str = None) -> ctk.CTkProgressBar:
        """Create a glass-style progress bar."""
        if accent_color is None:
            accent_color = self.theme["accent"]
            
        progress = ctk.CTkProgressBar(
            parent,
            width=width,
            height=6,
            corner_radius=3,
            progress_color=accent_color,
            fg_color=self.theme["progress_track"],
            border_width=0
        )
        progress.set(0)
        return progress

    def create_glass_label(self, parent, text: str, size_key: str = "body", weight: str = "normal", color_key: str = "text") -> ctk.CTkLabel:
        """Create a glass-style label with proper typography."""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=self._get_font_size(size_key), weight=weight),
            text_color=self.theme.get(color_key, self.theme["text"])
        )
    
    def _get_font_size(self, size_key: str) -> int:
        """Get font size with glass-appropriate scaling."""
        font_sizes = {
            "small": 11,
            "body": 13,
            "label": 14,
            "title": 16,
            "card_title": 18,
            "page_title": 24,
            "metric": 26,
            "hero": 28,
        }
        return font_sizes.get(size_key, 13)

    def create_glass_metric_label(self, parent, text: str = "0%") -> ctk.CTkLabel:
        """Create a large glass-style metric label."""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=self._get_font_size("hero"), weight="semibold"),
            text_color=self.theme["text"]
        )

    def create_glass_button(self, parent, text: str, command=None, width: int = None, height: int = 30) -> ctk.CTkButton:
        """Create a glass-style button."""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=self.CORNER_RADIUS_SMALL,
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            text_color=self.theme["text"],
            font=ctk.CTkFont(size=13, weight="medium"),
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

    def _on_configure(self, event) -> None:
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

    def do_drag(self, event) -> None:
        if self._is_resizing:
            return
        x = event.x_root - self._drag_start_x
        y = event.y_root - self._drag_start_y
        self.geometry(f"+{x}+{y}")

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
        direction = self.get_resize_direction(event.x, event.y)
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

        if "e" in direction:
            new_w = max(self.MIN_WIDTH, self._resize_start_w + dx)

        if "s" in direction:
            new_h = max(self.MIN_HEIGHT, self._resize_start_h + dy)

        if "w" in direction:
            proposed_w = self._resize_start_w - dx
            if proposed_w >= self.MIN_WIDTH:
                new_w = proposed_w
                new_x = self._resize_start_win_x + dx

        if "n" in direction:
            proposed_h = self._resize_start_h - dy
            if proposed_h >= self.MIN_HEIGHT:
                new_h = proposed_h
                new_y = self._resize_start_win_y + dy

        self.geometry(f"{int(new_w)}x{int(new_h)}+{int(new_x)}+{int(new_y)}")

    def on_mouse_up(self, event) -> None:
        self._is_resizing = False
        self._resize_dir = None
