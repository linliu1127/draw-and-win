from __future__ import annotations
import random
from core.card import Card, Suit


class Deck:
    """54-card deck: 52 regular + 2 ghost (魃)."""

    def __init__(self) -> None:
        self._cards: list[Card] = []
        self._discard: list[Card] = []
        self._build()

    # ------------------------------------------------------------------
    # Building
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._cards = []
        for suit in (Suit.SPADES, Suit.CLUBS, Suit.HEARTS, Suit.DIAMONDS):
            for rank in range(1, 14):
                self._cards.append(Card(suit, rank))
        self._cards.append(Card(Suit.GHOST, 0))
        self._cards.append(Card(Suit.GHOST, 0))
        self._discard = []

    def reset(self) -> None:
        """Rebuild and shuffle the deck."""
        self._build()
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self) -> Card | None:
        """Draw the top card from the deck. Returns None if empty."""
        return self._cards.pop() if self._cards else None

    def is_empty(self) -> bool:
        return len(self._cards) == 0

    @property
    def remaining(self) -> int:
        return len(self._cards)

    # ------------------------------------------------------------------
    # Discard pile
    # ------------------------------------------------------------------

    def discard(self, card: Card) -> None:
        self._discard.append(card)

    def peek_discard(self) -> Card | None:
        """Look at the top discard without removing it."""
        return self._discard[-1] if self._discard else None

    def pick_discard(self) -> Card | None:
        """Remove and return the top discard."""
        return self._discard.pop() if self._discard else None

    @property
    def discard_pile(self) -> list[Card]:
        return list(self._discard)

    @property
    def discard_count(self) -> int:
        return len(self._discard)
