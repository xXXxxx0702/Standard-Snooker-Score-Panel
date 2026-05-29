"""
Snooker Scoreboard - Windows-specific Utilities
"""

import sys
import ctypes
import ctypes.wintypes as wintypes

from PyQt6.QtCore import QAbstractNativeEventFilter, QCoreApplication
from PyQt6.QtWidgets import QWidget


def enable_win_blur(widget: QWidget, *, acrylic: bool = False, tint: tuple = (255, 255, 255, 0)):
    """
    Enable blur effect for a Qt top-level window (Windows 10/11).

    Args:
        widget: The Qt widget to apply blur to
        acrylic: True for acrylic blur, False for regular blur
        tint: (R, G, B, A) tuple, A=0~255, higher A means more "milky" color
    """
    if not sys.platform.startswith('win'):
        return

    try:
        hwnd = int(widget.winId())

        class ACCENTPOLICY(ctypes.Structure):
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

        WCA_ACCENT_POLICY = 19
        ACCENT_ENABLE_BLURBEHIND = 3
        ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

        r, g, b, a = tint
        gradient = (a << 24) | (b << 16) | (g << 8) | r

        accent = ACCENTPOLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND if acrylic else ACCENT_ENABLE_BLURBEHIND
        accent.AccentFlags = 0
        accent.GradientColor = gradient

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.SizeOfData = ctypes.sizeof(accent)
        data.Data = ctypes.addressof(accent)

        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
    except Exception:
        pass


def set_win11_rounded_corners(widget: QWidget):
    """Set rounded corners for Windows 11 windows."""
    if not sys.platform.startswith('win'):
        return

    try:
        hwnd = int(widget.winId())
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMCP_ROUND = 2
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            ctypes.c_uint(DWMWA_WINDOW_CORNER_PREFERENCE),
            ctypes.byref(ctypes.c_int(DWMCP_ROUND)),
            ctypes.sizeof(ctypes.c_int),
        )
    except Exception:
        pass


class GlobalHotkey(QAbstractNativeEventFilter):
    """
    Windows global hotkey handler using RegisterHotKey + native message filter.

    Works even when the window is not in foreground.
    """

    WM_HOTKEY = 0x0312
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004
    MOD_WIN = 0x0008

    def __init__(self, widget: QWidget, vk: int, modifiers: int, callback):
        super().__init__()
        self.widget = widget
        self.vk = int(vk)
        self.modifiers = int(modifiers)
        self.callback = callback
        self._id = 1
        self._registered = False
        self._user32 = ctypes.windll.user32

        hwnd = int(widget.winId())
        ok = self._user32.RegisterHotKey(hwnd, self._id, self.modifiers, self.vk)
        if not ok:
            raise RuntimeError("RegisterHotKey failed: possible conflict or permission issue.")

        self._registered = True
        QCoreApplication.instance().installNativeEventFilter(self)

    def nativeEventFilter(self, eventType, message):
        if eventType not in ("windows_generic_MSG", "windows_dispatcher_MSG"):
            return False, 0

        msg = wintypes.MSG.from_address(int(message))
        if msg.message == self.WM_HOTKEY and msg.wParam == self._id:
            try:
                if callable(self.callback):
                    self.callback()
            except Exception:
                pass
            return True, 0
        return False, 0

    def unregister(self):
        """Unregister the hotkey and remove the event filter."""
        if not self._registered:
            return

        try:
            hwnd = int(self.widget.winId())
            self._user32.UnregisterHotKey(hwnd, self._id)
        except Exception:
            pass
        finally:
            try:
                QCoreApplication.instance().removeNativeEventFilter(self)
            except Exception:
                pass
            self._registered = False
