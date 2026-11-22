from __future__ import annotations

from copy import deepcopy

from Tic_Tak_Toe.tic_tac_toe import ALLOWED_PLAYERS, GameState, Move, TicTacToe

DEFAULT_MAX_DEPTH = 6


def alpha_beta_search(
    game: TicTacToe,
    state: GameState,
    current_player: str,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> Move | None:
    """Return the best move for the player to move, or None for a terminal state."""
    if current_player not in ALLOWED_PLAYERS:
        raise ValueError("Player must be X or O")
    if max_depth < 1:
        raise ValueError("max_depth must be positive")

    _, move = _max_value(
        game,
        state,
        current_player,
        float("-inf"),
        float("inf"),
        0,
        max_depth,
    )
    return move


def result(
    game: TicTacToe,
    state: GameState,
    move: Move,
    player: str,
) -> GameState:
    """Return a new state after player makes move; leave state unchanged."""
    next_state = deepcopy(state)
    game.insert_piece(next_state, move[0], move[1], player)
    return next_state


def _max_value(
    game: TicTacToe,
    state: GameState,
    max_player: str,
    alpha: float,
    beta: float,
    depth: int,
    max_depth: int,
) -> tuple[float, Move | None]:
    if game.is_terminal(state) or depth >= max_depth:
        return game.utility(state, max_player), None

    value = float("-inf")
    best_move = None
    for move in game.actions(state):
        child = result(game, state, move, max_player)
        child_value, _ = _min_value(
            game,
            child,
            max_player,
            alpha,
            beta,
            depth + 1,
            max_depth,
        )
        if child_value > value:
            value, best_move = child_value, move
        alpha = max(alpha, value)
        if value >= beta:
            return value, best_move

    return value, best_move


def _min_value(
    game: TicTacToe,
    state: GameState,
    max_player: str,
    alpha: float,
    beta: float,
    depth: int,
    max_depth: int,
) -> tuple[float, Move | None]:
    if game.is_terminal(state) or depth >= max_depth:
        return game.utility(state, max_player), None

    min_player = next(player for player in ALLOWED_PLAYERS if player != max_player)
    value = float("inf")
    best_move = None
    for move in game.actions(state):
        child = result(game, state, move, min_player)
        child_value, _ = _max_value(
            game,
            child,
            max_player,
            alpha,
            beta,
            depth + 1,
            max_depth,
        )
        if child_value < value:
            value, best_move = child_value, move
        beta = min(beta, value)
        if value <= alpha:
            return value, best_move

    return value, best_move
