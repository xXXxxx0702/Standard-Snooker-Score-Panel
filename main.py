"""
Snooker Scoreboard 2.0
A professional snooker scoring application with overlay support.

Usage:
    python main.py

Author: Snooker Scoreboard Team
"""

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from core import SnookerScoreboard


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi)

    window = SnookerScoreboard()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
