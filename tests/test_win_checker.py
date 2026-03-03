"""Unit tests for win_checker.py"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.card import Card, Suit
from core.win_checker import check_win, _is_sequence, _is_valid_hand


# ── helpers ─────────────────────────────────────────────────────────

def c(suit_char: str, rank: int) -> Card:
    """Quick card factory: 's'=spades, 'c'=clubs, 'h'=hearts, 'd'=diamonds, 'g'=ghost."""
    mapping = {'s': Suit.SPADES, 'c': Suit.CLUBS, 'h': Suit.HEARTS, 'd': Suit.DIAMONDS, 'g': Suit.GHOST}
    return Card(mapping[suit_char], rank)


# ── _is_sequence ─────────────────────────────────────────────────────

def test_sequence_basic():
    assert _is_sequence([1, 2, 3]) is True
    assert _is_sequence([3, 2, 1]) is True
    assert _is_sequence([11, 12, 13]) is True

def test_sequence_fail():
    assert _is_sequence([1, 2, 4]) is False
    assert _is_sequence([1, 1, 2]) is False


# ── _is_valid_hand ───────────────────────────────────────────────────

def test_valid_hand_pair_plus_seq():
    # 10,10 + 2,3,4
    assert _is_valid_hand([10, 10, 2, 3, 4]) is True
    assert _is_valid_hand([2, 3, 4, 10, 10]) is True

def test_valid_hand_seq_at_start():
    # A,A + 5,6,7
    assert _is_valid_hand([1, 1, 5, 6, 7]) is True

def test_valid_hand_fail_no_pair():
    # 1,2,3,4,5 – sequence only, no pair
    assert _is_valid_hand([1, 2, 3, 4, 5]) is False

def test_valid_hand_fail_all_pairs():
    # 2,2,3,3,4 – two pairs + one extra, no valid pair+seq split
    assert _is_valid_hand([2, 2, 3, 3, 4]) is False

def test_valid_hand_three_of_a_kind():
    # 5,5,5,6,7 – triple: can be treated as pair(5,5)+seq(5,6,7) ✓
    assert _is_valid_hand([5, 5, 5, 6, 7]) is True


# ── check_win: regular hands ─────────────────────────────────────────

def test_win_all_black():
    hand = [c('s', 2), c('c', 3), c('s', 4), c('c', 10), c('s', 10)]
    assert check_win(hand) is True

def test_win_all_red():
    hand = [c('h', 1), c('d', 1), c('h', 5), c('d', 6), c('h', 7)]
    assert check_win(hand) is True

def test_fail_mixed_colors():
    hand = [c('s', 2), c('c', 3), c('s', 4), c('h', 10), c('s', 10)]
    assert check_win(hand) is False

def test_fail_wrong_structure():
    # All black, but ranks don't form pair+seq
    hand = [c('s', 1), c('c', 3), c('s', 5), c('c', 7), c('s', 9)]
    assert check_win(hand) is False


# ── check_win: ghost card ────────────────────────────────────────────

def test_win_one_ghost_as_pair():
    # Ghost completes pair: ♠2, ♣2, ghost, ♠5, ♣6, ♠7 → wait, 5 cards
    # Ghost = ♠3; hand: ♠2,♣3,ghost→4,♠4,♣4 → 4,4 pair + 2,3,4 seq ✓
    # Simpler: ♠2,♣3,♠4,♣5,ghost  ghost→5 → pair(5,5)+seq(2,3,4) ✓
    hand = [c('s', 2), c('c', 3), c('s', 4), c('c', 5), c('g', 0)]
    assert check_win(hand) is True

def test_win_two_ghosts():
    # Two ghosts; regular: ♠A,♣A,♠2 → ghosts→3,4 → pair(A,A)+seq(2,3,4) ✓
    hand = [c('s', 1), c('c', 1), c('s', 2), c('g', 0), c('g', 0)]
    assert check_win(hand) is True

def test_ghost_does_not_break_color():
    # 3 red cards + 1 black + 1 ghost → mixed color regular → fail
    hand = [c('h', 2), c('d', 3), c('h', 4), c('s', 5), c('g', 0)]
    assert check_win(hand) is False

def test_win_ghost_only_completes_color():
    # 4 black cards + 1 ghost → ghost provides the rank → should win
    hand = [c('s', 7), c('c', 7), c('s', 8), c('c', 9), c('g', 0)]
    assert check_win(hand) is True

def test_wrong_length():
    assert check_win([]) is False
    assert check_win([c('s', 1)] * 4) is False
    assert check_win([c('s', 1)] * 6) is False
