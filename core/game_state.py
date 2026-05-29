"""
Snooker Scoreboard - Pure Game Logic Layer

This module is intentionally free of any Qt / UI dependency so the scoring
rules can be reasoned about and unit-tested in isolation.

``GameState`` is the single source of truth for the numeric match/frame state
that used to live as ~40 scattered attributes on the main window. The window
keeps property proxies onto this object, so the existing UI code continues to
read/write the same attribute names while the data and rules live here.
"""

from dataclasses import dataclass, field

from config import Game


def _fresh_colors() -> dict:
    """Return a fresh colours-remaining map (yellow..black, one each)."""
    return {2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}


@dataclass
class PlayerState:
    """All per-player scoring state for one player."""

    score: int = 0
    break_score: int = 0
    frame_high_break: int = 0
    highest_break: int = 0
    match_high_break_start: int = 0
    frame_score: int = 0
    frame_scores: list = field(default_factory=list)
    break_scores: list = field(default_factory=list)


@dataclass
class PotOutcome:
    """Result of attempting to pot a ball, for the UI to react to."""

    potted: bool = False
    decider_triggered: bool = False
    century_triggered: bool = False
    value: int = 0
    red_after: int = 0          # red count to display after this pot
    color_after: int | None = None  # colour count to display (pre-decider)


@dataclass
class ManualOutcome:
    """Result of a manual score addition."""

    century_triggered: bool = False
    value: int = 0


class GameState:
    """Pure scoring model for a snooker match.

    Mutating methods replicate the exact rules previously embedded in the main
    window and push undo records onto ``action_stack`` in the same tuple
    formats, so save/load and the window-side undo continue to work unchanged.
    """

    def __init__(self):
        self.p1 = PlayerState()
        self.p2 = PlayerState()

        self.total_frames = 0
        self.first_break_player = 1
        self.current_frame_break_player = 1
        self.current_player = 1

        self.red_remaining = Game.INITIAL_REDS
        self.colors_remaining = _fresh_colors()
        self.just_potted_last_red = False
        self.in_black_ball_decider = False
        self.is100 = False

        self.action_stack = []

    # ---- helpers ----------------------------------------------------------

    def player(self, pid: int) -> PlayerState:
        return self.p1 if pid == 1 else self.p2

    @property
    def current(self) -> PlayerState:
        return self.player(self.current_player)

    # ---- pure computations -----------------------------------------------

    def remaining_points(self) -> int:
        """Points still on the table."""
        colors = sum(k * v for k, v in self.colors_remaining.items())
        if self.red_remaining > 0:
            return self.red_remaining * 8 + colors
        return colors

    def score_diff(self) -> int:
        return self.p1.score - self.p2.score

    def lead(self) -> int:
        return abs(self.score_diff())

    def winning_score(self) -> int:
        return self.total_frames // 2 + 1

    def compute_next_break_player(self) -> int:
        """Who breaks in the next frame (alternates each frame)."""
        finished_frames = len(self.p1.frame_scores)
        if finished_frames % 2 == 0:
            return self.first_break_player
        return 2 if self.first_break_player == 1 else 1

    def winner(self) -> int | None:
        """Return 1/2 if a player has reached the winning frame count, else None."""
        ws = self.winning_score()
        if self.p1.frame_score >= ws:
            return 1
        if self.p2.frame_score >= ws:
            return 2
        return None

    def can_pot(self, value: int) -> bool:
        """Whether the given ball may currently be potted."""
        if self.in_black_ball_decider and value != 7:
            return False
        if value == 1 and self.red_remaining == 0:
            return False
        if (value != 1 and self.red_remaining == 0 and not self.just_potted_last_red
                and value in self.colors_remaining and self.colors_remaining[value] == 0):
            return False
        return True

    # ---- mutating rules ---------------------------------------------------

    def apply_pot(self, value: int) -> PotOutcome:
        """Pot a ball. Returns a :class:`PotOutcome` describing the effect."""
        if not self.can_pot(value):
            return PotOutcome(potted=False, value=value)

        self.action_stack.append((
            "pot", value, self.current_player, self.red_remaining,
            dict(self.colors_remaining), self.just_potted_last_red,
            self.p1.highest_break, self.p2.highest_break, self.is100,
        ))

        p = self.current
        p.score += value
        p.break_score += value

        if value == 1:
            if self.red_remaining > 0:
                self.red_remaining -= 1
                if self.red_remaining == 0:
                    self.just_potted_last_red = True
        elif self.red_remaining == 0 and value in self.colors_remaining:
            if self.just_potted_last_red:
                self.just_potted_last_red = False
            elif self.colors_remaining[value] > 0:
                self.colors_remaining[value] -= 1

        # Display values, captured before any black-ball decider re-adds a ball
        red_after = self.red_remaining
        color_after = self.colors_remaining.get(value)

        decider_triggered = False
        if (not self.in_black_ball_decider and self.red_remaining == 0
                and all(v == 0 for v in self.colors_remaining.values())):
            if self.p1.score == self.p2.score:
                self.in_black_ball_decider = True
                self.colors_remaining[7] = 1
                decider_triggered = True

        century_triggered = p.break_score >= Game.CENTURY_BREAK and not self.is100
        if century_triggered:
            self.is100 = True

        return PotOutcome(
            potted=True,
            decider_triggered=decider_triggered,
            century_triggered=century_triggered,
            value=value,
            red_after=red_after,
            color_after=color_after,
        )

    def apply_manual(self, value: int) -> ManualOutcome:
        """Add a manual score to the current player's score and break."""
        self.action_stack.append((
            "manual", value, self.current_player,
            self.p1.highest_break, self.p2.highest_break,
        ))

        p = self.current
        p.score += value
        p.break_score += value

        century_triggered = p.break_score >= Game.CENTURY_BREAK and not self.is100
        if century_triggered:
            self.is100 = True

        return ManualOutcome(century_triggered=century_triggered, value=value)

    def apply_foul(self, value: int, snap_p1: dict, snap_p2: dict) -> int:
        """Award foul points to the opponent and reset the offender's break.

        ``snap_p1``/``snap_p2`` are break-stat snapshots stored in the undo
        record (used by the window to restore badges). Returns the id of the
        player whose break was cleared (the offender).
        """
        offender = self.current_player
        prev_break = self.current.break_score
        self.action_stack.append(("foul", value, offender, prev_break, snap_p1, snap_p2))

        if offender == 1:
            self.p2.score += value
            self.p1.break_score = 0
        else:
            self.p1.score += value
            self.p2.break_score = 0

        return offender

    def apply_switch(self, snap_p1: dict, snap_p2: dict) -> tuple:
        """Switch the player at the table.

        Returns ``(previous_player, animation_direction)``.
        """
        prev_player = self.current_player
        self.action_stack.append((
            "switch", prev_player, self.p1.break_score, self.p2.break_score, snap_p1, snap_p2,
        ))

        if self.red_remaining == 0:
            self.just_potted_last_red = False

        self.current_player = 2 if prev_player == 1 else 1

        if self.current_player == 1:
            self.p2.break_score = 0
            direction = "right_to_left"
        else:
            self.p1.break_score = 0
            direction = "left_to_right"

        return prev_player, direction

    def apply_remove_red(self) -> bool:
        """Manually remove one red. Returns True if a red was removed."""
        if self.red_remaining > 0:
            self.action_stack.append(("red_minus", self.red_remaining))
            self.red_remaining -= 1
            return True
        return False

    def record_high_breaks(self):
        """Update the current player's frame-high and match-high breaks."""
        p = self.current
        if p.break_score > p.frame_high_break:
            p.frame_high_break = p.break_score
        if p.break_score > p.highest_break:
            p.highest_break = p.break_score

    def end_frame(self) -> bool:
        """Close the current frame, updating the match score.

        Returns True if a frame was awarded (i.e. the frame was not a draw).
        Does not reset the frame; call :meth:`reset_frame` afterwards.
        """
        self.in_black_ball_decider = False
        score_updated = False

        if self.p1.score > self.p2.score:
            self.p1.frame_score += 1
            self.p1.frame_scores.append(self.p1.score)
            self.p2.frame_scores.append(self.p2.score)
            score_updated = True
        elif self.p2.score > self.p1.score:
            self.p2.frame_score += 1
            self.p1.frame_scores.append(self.p1.score)
            self.p2.frame_scores.append(self.p2.score)
            score_updated = True

        self.p1.break_scores.append(self.p1.frame_high_break)
        self.p2.break_scores.append(self.p2.frame_high_break)

        return score_updated

    def reset_frame(self):
        """Reset per-frame state for the next frame."""
        self.p1.frame_high_break = 0
        self.p2.frame_high_break = 0
        self.p1.score = 0
        self.p2.score = 0
        self.p1.break_score = 0
        self.p2.break_score = 0
        self.is100 = False
        self.red_remaining = Game.INITIAL_REDS
        self.colors_remaining = _fresh_colors()
        self.action_stack.clear()

        self.p1.match_high_break_start = self.p1.highest_break
        self.p2.match_high_break_start = self.p2.highest_break

        self.current_frame_break_player = self.compute_next_break_player()
        self.current_player = self.current_frame_break_player

    def rerack(self):
        """Re-rack the current frame without changing the match score."""
        self.in_black_ball_decider = False
        self.just_potted_last_red = False
        self.is100 = False
        self.p1.score = 0
        self.p2.score = 0
        self.p1.break_score = 0
        self.p2.break_score = 0
        self.p1.frame_high_break = 0
        self.p2.frame_high_break = 0
        self.red_remaining = Game.INITIAL_REDS
        self.colors_remaining = _fresh_colors()
        self.action_stack.clear()

        self.p1.highest_break = self.p1.match_high_break_start
        self.p2.highest_break = self.p2.match_high_break_start

        self.current_player = self.current_frame_break_player
