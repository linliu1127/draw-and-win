"""
Layout constants for the 1200×800 game window.

Seat positions
  0 = Human   – bottom
  1 = AI Right – right
  2 = AI Top   – top
  3 = AI Left  – left
"""
from constants import (
    CARD_W, CARD_H, WINDOW_WIDTH, WINDOW_HEIGHT,
    BTN_W, BTN_H, CENTER_X, CENTER_Y,
)

# Deck and discard pile positions (top-left corner of the card rect)
DECK_X    = CENTER_X + 20
DECK_Y    = CENTER_Y - CARD_H // 2

DISCARD_X = CENTER_X - CARD_W - 20
DISCARD_Y = CENTER_Y - CARD_H // 2

# ------------------------------------------------------------------
# Human player  (bottom, cards shown face-up)
# ------------------------------------------------------------------
HUMAN_CARD_Y    = WINDOW_HEIGHT - CARD_H - 30   # card top-y
HUMAN_CARD_GAP  = CARD_W + 8                     # x-step between cards
# 5 cards centred horizontally
HUMAN_CARD_X0   = CENTER_X - (5 * HUMAN_CARD_GAP) // 2 + 4
HUMAN_CARD_LIFT = 20          # how much a selected card rises

HUMAN_LABEL_X = 20
HUMAN_LABEL_Y = WINDOW_HEIGHT - 28

# ------------------------------------------------------------------
# Buttons (bottom-right area)
# ------------------------------------------------------------------
BTN_Y = WINDOW_HEIGHT - BTN_H - 10
BTN_GAP = BTN_W + 8

# Four action buttons: 摸牌 撿牌 棄牌 胡牌
BTN_DRAW_X    = CENTER_X + 220
BTN_PICK_X    = BTN_DRAW_X    + BTN_GAP
BTN_DISCARD_X = BTN_PICK_X    + BTN_GAP
BTN_WIN_X     = BTN_DISCARD_X + BTN_GAP

# RON / pass buttons (shown in RON_WINDOW state, centred)
BTN_RON_X    = CENTER_X - BTN_W - 20
BTN_PASS_X   = CENTER_X + 20
BTN_RON_Y    = CENTER_Y - BTN_H // 2

# Round-end buttons
BTN_NEXTROUND_X = CENTER_X - BTN_W - 20
BTN_QUIT_X      = CENTER_X + 20
BTN_NEXTROUND_Y = CENTER_Y + 80

# ------------------------------------------------------------------
# AI players  (cards shown face-down)
# ------------------------------------------------------------------

# --- AI 2  (top, same orientation as human) ---
AI2_CARD_Y   = 20
AI2_CARD_GAP = CARD_W + 8
AI2_CARD_X0  = CENTER_X - (5 * AI2_CARD_GAP) // 2 + 4

AI2_LABEL_X  = WINDOW_WIDTH // 2
AI2_LABEL_Y  = AI2_CARD_Y + CARD_H + 6

# --- AI 1  (right side, cards rotated 90°) ---
# After 90° rotation a card is CARD_H wide × CARD_W tall
AI1_CARD_X   = WINDOW_WIDTH - CARD_H - 20   # left edge of rotated card
AI1_CARD_Y0  = CENTER_Y - (5 * (CARD_W + 8)) // 2
AI1_CARD_GAP = CARD_W + 8

AI1_LABEL_X  = WINDOW_WIDTH - 10
AI1_LABEL_Y  = CENTER_Y

# --- AI 3  (left side, cards rotated 90°) ---
AI3_CARD_X   = 20                            # left edge of rotated card
AI3_CARD_Y0  = CENTER_Y - (5 * (CARD_W + 8)) // 2
AI3_CARD_GAP = CARD_W + 8

AI3_LABEL_X  = 10
AI3_LABEL_Y  = CENTER_Y

# ------------------------------------------------------------------
# Info panel  (right side, below AI1 cards)
# ------------------------------------------------------------------
INFO_X = WINDOW_WIDTH - 180
INFO_Y = 20

# Score panel  (bottom-left)
SCORE_X = 20
SCORE_Y = 20
SCORE_LINE_H = 22

# Log panel  (bottom-centre-left)
LOG_X = 20
LOG_Y = WINDOW_HEIGHT // 2
LOG_LINE_H = 18

# RON window overlay (semi-transparent)
RON_OVERLAY_RECT = (CENTER_X - 220, CENTER_Y - 70, 440, 140)
