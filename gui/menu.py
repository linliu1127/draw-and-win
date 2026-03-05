"""
Main menu: title screen + rules page.

Pages:
  'main'  – title '自摸' + 開始遊戲 / 規則說明 / 結束遊戲
  'rules' – README.md content + 返回
"""
from __future__ import annotations
import os
import pygame

from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    TABLE_GREEN, TABLE_BORDER,
    WHITE, GOLD, LIGHT_GRAY, DARK_GRAY,
    CENTER_X, CENTER_Y,
)
from gui.button import Button

# ── Font loading (same paths as renderer) ─────────────────────────────────
_FONT_PATHS = [
    'C:/Windows/Fonts/msjh.ttc',
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/NotoSansTC-VF.ttf',
    'C:/Windows/Fonts/kaiu.ttf',
    'C:/Windows/Fonts/mingliu.ttc',
    'C:/Windows/Fonts/simsun.ttc',
]


def _load_font(size: int) -> pygame.font.Font:
    for path in _FONT_PATHS:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except Exception:
                pass
    return pygame.font.SysFont(None, size)


# README path (project root = parent of gui/)
_README = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'README.md')

_BTN_W   = 200
_BTN_H   = 52
_BTN_GAP = 16


class Menu:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._page   = 'main'   # 'main' | 'rules'

        # Fonts
        self._font_hero = _load_font(88)   # huge title
        self._font_lg   = _load_font(32)
        self._font_md   = _load_font(22)
        self._font_sm   = _load_font(17)

        # ── Main menu buttons ──────────────────────────────────────
        bx = CENTER_X - _BTN_W // 2
        by = 330
        self._btn_start = Button(bx, by,                          _BTN_W, _BTN_H, '開始遊戲', font=self._font_md)
        self._btn_rules = Button(bx, by + (_BTN_H + _BTN_GAP),    _BTN_W, _BTN_H, '規則說明', font=self._font_md)
        self._btn_quit  = Button(bx, by + (_BTN_H + _BTN_GAP) * 2, _BTN_W, _BTN_H, '結束遊戲', style='ron', font=self._font_md)

        # ── Rules page back button ─────────────────────────────────
        self._btn_back = Button(
            CENTER_X - _BTN_W // 2, WINDOW_HEIGHT - _BTN_H - 24,
            _BTN_W, _BTN_H, '返回', font=self._font_md,
        )

        self._rules_lines = self._load_rules()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_rules(self) -> list[str]:
        try:
            with open(_README, encoding='utf-8') as f:
                return [line.rstrip('\n') for line in f]
        except Exception:
            return ['（無法讀取規則說明）']

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
        # Hero title
        hero = self._font_hero.render('自摸', True, GOLD)
        surf.blit(hero, (CENTER_X - hero.get_width() // 2, 140))

        # Decorative gold rule under title
        rule_y = 140 + hero.get_height() + 10
        rule_x0, rule_x1 = CENTER_X - 80, CENTER_X + 80
        pygame.draw.line(surf, GOLD, (rule_x0, rule_y), (rule_x1, rule_y), 2)
        pygame.draw.circle(surf, GOLD, (CENTER_X, rule_y), 4)

        self._btn_start.draw(surf)
        self._btn_rules.draw(surf)
        self._btn_quit.draw(surf)

    def _draw_rules(self, surf: pygame.Surface) -> None:
        # Page title
        title = self._font_lg.render('規則說明', True, GOLD)
        surf.blit(title, (CENTER_X - title.get_width() // 2, 22))

        # Divider
        pygame.draw.line(surf, DARK_GRAY, (60, 68), (WINDOW_WIDTH - 60, 68), 1)

        # README lines – basic markdown: # → h1, ## → h2, else body
        body_h = self._font_sm.get_height() + 10
        y = 82
        for line in self._rules_lines:
            stripped = line.strip()
            if not stripped:
                y += body_h // 2
                continue

            if stripped.startswith('## '):
                text  = stripped[3:]
                font  = self._font_md
                color = GOLD
                extra = 4   # extra top padding before sub-heading
            elif stripped.startswith('# '):
                text  = stripped[2:]
                font  = self._font_lg
                color = GOLD
                extra = 8
            else:
                text  = stripped
                font  = self._font_sm
                color = WHITE
                extra = 0

            y += extra
            surf.blit(font.render(text, True, color), (80, y))
            y += font.get_height() + 10

            if y > WINDOW_HEIGHT - _BTN_H - 40:
                break

        self._btn_back.draw(surf)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Returns 'start', 'quit', or None."""
        if self._page == 'main':
            if self._btn_start.handle_event(event):
                return 'start'
            if self._btn_rules.handle_event(event):
                self._page = 'rules'
            if self._btn_quit.handle_event(event):
                return 'quit'
        else:
            if self._btn_back.handle_event(event):
                self._page = 'main'
        return None
