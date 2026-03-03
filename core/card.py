from __future__ import annotations
from enum import Enum


class Suit(Enum):
    SPADES   = 'spades'
    CLUBS    = 'clubs'
    HEARTS   = 'hearts'
    DIAMONDS = 'diamonds'
    GHOST    = 'ghost'


class Color(Enum):
    BLACK = 'black'
    RED   = 'red'
    GHOST = 'ghost'


SUIT_COLOR: dict[Suit, Color] = {
    Suit.SPADES:   Color.BLACK,
    Suit.CLUBS:    Color.BLACK,
    Suit.HEARTS:   Color.RED,
    Suit.DIAMONDS: Color.RED,
    Suit.GHOST:    Color.GHOST,
}

SUIT_SYMBOL: dict[Suit, str] = {
    Suit.SPADES:   '♠',
    Suit.CLUBS:    '♣',
    Suit.HEARTS:   '♥',
    Suit.DIAMONDS: '♦',
    Suit.GHOST:    '魃',
}

RANK_SYMBOL: dict[int, str] = {
    0: '魃',
    1: 'A', 2: '2', 3: '3', 4: '4', 5: '5',
    6: '6', 7: '7', 8: '8', 9: '9', 10: '10',
    11: 'J', 12: 'Q', 13: 'K',
}

BLACK_SUITS = {Suit.SPADES, Suit.CLUBS}
RED_SUITS   = {Suit.HEARTS, Suit.DIAMONDS}


class Card:
    """Represents a single playing card."""

    __slots__ = ('suit', 'rank', 'color')

    def __init__(self, suit: Suit, rank: int) -> None:
        """
        suit : Suit enum value
        rank : 1-13 for regular cards; 0 for ghost (魃)
        """
        self.suit  = suit
        self.rank  = rank
        self.color = SUIT_COLOR[suit]

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_ghost(self) -> bool:
        return self.suit == Suit.GHOST

    @property
    def suit_symbol(self) -> str:
        return SUIT_SYMBOL[self.suit]

    @property
    def rank_symbol(self) -> str:
        return RANK_SYMBOL.get(self.rank, '?')

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        if self.is_ghost:
            return '魃'
        return f'{self.rank_symbol}{self.suit_symbol}'

    def __str__(self) -> str:
        return self.__repr__()

    # ------------------------------------------------------------------
    # Equality / hashing  (identity = suit + rank)
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.suit, self.rank))
