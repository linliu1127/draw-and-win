# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the game
python main.py

# Run all tests
python -m pytest tests/ -v

# 重建字型 subset（新增遊戲文字後執行）
python tools/rebuild_font_subset.py

# Run a single test file
python -m pytest tests/test_win_checker.py -v

# Run a single test by name
python -m pytest tests/test_win_checker.py::test_win_two_ghosts -v
```

**Python path (Windows):** `C:/Users/User/AppData/Local/Programs/Python/Python312/python.exe`
Use `dangerouslyDisableSandbox: true` on Bash calls that invoke Python.

## Workflow

- After every change, commit and push immediately without asking.
- Commit messages: concise, imperative, Traditional Chinese (e.g. `修正 X`、`新增 Y`、`移除 Z`).
- After every change, also sync to the Hugo blog:
  1. Rebuild: `python -m pygbag --build --width 1200 --height 800 main.py`
  2. Copy: `cp -r build/web/. <HUGO_BLOG_PATH>/static/games/draw-and-win/`
     （`HUGO_BLOG_PATH` 請查各台電腦的 MEMORY.md）

## Game Rules Summary

- 4 players (1 human + 3 AI), each dealt 4 cards from a 54-card deck (52 regular + 2 ghost 魃)
- Each turn: draw from deck OR pick up the top discard → hand reaches 5 cards → discard one
- **Win (胡牌):** 5 cards of the same color (all black ♠♣ or all red ♥♦), forming exactly one pair + one 3-card sequence
- **Ghost (魃):** substitutes any rank within the target color; at most 2 in a hand
- **Tsumo (自摸):** win on your own draw → collect 100pts from each other player
- **Ron (搶牌):** any tenpai player can claim a matching discard → collect 50pts from the discarder
- **End:** when any player reaches 0 points

## Architecture

### Data flow
`main.py` → `game.Game.update(dt)` (state machine) ← human action methods called by → `gui/renderer.Renderer.handle_event_for_game()`

The GUI layer is strictly read-only with respect to game state. All mutations go through `Game` action methods.

### `constants.py`
Single source of truth for all magic numbers: window size, card dimensions, timing delays, score values, button sizes, colours. `gui/layout.py` **imports** `BTN_W`, `BTN_H`, `CENTER_X`, `CENTER_Y`, `TENPAI_DOT_R` from here — do not redefine them in `layout.py`.

### `core/` — pure logic, no pygame
- `win_checker.check_win(cards)` — iterates over both colors; enumerates ghost substitutions (max 13² = 169) before calling `_is_valid_hand`
- `tenpai_checker.get_winning_cards(hand4)` — enumerates all 53 possible draw candidates; calls `check_win` for each
- `Card.rank` is `1–13` for regular cards, `0` for ghost; `Card.color` is `BLACK | RED | GHOST`

### `game/game.py` — state machine
States (see docstring at top of file):
```
INIT → DEALING → DRAWING → PLAYER_DRAWN → DISCARDING → RON_CHECK
                                └─ WIN_TSUMO                └─ RON_WINDOW → WIN_RON
                                                SCORING → ROUND_END → DEALING | GAME_OVER
```
- `update(dt)` dispatches to per-state handlers every frame
- AI actions fire after timer delays (`AI_DRAW_DELAY`, `AI_DISCARD_DELAY`)
- Human waits in `DRAWING` / `PLAYER_DRAWN` / `RON_WINDOW` states until GUI calls an action method
- `ROUND_END` / `GAME_OVER` wait for `human_next_round()` / dialog button

### `players/`
- `Player` base: manages `Hand`, score, tenpai state (auto-updated after every draw/discard via `_update_tenpai()`)
- `HumanPlayer` adds `selected_index` for card highlighting; selection is toggled by index
- `AIPlayer._score_hand(hand4)` returns 100+ for tenpai, else heuristic based on pairs/near-sequences/ghost count

### `gui/`
- `Renderer.draw(game)` — full repaint each frame; reads `game.state` and all public game fields
- `Renderer.handle_event_for_game(event, game)` — translates pygame events into game action calls; card clicks hit-test against `HUMAN_CARD_X0 + i * HUMAN_CARD_GAP`
- Dialogs (`RonDialog`, `RoundEndDialog`, `GameOverDialog`) are drawn as overlays; they own their own `Button` instances and return string action tokens from `handle_event()`
- AI side players (seats 1 and 3) render cards rotated 90° using `draw_card_back(rotated=True)` which swaps `CARD_W` ↔ `CARD_H`
