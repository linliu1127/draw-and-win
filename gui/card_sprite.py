"""
Card rendering helpers.

Number cards  : show the correct count of suit pips in standard arrangement.
Face cards    : stylised J / Q / K portraits drawn with pygame primitives.
Ace           : one large central suit symbol.
Ghost (魃)    : jester / joker design.
"""
from __future__ import annotations
import pygame
from core.card import Card, Color, Suit
from constants import (
    CARD_W, CARD_H, CARD_RADIUS,
    CARD_FACE_BG, CARD_BACK_BG, CARD_BACK_STRIPE, CARD_GHOST_BG,
    CARD_BORDER_COL, CARD_SEL_BORDER,
    BLACK_COLOR, RED_COLOR, GOLD,
)

# ── face-card palette ─────────────────────────────────────────────
_SKIN    = (255, 210, 170)
_HAIR    = (65,  40,  15)
_CROWN   = (220, 175, 20)
_BEARD   = (130, 90,  40)
_WHITE   = (245, 245, 245)
_SCEPTER = (200, 160, 15)


# ══════════════════════════════════════════════════════════════════
# Shared helper
# ══════════════════════════════════════════════════════════════════

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
        pygame.draw.rect(surf, border_color, rect, border_width,
                         border_radius=radius)


# ══════════════════════════════════════════════════════════════════
# Suit-shape primitives  (centre cx, cy; half-size s)
# ══════════════════════════════════════════════════════════════════

def _diamond(s: pygame.Surface, cx, cy, sz, col):
    pygame.draw.polygon(s, col,
                        [(cx, cy-sz), (cx+sz, cy), (cx, cy+sz), (cx-sz, cy)])


def _heart(s: pygame.Surface, cx, cy, sz, col):
    r   = max(1, int(sz * 0.65))
    lcx = cx - r // 2
    rcx = cx + r // 2
    bcy = cy - sz // 4
    pygame.draw.circle(s, col, (lcx, bcy), r)
    pygame.draw.circle(s, col, (rcx, bcy), r)
    pygame.draw.polygon(s, col,
                        [(lcx - r + 1, bcy), (rcx + r - 1, bcy), (cx, cy + sz)])


def _spade(s: pygame.Surface, cx, cy, sz, col):
    r   = max(1, int(sz * 0.65))
    lcx = cx - r // 2
    rcx = cx + r // 2
    bcy = cy + sz // 4
    pygame.draw.circle(s, col, (lcx, bcy), r)
    pygame.draw.circle(s, col, (rcx, bcy), r)
    pygame.draw.polygon(s, col,
                        [(lcx - r + 1, bcy), (rcx + r - 1, bcy), (cx, cy - sz)])
    sw = max(2, sz // 4)
    sh = max(3, sz // 3)
    bw = max(4, int(sz * 1.1))
    bh = max(2, sz // 4)
    pygame.draw.rect(s, col, (cx - sw//2, bcy + r - 1, sw, sh))
    pygame.draw.rect(s, col, (cx - bw//2, bcy + r + sh - bh - 1, bw, bh))


def _club(s: pygame.Surface, cx, cy, sz, col):
    r = max(1, int(sz * 0.60))
    pygame.draw.circle(s, col, (cx,         cy - r // 2), r)
    pygame.draw.circle(s, col, (cx - r + 1, cy + r // 2), r)
    pygame.draw.circle(s, col, (cx + r - 1, cy + r // 2), r)
    sw = max(2, sz // 4)
    sh = max(3, sz // 3)
    bw = max(4, int(sz * 1.1))
    bh = max(2, sz // 4)
    st = cy + r // 2 + r - 1
    pygame.draw.rect(s, col, (cx - sw//2, st, sw, sh))
    pygame.draw.rect(s, col, (cx - bw//2, st + sh - bh, bw, bh))


_SUIT_FN = {
    Suit.DIAMONDS: _diamond,
    Suit.HEARTS:   _heart,
    Suit.SPADES:   _spade,
    Suit.CLUBS:    _club,
}

_CORNER_S = 5    # corner pip half-size
_ACE_S    = 22   # ace large pip half-size


def _suit(surf, suit, cx, cy, sz, color):
    fn = _SUIT_FN.get(suit)
    if fn:
        fn(surf, cx, cy, sz, color)


# ══════════════════════════════════════════════════════════════════
# Pip layouts for number cards  (dx, dy offsets from card x, y)
# ══════════════════════════════════════════════════════════════════

# Pip span: top=y+20, bottom=y+80 (60px), centred at y+50 (card centre).
# Columns: L=x+22  C=x+35  R=x+48
_PIP_LAYOUTS: dict[int, list[tuple[int, int]]] = {
    #       ← pip centres given as (dx, dy) from card origin ──────────
    2:  [(35, 20), (35, 80)],
    3:  [(35, 20), (35, 50), (35, 80)],
    4:  [(26, 20), (44, 20),
         (26, 80), (44, 80)],
    5:  [(26, 20), (44, 20), (35, 50),
         (26, 80), (44, 80)],
    6:  [(26, 20), (44, 20),
         (26, 50), (44, 50),
         (26, 80), (44, 80)],
    7:  [(26, 20), (44, 20), (35, 40),
         (26, 55), (44, 55),
         (26, 80), (44, 80)],
    8:  [(26, 20), (44, 20), (35, 38),
         (26, 50), (44, 50), (35, 62),
         (26, 80), (44, 80)],
    9:  [(26, 20), (44, 20),
         (26, 40), (44, 40), (35, 50),
         (26, 60), (44, 60),
         (26, 80), (44, 80)],
    10: [(26, 20), (44, 20), (35, 30),
         (26, 40), (44, 40),
         (26, 60), (44, 60), (35, 70),
         (26, 80), (44, 80)],
}

_PIP_SIZE: dict[int, int] = {
    2: 7, 3: 7, 4: 6, 5: 6, 6: 6, 7: 5, 8: 5, 9: 5, 10: 5,
}


# ══════════════════════════════════════════════════════════════════
# Face-card portrait helpers
# ══════════════════════════════════════════════════════════════════

def _draw_jack(surf, x, y, ink):
    """Jack – jester with two-tone hat."""
    cx = x + CARD_W // 2
    # Jester hat  (left half = ink, right half = lighter)
    lighter = tuple(min(255, c + 70) for c in ink)
    pygame.draw.polygon(surf, ink,    [(cx-9, y+41), (cx-3, y+29), (cx+1, y+41)])
    pygame.draw.polygon(surf, lighter,[(cx+1, y+41), (cx+3, y+29), (cx+9, y+41)])
    # Hat bells
    pygame.draw.circle(surf, _CROWN, (cx-3, y+29), 3)
    pygame.draw.circle(surf, _CROWN, (cx+3, y+29), 3)
    # Head
    pygame.draw.circle(surf, _SKIN, (cx, y+50), 9)
    # Hair along top of head
    pygame.draw.ellipse(surf, _HAIR, (cx-9, y+41, 18, 8))
    # Body tunic
    pygame.draw.polygon(surf, ink,
                        [(cx-11, y+60), (cx+11, y+60), (cx+14, y+73), (cx-14, y+73)])
    # White collar
    pygame.draw.polygon(surf, _WHITE,
                        [(cx-9, y+60), (cx, y+67), (cx+9, y+60)])


def _draw_queen(surf, x, y, ink):
    """Queen – lady with crown and gown."""
    cx = x + CARD_W // 2
    # Crown
    crown_pts = [
        (cx-10, y+41), (cx-10, y+32),
        (cx-5,  y+36), (cx,    y+29),
        (cx+5,  y+36), (cx+10, y+32),
        (cx+10, y+41),
    ]
    pygame.draw.polygon(surf, _CROWN, crown_pts)
    pygame.draw.circle(surf, (220, 50, 50), (cx, y+31), 2)     # crown jewel
    # Long hair
    pygame.draw.rect(surf, _HAIR, (cx-12, y+43, 4, 22))
    pygame.draw.rect(surf, _HAIR, (cx+8,  y+43, 4, 22))
    # Head
    pygame.draw.circle(surf, _SKIN, (cx, y+50), 9)
    # Gown
    pygame.draw.polygon(surf, ink,
                        [(cx-11, y+60), (cx+11, y+60), (cx+16, y+73), (cx-16, y+73)])
    # White bodice accent
    pygame.draw.polygon(surf, _WHITE,
                        [(cx-9, y+60), (cx, y+68), (cx+9, y+60)])


def _draw_king(surf, x, y, ink):
    """King – man with elaborate crown, beard, and sceptre."""
    cx = x + CARD_W // 2
    # Crown
    crown_pts = [
        (cx-11, y+40), (cx-11, y+30),
        (cx-6,  y+34), (cx-3,  y+27),
        (cx,    y+31), (cx+3,  y+27),
        (cx+6,  y+34), (cx+11, y+30),
        (cx+11, y+40),
    ]
    pygame.draw.polygon(surf, _CROWN, crown_pts)
    # Crown jewels
    pygame.draw.circle(surf, (220, 50, 50),  (cx,   y+29), 3)
    pygame.draw.circle(surf, (50,  50, 220), (cx-3, y+28), 2)
    pygame.draw.circle(surf, (50, 200, 50),  (cx+3, y+28), 2)
    # Head
    pygame.draw.circle(surf, _SKIN, (cx, y+49), 9)
    # Beard
    pygame.draw.ellipse(surf, _BEARD, (cx-8, y+53, 16, 12))
    # Sceptre
    pygame.draw.line(surf, _SCEPTER, (cx+10, y+54), (cx+15, y+72), 2)
    pygame.draw.circle(surf, _SCEPTER, (cx+10, y+53), 3)
    # Robe
    pygame.draw.polygon(surf, ink,
                        [(cx-12, y+60), (cx+12, y+60), (cx+17, y+73), (cx-17, y+73)])
    # White collar
    pygame.draw.polygon(surf, _WHITE,
                        [(cx-9, y+60), (cx, y+67), (cx+9, y+60)])


# ══════════════════════════════════════════════════════════════════
# Card back
# ══════════════════════════════════════════════════════════════════

def draw_card_back(
    surface: pygame.Surface,
    x: int, y: int,
    *,
    rotated: bool = False,
) -> None:
    w, h = (CARD_H, CARD_W) if rotated else (CARD_W, CARD_H)
    rect = pygame.Rect(x, y, w, h)
    _draw_rounded_rect(surface, CARD_BACK_BG, rect, CARD_RADIUS, CARD_BORDER_COL)
    for i in range(0, w, 8):
        pygame.draw.line(surface, CARD_BACK_STRIPE,
                         (x + i, y + 2), (x + i, y + h - 3), 1)


# ══════════════════════════════════════════════════════════════════
# Card face (regular)
# ══════════════════════════════════════════════════════════════════

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
        draw_ghost_face(surface, x, y,
                        font_md=font_md, font_sm=font_sm, selected=selected)
        return

    # ── card background ───────────────────────────────────────────
    rect       = pygame.Rect(x, y, CARD_W, CARD_H)
    border_col = CARD_SEL_BORDER if selected else CARD_BORDER_COL
    bw         = 3 if selected else 2
    _draw_rounded_rect(surface, CARD_FACE_BG, rect, CARD_RADIUS, border_col, bw)

    ink = BLACK_COLOR if card.color == Color.BLACK else RED_COLOR

    # ── top-left corner ───────────────────────────────────────────
    rank_tl = font_sm.render(card.rank_symbol, True, ink)
    rw, rh  = rank_tl.get_width(), rank_tl.get_height()
    tx0, ty0 = x + 4, y + 2
    surface.blit(rank_tl, (tx0, ty0))
    _suit(surface, card.suit, tx0 + rw//2, ty0 + rh + _CORNER_S + 1, _CORNER_S, ink)

    # ── bottom-right corner ───────────────────────────────────────
    rank_br  = font_sm.render(card.rank_symbol, True, ink)
    rw2, rh2 = rank_br.get_width(), rank_br.get_height()
    tx2 = x + CARD_W - rw2 - 4
    ty2 = y + CARD_H - rh2 - 2
    surface.blit(rank_br, (tx2, ty2))
    _suit(surface, card.suit, tx2 + rw2//2, ty2 - _CORNER_S - 1, _CORNER_S, ink)

    # ── centre content ────────────────────────────────────────────
    rank = card.rank

    if rank == 1:
        # Ace: one large central suit symbol
        _suit(surface, card.suit, x + CARD_W//2, y + CARD_H//2, _ACE_S, ink)

    elif rank in _PIP_LAYOUTS:
        # Number card: correct pip arrangement
        sz = _PIP_SIZE[rank]
        for dx, dy in _PIP_LAYOUTS[rank]:
            _suit(surface, card.suit, x + dx, y + dy, sz, ink)

    elif rank == 11:   # Jack
        _draw_jack(surface, x, y, ink)

    elif rank == 12:   # Queen
        _draw_queen(surface, x, y, ink)

    elif rank == 13:   # King
        _draw_king(surface, x, y, ink)


# ══════════════════════════════════════════════════════════════════
# Ghost (魃) card face – jester / joker design
# ══════════════════════════════════════════════════════════════════

def draw_ghost_face(
    surface: pygame.Surface,
    x: int, y: int,
    *,
    font_md: pygame.font.Font,
    font_sm: pygame.font.Font,
    selected: bool = False,
) -> None:
    rect       = pygame.Rect(x, y, CARD_W, CARD_H)
    border_col = CARD_SEL_BORDER if selected else (160, 80, 220)
    _draw_rounded_rect(surface, CARD_GHOST_BG, rect, CARD_RADIUS, border_col, 2)

    cx = x + CARD_W  // 2
    cy = y + CARD_H  // 2

    # ── two-colour jester hat ─────────────────────────────────────
    # left lobe (red)
    pygame.draw.polygon(surface, (200, 20,  20),
                        [(cx-13, cy-8), (cx-6, cy-30), (cx+1, cy-8)])
    # right lobe (teal)
    pygame.draw.polygon(surface, (20,  160, 180),
                        [(cx-1,  cy-8), (cx+6, cy-30), (cx+13, cy-8)])
    # hat brim bar
    pygame.draw.rect(surface, (160, 0, 220), (cx-14, cy-10, 28, 6), border_radius=3)
    # bells at hat tips
    pygame.draw.circle(surface, GOLD, (cx-6, cy-30), 4)
    pygame.draw.circle(surface, GOLD, (cx+6, cy-30), 4)

    # ── jester face ───────────────────────────────────────────────
    pygame.draw.circle(surface, _SKIN, (cx, cy+8), 13)
    # rosy cheeks
    pygame.draw.circle(surface, (230, 120, 120), (cx-7,  cy+11), 4)
    pygame.draw.circle(surface, (230, 120, 120), (cx+7,  cy+11), 4)
    # eyes
    pygame.draw.circle(surface, (30, 30, 30),   (cx-4,  cy+5),  2)
    pygame.draw.circle(surface, (30, 30, 30),   (cx+4,  cy+5),  2)
    # big grin
    pygame.draw.arc(surface, (180, 30, 30),
                    pygame.Rect(cx-7, cy+9, 14, 8), 3.14, 0.0, 2)

    # ── collar ────────────────────────────────────────────────────
    for i, col in enumerate([(200,20,20), (20,160,180), (200,20,20)]):
        pygame.draw.circle(surface, col, (cx - 8 + i*8, cy+22), 4)

    # ── 魃 labels in corners ──────────────────────────────────────
    lbl = font_sm.render('魃', True, GOLD)
    surface.blit(lbl, (x + 3, y + 3))
    surface.blit(lbl, (x + CARD_W - lbl.get_width() - 3,
                        y + CARD_H - lbl.get_height() - 3))
