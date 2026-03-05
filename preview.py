"""
Card preview – shows all 54 cards in a window.
Run from the self-draw_win directory:  python preview.py
Close the window (X button) to exit.
"""
import os, sys, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pygame
    from core.card import Card, Suit
    from gui.card_sprite import draw_card_face
    from constants import TABLE_GREEN, FONT_SM, FONT_MD, CARD_W, CARD_H

    GAP_X = CARD_W + 6
    GAP_Y = CARD_H + 10
    X0, Y0 = 15, 10
    W = X0 * 2 + 13 * GAP_X
    H = Y0 * 2 + 5  * GAP_Y

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Card Preview")

    font_paths = [
        'C:/Windows/Fonts/msjh.ttc',
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/kaiu.ttf',
        'C:/Windows/Fonts/mingliu.ttc',
    ]
    font_path = next((p for p in font_paths if os.path.exists(p)), None)
    font_md = pygame.font.Font(font_path, FONT_MD)
    font_sm = pygame.font.Font(font_path, FONT_SM)

    screen.fill(TABLE_GREEN)

    suits = [Suit.SPADES, Suit.CLUBS, Suit.HEARTS, Suit.DIAMONDS]
    for row, suit in enumerate(suits):
        for col, rank in enumerate(range(1, 14)):
            draw_card_face(screen, Card(suit, rank),
                           X0 + col * GAP_X, Y0 + row * GAP_Y,
                           font_md=font_md, font_sm=font_sm)
    for i in range(2):
        draw_card_face(screen, Card(Suit.GHOST, 0),
                       X0 + i * GAP_X, Y0 + 4 * GAP_Y,
                       font_md=font_md, font_sm=font_sm)

    pygame.display.flip()

    # Drain any events queued during startup
    pygame.time.wait(200)
    pygame.event.clear()

    clock = pygame.time.Clock()
    while True:
        clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

except SystemExit:
    pass
except Exception:
    log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preview_error.log')
    with open(log, 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
    print(f"Error logged to {log}")
    input("Press Enter to close...")
