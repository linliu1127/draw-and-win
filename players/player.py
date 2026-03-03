from __future__ import annotations
from core.hand import Hand
from core.card import Card
from core.tenpai_checker import get_winning_cards, can_win_with


class Player:
    """Base class for all players (human and AI)."""

    def __init__(self, player_id: int, name: str) -> None:
        self.player_id: int       = player_id
        self.name:      str       = name
        self.hand:      Hand      = Hand()
        self.score:     int       = 1000

        self._tenpai_cards: list[Card] = []
        self._in_tenpai:    bool       = False

    # ------------------------------------------------------------------
    # Card management
    # ------------------------------------------------------------------

    def draw_card(self, card: Card) -> None:
        self.hand.add(card)
        self._update_tenpai()

    def discard_card(self, card: Card) -> Card:
        self.hand.remove(card)
        self._update_tenpai()
        return card

    def discard_at(self, index: int) -> Card:
        card = self.hand.remove_at(index)
        self._update_tenpai()
        return card

    def clear_hand(self) -> None:
        self.hand.clear()
        self._tenpai_cards = []
        self._in_tenpai    = False

    # ------------------------------------------------------------------
    # Tenpai
    # ------------------------------------------------------------------

    def _update_tenpai(self) -> None:
        if len(self.hand) == 4:
            self._tenpai_cards = get_winning_cards(self.hand.cards)
            self._in_tenpai    = bool(self._tenpai_cards)
        else:
            self._tenpai_cards = []
            self._in_tenpai    = False

    @property
    def in_tenpai(self) -> bool:
        return self._in_tenpai

    @property
    def tenpai_cards(self) -> list[Card]:
        return self._tenpai_cards

    def can_win_with(self, card: Card) -> bool:
        """True if this card completes the hand."""
        return can_win_with(self.hand.cards, card)

    # ------------------------------------------------------------------
    # Score
    # ------------------------------------------------------------------

    def is_bankrupt(self) -> bool:
        return self.score <= 0

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f'{self.name}(score={self.score})'
