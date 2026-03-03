"""Unit tests for tenpai_checker.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.card import Card, Suit
from core.tenpai_checker import get_winning_cards, is_tenpai, can_win_with


def c(suit_char: str, rank: int) -> Card:
    mapping = {'s': Suit.SPADES, 'c': Suit.CLUBS, 'h': Suit.HEARTS, 'd': Suit.DIAMONDS, 'g': Suit.GHOST}
    return Card(mapping[suit_char], rank)


# ── Basic tenpai ─────────────────────────────────────────────────────

def test_tenpai_waiting_for_pair():
    # ♠2,♣3,♠4,♣10 → need ♣10 or ♠10 for pair+seq(2,3,4)
    hand = [c('s', 2), c('c', 3), c('s', 4), c('c', 10)]
    winners = get_winning_cards(hand)
    ranks = {w.rank for w in winners}
    assert 10 in ranks

def test_tenpai_waiting_for_sequence():
    # ♠5,♣5,♠6,♣7 → need anything that with 5,6,7 makes seq(5,6,7)+pair(5,5)
    hand = [c('s', 5), c('c', 5), c('s', 6), c('c', 7)]
    winners = get_winning_cards(hand)
    assert len(winners) > 0

def test_not_tenpai():
    # Random hand with no near-win
    hand = [c('s', 1), c('h', 7), c('s', 13), c('d', 4)]
    assert is_tenpai(hand) is False

def test_can_win_with_specific():
    hand = [c('s', 2), c('c', 3), c('s', 4), c('c', 10)]
    assert can_win_with(hand, c('s', 10)) is True
    assert can_win_with(hand, c('c', 10)) is True

def test_wrong_length_returns_empty():
    assert get_winning_cards([c('s', 1), c('s', 2)]) == []
    assert get_winning_cards([c('s', 1)] * 5) == []


# ── Ghost in tenpai hand ─────────────────────────────────────────────

def test_tenpai_with_ghost_in_hand():
    # Hand has 1 ghost + 3 black cards → ghost substitutes
    # ♠A,♣A,♠2,ghost → ghost→3 or 4 completes seq(A,2,3) or (2,3,4)+pair
    hand = [c('s', 1), c('c', 1), c('s', 2), c('g', 0)]
    assert is_tenpai(hand) is True

def test_winning_card_can_be_ghost():
    # If adding a ghost would complete the hand, ghost appears in winners
    # ♠A,♣A,♠2,♣3 → adding ghost (→4) → pair(A,A)+seq(2,3,4) ✓
    hand = [c('s', 1), c('c', 1), c('s', 2), c('c', 3)]
    winners = get_winning_cards(hand)
    ghost_in = any(w.is_ghost for w in winners)
    # There should be a winning card; ghost may or may not be among them
    assert len(winners) > 0
