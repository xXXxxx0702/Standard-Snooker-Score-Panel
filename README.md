# Snooker Scoreboard 斯诺克记分牌

A professional snooker scoring application built with **PyQt6**. It provides a
control window for the operator and a separate, always-on-top floating
**overlay** (with acrylic blur) that can be placed over a video feed or stream —
much like the broadcast scoreboards seen on televised snooker.

> The application UI is in Chinese; this document is in English.

## Features

- **Full match scoring** — best-of-N frames (any odd number ≤ 99), per-frame
  scores, and running match score.
- **Ball-by-ball potting** — one button per ball (red + six colours) with
  automatic tracking of reds and colours remaining.
- **Break tracking** — live current break, frame-high break, and match-high
  break for each player, plus per-ball break/frame statistics shown as coloured
  badges.
- **"Ahead / Remaining"** display, including a highlighted alert when a player
  is mathematically ahead.
- **Black-ball decider** — automatically triggered when scores are level after
  the final colour.
- **Century animation** — celebratory animation when a break reaches 100.
- **Fouls** — quick foul buttons (4/5/6/7) that award points to the opponent
  and reset the break.
- **Undo** — multi-step undo of pots, fouls, manual scores, and player switches.
- **Manual scoring** (`+1` … `+7`) for unusual situations.
- **Frame / match management** — end frame, re-rack the current frame, and full
  match reset.
- **Floating overlay** — frameless, draggable, always-on-top scoreboard with
  Windows acrylic blur, toggleable with a global hotkey.
- **Player flags** — click a flag to change either player's country flag (SVG).
- **Statistics dialog** — per-frame score breakdown with century markers.
- **Excel export** — export an overview and per-frame detail to `.xlsx`
  (requires `openpyxl`).
- **Save / load** — persist and restore match state.

## Requirements

- **Windows** — the overlay blur, rounded corners, and global hotkey rely on the
  Win32 API. The app still runs on other platforms, but those features are
  skipped.
- **Python 3.13** (developed/tested on 3.13)
- **PyQt6** (developed/tested on 6.11)
- **openpyxl** — only required for the *Export to Excel* feature

### Install dependencies

```powershell
pip install PyQt6 openpyxl
```

## Running

From the project root:

```powershell
python main.py
```

On launch you'll be prompted for:

1. **Match length (BO)** — an odd number ≤ 99.
2. **First to break** — left or right player.

## Keyboard Shortcuts

| Key                | Action                                  |
| ------------------ | --------------------------------------- |
| `1`–`7`            | Pot the corresponding ball              |
| `Ctrl` + `4`–`7`   | Foul of 4/5/6/7 points                  |
| `Space`            | Switch the player at the table          |
| `R`                | End the current frame                   |
| `Ctrl` + `R`       | Full reset (new match)                  |
| `Ctrl` + `Z`       | Undo                                    |
| `-`                | Remove one red ball                     |
| `H`                | Toggle the floating overlay             |
| `Ctrl` + `Alt` + `H` | Toggle the overlay (global hotkey, works when unfocused) |

## Project Structure

```
SnookerScoreBoard/
├── main.py                 # Application entry point
├── config.py               # UI / game / style constants and resource paths
├── core/
│   └── scoreboard.py       # Main scoreboard window and game logic
├── widgets/
│   ├── overlay.py          # Floating always-on-top overlay
│   ├── clickable_svg.py    # Clickable SVG flag widget
│   └── badge_ghost.py      # Animated stat badge helper
├── utils/
│   ├── windows_utils.py    # Win32 blur, rounded corners, global hotkey
│   └── animation.py        # Animation helpers
└── resources/              # Icons and flag SVGs
```

## Packaging

The code is PyInstaller-aware: `config.get_resource_path()` resolves bundled
resources from `sys._MEIPASS` when frozen, so resources are looked up correctly
in a one-file build.
