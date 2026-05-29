"""
Snooker Scoreboard - Clickable SVG Widget
"""

from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QPainterPath
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QWidget


class ClickableSvg(QWidget):
    """A clickable widget that displays an SVG image with rounded corners."""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 27)
        self._svg_renderer = None
        self._radius = 7

    def load(self, file_path: str) -> bool:
        """
        Load an SVG file.

        Args:
            file_path: Path to the SVG file

        Returns:
            True if loading was successful
        """
        renderer = QSvgRenderer(file_path)
        if renderer.isValid():
            self._svg_renderer = renderer
            self.update()
            return True
        return False

    def paintEvent(self, event):
        if not self._svg_renderer:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)
        painter.setClipPath(path)

        self._svg_renderer.render(painter, rect)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
