"""
Card rendering helpers.

draw_card_face(surface, card, x, y, *, selected=False, font_md, font_sm)
draw_card_back(surface, x, y, *, rotated=False)
draw_ghost_face(surface, card, x, y, *, font_md, font_sm)
"""
from __future__ import annotations
import pygame
from core.card import Card, Color, Suit
from constants import (
    CARD_W, CARD_H, CARD_RADIUS,
    CARD_FACE_BG, CARD_BACK_BG, CARD_BACK_STRIPE, CARD_GHOST_BG,
    CARD_BORDER_COL, CARD_SEL_BORDER,
    BLACK_COLOR, RED_COLOR, GOLD, WHITE,
)


def _draw_rounded_rect(
    surf: pygame.Surface,
    color: tuple,
    rect: pygame.Rect,
    radius: int,
    border_color: tuple | None = None,
    border_width: int = 2,
) -> None:
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surf, border_color, rect, border_width, border_radius=radius)


# ------------------------------------------------------------------
# Face-down back
# ------------------------------------------------------------------

def draw_card_back(
    surface: pygame.Surface,
    x: int, y: int,
    *,
    rotated: bool = False,
) -> None:
    """Draw a face-down card.  If rotated=True the card is 90° clockwise (CARD_H × CARD_W)."""
    w, h = (CARD_H, CARD_W) if rotated else (CARD_W, CARD_H)
    r    = pygame.Rect(x, y, w, h)
    _draw_rounded_rect(surface, CARD_BACK_BG, r, CARD_RADIUS, CARD_BORDER_COL)
    # stripe pattern
    for i in range(0, w, 8):
        pygame.draw.line(surface, CARD_BACK_STRIPE, (x + i, y + 2), (x + i, y + h - 3), 1)


# ------------------------------------------------------------------
# Face-up regular card
# ------------------------------------------------------------------

def draw_card_face(
    surface: pygame.Surface,
    card: Card,
    x: int, y: int,
    *,
    selected: bool = False,
    font_md: pygame.font.Font,
    font_sm: pygame.font.Font,
) -> None:
    if card.is_ghost:
        draw_ghost_face(surface, x, y, font_md=font_md, font_sm=font_sm, selected=selected)
        return

    r          = pygame.Rect(x, y, CARD_W, CARD_H)
    border_col = CARD_SEL_BORDER if selected else CARD_BORDER_COL
    bw         = 3 if selected else 2
    _draw_rounded_rect(surface, CARD_FACE_BG, r, CARD_RADIUS, border_col, bw)

    ink = BLACK_COLOR if card.color == Color.BLACK else RED_COLOR

    # Rank + suit in top-left
    rank_surf = font_sm.render(card.rank_symbol, True, ink)
    suit_surf = font_sm.render(card.suit_symbol, True, ink)
    surface.blit(rank_surf, (x + 4, y + 2))
    surface.blit(suit_surf, (x + 4, y + 2 + rank_surf.get_height()))

    # Large suit symbol centred
    big_suit = font_md.render(card.suit_symbol, True, ink)
    bsx = x + (CARD_W - big_suit.get_width())  // 2
    bsy = y + (CARD_H - big_suit.get_height()) // 2
    surface.blit(big_suit, (bsx, bsy))

    # Rank + suit in bottom-right (rotated 180° – just mirrored position)
    rank_surf2 = font_sm.render(card.rank_symbol, True, ink)
    suit_surf2 = font_sm.render(card.suit_symbol, True, ink)
    rx = x + CARD_W - rank_surf2.get_width()  - 4
    ry = y + CARD_H - rank_surf2.get_height() - suit_surf2.get_height() - 2
    surface.blit(rank_surf2, (rx, ry))
    surface.blit(suit_surf2, (rx, ry + rank_surf2.get_height()))


# ------------------------------------------------------------------
# Ghost (魃) card face
# ------------------------------------------------------------------

def draw_ghost_face(
    surface: pygame.Surface,
    x: int, y: int,
    *,
    font_md: pygame.font.Font,
    font_sm: pygame.font.Font,
    selected: bool = False,
) -> None:
    r          = pygame.Rect(x, y, CARD_W, CARD_H)
    border_col = CARD_SEL_BORDER if selected else (160, 80, 220)
    bw         = 3 if selected else 2
    _draw_rounded_rect(surface, CARD_GHOST_BG, r, CARD_RADIUS, border_col, bw)

    # 魃 character in gold
    ghost_surf = font_md.render('魃', True, GOLD)
    gx = x + (CARD_W - ghost_surf.get_width())  // 2
    gy = y + (CARD_H - ghost_surf.get_height()) // 2
    surface.blit(ghost_surf, (gx, gy))

    # Small label
    lbl = font_sm.render('鬼', True, GOLD)
    surface.blit(lbl, (x + 4, y + 4))
