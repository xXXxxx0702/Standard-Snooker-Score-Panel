"""Unit tests for the pure scoring logic in core.game_state.

These run without Qt; they exercise the scoring rules that used to be buried
inside the main window.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.game_state import GameState  # noqa: E402


def new_game(total_frames=3, first_break=1):
    g = GameState()
    g.total_frames = total_frames
    g.first_break_player = first_break
    g.current_frame_break_player = first_break
    g.current_player = first_break
    return g


def clear_reds(g):
    """Pot all 15 reds (with no colours between) for the current player."""
    for _ in range(15):
        g.apply_pot(1)


# ---------------------------------------------------------------------------
# Basic scoring
# ---------------------------------------------------------------------------

def test_initial_remaining_is_147():
    g = new_game()
    assert g.remaining_points() == 147


def test_pot_red_adds_score_and_break():
    g = new_game()
    out = g.apply_pot(1)
    assert out.potted
    assert g.p1.score == 1
    assert g.p1.break_score == 1
    assert g.red_remaining == 14
    assert out.red_after == 14


def test_pot_color_during_reds_does_not_decrement_colour():
    g = new_game()
    g.apply_pot(1)          # red
    out = g.apply_pot(7)    # black after red
    assert out.potted
    assert g.p1.score == 8
    assert g.colors_remaining[7] == 1  # colours respotted while reds remain
    # reds still on the table -> window leaves the colour label untouched
    assert out.red_after != 0


def test_cannot_pot_red_when_none_left():
    g = new_game()
    clear_reds(g)
    assert g.red_remaining == 0
    out = g.apply_pot(1)
    assert not out.potted
    assert g.p1.score == 15  # unchanged


def test_remaining_points_decreases_as_reds_potted():
    g = new_game()
    g.apply_pot(1)
    # 14 reds left -> 14*8 + (2+3+4+5+6+7) = 112 + 27 = 139
    assert g.remaining_points() == 139


# ---------------------------------------------------------------------------
# Manual score and fouls
# ---------------------------------------------------------------------------

def test_manual_score():
    g = new_game()
    out = g.apply_manual(4)
    assert g.p1.score == 4
    assert g.p1.break_score == 4
    assert not out.century_triggered


def test_foul_awards_opponent_and_resets_break():
    g = new_game()
    g.apply_pot(1)
    g.apply_pot(7)  # break now 8
    offender = g.apply_foul(4, {}, {})
    assert offender == 1
    assert g.p1.break_score == 0
    assert g.p2.score == 4
    # offender's own score is untouched by their foul
    assert g.p1.score == 8


# ---------------------------------------------------------------------------
# High break tracking and century
# ---------------------------------------------------------------------------

def test_record_high_breaks():
    g = new_game()
    for _ in range(5):
        g.apply_pot(1)
        g.apply_pot(7)
        g.record_high_breaks()
    # 5 * (1 + 7) = 40
    assert g.p1.break_score == 40
    assert g.p1.frame_high_break == 40
    assert g.p1.highest_break == 40


def test_century_triggers_once():
    g = new_game()
    out = g.apply_manual(100)
    assert out.century_triggered
    assert g.is100
    out2 = g.apply_manual(7)
    assert not out2.century_triggered  # only once per frame


# ---------------------------------------------------------------------------
# Black-ball decider
# ---------------------------------------------------------------------------

def test_black_ball_decider_triggers_on_level_scores():
    g = new_game()
    # Only the black remains; potting it makes the scores level (43 + 7 == 50).
    g.p1.score = 43
    g.p2.score = 50
    g.red_remaining = 0
    g.colors_remaining = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1}
    g.just_potted_last_red = False
    out = g.apply_pot(7)  # pot final black, scores become level
    assert g.p1.score == 50 and g.p2.score == 50
    assert out.decider_triggered
    assert g.in_black_ball_decider
    assert g.colors_remaining[7] == 1  # black respotted
    # display value captured before respot
    assert out.color_after == 0


def test_no_decider_when_scores_not_level():
    g = new_game()
    g.p1.score = 60
    g.p2.score = 50
    g.red_remaining = 0
    g.colors_remaining = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1}
    out = g.apply_pot(7)  # p1 -> 67, never level
    assert not out.decider_triggered
    assert not g.in_black_ball_decider


def test_in_decider_only_black_pottable():
    g = new_game()
    g.in_black_ball_decider = True
    assert not g.can_pot(1)
    assert not g.can_pot(5)
    assert g.can_pot(7)


# ---------------------------------------------------------------------------
# Frame end / winner / next breaker
# ---------------------------------------------------------------------------

def test_end_frame_awards_higher_scorer():
    g = new_game()
    g.p1.score = 70
    g.p2.score = 40
    updated = g.end_frame()
    assert updated
    assert g.p1.frame_score == 1
    assert g.p2.frame_score == 0
    assert g.p1.frame_scores == [70]
    assert g.p2.frame_scores == [40]


def test_end_frame_draw_awards_nobody():
    g = new_game()
    g.p1.score = 50
    g.p2.score = 50
    updated = g.end_frame()
    assert not updated
    assert g.p1.frame_score == 0
    assert g.p2.frame_score == 0


def test_winner_at_best_of_three():
    g = new_game(total_frames=3)
    assert g.winning_score() == 2
    g.p1.frame_score = 2
    assert g.winner() == 1
    g.p1.frame_score = 1
    g.p2.frame_score = 2
    assert g.winner() == 2
    g.p2.frame_score = 1
    assert g.winner() is None


def test_next_break_player_alternates():
    g = new_game(first_break=1)
    assert g.compute_next_break_player() == 1  # no frames finished
    g.p1.frame_scores.append(70)  # 1 frame finished
    assert g.compute_next_break_player() == 2
    g.p1.frame_scores.append(70)  # 2 frames finished
    assert g.compute_next_break_player() == 1


def test_reset_frame_clears_state_and_sets_breaker():
    g = new_game(first_break=1)
    g.p1.score = 70
    g.p2.score = 40
    g.p1.highest_break = 70
    g.end_frame()
    g.reset_frame()
    assert g.p1.score == 0 and g.p2.score == 0
    assert g.red_remaining == 15
    assert g.colors_remaining == {2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}
    assert g.p1.match_high_break_start == 70
    # one frame finished -> next breaker is player 2
    assert g.current_player == 2


# ---------------------------------------------------------------------------
# Switch / rerack / remove red
# ---------------------------------------------------------------------------

def test_switch_player_resets_incoming_break():
    g = new_game()
    g.apply_pot(1)  # p1 break = 1
    prev, direction = g.apply_switch({}, {})
    assert prev == 1
    assert g.current_player == 2
    assert direction == "left_to_right"
    # incoming player's break starts at 0
    assert g.p2.break_score == 0


def test_rerack_restores_match_high_break_start():
    g = new_game()
    g.p1.highest_break = 80
    g.p1.match_high_break_start = 30
    g.p1.score = 80
    g.rerack()
    assert g.p1.score == 0
    assert g.p1.highest_break == 30
    assert g.red_remaining == 15


def test_remove_red():
    g = new_game()
    assert g.apply_remove_red()
    assert g.red_remaining == 14
    g.red_remaining = 0
    assert not g.apply_remove_red()


# ---------------------------------------------------------------------------
# Undo record formats (consumed by the window-side undo)
# ---------------------------------------------------------------------------

def test_pot_pushes_undo_record():
    g = new_game()
    g.apply_pot(1)
    rec = g.action_stack[-1]
    assert rec[0] == "pot"
    assert rec[1] == 1          # value
    assert rec[2] == 1          # player
    assert rec[3] == 15         # red_remaining before pot


def test_foul_and_switch_records_carry_snapshots():
    g = new_game()
    g.apply_foul(4, {7: 2}, {})
    assert g.action_stack[-1][0] == "foul"
    assert g.action_stack[-1][4] == {7: 2}
    g.apply_switch({1: 1}, {})
    assert g.action_stack[-1][0] == "switch"
    assert g.action_stack[-1][4] == {1: 1}


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
