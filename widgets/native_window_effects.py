from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes


ACCENT_DISABLED = 0
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
WCA_ACCENT_POLICY = 19
DWM_BB_ENABLE = 0x00000001


class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_int),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.c_void_p),
        ("SizeOfData", ctypes.c_size_t),
    ]


class DWM_BLURBEHIND(ctypes.Structure):
    _fields_ = [
        ("dwFlags", wintypes.DWORD),
        ("fEnable", wintypes.BOOL),
        ("hRgnBlur", wintypes.HRGN),
        ("fTransitionOnMaximized", wintypes.BOOL),
    ]


def is_windows() -> bool:
    return sys.platform.startswith("win")


def hex_to_abgr(color: str, alpha: int) -> int:
    color = str(color or "#202020").strip().lstrip("#")
    if len(color) == 3:
        color = "".join(char * 2 for char in color)
    if len(color) != 6:
        color = "202020"
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    alpha = max(0, min(int(alpha), 255))
    return (alpha << 24) | (blue << 16) | (green << 8) | red


def _hwnd(window) -> int:
    try:
        window.update_idletasks()
        return int(window.winfo_id())
    except Exception:
        return 0


def _set_composition(hwnd: int, state: int, tint: str, alpha: int) -> bool:
    try:
        user32 = ctypes.windll.user32
        setter = user32.SetWindowCompositionAttribute
    except Exception:
        return False

    accent = ACCENT_POLICY()
    accent.AccentState = state
    accent.AccentFlags = 2 if state == ACCENT_ENABLE_ACRYLICBLURBEHIND else 0
    accent.GradientColor = hex_to_abgr(tint, alpha)
    accent.AnimationId = 0

    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = WCA_ACCENT_POLICY
    data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
    data.SizeOfData = ctypes.sizeof(accent)
    try:
        return bool(setter(hwnd, ctypes.byref(data)))
    except Exception:
        return False


def _set_dwm_blur(hwnd: int, enabled: bool) -> bool:
    try:
        blur = DWM_BLURBEHIND()
        blur.dwFlags = DWM_BB_ENABLE
        blur.fEnable = bool(enabled)
        blur.hRgnBlur = None
        blur.fTransitionOnMaximized = False
        return ctypes.windll.dwmapi.DwmEnableBlurBehindWindow(hwnd, ctypes.byref(blur)) == 0
    except Exception:
        return False


def apply_native_window_effect(window, *, enabled: bool, tint: str = "#202020", alpha: int = 180) -> bool:
    """Apply Windows blur/acrylic to a Tk top-level window when available."""
    if not is_windows():
        return False
    hwnd = _hwnd(window)
    if not hwnd:
        return False
    if not enabled:
        _set_composition(hwnd, ACCENT_DISABLED, tint, 0)
        _set_dwm_blur(hwnd, False)
        return True
    if _set_composition(hwnd, ACCENT_ENABLE_ACRYLICBLURBEHIND, tint, alpha):
        return True
    if _set_composition(hwnd, ACCENT_ENABLE_BLURBEHIND, tint, alpha):
        return True
    return _set_dwm_blur(hwnd, True)
