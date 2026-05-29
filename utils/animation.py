"""
Snooker Scoreboard - Animation Utilities
"""

from PyQt6.QtCore import QObject, pyqtProperty
from PyQt6.QtWidgets import QHBoxLayout, QSpacerItem, QSizePolicy


class HSpacerAnimator(QObject):
    """
    Animatable property wrapper for QSpacerItem width.

    Makes QSpacerItem width animatable via QPropertyAnimation.
    Refreshes layout on each frame.
    """

    def __init__(self, layout: QHBoxLayout, spacer: QSpacerItem, height: int, parent=None):
        super().__init__(parent)
        self._w = 0
        self.layout = layout
        self.spacer = spacer
        self.h = height

    def getWidth(self) -> int:
        return self._w

    def setWidth(self, w: int):
        self._w = int(w)
        self.spacer.changeSize(
            self._w, self.h,
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.layout.invalidate()
        pw = self.layout.parentWidget()
        if pw:
            pw.update()

    width = pyqtProperty(int, fget=getWidth, fset=setWidth)
