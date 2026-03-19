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
    DISCARD_MAX_H, DISCARD_MAX_V,
)

# Deck position – centred on the table
DECK_X = CENTER_X - CARD_W // 2
DECK_Y = CENTER_Y - CARD_H // 2

# Per-seat discard history layout: (start_x, start_y, step_x, step_y, max_visible)
# Cards overlap so the pile is compact; all seats use the same step.
# Horizontal rows (seats 0, 2) and vertical columns (seats 1, 3) are
# centred on the table such that a 4-card pile sits symmetrically.
#
# _D_STEP = 20 px exposed per card (overlap = CARD dimension - 20)
# _HX / _VY  centre the pile around CENTER_X / CENTER_Y for 4 cards
_D_STEP = 20
_D_MAXH = DISCARD_MAX_H   # horizontal: up to 15 cards → 14*20+70=350 px
_D_MAXV = DISCARD_MAX_V   # vertical:   up to 11 cards → 10*20+100=300 px (fits play area)
_HX = CENTER_X - (3 * _D_STEP + CARD_W)  // 2   # 535
_VY = CENTER_Y - (3 * _D_STEP + CARD_H)  // 2   # 320
DISCARD_ROWS = {
    0: (_HX,  535, _D_STEP, 0,       _D_MAXH),   # human: horizontal
    1: (890,  _VY, 0,       _D_STEP, _D_MAXV),   # AI right: vertical
    2: (_HX,  165, _D_STEP, 0,       _D_MAXH),   # AI top: horizontal
    3: (215,  _VY, 0,       _D_STEP, _D_MAXV),   # AI left: vertical
}

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

# 胡牌 button
BTN_WIN_X = CENTER_X + 220 + 3 * BTN_GAP

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

AI1_LABEL_X  = AI1_CARD_X + CARD_H // 2              # horizontal centre of card column
AI1_LABEL_Y  = AI1_CARD_Y0 + 4 * AI1_CARD_GAP + CARD_W + 8  # below last card

# --- AI 3  (left side, cards rotated 90°) ---
AI3_CARD_X   = 20                            # left edge of rotated card
AI3_CARD_Y0  = CENTER_Y - (5 * (CARD_W + 8)) // 2
AI3_CARD_GAP = CARD_W + 8

AI3_LABEL_X  = AI3_CARD_X + CARD_H // 2
AI3_LABEL_Y  = AI3_CARD_Y0 + 4 * AI3_CARD_GAP + CARD_W + 8

# ------------------------------------------------------------------
# Info panel  (right side, below AI1 cards)
# ------------------------------------------------------------------
INFO_X = WINDOW_WIDTH - 180
INFO_Y = 20

# Score panel  (bottom-left)
SCORE_X = 20
SCORE_Y = 20
SCORE_LINE_H = 22

# Log panel  (bottom-left, beside human cards)
LOG_X = 20
LOG_Y = WINDOW_HEIGHT - CARD_H - 30   # same top-y as human cards; human cards start at x≈409
LOG_LINE_H = 18

# RON window overlay (semi-transparent)
RON_OVERLAY_RECT = (CENTER_X - 220, CENTER_Y - 70, 440, 140)

# Speech bubble layout – each bubble sits beside the player's name label.
# AI2 (top):   bubble to the right of name; tail points left toward name.
# AI1 (right): bubble to the left  of name; tail points right toward name.
# AI3 (left):  bubble to the right of name; tail points left  toward name.
SPEECH_BUBBLE_POS  = {1: (1030, 604), 2: (705, 135), 3: (165, 604)}
SPEECH_BUBBLE_TAIL = {1: 'right',     2: 'left',     3: 'left'}
SPEECH_BUBBLE_W = 116
SPEECH_BUBBLE_H = 40
