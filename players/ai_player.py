from __future__ import annotations
import random
from collections import Counter

from players.player import Player
from core.card import Card
from core.tenpai_checker import get_winning_cards, can_win_with
from core.win_checker import check_win

# Probability of declaring Ron depending on how many ghosts (魃) are in hand.
# More ghosts → better tsumo potential → less incentive to Ron.
_RON_PROB_BY_GHOSTS = {0: 1.0, 1: 0.30, 2: 0.10}


class AIPlayer(Player):
    """Computer-controlled player with a simple heuristic strategy."""

    def __init__(self, player_id: int, name: str) -> None:
        super().__init__(player_id, name)

    # ------------------------------------------------------------------
    # Decision methods  (called by game.py after AI_DELAY)
    # ------------------------------------------------------------------

    def should_pick_discard(self, discard_card: Card) -> bool:
        """Return True if picking the discard improves the hand."""
        if discard_card is None:
            return False

        current_score = self._score_hand(self.hand.cards)

        # Simulate picking + discarding our worst card
        trial_hand  = self.hand.cards + [discard_card]
        best_discard = self._best_discard_from(trial_hand)
        if best_discard is None:
            return False

        new_hand  = [c for c in trial_hand if c is not best_discard]
        new_score = self._score_hand(new_hand)
        return new_score > current_score

    def should_declare_ron(self, card: Card) -> bool:
        """RON if the card completes the hand, but ghost holders prefer to wait for tsumo."""
        if not self.can_win_with(card):
            return False
        ghost_count = sum(1 for c in self.hand.cards if c.is_ghost)
        prob = _RON_PROB_BY_GHOSTS.get(ghost_count, 0.10)
        return random.random() < prob

    def should_declare_tsumo(self) -> bool:
        """Always declare tsumo when possible."""
        from core.win_checker import check_win
        return check_win(self.hand.cards)

    def choose_discard(self) -> Card:
        """Return the card that, when removed, maximises the hand score."""
        cards = self.hand.cards
        if not cards:
            return None
        best_card  = None
        best_score = -1
        for card in cards:
            remaining = [c for c in cards if c is not card]
            s = self._score_hand(remaining)
            if s > best_score:
                best_score = s
                best_card  = card
        return best_card

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _best_discard_from(self, five_cards: list[Card]) -> Card | None:
        best_card  = None
        best_score = -1
        for card in five_cards:
            remaining = [c for c in five_cards if c is not card]
            s = self._score_hand(remaining)
            if s > best_score:
                best_score = s
                best_card  = card
        return best_card

    def _score_hand(self, hand4: list[Card]) -> int:
        """Heuristic score for a 4-card hand (higher = closer to winning)."""
        if len(hand4) != 4:
            return 0

        # Tenpai: base 100 + 2 per winning card
        winners = get_winning_cards(hand4)
        if winners:
            return 100 + len(winners) * 2

        ghosts  = [c for c in hand4 if c.is_ghost]
        regular = [c for c in hand4 if not c.is_ghost]
        score   = len(ghosts) * 15  # ghost is versatile

        # Pairs
        rank_cnt = Counter(c.rank for c in regular)
        score += sum(10 for cnt in rank_cnt.values() if cnt >= 2)

        # Near-sequences
        ranks = sorted(c.rank for c in regular)
        for i in range(len(ranks) - 1):
            diff = ranks[i + 1] - ranks[i]
            if diff == 1:
                score += 5
            elif diff == 2:
                score += 2

        return score
