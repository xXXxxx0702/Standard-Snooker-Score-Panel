"""
Snooker Scoreboard - Configuration and Constants
"""

import os
import sys

# ==============================
# Path Utilities
# ==============================
def _base_path() -> str:
    """Base directory for bundled assets (handles PyInstaller one-file)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(filename: str) -> str:
    """Get absolute path to a resource, works for dev and PyInstaller."""
    return os.path.join(_base_path(), 'resources', filename)


def get_flag_path(filename: str) -> str:
    """Get absolute path to a flag SVG, works for dev and PyInstaller."""
    return os.path.join(_base_path(), 'resources', 'flag_svg', filename)


# ==============================
# UI Constants
# ==============================
class UI:
    # Window sizes
    MAIN_WINDOW_WIDTH = 900
    OVERLAY_WIDTH = 1000
    OVERLAY_HEIGHT = 137
    YELLOW_BAR_HEIGHT = 36
    BREAK_BAR_HEIGHT = 100

    # Ball button size
    BALL_BUTTON_SIZE = 60

    # Badge sizes
    BADGE_SIZE_LARGE = 28
    BADGE_SIZE_SMALL = 20

    # Animation durations (ms)
    BALL_COOLDOWN = 430
    SWITCH_COOLDOWN = 600
    MANUAL_SCORE_COOLDOWN = 500
    ARROW_ANIMATION_DURATION = 250
    FLY_IN_DURATION = 220
    STAT_UPDATE_DURATION = 160
    CENTURY_GROW_DURATION = 800
    CENTURY_PAUSE_DURATION = 3000
    CENTURY_SHRINK_DURATION = 400


# ==============================
# Game Constants
# ==============================
class Game:
    INITIAL_REDS = 15
    MAX_FRAMES = 99
    CENTURY_BREAK = 100

    # Ball values and colors
    BALL_CONFIG = [
        ("红", "#c91605", 1),
        ("黄", "#ffd904", 2),
        ("绿", "#028241", 3),
        ("棕", "#a34e13", 4),
        ("蓝", "#0074de", 5),
        ("粉", "#f68083", 6),
        ("黑", "#0d130f", 7),
    ]

    # Colors that need dark text
    LIGHT_BALLS = {2, 6}


# ==============================
# Default Resources
# ==============================
class Resources:
    ICON = "billiard-svgrepo-com.ico"
    FLAG_P1_DEFAULT = "gb-eng.svg"
    FLAG_P2_DEFAULT = "cn.svg"


# ==============================
# Style Constants
# ==============================
class Styles:
    YELLOW_BAR_BG = "#ffd110"
    TEAL_BG = "#007F7B"
    BREAK_BAR_BG = "rgba(60, 60, 60, 80)"
    ALERT_COLOR = "#f3ff10"
    WINNER_HIGHLIGHT = "#FFF275"
