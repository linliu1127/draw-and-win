"""
Main menu: title screen + rules page.

Pages:
  'main'  – title '自摸' + 開始遊戲 / 規則說明 / 結束遊戲
  'rules' – 7 頁翻頁式規則說明 (page 0–6)
"""
from __future__ import annotations
import math
import pygame

from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    TABLE_GREEN, TABLE_BORDER,
    WHITE, GOLD, DARK_GRAY, BLACK_COLOR, RED_COLOR,
    CARD_FACE_BG, CARD_BACK_BG, CARD_BACK_STRIPE, CARD_BORDER_COL,
    CARD_W, CARD_H,
    GREEN_COLOR,
    CENTER_X, CENTER_Y,
)
from gui.button import Button
from gui.font_loader import load_font as _load_font
from gui.card_sprite import draw_card_face, draw_card_back, draw_ghost_face
from core.card import Card, Suit, Color

_BTN_W   = 200
_BTN_H   = 52
_BTN_GAP = 16

# ── Rules data ─────────────────────────────────────────────────────────
_RULES = [
    ("1. 發牌",
     "共有 4 名玩家，各從 54 張牌庫\n（52 張 + 2 張魃）發 4 張牌。"),
    ("2. 胡牌條件",
     "湊齊 5 張同色牌（全黑 ♠♣ 或全紅 ♥♦），\n恰好包含【一對】＋【一順（連續3張）】。"),
    ("3. 摸牌與棄牌",
     "輪到你時，連點兩下牌庫摸 1 張牌或撿上家的棄牌。\n若不構成自摸就棄一張牌，換下家。"),
    ("4. 胡",
     "任一玩家打出你聽的牌，\n可立即按「胡」鍵胡牌；\n也可放棄，等待自摸。"),
    ("5. 計分",
     "自摸：向每位玩家收 100 點（共 ＋300）。\n搶牌：向被胡牌者收 50 點（共 ＋50）。\n勝者先開下一局。"),
    ("6. 魃（鬼牌）",
     "牌庫有 2 張魃，可當成任意一張牌。。"),
    ("7. 結束條件",
     "每人起始 1000 點。\n當有玩家破產，\n或四人同意結束時遊戲結束。"),
]

# ── Illustration area (right half) ─────────────────────────────────────
_IX0 = 580   # left edge
_IX1 = 1140  # right edge
_IY0 = 80    # top edge
_IY1 = 680   # bottom edge
_ICX = (_IX0 + _IX1) // 2   # 860
_ICY = (_IY0 + _IY1) // 2   # 380

# Mini card dimensions (≈ 0.5 scale)
_MC_W   = 35
_MC_H   = 50
_MC_GAP = 5
_MC_R   = 4


class Menu:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen    = screen
        self._page      = 'main'   # 'main' | 'rules'
        self._rule_page = 0        # 0–6

        # Fonts
        self._font_hero = _load_font(88)
        self._font_lg   = _load_font(32)
        self._font_md   = _load_font(22)
        self._font_sm   = _load_font(20)
        self._font_xs   = _load_font(14)

        # ── Main menu buttons ──────────────────────────────────────
        bx = CENTER_X - _BTN_W // 2
        by = 330
        self._btn_start = Button(bx, by,                       _BTN_W, _BTN_H, '開始遊戲', font=self._font_md)
        self._btn_rules = Button(bx, by + (_BTN_H + _BTN_GAP), _BTN_W, _BTN_H, '規則說明', font=self._font_md)

        # ── Rules page navigation buttons ─────────────────────────
        btn_y = WINDOW_HEIGHT - _BTN_H - 24
        self._btn_back_l = Button(40,                          btn_y, _BTN_W, _BTN_H, '返回',     font=self._font_md)
        self._btn_prev   = Button(40,                          btn_y, _BTN_W, _BTN_H, '◀ 上一頁', font=self._font_md)
        self._btn_next   = Button(WINDOW_WIDTH - _BTN_W - 40, btn_y, _BTN_W, _BTN_H, '下一頁 ▶', font=self._font_md)
        self._btn_back_r = Button(WINDOW_WIDTH - _BTN_W - 40, btn_y, _BTN_W, _BTN_H, '返回',     font=self._font_md)

    # ------------------------------------------------------------------
    # Mini card helpers
    # ------------------------------------------------------------------

    def _mini_back(self, surf: pygame.Surface, x: int, y: int,
                   w: int = _MC_W, h: int = _MC_H) -> None:
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surf, CARD_BACK_BG, rect, border_radius=_MC_R)
        pygame.draw.rect(surf, CARD_BORDER_COL, rect, 1, border_radius=_MC_R)
        for i in range(0, w, 6):
            pygame.draw.line(surf, CARD_BACK_STRIPE, (x + i, y + 2), (x + i, y + h - 3), 1)

    def _mini_face(self, surf: pygame.Surface, card: Card, x: int, y: int,
                   w: int = _MC_W, h: int = _MC_H) -> None:
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surf, CARD_FACE_BG, rect, border_radius=_MC_R)
        pygame.draw.rect(surf, CARD_BORDER_COL, rect, 1, border_radius=_MC_R)
        ink = BLACK_COLOR if card.color == Color.BLACK else RED_COLOR
        label = f"{card.rank_symbol}{card.suit_symbol}"
        txt = self._font_xs.render(label, True, ink)
        surf.blit(txt, (x + 2, y + 2))

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self) -> None:
        surf = self._screen
        surf.fill(TABLE_GREEN)
        pygame.draw.rect(surf, TABLE_BORDER, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 4)

        if self._page == 'main':
            self._draw_main(surf)
        else:
            self._draw_rules(surf)

    def _draw_main(self, surf: pygame.Surface) -> None:
        hero = self._font_hero.render('自摸·釣寶', True, GOLD)
        surf.blit(hero, (CENTER_X - hero.get_width() // 2, 140))

        rule_y = 140 + hero.get_height() + 10
        pygame.draw.line(surf, GOLD, (CENTER_X - 80, rule_y), (CENTER_X + 80, rule_y), 2)
        pygame.draw.circle(surf, GOLD, (CENTER_X, rule_y), 4)

        self._btn_start.draw(surf)
        self._btn_rules.draw(surf)

    def _draw_rules(self, surf: pygame.Surface) -> None:
        p = self._rule_page
        title_str, body_str = _RULES[p]

        # Header
        title = self._font_lg.render('規則說明', True, GOLD)
        surf.blit(title, (CENTER_X - title.get_width() // 2, 22))

        counter = self._font_sm.render(f'{p + 1} / 7', True, DARK_GRAY)
        surf.blit(counter, (WINDOW_WIDTH - counter.get_width() - 50, 28))

        pygame.draw.line(surf, DARK_GRAY, (60, 68), (WINDOW_WIDTH - 60, 68), 1)
        pygame.draw.line(surf, DARK_GRAY, (_IX0 - 20, 75), (_IX0 - 20, 700), 1)

        # Left text
        t = self._font_lg.render(title_str, True, GOLD)
        surf.blit(t, (40, 100))

        y = 160
        for line in body_str.split('\n'):
            lt = self._font_sm.render(line, True, WHITE)
            surf.blit(lt, (40, y))
            y += self._font_sm.get_height() + 8

        # Right illustration
        [self._illus_0, self._illus_1, self._illus_2,
         self._illus_3, self._illus_4, self._illus_5,
         self._illus_6][p](surf)

        # Navigation buttons
        if p == 0:
            self._btn_back_l.draw(surf)
            self._btn_next.draw(surf)
        elif p == 6:
            self._btn_prev.draw(surf)
            self._btn_back_r.draw(surf)
        else:
            self._btn_prev.draw(surf)
            self._btn_next.draw(surf)

    # ------------------------------------------------------------------
    # Illustrations
    # ------------------------------------------------------------------

    def _illus_0(self, surf: pygame.Surface) -> None:
        """發牌 — mini game board: 4 players, each 4 cards."""
        cx, cy = _ICX, _ICY

        cards_span = 4 * _MC_W + 3 * _MC_GAP   # 155
        x0_h = cx - cards_span // 2             # horizontal x-start for top/bottom

        # AI2 (top) — 4 card backs horizontal
        ai2_y = 160
        for i in range(4):
            self._mini_back(surf, x0_h + i * (_MC_W + _MC_GAP), ai2_y)
        lbl = self._font_xs.render('AI2', True, WHITE)
        surf.blit(lbl, (cx - lbl.get_width() // 2, ai2_y + _MC_H + 4))

        # Human (bottom) — 4 card faces horizontal
        h_y = 560
        human_cards = [Card(Suit.SPADES, 3), Card(Suit.CLUBS, 7),
                       Card(Suit.SPADES, 10), Card(Suit.CLUBS, 2)]
        for i, card in enumerate(human_cards):
            self._mini_face(surf, card, x0_h + i * (_MC_W + _MC_GAP), h_y)
        lbl = self._font_xs.render('你', True, GOLD)
        surf.blit(lbl, (cx - lbl.get_width() // 2, h_y - lbl.get_height() - 4))

        # Rotated card stacks: w=_MC_H=50, h=_MC_W=35 (landscape)
        vert_span = 4 * _MC_W + 3 * _MC_GAP    # 155
        vy0 = cy - vert_span // 2

        # AI1 (right) — 4 rotated card backs, stacked vertically
        ai1_x = 1060
        for i in range(4):
            self._mini_back(surf, ai1_x, vy0 + i * (_MC_W + _MC_GAP),
                            w=_MC_H, h=_MC_W)
        lbl = self._font_xs.render('AI1', True, WHITE)
        surf.blit(lbl, (ai1_x + _MC_H + 4, cy - lbl.get_height() // 2))

        # AI3 (left) — 4 rotated card backs, stacked vertically
        ai3_x = 608
        for i in range(4):
            self._mini_back(surf, ai3_x, vy0 + i * (_MC_W + _MC_GAP),
                            w=_MC_H, h=_MC_W)
        lbl = self._font_xs.render('AI3', True, WHITE)
        surf.blit(lbl, (ai3_x - lbl.get_width() - 4, cy - lbl.get_height() // 2))

        # Deck (center)
        deck_x = cx - _MC_W // 2
        deck_y = cy - _MC_H // 2
        self._mini_back(surf, deck_x, deck_y)
        lbl = self._font_xs.render('牌庫', True, GOLD)
        surf.blit(lbl, (cx - lbl.get_width() // 2, deck_y + _MC_H + 4))

    def _illus_1(self, surf: pygame.Surface) -> None:
        """胡牌條件 — 5 cards with bracket labels."""
        cards = [
            Card(Suit.SPADES,  2),
            Card(Suit.CLUBS,   3),
            Card(Suit.CLUBS,   4),
            Card(Suit.SPADES, 10),
            Card(Suit.CLUBS,  10),
        ]
        gap = 10
        total_w = 5 * CARD_W + 4 * gap
        x0 = _ICX - total_w // 2
        cy = _ICY - CARD_H // 2 - 20

        for i, card in enumerate(cards):
            draw_card_face(surf, card, x0 + i * (CARD_W + gap), cy,
                           font_md=self._font_md, font_sm=self._font_sm)

        bkt_y = cy + CARD_H + 10

        # Bracket: 一順 (first 3 cards)
        sx0 = x0
        sx1 = x0 + 3 * (CARD_W + gap) - gap
        pygame.draw.line(surf, GOLD, (sx0, bkt_y), (sx1, bkt_y), 2)
        pygame.draw.line(surf, GOLD, (sx0, bkt_y), (sx0, bkt_y - 6), 2)
        pygame.draw.line(surf, GOLD, (sx1, bkt_y), (sx1, bkt_y - 6), 2)
        ls = self._font_sm.render('一順', True, GOLD)
        surf.blit(ls, ((sx0 + sx1) // 2 - ls.get_width() // 2, bkt_y + 4))

        # Bracket: 一對 (last 2 cards)
        px0 = x0 + 3 * (CARD_W + gap)
        px1 = x0 + total_w
        pygame.draw.line(surf, RED_COLOR, (px0, bkt_y), (px1, bkt_y), 2)
        pygame.draw.line(surf, RED_COLOR, (px0, bkt_y), (px0, bkt_y - 6), 2)
        pygame.draw.line(surf, RED_COLOR, (px1, bkt_y), (px1, bkt_y - 6), 2)
        lp = self._font_sm.render('一對', True, RED_COLOR)
        surf.blit(lp, ((px0 + px1) // 2 - lp.get_width() // 2, bkt_y + 4))

    def _illus_2(self, surf: pygame.Surface) -> None:
        """摸牌與棄牌 — mini game board: deck, human hand, AI3 discard, arrows."""
        h_gap = 5
        h_span = 5 * _MC_W + 4 * h_gap   # 195
        hx0 = _ICX - h_span // 2          # 763
        hy  = 600

        # ── Deck (center-top) ──────────────────────────────────────────────
        deck_x = _ICX - _MC_W // 2        # 843
        deck_y = 310
        # Shadow
        self._mini_back(surf, deck_x - 3, deck_y - 3)
        # Gold highlight (clickable hint)
        pygame.draw.rect(surf, GOLD,
                         (deck_x - 4, deck_y - 4, _MC_W + 8, _MC_H + 8),
                         2, border_radius=_MC_R + 2)
        self._mini_back(surf, deck_x, deck_y)
        cnt = self._font_xs.render('46', True, WHITE)
        surf.blit(cnt, (deck_x + _MC_W // 2 - cnt.get_width() // 2,
                         deck_y + _MC_H + 2))
        deck_lbl = self._font_xs.render('牌庫', True, GOLD)
        surf.blit(deck_lbl, (deck_x + _MC_W // 2 - deck_lbl.get_width() // 2,
                              deck_y + _MC_H + 14))

        # ── Human hand (bottom) ────────────────────────────────────────────
        hand_cards = [Card(Suit.SPADES, 3), Card(Suit.CLUBS, 7),
                      Card(Suit.SPADES, 10), Card(Suit.CLUBS, 2),
                      Card(Suit.SPADES, 5)]
        turn_lbl = self._font_xs.render('▲ 你的回合', True, GOLD)
        surf.blit(turn_lbl, (_ICX - turn_lbl.get_width() // 2,
                              hy - turn_lbl.get_height() - 4))
        for i, card in enumerate(hand_cards):
            cx_i = hx0 + i * (_MC_W + h_gap)
            if i == 4:  # Newly drawn card: gold highlight
                pygame.draw.rect(surf, GOLD,
                                 (cx_i - 4, hy - 4, _MC_W + 8, _MC_H + 8),
                                 2, border_radius=_MC_R + 2)
            self._mini_face(surf, card, cx_i, hy)

        # ── AI3 left discard pile (landscape cards) ────────────────────────
        ai3_discard = [Card(Suit.CLUBS, 8), Card(Suit.SPADES, 4)]
        ai3_x = 623
        ai3_cw, ai3_ch = _MC_H, _MC_W   # landscape: 50×35
        ai3_gap = 8
        ai3_y0 = 310
        disc_lbl = self._font_xs.render('上家棄牌', True, GOLD)
        surf.blit(disc_lbl, (ai3_x + ai3_cw // 2 - disc_lbl.get_width() // 2,
                              ai3_y0 - disc_lbl.get_height() - 4))
        for i, card in enumerate(ai3_discard):
            cy_i = ai3_y0 + i * (ai3_ch + ai3_gap)
            if i == 0:  # Top card highlighted
                pygame.draw.rect(surf, GOLD,
                                 (ai3_x - 4, cy_i - 4, ai3_cw + 8, ai3_ch + 8),
                                 2, border_radius=_MC_R + 2)
            rect = pygame.Rect(ai3_x, cy_i, ai3_cw, ai3_ch)
            pygame.draw.rect(surf, CARD_FACE_BG, rect, border_radius=_MC_R)
            pygame.draw.rect(surf, CARD_BORDER_COL, rect, 1, border_radius=_MC_R)
            ink = BLACK_COLOR if card.color == Color.BLACK else RED_COLOR
            txt = self._font_xs.render(
                f"{card.rank_symbol}{card.suit_symbol}", True, ink)
            surf.blit(txt, (ai3_x + 2, cy_i + 2))

        # ── Arrow 1: Deck → Hand (downward) ───────────────────────────────
        a1_x  = _ICX
        a1_y1 = deck_y + _MC_H + 32
        a1_y2 = hy - 22
        pygame.draw.line(surf, GOLD, (a1_x, a1_y1), (a1_x, a1_y2), 2)
        pygame.draw.polygon(surf, GOLD, [
            (a1_x,     a1_y2 + 7),
            (a1_x - 5, a1_y2 - 1),
            (a1_x + 5, a1_y2 - 1),
        ])
        a1_lbl = self._font_xs.render('摸牌', True, GOLD)
        surf.blit(a1_lbl, (a1_x + 6, (a1_y1 + a1_y2) // 2 - a1_lbl.get_height() // 2))

        # ── Arrow 2: AI3 discard → Hand (diagonal) ────────────────────────
        a2_x1 = ai3_x + ai3_cw + 4
        a2_y1 = ai3_y0 + ai3_ch // 2
        a2_x2 = hx0 - 6
        a2_y2 = hy + _MC_H // 2
        pygame.draw.line(surf, (150, 220, 150), (a2_x1, a2_y1), (a2_x2, a2_y2), 2)
        ang = math.atan2(a2_y2 - a2_y1, a2_x2 - a2_x1)
        ah = 8
        pygame.draw.polygon(surf, (150, 220, 150), [
            (int(a2_x2), int(a2_y2)),
            (int(a2_x2 - ah * math.cos(ang - 0.5)),
             int(a2_y2 - ah * math.sin(ang - 0.5))),
            (int(a2_x2 - ah * math.cos(ang + 0.5)),
             int(a2_y2 - ah * math.sin(ang + 0.5))),
        ])
        a2_lbl = self._font_xs.render('撿牌', True, (150, 220, 150))
        surf.blit(a2_lbl, ((a2_x1 + a2_x2) // 2 - a2_lbl.get_width() // 2,
                            (a2_y1 + a2_y2) // 2 - a2_lbl.get_height() - 4))

    def _illus_3(self, surf: pygame.Surface) -> None:
        """搶牌胡 — 複製 RonDialog 外觀（靜態插圖）."""
        panel_x, panel_y = 640, 291
        panel_w, panel_h = 440, 178
        pcx = panel_x + panel_w // 2   # 860

        # Semi-transparent dark-purple panel
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((30, 30, 50, 210))
        surf.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(surf, (120, 120, 180),
                         (panel_x, panel_y, panel_w, panel_h), 2, border_radius=10)

        # Title "可以胡牌！" — gold
        title = self._font_lg.render('可以胡牌！', True, (255, 220, 80))
        surf.blit(title, (pcx - title.get_width() // 2, panel_y + 8))

        # Discard description "對方棄牌：♣8" — white
        disc = self._font_md.render('對方棄牌：♣8', True, WHITE)
        surf.blit(disc, (pcx - disc.get_width() // 2, panel_y + 44))

        # Timer bar (static, ~60% progress)
        bar_x = panel_x + 15
        bar_y = panel_y + 96
        bar_w = 410
        pygame.draw.rect(surf, DARK_GRAY, (bar_x, bar_y, bar_w, 10))
        pygame.draw.rect(surf, (80, 200, 80), (bar_x, bar_y, int(bar_w * 0.6), 10))

        # Buttons
        btn_y = panel_y + 130

        # 胡牌 button (dark red)
        hu_x = 765
        pygame.draw.rect(surf, (170, 40, 40), (hu_x, btn_y, 80, 36), border_radius=6)
        pygame.draw.rect(surf, BLACK_COLOR, (hu_x, btn_y, 80, 36), 1, border_radius=6)
        hu_lbl = self._font_md.render('胡牌', True, WHITE)
        surf.blit(hu_lbl, (hu_x + 40 - hu_lbl.get_width() // 2,
                            btn_y + 18 - hu_lbl.get_height() // 2))

        # 跳過 button (dark blue)
        skip_x = 875
        pygame.draw.rect(surf, (80, 80, 140), (skip_x, btn_y, 80, 36), border_radius=6)
        pygame.draw.rect(surf, BLACK_COLOR, (skip_x, btn_y, 80, 36), 1, border_radius=6)
        skip_lbl = self._font_md.render('跳過', True, WHITE)
        surf.blit(skip_lbl, (skip_x + 40 - skip_lbl.get_width() // 2,
                              btn_y + 18 - skip_lbl.get_height() // 2))

    def _illus_4(self, surf: pygame.Surface) -> None:
        """計分 — text-only scoring layout."""
        x = _IX0 + 20
        y = 120

        # 自摸 block
        t = self._font_md.render('自摸', True, GOLD)
        surf.blit(t, (x, y));  y += t.get_height() + 10

        for line, col in [('你          ＋300', GREEN_COLOR),
                           ('其他三方各  −100', RED_COLOR)]:
            s = self._font_sm.render(line, True, col)
            surf.blit(s, (x + 20, y));  y += s.get_height() + 6
        y += 20

        pygame.draw.line(surf, DARK_GRAY, (x, y), (x + 460, y), 1)
        y += 20

        # 搶牌 block
        t = self._font_md.render('搶牌勝利', True, GOLD)
        surf.blit(t, (x, y));  y += t.get_height() + 10

        for line, col in [('你          ＋50', GREEN_COLOR),
                           ('被胡牌者    −50', RED_COLOR)]:
            s = self._font_sm.render(line, True, col)
            surf.blit(s, (x + 20, y));  y += s.get_height() + 6

    def _illus_5(self, surf: pygame.Surface) -> None:
        """魃 — ghost card → ♠7."""
        cy = _ICY

        # Ghost card (full size)
        gx = 700
        gy = cy - CARD_H // 2
        draw_ghost_face(surf, gx, gy, font_md=self._font_md, font_sm=self._font_sm)

        # Arrow
        arrow = self._font_lg.render('→', True, GOLD)
        ax = gx + CARD_W + 16
        surf.blit(arrow, (ax, cy - arrow.get_height() // 2))

        note = self._font_xs.render('可替換', True, WHITE)
        surf.blit(note, (ax + arrow.get_width() // 2 - note.get_width() // 2,
                          cy + arrow.get_height() // 2 + 4))

        # ♠7 card (full size)
        cx2 = ax + arrow.get_width() + 16
        draw_card_face(surf, Card(Suit.SPADES, 7), cx2, cy - CARD_H // 2,
                       font_md=self._font_md, font_sm=self._font_sm)

        lbl = self._font_xs.render('任意牌', True, WHITE)
        surf.blit(lbl, (cx2 + CARD_W // 2 - lbl.get_width() // 2,
                         cy + CARD_H // 2 + 8))

    def _illus_6(self, surf: pygame.Surface) -> None:
        """結束條件 — 4 score bars."""
        bar_max_w = 440
        bar_h     = 36
        gap       = 28
        x_lbl     = _IX0 + 20
        x_bar     = x_lbl + 65
        total_h   = 4 * bar_h + 3 * gap
        y0        = _ICY - total_h // 2

        players = [
            ('你',   1000, GOLD),
            ('AI1',  800,  WHITE),
            ('AI2',  600,  WHITE),
            ('AI3',  0,    WHITE),
        ]

        for i, (name, score, nc) in enumerate(players):
            y = y0 + i * (bar_h + gap)

            lbl = self._font_sm.render(name, True, nc)
            surf.blit(lbl, (x_lbl, y + (bar_h - lbl.get_height()) // 2))

            # Background bar
            pygame.draw.rect(surf, DARK_GRAY, (x_bar, y, bar_max_w, bar_h),
                             border_radius=4)

            # Filled bar
            if score > 0:
                fill_w  = int(bar_max_w * score / 1000)
                bar_col = (60, 160, 80) if name == '你' else (80, 140, 200)
                pygame.draw.rect(surf, bar_col, (x_bar, y, fill_w, bar_h),
                                 border_radius=4)

            # Score number
            sl = self._font_sm.render(str(score), True, WHITE)
            surf.blit(sl, (x_bar + bar_max_w + 10,
                            y + (bar_h - sl.get_height()) // 2))

            # Bankrupt label
            if score == 0:
                bust = self._font_md.render('破產！', True, RED_COLOR)
                surf.blit(bust, (x_bar + bar_max_w // 2 - bust.get_width() // 2,
                                  y + (bar_h - bust.get_height()) // 2))

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Returns 'start' or None."""
        if self._page == 'main':
            if self._btn_start.handle_event(event):
                return 'start'
            if self._btn_rules.handle_event(event):
                self._page      = 'rules'
                self._rule_page = 0
        else:
            p = self._rule_page
            if p == 0:
                if self._btn_back_l.handle_event(event):
                    self._page = 'main'
                elif self._btn_next.handle_event(event):
                    self._rule_page = 1
            elif p == 6:
                if self._btn_prev.handle_event(event):
                    self._rule_page = 5
                elif self._btn_back_r.handle_event(event):
                    self._page = 'main'
            else:
                if self._btn_prev.handle_event(event):
                    self._rule_page -= 1
                elif self._btn_next.handle_event(event):
                    self._rule_page += 1
        return None
