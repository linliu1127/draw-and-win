"""
Main game logic / state machine for 自摸勝.

State transitions:
  INIT → DEALING → DRAWING → PLAYER_DRAWN
    ├─ tsumo  → WIN_TSUMO → SCORING → ROUND_END → DEALING | GAME_OVER
    └─ discard → DISCARDING → RON_CHECK
           ├─ RON_WINDOW (human) → WIN_RON → SCORING → …
           ├─ WIN_RON  (AI)      → SCORING → …
           └─ (no RON)           → DRAWING (next player)
"""
from __future__ import annotations

from constants import (
    STARTING_SCORE, TSUMO_WIN_AMOUNT, RON_WIN_AMOUNT,
    AI_DRAW_DELAY, AI_DISCARD_DELAY, AI_RON_DELAY, RON_WINDOW_TIME,
    SEAT_HUMAN,
)
from core.deck import Deck
from core.card import Card
from core.win_checker import check_win
from game.game_state import GameState
from players.player import Player
from players.human_player import HumanPlayer
from players.ai_player import AIPlayer


NUM_PLAYERS  = 4
INITIAL_HAND = 4        # cards dealt to each player before first draw


class Game:
    """Central state machine.  GUI calls action methods; calls update(dt) per frame."""

    def __init__(self) -> None:
        # Players: index 0 = human, 1–3 = AI
        self.players: list[Player] = [
            HumanPlayer(0, '玩家'),
            AIPlayer(1, 'AI 右'),
            AIPlayer(2, 'AI 上'),
            AIPlayer(3, 'AI 左'),
        ]
        self.deck  = Deck()
        self.state = GameState.INIT

        # Round metadata
        self.round_number:       int  = 0
        self.first_player_index: int  = SEAT_HUMAN
        self.current_player_index: int = SEAT_HUMAN

        # Win info
        self.winner:       Player | None = None
        self.win_type:     str    | None = None   # 'tsumo' | 'ron' | 'draw'
        self.ron_discarder: Player | None = None  # who discarded the winning card

        # Discard tracking
        self.last_discard:        Card   | None = None
        self.last_discard_player: Player | None = None

        # RON window
        self.human_can_ron:   bool = False
        self.ron_window_ms:   int  = 0   # countdown
        self._ai_ron_queue:   list[int] = []   # AI seat indices that want RON

        # AI action timer
        self._ai_timer_ms: int = 0
        self._ai_phase:    str = ''   # 'draw' | 'discard' | 'ron_check'

        # Log messages (newest first, max 8)
        self.log: list[str] = []

        # Whether the deck ran empty → draw round
        self.is_draw_round: bool = False

    # ==================================================================
    # Main update – called once per frame with delta-time in ms
    # ==================================================================

    def update(self, dt: int) -> None:
        s = self.state

        if s == GameState.INIT:
            self._do_init()

        elif s == GameState.DEALING:
            self._do_dealing()

        elif s == GameState.DRAWING:
            self._update_drawing(dt)

        elif s == GameState.PLAYER_DRAWN:
            self._update_player_drawn(dt)

        elif s == GameState.DISCARDING:
            self._do_discarding()

        elif s == GameState.RON_CHECK:
            self._do_ron_check()

        elif s == GameState.RON_WINDOW:
            self._update_ron_window(dt)

        elif s == GameState.WIN_TSUMO:
            self._do_scoring()

        elif s == GameState.WIN_RON:
            self._do_scoring()

        elif s == GameState.SCORING:
            self._set_state(GameState.ROUND_END)

        # ROUND_END and GAME_OVER wait for human input (handled by action methods)

    # ==================================================================
    # Human action methods (called by GUI)
    # ==================================================================

    def human_draw(self) -> bool:
        """Human draws from the deck.  Valid only in DRAWING state, human's turn."""
        if self.state != GameState.DRAWING or self.current_player_index != SEAT_HUMAN:
            return False
        card = self.deck.draw()
        if card is None:
            self._end_draw_round()
            return False
        human = self.players[SEAT_HUMAN]
        human.draw_card(card)
        self._log(f'{human.name} 摸牌')
        self._set_state(GameState.PLAYER_DRAWN)
        return True

    def human_pick_discard(self) -> bool:
        """Human picks the top discard.  Valid only in DRAWING state, human's turn."""
        if self.state != GameState.DRAWING or self.current_player_index != SEAT_HUMAN:
            return False
        card = self.deck.peek_discard()
        if card is None:
            return False
        self.deck.pick_discard()
        self.last_discard        = None
        self.last_discard_player = None
        human = self.players[SEAT_HUMAN]
        human.draw_card(card)
        self._log(f'{human.name} 撿牌 {card}')
        self._set_state(GameState.PLAYER_DRAWN)
        return True

    def human_discard(self, card_index: int) -> bool:
        """Human discards the card at hand index.  Valid in PLAYER_DRAWN state."""
        if self.state != GameState.PLAYER_DRAWN or self.current_player_index != SEAT_HUMAN:
            return False
        human = self.players[SEAT_HUMAN]
        if not (0 <= card_index < len(human.hand)):
            return False
        card = human.discard_at(card_index)
        human.clear_selection()
        self._process_discard(human, card)
        return True

    def human_declare_tsumo(self) -> bool:
        """Human declares tsumo win.  Valid in PLAYER_DRAWN state."""
        if self.state != GameState.PLAYER_DRAWN or self.current_player_index != SEAT_HUMAN:
            return False
        human = self.players[SEAT_HUMAN]
        if not check_win(human.hand.cards):
            return False
        self.winner   = human
        self.win_type = 'tsumo'
        self._log(f'{human.name} 自摸！')
        self._set_state(GameState.WIN_TSUMO)
        return True

    def human_declare_ron(self) -> bool:
        """Human claims RON.  Valid in RON_WINDOW state."""
        if self.state != GameState.RON_WINDOW or not self.human_can_ron:
            return False
        human = self.players[SEAT_HUMAN]
        self.winner       = human
        self.win_type     = 'ron'
        self.ron_discarder = self.last_discard_player
        self._log(f'{human.name} 胡牌！（搶 {self.ron_discarder.name} 的牌）')
        self._set_state(GameState.WIN_RON)
        return True

    def human_pass_ron(self) -> bool:
        """Human passes RON opportunity.  Valid in RON_WINDOW state."""
        if self.state != GameState.RON_WINDOW:
            return False
        self.human_can_ron = False
        self._check_ai_ron()
        return True

    def human_next_round(self) -> bool:
        """Start next round.  Valid in ROUND_END state."""
        if self.state != GameState.ROUND_END:
            return False
        # Check for bankruptcy
        bankrupt = [p for p in self.players if p.is_bankrupt()]
        if bankrupt:
            self._set_state(GameState.GAME_OVER)
        else:
            self._set_state(GameState.DEALING)
        return True

    def human_quit(self) -> None:
        """Force game over."""
        self._set_state(GameState.GAME_OVER)

    # ==================================================================
    # State handlers
    # ==================================================================

    def _do_init(self) -> None:
        self.round_number       = 0
        self.first_player_index = SEAT_HUMAN
        for p in self.players:
            p.score = STARTING_SCORE
        self._set_state(GameState.DEALING)

    def _do_dealing(self) -> None:
        self.round_number += 1
        self.deck.reset()
        self.last_discard        = None
        self.last_discard_player = None
        self.winner              = None
        self.win_type            = None
        self.ron_discarder       = None
        self.human_can_ron       = False
        self.is_draw_round       = False
        self._ai_timer_ms        = 0
        self._ai_phase           = ''
        self._ai_ron_queue       = []

        for p in self.players:
            p.clear_hand()

        # Deal INITIAL_HAND cards to each player
        for _ in range(INITIAL_HAND):
            for p in self.players:
                card = self.deck.draw()
                if card:
                    p.draw_card(card)

        self.current_player_index = self.first_player_index
        self._log(f'第 {self.round_number} 局開始')
        self._set_state(GameState.DRAWING)

    # ------------------------------------------------------------------
    # DRAWING state
    # ------------------------------------------------------------------

    def _update_drawing(self, dt: int) -> None:
        cp = self.current_player_index
        if cp == SEAT_HUMAN:
            return   # Wait for human_draw() / human_pick_discard()

        # AI turn
        if self._ai_phase != 'draw':
            self._ai_phase    = 'draw'
            self._ai_timer_ms = AI_DRAW_DELAY

        self._ai_timer_ms -= dt
        if self._ai_timer_ms > 0:
            return

        # Deck empty check
        discard_top = self.deck.peek_discard()
        ai: AIPlayer = self.players[cp]  # type: ignore

        picked = False
        if discard_top and ai.should_pick_discard(discard_top):
            self.deck.pick_discard()
            self.last_discard        = None
            self.last_discard_player = None
            ai.draw_card(discard_top)
            self._log(f'{ai.name} 撿牌 {discard_top}')
            picked = True

        if not picked:
            card = self.deck.draw()
            if card is None:
                self._end_draw_round()
                return
            ai.draw_card(card)
            self._log(f'{ai.name} 摸牌')

        self._ai_phase = ''
        self._set_state(GameState.PLAYER_DRAWN)

    # ------------------------------------------------------------------
    # PLAYER_DRAWN state
    # ------------------------------------------------------------------

    def _update_player_drawn(self, dt: int) -> None:
        cp = self.current_player_index
        if cp == SEAT_HUMAN:
            return   # Wait for human_discard() / human_declare_tsumo()

        # AI turn
        ai: AIPlayer = self.players[cp]  # type: ignore

        if self._ai_phase != 'discard':
            self._ai_phase    = 'discard'
            self._ai_timer_ms = AI_DISCARD_DELAY

        self._ai_timer_ms -= dt
        if self._ai_timer_ms > 0:
            return

        # Tsumo?
        if check_win(ai.hand.cards):
            self.winner   = ai
            self.win_type = 'tsumo'
            self._log(f'{ai.name} 自摸！')
            self._ai_phase = ''
            self._set_state(GameState.WIN_TSUMO)
            return

        # Discard
        card = ai.choose_discard()
        if card is None:
            card = ai.hand[0]
        ai.discard_card(card)
        self._ai_phase = ''
        self._process_discard(ai, card)

    # ------------------------------------------------------------------
    # DISCARDING  (instant)
    # ------------------------------------------------------------------

    def _do_discarding(self) -> None:
        self._set_state(GameState.RON_CHECK)

    def _process_discard(self, player: Player, card: Card) -> None:
        self.deck.discard(card)
        self.last_discard        = card
        self.last_discard_player = player
        self._log(f'{player.name} 棄牌 {card}')
        self._set_state(GameState.DISCARDING)

    # ------------------------------------------------------------------
    # RON_CHECK  (instant)
    # ------------------------------------------------------------------

    def _do_ron_check(self) -> None:
        card = self.last_discard
        if card is None:
            self._advance_turn()
            return

        # Collect AI players who want to RON (in turn order after discarder)
        discarder_idx = self.players.index(self.last_discard_player)
        order = [(discarder_idx + i) % NUM_PLAYERS for i in range(1, NUM_PLAYERS)]

        self._ai_ron_queue = []
        for idx in order:
            if idx == SEAT_HUMAN:
                continue
            p: AIPlayer = self.players[idx]  # type: ignore
            if p.can_win_with(card) and p.should_declare_ron(card):
                self._ai_ron_queue.append(idx)

        # Check human
        human = self.players[SEAT_HUMAN]
        if human.can_win_with(card):
            self.human_can_ron = True
            self.ron_window_ms = RON_WINDOW_TIME
            self._ai_timer_ms  = AI_RON_DELAY
            self._ai_phase     = 'ron_check'
            self._set_state(GameState.RON_WINDOW)
            return

        # No human RON → check AIs
        self._check_ai_ron()

    # ------------------------------------------------------------------
    # RON_WINDOW
    # ------------------------------------------------------------------

    def _update_ron_window(self, dt: int) -> None:
        self.ron_window_ms -= dt
        if self.ron_window_ms <= 0:
            self.human_can_ron = False
            self._check_ai_ron()

    def _check_ai_ron(self) -> None:
        if self._ai_ron_queue:
            idx = self._ai_ron_queue[0]
            ai  = self.players[idx]
            self.winner       = ai
            self.win_type     = 'ron'
            self.ron_discarder = self.last_discard_player
            self._log(f'{ai.name} 胡牌！（搶 {self.ron_discarder.name} 的牌）')
            self._set_state(GameState.WIN_RON)
        else:
            self._advance_turn()

    # ------------------------------------------------------------------
    # SCORING
    # ------------------------------------------------------------------

    def _do_scoring(self) -> None:
        if self.win_type == 'tsumo':
            winner = self.winner
            for p in self.players:
                if p is not winner:
                    transfer = min(p.score, TSUMO_WIN_AMOUNT)
                    p.score     -= transfer
                    winner.score += transfer
            self._log(
                f'{winner.name} 自摸勝！各收 {TSUMO_WIN_AMOUNT} 點'
            )
        elif self.win_type == 'ron':
            winner    = self.winner
            discarder = self.ron_discarder
            transfer  = min(discarder.score, RON_WIN_AMOUNT)
            discarder.score -= transfer
            winner.score    += transfer
            self._log(
                f'{winner.name} 胡牌！向 {discarder.name} 收 {RON_WIN_AMOUNT} 點'
            )

        # Record winner as first player next round
        if self.winner:
            self.first_player_index = self.winner.player_id

        self._set_state(GameState.ROUND_END)

    def _end_draw_round(self) -> None:
        self.winner       = None
        self.win_type     = 'draw'
        self.is_draw_round = True
        self._log('牌庫抽完，本局流局')
        self._set_state(GameState.ROUND_END)

    # ------------------------------------------------------------------
    # Turn management
    # ------------------------------------------------------------------

    def _advance_turn(self) -> None:
        self.current_player_index = (
            (self.current_player_index + 1) % NUM_PLAYERS
        )
        self._ai_phase    = ''
        self._ai_timer_ms = 0
        self._set_state(GameState.DRAWING)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_state(self, new_state: GameState) -> None:
        self.state = new_state

    def _log(self, msg: str) -> None:
        self.log.insert(0, msg)
        if len(self.log) > 8:
            self.log.pop()

    # ------------------------------------------------------------------
    # Read-only helpers for GUI
    # ------------------------------------------------------------------

    @property
    def human(self) -> HumanPlayer:
        return self.players[SEAT_HUMAN]  # type: ignore

    @property
    def is_human_turn(self) -> bool:
        return self.current_player_index == SEAT_HUMAN

    @property
    def can_human_pick(self) -> bool:
        return (
            self.state == GameState.DRAWING
            and self.is_human_turn
            and self.last_discard is not None
        )

    @property
    def can_human_draw(self) -> bool:
        return (
            self.state == GameState.DRAWING
            and self.is_human_turn
            and not self.deck.is_empty()
        )

    @property
    def can_human_discard(self) -> bool:
        return (
            self.state == GameState.PLAYER_DRAWN
            and self.is_human_turn
            and self.human.selected_index >= 0
        )

    @property
    def can_human_tsumo(self) -> bool:
        return (
            self.state == GameState.PLAYER_DRAWN
            and self.is_human_turn
            and check_win(self.human.hand.cards)
        )
