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

    @staticmethod
    def _sort_key(c: Card) -> tuple:
        """Black (♠♣) asc → red (♥♦) asc → ghost last."""
        if c.is_ghost:
            return (2, 0)
        return (0 if c.color == Color.BLACK else 1, c.rank)

    def sort(self) -> None:
        """Sort cards in place."""
        self._cards.sort(key=self._sort_key)

    def sorted_cards(self) -> list[Card]:
        """Return a sorted copy: black asc, red asc, ghost last."""
        return sorted(self._cards, key=self._sort_key)
