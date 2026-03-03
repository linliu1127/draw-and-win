"""
Tenpai (聽牌) detection.

A 4-card hand is in tenpai if there exists at least one card that,
when added, produces a winning 5-card hand.
"""
from __future__ import annotations
from core.card import Card, Suit
from core.win_checker import check_win

_ALL_REGULAR: list[Card] = [
    Card(suit, rank)
    for suit in (Suit.SPADES, Suit.CLUBS, Suit.HEARTS, Suit.DIAMONDS)
    for rank in range(1, 14)
]
_GHOST_CARD = Card(Suit.GHOST, 0)


def get_winning_cards(hand: list[Card]) -> list[Card]:
    """
    Given a 4-card hand, return every Card that would complete a win.
    Includes ghost if it would complete the hand.
    """
    if len(hand) != 4:
        return []

    winners: list[Card] = []
    for card in _ALL_REGULAR:
        if check_win(hand + [card]):
            winners.append(card)

    if check_win(hand + [_GHOST_CARD]):
        winners.append(_GHOST_CARD)

    return winners


def is_tenpai(hand: list[Card]) -> bool:
    """Return True if the 4-card hand is in tenpai."""
    return bool(get_winning_cards(hand))


def can_win_with(hand: list[Card], card: Card) -> bool:
    """Return True if adding *card* to the 4-card hand creates a win."""
    if len(hand) != 4:
        return False
    return check_win(hand + [card])
