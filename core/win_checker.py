"""
Win condition checker for 自摸勝.

A winning 5-card hand must satisfy ALL of:
  1. All 5 cards are the same color (all black or all red).
  2. The 5 ranks contain exactly one pair (two equal ranks) and
     one sequence (three consecutive ranks).

Ghost cards (魃) may substitute for any rank in the required color.
Up to 2 ghosts can appear in a hand.
"""
from __future__ import annotations
from core.card import Card, Color


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def check_win(cards: list[Card]) -> bool:
    """Return True if the 5-card hand is a winning hand."""
    if len(cards) != 5:
        return False

    ghosts  = [c for c in cards if c.is_ghost]
    regular = [c for c in cards if not c.is_ghost]
    n_ghost = len(ghosts)

    for target_color in (Color.BLACK, Color.RED):
        # All regular (non-ghost) cards must be the target color.
        if not all(c.color == target_color for c in regular):
            continue
        reg_ranks = [c.rank for c in regular]
        if _check_ranks(reg_ranks, n_ghost):
            return True

    return False


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _check_ranks(reg_ranks: list[int], n_ghost: int) -> bool:
    """Try all ghost substitutions and see if any arrangement wins."""
    if n_ghost == 0:
        return _is_valid_hand(reg_ranks)
    if n_ghost == 1:
        for r in range(1, 14):
            if _is_valid_hand(reg_ranks + [r]):
                return True
        return False
    if n_ghost == 2:
        for r1 in range(1, 14):
            for r2 in range(1, 14):
                if _is_valid_hand(reg_ranks + [r1, r2]):
                    return True
        return False
    return False


def _is_valid_hand(ranks: list[int]) -> bool:
    """Check whether 5 ranks form (one pair) + (one 3-card sequence)."""
    if len(ranks) != 5:
        return False
    for i in range(5):
        for j in range(i + 1, 5):
            if ranks[i] == ranks[j]:
                remaining = [ranks[k] for k in range(5) if k != i and k != j]
                if _is_sequence(remaining):
                    return True
    return False


def _is_sequence(ranks: list[int]) -> bool:
    """Return True if the 3 ranks are three consecutive integers."""
    if len(ranks) != 3:
        return False
    s = sorted(ranks)
    return s[1] == s[0] + 1 and s[2] == s[1] + 1
