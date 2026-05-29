"""
Snooker Scoreboard - Badge Ghost Widget for Bounce Animation
"""

import math

from PyQt6.QtCore import Qt, QRect, QRectF, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QPainter
from PyQt6.QtWidgets import QWidget


class BadgeGhost(QWidget):
    """
    Temporary vector-drawn circle badge for bounce animation.

    The widget geometry is expanded to avoid clipping during scale animation.
    Supports text padding from top.
    """

    def __init__(
        self,
        base_rect: QRect,
        bg: QColor,
        fg: QColor,
        text: str,
        base_font: QFont,
        parent=None,
        max_scale: float = 1.2,
        text_pad_top: int = 0,
    ):
        super().__init__(parent)
        self._factor = 1.0
        self.bg = QColor(bg)
        self.fg = QColor(fg)
        self.text = text
        self.base_font = QFont(base_font)
        self.text_pad_top = int(text_pad_top)

        self.base_d = min(base_rect.width(), base_rect.height())
        pad = int(math.ceil((max_scale - 1.0) * self.base_d / 2.0)) + 1
        grown = base_rect.adjusted(-pad, -pad, +pad, +pad)
        self.setGeometry(grown)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)
        self.show()
        self.raise_()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform,
            True,
        )

        side = self.base_d * self._factor
        x = (self.width() - side) / 2.0
        y = (self.height() - side) / 2.0
        circle_rect = QRectF(x, y, side, side)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self.bg)
        p.drawEllipse(circle_rect)

        f = QFont(self.base_font)
        f.setPixelSize(int(0.6 * side))
        p.setFont(f)
        p.setPen(self.fg)

        pad_top_scaled = self.text_pad_top * self._factor
        text_rect = QRectF(
            circle_rect.x(),
            circle_rect.y() + pad_top_scaled,
            circle_rect.width(),
            circle_rect.height() - pad_top_scaled,
        )
        p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text)
        p.end()

    def getFactor(self) -> float:
        return self._factor

    def setFactor(self, v: float):
        self._factor = float(v)
        self.update()

    factor = pyqtProperty(float, fget=getFactor, fset=setFactor)
