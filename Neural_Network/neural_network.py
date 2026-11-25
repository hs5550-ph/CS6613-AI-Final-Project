"""Neural network player that plugs into the project's simulation.

``neural_network_move`` has the same signature as ``alpha_beta_search``, so it
can be passed to ``run_stimulation`` as ``x_strategy`` or ``o_strategy``.

To choose a move, the player:
1. builds every board it could reach with one legal move,
2. asks the trained network to score each board, and
3. plays the move with the highest score.

It does no lookahead or tree search: the move comes from one batch of network
predictions. A separate network is trained for each board size and win length.
See ``Neural_Network/train.py``.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np

from Tic_Tak_Toe.tic_tac_toe import ALLOWED_PLAYERS, O, X, GameState, Move, TicTacToe

from .network import EMPTY_VALUE, MLP, O_VALUE, X_VALUE, candidate_afterstates
from .train import MODEL_DIR, model_path

_MODEL_CACHE: Dict[Tuple[str, int, int, int], MLP] = {}


def load_model(rows: int, columns: int, win: int, model_dir: str = MODEL_DIR) -> MLP:
    """Load (and cache) the trained network for a board configuration."""
    key = (model_dir, rows, columns, win)
    if key not in _MODEL_CACHE:
        path = model_path(rows, columns, win, model_dir)
        try:
            network, _ = MLP.load(path)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"No trained neural network for a {rows}x{columns} board with "
                f"{win} in a row (expected {path}). Train one from the project "
                f"root with:\n    python -m Neural_Network.train "
                f"--rows {rows} --columns {columns} --win {win}"
            ) from None
        if network.input_size != 2 * rows * columns:
            raise ValueError(f"Model at {path} was trained for a different board size")
        _MODEL_CACHE[key] = network
    return _MODEL_CACHE[key]


def state_to_array(state: GameState) -> np.ndarray:
    """Convert a GameState board of "X"/"O"/" " into a flat array of 1/-1/0."""
    values = {X: X_VALUE, O: O_VALUE}
    return np.array(
        [values.get(piece, EMPTY_VALUE) for row in state.board for piece in row],
        dtype=np.int8,
    )


def move_values(
    game: TicTacToe,
    state: GameState,
    current_player: str,
    model_dir: str = MODEL_DIR,
) -> Dict[Move, float]:
    """Return the network's score (-1 to 1) for every legal move. Handy for debugging."""
    moves = game.actions(state)
    if not moves:
        return {}
    network = load_model(state.rows, state.columns, game.connecting_pieces_to_win, model_dir)
    player = X_VALUE if current_player == X else O_VALUE
    cells = [row * state.columns + column for row, column in moves]
    scores = network.forward(candidate_afterstates(state_to_array(state), cells, player))
    return {move: float(score) for move, score in zip(moves, scores)}


def neural_network_move(
    game: TicTacToe,
    state: GameState,
    current_player: str,
    model_dir: str = MODEL_DIR,
) -> Optional[Move]:
    """Return the move the network rates highest, or None for a finished game."""
    if current_player not in ALLOWED_PLAYERS:
        raise ValueError("Player must be X or O")
    if game.is_terminal(state):
        return None

    values = move_values(game, state, current_player, model_dir)
    return max(values, key=values.get)
