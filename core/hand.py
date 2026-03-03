from __future__ import annotations
from core.card import Card, Color


class Hand:
    """A player's hand of cards."""

    def __init__(self) -> None:
        self._cards: list[Card] = []

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(self, card: Card) -> None:
        self._cards.append(card)

    def remove(self, card: Card) -> bool:
        """Remove first occurrence of card. Returns True if found."""
        try:
            self._cards.remove(card)
            return True
        except ValueError:
            return False

    def remove_at(self, index: int) -> Card:
        return self._cards.pop(index)

    def clear(self) -> None:
        self._cards.clear()

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self):
        return iter(self._cards)

    def __getitem__(self, index: int) -> Card:
        return self._cards[index]

    @property
    def cards(self) -> list[Card]:
        return list(self._cards)

    def count(self) -> int:
        return len(self._cards)

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def sorted_cards(self) -> list[Card]:
        """Ghost first, then black (♠♣) by rank, then red (♥♦) by rank."""
        def _key(c: Card):
            if c.is_ghost:
                return (0, 0, 0)
            color_order = 0 if c.color == Color.BLACK else 1
            return (1, color_order, c.rank)
        return sorted(self._cards, key=_key)
