"""Simple clickable button component."""
from __future__ import annotations
import pygame
from constants import (
    BTN_NORMAL, BTN_HOVER, BTN_PRESSED, BTN_DISABLED, BTN_TEXT,
    BTN_RON_NORMAL, BTN_RON_HOVER,
    BTN_SKIP_NORMAL, BTN_SKIP_HOVER,
    WHITE,
)

_STYLE_NORMAL = (BTN_NORMAL,  BTN_HOVER,  BTN_PRESSED)
_STYLE_RON    = (BTN_RON_NORMAL, BTN_RON_HOVER,  BTN_PRESSED)
_STYLE_SKIP   = (BTN_SKIP_NORMAL, BTN_SKIP_HOVER, BTN_PRESSED)


class Button:
    """Axis-aligned rectangular button."""

    def __init__(
        self,
        x: int, y: int, w: int, h: int,
        label: str,
        *,
        style: str = 'normal',   # 'normal' | 'ron' | 'skip'
        font: pygame.font.Font | None = None,
    ) -> None:
        self.rect    = pygame.Rect(x, y, w, h)
        self.label   = label
        self.enabled = True
        self._style  = style
        self._font   = font
        self._held   = False

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def set_font(self, font: pygame.font.Font) -> None:
        self._font = font

    def enable(self)  -> None: self.enabled = True
    def disable(self) -> None: self.enabled = False

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if button was clicked (mouse-up inside)."""
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._held = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            held = self._held
            self._held = False
            if held and self.rect.collidepoint(event.pos):
                return True
        return False

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if not self._font:
            return

        if not self.enabled:
            col = BTN_DISABLED
        else:
            if self._style == 'ron':
                cols = _STYLE_RON
            elif self._style == 'skip':
                cols = _STYLE_SKIP
            else:
                cols = _STYLE_NORMAL

            mouse = pygame.mouse.get_pos()
            if self._held and self.rect.collidepoint(mouse):
                col = cols[2]
            elif self.rect.collidepoint(mouse) and self.enabled:
                col = cols[1]
            else:
                col = cols[0]

        pygame.draw.rect(surface, col, self.rect, border_radius=6)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 1, border_radius=6)

        text_surf = self._font.render(self.label, True, BTN_TEXT)
        tx = self.rect.x + (self.rect.w - text_surf.get_width())  // 2
        ty = self.rect.y + (self.rect.h - text_surf.get_height()) // 2
        surface.blit(text_surf, (tx, ty))
