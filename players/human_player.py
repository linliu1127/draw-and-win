from __future__ import annotations
from players.player import Player


class HumanPlayer(Player):
    """Human-controlled player.  GUI drives actions via game action methods."""

    def __init__(self, player_id: int = 0, name: str = '玩家') -> None:
        super().__init__(player_id, name)
        self.selected_index: int = -1   # index of highlighted card in hand

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def select_card(self, index: int) -> None:
        """Toggle selection on a card by index."""
        if self.selected_index == index:
            self.selected_index = -1
        else:
            self.selected_index = index

    def get_selected_card(self):
        """Return currently selected Card, or None."""
        if 0 <= self.selected_index < len(self.hand):
            return self.hand[self.selected_index]
        return None

    def clear_selection(self) -> None:
        self.selected_index = -1
