"""
自摸勝 – main entry point.

Run with:  python main.py
"""
import sys
import pygame

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from game.game import Game
from gui.renderer import Renderer


def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('自摸勝')

    renderer = Renderer(screen)
    renderer.setup_fonts()

    game  = Game()
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(FPS)   # milliseconds since last frame

        # ── Event handling ────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit(0)
            renderer.handle_event_for_game(event, game)

        # ── Game logic update ─────────────────────────────────────
        game.update(dt)

        # ── Render ────────────────────────────────────────────────
        renderer.draw(game)
        pygame.display.flip()


if __name__ == '__main__':
    main()
