"""
Overlay dialogs: RON window, round-end result, game-over screen.
These are drawn ON TOP of the main renderer.
"""
from __future__ import annotations
import pygame
from constants import (
    WHITE, BLACK_COLOR, DARK_GRAY, LIGHT_GRAY,
    BTN_W, BTN_H,
    CENTER_X, CENTER_Y,
)
from gui.button import Button


# Semi-transparent overlay colour
_OVERLAY_BG   = (0, 0, 0, 160)      # RGBA
_PANEL_BG     = (40, 40, 60)
_PANEL_BORDER = (120, 120, 180)


def _panel(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draw a dark semi-transparent panel."""
    overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
    overlay.fill((30, 30, 50, 210))
    surface.blit(overlay, rect.topleft)
    pygame.draw.rect(surface, _PANEL_BORDER, rect, 2, border_radius=10)


class RonDialog:
    """
    Shown when a player can RON.  Displays the winning card and a countdown.
    Buttons: 胡牌 (ron)  |  跳過 (pass)
    """

    def __init__(self, font_lg, font_md, font_sm) -> None:
        self._font_lg = font_lg
        self._font_md = font_md
        self._font_sm = font_sm

        cx = 600
        cy = 400
        w, h = 440, 178
        px = cx - w // 2
        py = cy - h // 2

        self.rect = pygame.Rect(px, py, w, h)

        btn_y = py + h - BTN_H - 12
        self.btn_ron  = Button(cx - BTN_W - 15, btn_y, BTN_W, BTN_H, '胡牌',  style='ron',  font=font_md)
        self.btn_pass = Button(cx + 15,          btn_y, BTN_W, BTN_H, '跳過',  style='skip', font=font_md)

    def draw(
        self,
        surface: pygame.Surface,
        discard_card_str: str,
        countdown_ms: int,
        claimant_names: list[str] | None = None,
    ) -> None:
        _panel(surface, self.rect)

        # Title
        title = self._font_lg.render('可以胡牌！', True, (255, 220, 80))
        tx = self.rect.x + (self.rect.w - title.get_width()) // 2
        surface.blit(title, (tx, self.rect.y + 8))

        # Card info
        card_txt = self._font_md.render(f'對方棄牌：{discard_card_str}', True, WHITE)
        cx2 = self.rect.x + (self.rect.w - card_txt.get_width()) // 2
        surface.blit(card_txt, (cx2, self.rect.y + 44))

        # Multi-Ron notice (shown when multiple claimants exist)
        if claimant_names and len(claimant_names) > 1:
            others = '、'.join(claimant_names[1:])
            notice_str = f'競爭：{others} 也胡牌，但你順位最近'
            notice = self._font_sm.render(notice_str, True, (255, 160, 60))
            nx = self.rect.x + (self.rect.w - notice.get_width()) // 2
            surface.blit(notice, (nx, self.rect.y + 70))

        # Countdown bar
        secs = max(0, countdown_ms / 1000)
        bar_w = self.rect.w - 30
        bar_x = self.rect.x + 15
        bar_y = self.rect.y + 96
        pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_w, 10), border_radius=5)
        fill = int(bar_w * secs / 5)
        col  = (80, 200, 80) if secs > 2 else (200, 100, 30)
        pygame.draw.rect(surface, col, (bar_x, bar_y, fill, 10), border_radius=5)

        timer_txt = self._font_sm.render(f'{secs:.1f}s', True, LIGHT_GRAY)
        surface.blit(timer_txt, (bar_x + bar_w - timer_txt.get_width(), bar_y + 12))

        self.btn_ron.draw(surface)
        self.btn_pass.draw(surface)

    def handle_event(self, event) -> str | None:
        """Returns 'ron', 'pass', or None."""
        if self.btn_ron.handle_event(event):
            return 'ron'
        if self.btn_pass.handle_event(event):
            return 'pass'
        return None


class RoundEndDialog:
    """
    Shown at ROUND_END: displays result and next-round / quit buttons.
    """

    def __init__(self, font_lg, font_md, font_sm) -> None:
        self._font_lg = font_lg
        self._font_md = font_md
        self._font_sm = font_sm

        cx, cy = 600, 400
        w, h   = 520, 280
        self.rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

        btn_y = self.rect.bottom - BTN_H - 14
        self.btn_next = Button(cx - BTN_W - 15, btn_y, BTN_W, BTN_H, '下一局', font=font_md)
        self.btn_quit = Button(cx + 15,          btn_y, BTN_W, BTN_H, '結束',  style='ron', font=font_md)

    def draw(
        self,
        surface: pygame.Surface,
        winner_name: str | None,
        win_type: str | None,
        scores: list[tuple[str, int]],
        bankrupt_names: list[str],
    ) -> None:
        _panel(surface, self.rect)

        # Title
        if win_type == 'draw':
            title_str = '流局'
            title_col = (180, 180, 80)
        elif winner_name:
            verb = '自摸！' if win_type == 'tsumo' else '胡牌！'
            title_str = f'{winner_name} {verb}'
            title_col = (255, 220, 80)
        else:
            title_str = '本局結束'
            title_col = WHITE

        title = self._font_lg.render(title_str, True, title_col)
        tx = self.rect.x + (self.rect.w - title.get_width()) // 2
        surface.blit(title, (tx, self.rect.y + 12))

        # Scores
        y = self.rect.y + 60
        for name, score in scores:
            line = self._font_md.render(f'{name}：{score} 點', True, WHITE)
            surface.blit(line, (self.rect.x + 40, y))
            y += 30

        # Bankruptcy warning
        if bankrupt_names:
            warn = self._font_sm.render(
                '破產：' + '、'.join(bankrupt_names) + '  遊戲結束！',
                True, (255, 80, 80)
            )
            wx = self.rect.x + (self.rect.w - warn.get_width()) // 2
            surface.blit(warn, (wx, self.rect.bottom - BTN_H - 40))

        self.btn_next.draw(surface)
        self.btn_quit.draw(surface)

    def handle_event(self, event) -> str | None:
        """Returns 'next', 'quit', or None."""
        if self.btn_next.handle_event(event):
            return 'next'
        if self.btn_quit.handle_event(event):
            return 'quit'
        return None


class GameOverDialog:
    """Final screen showing all scores."""

    def __init__(self, font_lg, font_md) -> None:
        self._font_lg = font_lg
        self._font_md = font_md

        cx, cy = 600, 400
        w, h   = 500, 320
        self.rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

        self.btn_quit = Button(cx - BTN_W // 2, self.rect.bottom - BTN_H - 14,
                               BTN_W, BTN_H, '結束遊戲', style='ron', font=font_md)

    def draw(
        self,
        surface: pygame.Surface,
        scores: list[tuple[str, int]],
    ) -> None:
        _panel(surface, self.rect)

        title = self._font_lg.render('遊戲結束', True, (255, 220, 80))
        tx = self.rect.x + (self.rect.w - title.get_width()) // 2
        surface.blit(title, (tx, self.rect.y + 14))

        sorted_scores = sorted(scores, key=lambda x: -x[1])
        y = self.rect.y + 70
        medals = ['🥇', '🥈', '🥉', '  ']
        for i, (name, score) in enumerate(sorted_scores):
            medal = medals[min(i, 3)]
            line  = self._font_md.render(f'{medal} {name}：{score} 點', True, WHITE)
            surface.blit(line, (self.rect.x + 50, y))
            y += 36

        self.btn_quit.draw(surface)

    def handle_event(self, event) -> bool:
        return self.btn_quit.handle_event(event)
