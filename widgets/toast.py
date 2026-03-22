
from __future__ import annotations

import customtkinter as ctk

from config.constants import STATUS_BADGE_COLORS, FONT_SIZES


class ToastManager:
    """Simple toast notifications anchored to the bottom-right of the main window."""

    def __init__(self, parent) -> None:
        self.parent = parent
        self.active_toasts: list[ctk.CTkToplevel] = []

    def show(self, message: str, level: str = "info", duration_ms: int = 2200) -> None:
        toast = ctk.CTkToplevel(self.parent)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)

        colors = STATUS_BADGE_COLORS.get(level, STATUS_BADGE_COLORS["info"])
        toast.configure(fg_color=colors["fg"])

        frame = ctk.CTkFrame(toast, corner_radius=14, fg_color=colors["fg"])
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        title = ctk.CTkLabel(
            frame,
            text=level.upper(),
            font=ctk.CTkFont(size=FONT_SIZES["label"], weight="bold"),
            text_color=colors["text"],
        )
        title.pack(anchor="w", padx=14, pady=(10, 2))

        body = ctk.CTkLabel(
            frame,
            text=message,
            justify="left",
            wraplength=300,
            text_color=colors["text"],
            font=ctk.CTkFont(size=FONT_SIZES["body"]),
        )
        body.pack(anchor="w", padx=14, pady=(0, 12))

        toast.update_idletasks()
        width = max(260, toast.winfo_reqwidth())
        height = toast.winfo_reqheight()

        self.parent.update_idletasks()
        px = self.parent.winfo_rootx() + self.parent.winfo_width() - width - 24
        py = self.parent.winfo_rooty() + self.parent.winfo_height() - height - 24 - (len(self.active_toasts) * (height + 10))
        toast.geometry(f"{width}x{height}+{px}+{py}")

        self.active_toasts.append(toast)

        def close_toast() -> None:
            if toast in self.active_toasts:
                self.active_toasts.remove(toast)
            try:
                toast.destroy()
            except Exception:
                pass

        toast.after(duration_ms, close_toast)
