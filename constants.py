# Window dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Card dimensions
CARD_W = 70
CARD_H = 100
CARD_RADIUS = 6

# RGB Colors
WHITE       = (255, 255, 255)
BLACK_COLOR = (0,   0,   0)
RED_COLOR   = (210, 40,  40)
GREEN_COLOR = (0,   160, 0)
BLUE_COLOR  = (50,  100, 220)
YELLOW      = (255, 220, 0)
GRAY        = (160, 160, 160)
DARK_GRAY   = (80,  80,  80)
LIGHT_GRAY  = (230, 230, 230)
DARK_GREEN  = (30,  100, 30)
PURPLE      = (130, 0,   200)
GOLD        = (220, 180, 0)
ORANGE      = (230, 120, 30)

# Table color
TABLE_GREEN  = (35, 100, 50)
TABLE_BORDER = (25, 75, 35)

# Card face / back
CARD_FACE_BG    = (255, 250, 240)
CARD_BACK_BG    = (40,  70,  170)
CARD_BACK_STRIPE= (60,  100, 210)
CARD_GHOST_BG   = (80,  0,   130)
CARD_BORDER_COL = (90,  90,  90)
CARD_SEL_BORDER = (255, 220, 0)

# Button colors
BTN_NORMAL  = (70,  130, 80)
BTN_HOVER   = (90,  160, 100)
BTN_PRESSED = (50,  100, 60)
BTN_DISABLED= (100, 100, 100)
BTN_TEXT    = (255, 255, 255)

BTN_RON_NORMAL  = (170, 40,  40)
BTN_RON_HOVER   = (200, 60,  60)

BTN_SKIP_NORMAL = (80,  80,  140)
BTN_SKIP_HOVER  = (100, 100, 170)

# Game settings
STARTING_SCORE    = 1000
TSUMO_WIN_AMOUNT  = 100
RON_WIN_AMOUNT    = 50

# Timing (milliseconds)
FPS              = 60
AI_DRAW_DELAY    = 2000
AI_DISCARD_DELAY = 2000
AI_RON_DELAY     = 600
RON_WINDOW_TIME  = 5000
AI_WIN_DISPLAY_MS  = 1000   # 自摸/夠 顯示 1 秒後才結算
SPEECH_BUBBLE_DUR  = 2500   # 出牌泡泡顯示時間
SPEECH_BUBBLE_PICK = 2000   # 撿牌泡泡顯示時間

# Font sizes
FONT_LG  = 32
FONT_MD  = 22
FONT_SM  = 16
FONT_XSM = 13

# Button dimensions
BTN_W = 80
BTN_H = 36

# Tenpai indicator dot radius
TENPAI_DOT_R = 7

# Discard history max visible cards per seat orientation
# Matches the DISCARD_ROWS max_visible values in gui/layout.py
DISCARD_MAX_H = 15   # horizontal rows  (seats 0, 2)
DISCARD_MAX_V = 11   # vertical columns (seats 1, 3)

# Window centre (derived)
CENTER_X = WINDOW_WIDTH  // 2
CENTER_Y = WINDOW_HEIGHT // 2

# Player seat positions (indices)
SEAT_HUMAN = 0
SEAT_AI1   = 1  # right
SEAT_AI2   = 2  # top
SEAT_AI3   = 3  # left
