"""
Main game renderer.  Draws the entire frame each tick.

Usage:
    renderer = Renderer(screen)
    renderer.setup_fonts()
    # each frame:
    renderer.draw(game)
"""
from __future__ import annotations
import os
import re
import pygame

from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, CARD_W, CARD_H, SEAT_HUMAN,
    TABLE_GREEN, TABLE_BORDER,
    WHITE, BLACK_COLOR, LIGHT_GRAY, DARK_GRAY, GRAY, GOLD,
    GREEN_COLOR, RED_COLOR,
    FONT_LG, FONT_MD, FONT_SM, FONT_XSM,
    BTN_W, BTN_H,
    TENPAI_DOT_R,
)
from game.game_state import GameState
from constants import CENTER_Y

# States where all hands are revealed
_REVEAL_STATES = frozenset({
    GameState.ROUND_END,
    GameState.GAME_OVER,
})

# Side-player face-up layout constants
_REVEAL_SIDE_STEP   = CARD_H // 2 + 2          # 52 – overlapping spread
_REVEAL_SIDE_START_Y = CENTER_Y - (4 * _REVEAL_SIDE_STEP + CARD_H) // 2
from gui.layout import (
    HUMAN_CARD_X0, HUMAN_CARD_Y, HUMAN_CARD_GAP, HUMAN_CARD_LIFT,
    HUMAN_LABEL_X, HUMAN_LABEL_Y,
    AI2_CARD_X0, AI2_CARD_Y, AI2_CARD_GAP,
    AI2_LABEL_X, AI2_LABEL_Y,
    AI1_CARD_X, AI1_CARD_Y0, AI1_CARD_GAP,
    AI1_LABEL_X, AI1_LABEL_Y,
    AI3_CARD_X, AI3_CARD_Y0, AI3_CARD_GAP,
    AI3_LABEL_X, AI3_LABEL_Y,
    DECK_X, DECK_Y, DISCARD_ROWS,
    BTN_WIN_X, BTN_Y,
    SCORE_X, SCORE_Y, SCORE_LINE_H,
    LOG_X, LOG_Y, LOG_LINE_H,
    RON_OVERLAY_RECT,
    SPEECH_BUBBLE_POS, SPEECH_BUBBLE_TAIL, SPEECH_BUBBLE_W, SPEECH_BUBBLE_H,
)
from gui.card_sprite import draw_card_face, draw_card_back, draw_ghost_face, _suit as _draw_suit
from core.card import Suit as _Suit
# Log suit-symbol rendering helpers
_LOG_SUIT_RE  = re.compile('([♠♣♥♦])')
_LOG_SUIT_MAP = {
    '♠': (_Suit.SPADES,   BLACK_COLOR),
    '♣': (_Suit.CLUBS,    BLACK_COLOR),
    '♥': (_Suit.HEARTS,   RED_COLOR),
    '♦': (_Suit.DIAMONDS, RED_COLOR),
}

from gui.button import Button
from gui.dialog import RonDialog, RoundEndDialog, GameOverDialog


from gui.font_loader import load_font as _load_font


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._fonts_ready = False

        # Fonts
        self.font_lg:  pygame.font.Font | None = None
        self.font_md:  pygame.font.Font | None = None
        self.font_sm:  pygame.font.Font | None = None
        self.font_xsm: pygame.font.Font | None = None

        # Buttons
        self._btn_win: Button | None = None

        # Double-click tracking
        self._last_click_ms:     int = 0
        self._last_click_target: str = ''

        # Invalid-pick feedback (red border + message, auto-expires)
        self._invalid_pick_msg:    str             = ''
        self._invalid_pick_pos:    tuple[int, int] = (0, 0)
        self._invalid_pick_end_ms: int             = 0

        # Dialogs
        self._dlg_ron:       RonDialog | None = None
        self._dlg_round_end: RoundEndDialog | None = None
        self._dlg_game_over: GameOverDialog | None = None

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def setup_fonts(self) -> None:
        self.font_lg  = _load_font(FONT_LG)
        self.font_md  = _load_font(FONT_MD)
        self.font_sm  = _load_font(FONT_SM)
        self.font_xsm = _load_font(FONT_XSM)

        self._btn_win = Button(BTN_WIN_X, BTN_Y, BTN_W, BTN_H, '自摸', style='ron', font=self.font_md)
        self._font_md_bold = _load_font(FONT_MD)
        self._font_md_bold.bold = True

        self._dlg_ron       = RonDialog(self.font_lg, self.font_md, self.font_sm)
        self._dlg_round_end = RoundEndDialog(self.font_lg, self.font_md, self.font_sm)
        self._dlg_game_over = GameOverDialog(self.font_lg, self.font_md)

        self._fonts_ready = True

    # ------------------------------------------------------------------
    # Button state sync
    # ------------------------------------------------------------------

    def _sync_buttons(self, game) -> None:
        self._btn_win.enabled = game.can_human_tsumo

    # ------------------------------------------------------------------
    # Main draw entry point
    # ------------------------------------------------------------------

    def draw(self, game) -> None:
        if not self._fonts_ready:
            return
        self._sync_buttons(game)
        surf = self._screen

        # ── Table background ───────────────────────────────────────
        surf.fill(TABLE_GREEN)
        # Thin border
        pygame.draw.rect(surf, TABLE_BORDER, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 4)

        # ── Central play area border ───────────────────────────────
        play_rect = pygame.Rect(180, 160, WINDOW_WIDTH - 360, WINDOW_HEIGHT - 320)
        pygame.draw.rect(surf, (25, 80, 40), play_rect, border_radius=10)
        pygame.draw.rect(surf, (40, 110, 60), play_rect, 2, border_radius=10)

        # ── Deck ───────────────────────────────────────────────────
        self._draw_deck(surf, game)

        # ── Per-player discard history ─────────────────────────────
        self._draw_discard_history(surf, game)

        # ── Invalid-pick feedback ───────────────────────────────────
        if self._invalid_pick_msg:
            if pygame.time.get_ticks() < self._invalid_pick_end_ms:
                ix, iy = self._invalid_pick_pos
                pygame.draw.rect(surf, (220, 60, 60),
                                 (ix - 2, iy - 2, CARD_W + 4, CARD_H + 4), 3, border_radius=8)
                err = self.font_sm.render(self._invalid_pick_msg, True, (220, 60, 60))
                surf.blit(err, (ix + (CARD_W - err.get_width()) // 2, iy - err.get_height() - 4))
            else:
                self._invalid_pick_msg = ''

        # ── Players ────────────────────────────────────────────────
        self._draw_human(surf, game)
        self._draw_ai2(surf, game)    # top
        self._draw_ai1(surf, game)    # right
        self._draw_ai3(surf, game)    # left

        # ── AI speech bubbles ──────────────────────────────────────
        self._draw_ai_speech_bubbles(surf, game)

        # ── Scores (top-left) ──────────────────────────────────────
        self._draw_scores(surf, game)

        # ── Log (mid-left) ─────────────────────────────────────────
        self._draw_log(surf, game)

        # ── Buttons (bottom) ───────────────────────────────────────
        if game.state not in (GameState.RON_WINDOW, GameState.ROUND_END, GameState.GAME_OVER):
            self._btn_win.draw(surf)

        # ── Round label ────────────────────────────────────────────
        rl = self.font_sm.render(f'第 {game.round_number} 局', True, LIGHT_GRAY)
        surf.blit(rl, (WINDOW_WIDTH - rl.get_width() - 10, 8))

        # ── 釣寶 indicator (left of 自摸 button) ───────────────────
        if game.human.is_diaobao:
            db = self._font_md_bold.render('釣寶中！', True, GOLD)
            surf.blit(db, (BTN_WIN_X - db.get_width() - 10,
                           BTN_Y + (BTN_H - db.get_height()) // 2))

        # ── Overlay dialogs ────────────────────────────────────────
        if game.state == GameState.RON_WINDOW and game.human_can_ron:
            card_str = str(game.last_discard) if game.last_discard else '?'
            claimant_names = [game.players[i].name for i in game.ron_claimants]
            self._dlg_ron.draw(surf, card_str, game.ron_window_ms, claimant_names)

        elif game.state == GameState.ROUND_END:
            scores = [(p.name, p.score) for p in game.players]
            bankrupt = [p.name for p in game.players if p.is_bankrupt()]
            winner_name = game.winner.name if game.winner else None
            self._dlg_round_end.draw(surf, winner_name, game.win_type, scores, bankrupt)

        elif game.state == GameState.GAME_OVER:
            scores = [(p.name, p.score) for p in game.players]
            self._dlg_game_over.draw(surf, scores)

    # ------------------------------------------------------------------
    # Sub-drawers
    # ------------------------------------------------------------------

    def _is_pending(self, target: str) -> bool:
        """Return True if *target* was first-clicked and still within the double-click window."""
        return (
            self._last_click_target == target
            and (pygame.time.get_ticks() - self._last_click_ms) <= 400
        )

    def _draw_highlight(self, surf: pygame.Surface, x: int, y: int) -> None:
        """Draw a gold glow border around a card-sized area."""
        pad = 4
        rect = pygame.Rect(x - pad, y - pad, CARD_W + pad * 2, CARD_H + pad * 2)
        pygame.draw.rect(surf, GOLD, rect, 3, border_radius=9)

    def _draw_deck(self, surf: pygame.Surface, game) -> None:
        draw_card_back(surf, DECK_X, DECK_Y)
        # Stack effect
        if game.deck.remaining > 1:
            draw_card_back(surf, DECK_X - 2, DECK_Y - 2)
        if game.deck.remaining > 5:
            draw_card_back(surf, DECK_X - 4, DECK_Y - 4)
        # Highlight on first click
        if self._is_pending('deck'):
            self._draw_highlight(surf, DECK_X, DECK_Y)
        # Count
        cnt = self.font_sm.render(str(game.deck.remaining), True, WHITE)
        surf.blit(cnt, (DECK_X + (CARD_W - cnt.get_width()) // 2, DECK_Y + CARD_H + 4))
        lbl = self.font_xsm.render('牌庫', True, LIGHT_GRAY)
        surf.blit(lbl, (DECK_X + (CARD_W - lbl.get_width()) // 2, DECK_Y + CARD_H + 4 + cnt.get_height()))

    def _draw_discard_history(self, surf: pygame.Surface, game) -> None:
        """Draw each player's full discard history in front of their position.
        Only 上家's most-recent card is eligible for pickup (gold highlight).
        """
        upjia = (SEAT_HUMAN + 3) % 4          # seat 3 for human
        now   = pygame.time.get_ticks()

        for seat, (sx, sy, sdx, sdy, max_v) in DISCARD_ROWS.items():
            cards     = game.discard_history[seat]
            n         = len(cards)
            start_idx = max(0, n - max_v)

            for disp_i, card_i in enumerate(range(start_idx, n)):
                card = cards[card_i]
                x = sx + disp_i * sdx
                y = sy + disp_i * sdy
                draw_card_face(surf, card, x, y,
                               font_md=self.font_md, font_sm=self.font_sm)

                # Gold highlight on first-click pending only
                target_key = f'discard_{seat}_{card_i}'
                if (self._last_click_target == target_key
                        and (now - self._last_click_ms) <= 400):
                    self._draw_highlight(surf, x, y)

    def _draw_human(self, surf: pygame.Surface, game) -> None:
        human  = game.human
        cards  = human.hand.cards
        is_turn = game.is_human_turn

        # Player label + tenpai indicator
        self._draw_player_label(
            surf, human.name, HUMAN_LABEL_X, HUMAN_LABEL_Y,
            tenpai=human.in_tenpai, is_turn=is_turn, anchor='left',
        )

        # Cards
        for i, card in enumerate(cards):
            selected = (i == human.selected_index)
            x = HUMAN_CARD_X0 + i * HUMAN_CARD_GAP
            y = HUMAN_CARD_Y - (HUMAN_CARD_LIFT if selected else 0)
            draw_card_face(surf, card, x, y,
                           selected=selected,
                           font_md=self.font_md,
                           font_sm=self.font_sm)

        # "你的回合" indicator
        if is_turn and game.state in (GameState.DRAWING, GameState.PLAYER_DRAWN):
            ind = self.font_sm.render('▲ 你的回合', True, GOLD)
            surf.blit(ind, (HUMAN_CARD_X0, HUMAN_CARD_Y - 22))

    def _draw_ai2(self, surf: pygame.Surface, game) -> None:
        """Top player."""
        ai      = game.players[2]
        reveal  = game.state in _REVEAL_STATES

        for i, card in enumerate(ai.hand):
            x = AI2_CARD_X0 + i * AI2_CARD_GAP
            if reveal:
                draw_card_face(surf, card, x, AI2_CARD_Y,
                               font_md=self.font_md, font_sm=self.font_sm)
            else:
                draw_card_back(surf, x, AI2_CARD_Y)

        is_turn = (game.current_player_index == 2)
        self._draw_player_label(
            surf, ai.name, AI2_LABEL_X, AI2_LABEL_Y,
            tenpai=ai.in_tenpai, is_turn=is_turn, anchor='center',
        )

    def _draw_ai1(self, surf: pygame.Surface, game) -> None:
        """Right player – rotated back / upright face-up on reveal."""
        ai     = game.players[1]
        reveal = game.state in _REVEAL_STATES

        for i, card in enumerate(ai.hand):
            if reveal:
                x = WINDOW_WIDTH - CARD_W - 20
                y = _REVEAL_SIDE_START_Y + i * _REVEAL_SIDE_STEP
                draw_card_face(surf, card, x, y,
                               font_md=self.font_md, font_sm=self.font_sm)
            else:
                draw_card_back(surf, AI1_CARD_X, AI1_CARD_Y0 + i * AI1_CARD_GAP,
                               rotated=True)

        is_turn = (game.current_player_index == 1)
        self._draw_player_label(
            surf, ai.name, AI1_LABEL_X, AI1_LABEL_Y,
            tenpai=ai.in_tenpai, is_turn=is_turn, anchor='center',
        )

    def _draw_ai3(self, surf: pygame.Surface, game) -> None:
        """Left player – rotated back / upright face-up on reveal."""
        ai     = game.players[3]
        reveal = game.state in _REVEAL_STATES

        for i, card in enumerate(ai.hand):
            if reveal:
                x = 20
                y = _REVEAL_SIDE_START_Y + i * _REVEAL_SIDE_STEP
                draw_card_face(surf, card, x, y,
                               font_md=self.font_md, font_sm=self.font_sm)
            else:
                draw_card_back(surf, AI3_CARD_X, AI3_CARD_Y0 + i * AI3_CARD_GAP,
                               rotated=True)

        is_turn = (game.current_player_index == 3)
        self._draw_player_label(
            surf, ai.name, AI3_LABEL_X, AI3_LABEL_Y,
            tenpai=ai.in_tenpai, is_turn=is_turn, anchor='center',
        )

    def _draw_player_label(
        self,
        surf: pygame.Surface,
        name: str,
        x: int, y: int,
        *,
        tenpai: bool,
        is_turn: bool,
        anchor: str = 'left',
    ) -> None:
        color = GOLD if is_turn else WHITE
        font  = self.font_md if is_turn else self.font_sm
        txt   = font.render(name, True, color)
        if anchor == 'center':
            x -= txt.get_width() // 2
        elif anchor == 'right':
            x -= txt.get_width()
        surf.blit(txt, (x, y))

    def _draw_scores(self, surf: pygame.Surface, game) -> None:
        header = self.font_sm.render('分數', True, GOLD)
        surf.blit(header, (SCORE_X, SCORE_Y))
        y = SCORE_Y + SCORE_LINE_H
        for p in game.players:
            col = WHITE if p.score > 0 else RED_COLOR
            line = self.font_xsm.render(f'{p.name}: {p.score}', True, col)
            surf.blit(line, (SCORE_X, y))
            y += SCORE_LINE_H

    def _draw_log(self, surf: pygame.Surface, game) -> None:
        y = LOG_Y
        for msg in game.log[:5]:
            self._draw_log_line(surf, msg, LOG_X, y)
            y += LOG_LINE_H

    def _draw_log_line(self, surf: pygame.Surface, text: str, x: int, y: int) -> None:
        """Render one log line; suit symbols (♠♣♥♦) are drawn as small graphics."""
        fh = self.font_xsm.get_height()
        cx = x
        for token in _LOG_SUIT_RE.split(text):
            if not token:
                continue
            if token in _LOG_SUIT_MAP:
                suit_enum, col = _LOG_SUIT_MAP[token]
                sz = 4
                _draw_suit(surf, suit_enum, cx + sz + 1, y + fh // 2, sz, col)
                cx += sz * 2 + 4
            else:
                t = self.font_xsm.render(token, True, LIGHT_GRAY)
                surf.blit(t, (cx, y))
                cx += t.get_width()

    # ------------------------------------------------------------------
    # Event forwarding helpers (called by main.py)
    # ------------------------------------------------------------------

    def handle_event_for_game(self, event: pygame.event.Event, game) -> str | None:
        """Translate button clicks and card clicks into game actions.
        Returns 'menu' when the player requests to return to the main menu."""
        state = game.state

        # ── RON window ────────────────────────────────────────────
        if state == GameState.RON_WINDOW and game.human_can_ron:
            action = self._dlg_ron.handle_event(event)
            if action == 'ron':
                game.human_declare_ron()
            elif action == 'pass':
                game.human_pass_ron()
            return

        # ── Round end ─────────────────────────────────────────────
        if state == GameState.ROUND_END:
            action = self._dlg_round_end.handle_event(event)
            if action == 'next':
                game.human_next_round()
            elif action == 'quit':
                game.human_quit()
            return

        # ── Game over ─────────────────────────────────────────────
        if state == GameState.GAME_OVER:
            if self._dlg_game_over.handle_event(event):
                return 'menu'
            return

        # ── 胡牌 button ───────────────────────────────────────────
        if self._btn_win.handle_event(event):
            game.human_declare_tsumo()
            return

        # ── Double-click interactions ──────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            now    = pygame.time.get_ticks()
            target = self._get_click_target(event.pos, game)

            if target and target == self._last_click_target and (now - self._last_click_ms) <= 400:
                # ── Second click: execute action ───────────────────
                self._last_click_target = ''
                self._last_click_ms     = 0
                if target == 'deck' and game.can_human_draw:
                    game.human_draw()
                elif (target and target.startswith('discard_')
                      and game.state == GameState.DRAWING and game.is_human_turn):
                    _, seat_s, idx_s = target.split('_')
                    seat, card_idx   = int(seat_s), int(idx_s)
                    upjia            = (SEAT_HUMAN + 3) % 4
                    history          = game.discard_history[seat]
                    # Compute screen position for this card (for error overlay)
                    sx, sy, sdx, sdy, max_v = DISCARD_ROWS[seat]
                    n         = len(history)
                    start_idx = max(0, n - max_v)
                    disp_i    = card_idx - start_idx
                    cx, cy    = sx + disp_i * sdx, sy + disp_i * sdy
                    if game.can_human_pick and seat == upjia and card_idx == n - 1:
                        game.human_pick_discard()
                    elif seat != upjia:
                        self._invalid_pick_msg    = '你不能撿上家以外的牌'
                        self._invalid_pick_pos    = (cx, cy)
                        self._invalid_pick_end_ms = pygame.time.get_ticks() + 1800
                    else:
                        self._invalid_pick_msg    = '你不能撿前一輪的牌'
                        self._invalid_pick_pos    = (cx, cy)
                        self._invalid_pick_end_ms = pygame.time.get_ticks() + 1800
                elif target.startswith('card_') and game.can_human_discard:
                    game.human_discard(int(target[5:]))
            else:
                # ── First click: record; select card if applicable ─
                self._last_click_target = target or ''
                self._last_click_ms     = now
                if (target and target.startswith('card_')
                        and state == GameState.PLAYER_DRAWN
                        and game.is_human_turn):
                    game.human.select_card(int(target[5:]))

    def _draw_ai_speech_bubbles(self, surf: pygame.Surface, game) -> None:
        for seat, bubble in list(game.ai_speech.items()):
            cx, cy = SPEECH_BUBBLE_POS[seat]
            self._draw_speech_bubble(surf, cx, cy,
                                     bubble['text'], bubble.get('card'),
                                     SPEECH_BUBBLE_TAIL[seat])

    def _draw_speech_bubble(self, surf, cx, cy, text, card, tail) -> None:
        BW, BH = SPEECH_BUBBLE_W, SPEECH_BUBBLE_H
        rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
        TAIL_LEN = 10

        if tail == 'up':
            tip  = (cx, cy - BH // 2 - TAIL_LEN)
            pts  = [(cx - 6, cy - BH // 2 + 2), (cx + 6, cy - BH // 2 + 2), tip]
            edge = [pts[0], tip, pts[1]]
        elif tail == 'right':
            tip  = (cx + BW // 2 + TAIL_LEN, cy)
            pts  = [(cx + BW // 2 - 2, cy - 6), (cx + BW // 2 - 2, cy + 6), tip]
            edge = [pts[0], tip, pts[1]]
        else:  # left
            tip  = (cx - BW // 2 - TAIL_LEN, cy)
            pts  = [(cx - BW // 2 + 2, cy - 6), (cx - BW // 2 + 2, cy + 6), tip]
            edge = [pts[0], tip, pts[1]]

        pygame.draw.polygon(surf, WHITE, pts)
        pygame.draw.rect(surf, WHITE, rect, border_radius=8)
        pygame.draw.rect(surf, (60, 60, 60), rect, 2, border_radius=8)
        pygame.draw.lines(surf, (60, 60, 60), False, edge, 2)

        text_y = cy - self.font_md.get_height() // 2

        if card is not None:
            ink = BLACK_COLOR if card.color.name == 'BLACK' else RED_COLOR
            prefix = self.font_md.render(f'出 {card.rank_symbol}', True, (20, 20, 20))
            px = cx - BW // 2 + 6
            surf.blit(prefix, (px, text_y))
            sx = px + prefix.get_width() + 4
            sy = cy
            _draw_suit(surf, card.suit, sx, sy, 8, ink)
        else:
            lbl = self.font_md.render(text, True, (20, 20, 20))
            surf.blit(lbl, (cx - lbl.get_width() // 2, text_y))

    def _get_click_target(self, pos: tuple, game) -> str | None:
        """Return a stable string identifier for whatever was clicked, or None."""
        # Deck
        if pygame.Rect(DECK_X, DECK_Y, CARD_W, CARD_H).collidepoint(pos):
            return 'deck'
        # Discard history cards (all seats) — iterate newest→oldest so topmost card wins
        for seat, (sx, sy, sdx, sdy, max_v) in DISCARD_ROWS.items():
            cards     = game.discard_history[seat]
            n         = len(cards)
            start_idx = max(0, n - max_v)
            for card_i in range(n - 1, start_idx - 1, -1):
                disp_i = card_i - start_idx
                x = sx + disp_i * sdx
                y = sy + disp_i * sdy
                if pygame.Rect(x, y, CARD_W, CARD_H).collidepoint(pos):
                    return f'discard_{seat}_{card_i}'
        # Human hand cards (use a taller hit-rect covering both lifted/non-lifted)
        if game.is_human_turn:
            for i in range(len(game.human.hand.cards)):
                x    = HUMAN_CARD_X0 + i * HUMAN_CARD_GAP
                y_hi = HUMAN_CARD_Y - HUMAN_CARD_LIFT      # top when fully lifted
                rect = pygame.Rect(x, y_hi, CARD_W, CARD_H + HUMAN_CARD_LIFT)
                if rect.collidepoint(pos):
                    return f'card_{i}'
        return None
