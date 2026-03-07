"""
自摸 – main entry point.

Run with:  python main.py
"""
import sys
import pygame

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from game.game import Game
from gui.renderer import Renderer
from gui.menu import Menu


def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('自摸·釣寶')

    menu     = Menu(screen)
    renderer = Renderer(screen)
    renderer.setup_fonts()

    game:      Game | None = None
    app_state: str         = 'menu'

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(FPS)

        # ── Event handling ────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit(0)

            if app_state == 'menu':
                result = menu.handle_event(event)
                if result == 'start':
                    game      = Game()
                    app_state = 'game'
                elif result == 'quit':
                    pygame.quit()
                    sys.exit(0)
            else:
                renderer.handle_event_for_game(event, game)

        # ── Update & render ───────────────────────────────────────
        if app_state == 'menu':
            menu.draw()
        else:
            game.update(dt)
            renderer.draw(game)

        pygame.display.flip()


if __name__ == '__main__':
    main()
