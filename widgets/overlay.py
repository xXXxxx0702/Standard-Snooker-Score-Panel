"""
Snooker Scoreboard - Floating Overlay Widget
"""

import ctypes
import ctypes.wintypes as wintypes
import sys

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit

from utils.windows_utils import set_win11_rounded_corners
from config import UI


class ScoreboardOverlay(QWidget):
    """
    Floating scoreboard overlay that stays on top of other windows.

    Supports dragging and keyboard events forwarding to main window.
    """

    def __init__(self, yellow_bar: QWidget, break_bar: QWidget, main_window=None):
        super().__init__(
            flags=Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.main_window = main_window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("记分牌")

        self._startPos = None
        self._isTracking = False

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(yellow_bar)
        layout.addWidget(break_bar)
        layout.addStretch(1)
        self.setLayout(layout)

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(UI.OVERLAY_WIDTH, UI.OVERLAY_HEIGHT)

        self._install_drag_filter(yellow_bar)
        self._install_drag_filter(break_bar)
        self._install_drag_filter(self)

        self.adjustSize()
        set_win11_rounded_corners(self)

    def _install_drag_filter(self, w: QWidget):
        """Install event filter on widget and its children (except QLineEdit)."""
        w.installEventFilter(self)
        for child in w.findChildren(QWidget):
            if not isinstance(child, QLineEdit):
                child.installEventFilter(self)

    def _is_line_edit_or_child(self, obj) -> bool:
        """Check if event target is a QLineEdit or its child."""
        w = obj if isinstance(obj, QWidget) else None
        while w is not None:
            if isinstance(w, QLineEdit):
                return True
            w = w.parentWidget()
        return False

    def eventFilter(self, obj, event):
        if self._is_line_edit_or_child(obj):
            return False

        if (
            event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
        ):
            if self.main_window:
                self.main_window.name_input_p1.clearFocus()
                self.main_window.name_input_p2.clearFocus()
            self._isTracking = True
            self._startPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            return True

        elif event.type() == QEvent.Type.MouseMove and self._isTracking:
            self.move(event.globalPosition().toPoint() - self._startPos)
            return True

        elif event.type() == QEvent.Type.MouseButtonRelease:
            if self._isTracking:
                self._isTracking = False
                return True

        return False

    def clear_name_focus(self, event):
        if self.main_window:
            self.main_window.name_input_p1.clearFocus()
            self.main_window.name_input_p2.clearFocus()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._isTracking = True
            self._startPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._isTracking:
            self.move(event.globalPosition().toPoint() - self._startPos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._isTracking = False

    def keyPressEvent(self, event):
        if self.main_window:
            self.main_window.keyPressEvent(event)

        if event.key() == Qt.Key.Key_Escape:
            if self.main_window:
                self.main_window.name_input_p1.clearFocus()
                self.main_window.name_input_p2.clearFocus()
            event.accept()
        else:
            super().keyPressEvent(event)
