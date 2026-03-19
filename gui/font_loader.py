import os
import sys
import pygame

_WIN_PATHS = [
    'Iansui-Regular.ttf',
    'C:/Windows/Fonts/kaiu.ttf',
]
_WASM_PATHS = ['Iansui-Regular.ttf']

_cached: str | None = None


def _find() -> str | None:
    global _cached
    if _cached is not None:
        return _cached
    for p in (_WASM_PATHS if sys.platform == 'emscripten' else _WIN_PATHS):
        if os.path.exists(p):
            _cached = p
            return p
    return None


def load_font(size: int) -> pygame.font.Font:
    path = _find()
    if path:
        try:
            return pygame.font.Font(path, size)
        except Exception:
            pass
    return pygame.font.SysFont(None, size)
