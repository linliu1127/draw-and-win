from enum import Enum, auto


class GameState(Enum):
    INIT             = auto()   # Initial setup
    DEALING          = auto()   # Dealing cards
    DRAWING          = auto()   # Current player choosing draw/pick
    PLAYER_DRAWN     = auto()   # Player has 5 cards; must discard or declare tsumo
    DISCARDING       = auto()   # Processing the discard (instant transition)
    RON_CHECK        = auto()   # Checking all players for RON eligibility
    RON_WINDOW       = auto()   # Human deciding whether to RON
    WIN_TSUMO        = auto()   # A player won by tsumo
    WIN_RON          = auto()   # A player won by RON
    SCORING          = auto()   # Calculating and applying score changes
    ROUND_END        = auto()   # Round finished; waiting for human to continue
    GAME_OVER        = auto()   # Game finished
