"""Train the neural network player by self-play.

No tree search is used. The network learns a value function with temporal
difference (TD) learning:

* The network scores every board the current player could move to.
* The player usually picks the best-scoring move. Sometimes it picks a random
  move instead (epsilon-greedy exploration) so it sees many positions.
* After each move, the previous position is trained toward the negative of the
  opponent's best score ("what is good for my opponent is bad for me").
  Finished games give exact targets: +1 for a win, 0 for a draw.

Every training position is also added under every rotation and reflection of the
board.

Run from the project root, for example::

    python -m Neural_Network.train --rows 3 --columns 3 --win 3
    python -m Neural_Network.train --preset all
"""

from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np

from .network import (
    MLP,
    augment_with_symmetries,
    candidate_afterstates,
    symmetry_permutations,
)

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# (rows, columns, connecting_pieces_to_win, number_of_training_games)
PRESETS: List[Tuple[int, int, int, int]] = [
    (3, 3, 3, 20_000),
    (4, 4, 3, 30_000),
    (4, 4, 4, 30_000),
    (5, 5, 4, 50_000),
]


def model_filename(rows: int, columns: int, win: int) -> str:
    return f"nn_{rows}x{columns}_win{win}.npz"


def model_path(rows: int, columns: int, win: int, model_dir: str = MODEL_DIR) -> str:
    return os.path.join(model_dir, model_filename(rows, columns, win))


def default_hidden_layers(cells: int) -> Tuple[int, ...]:
    if cells <= 9:
        return (128, 64)
    if cells <= 16:
        return (256, 128)
    return (512, 256)


@dataclass
class BoardConfig:
    rows: int
    columns: int
    win: int

    @property
    def cells(self) -> int:
        return self.rows * self.columns


# --------------------------------------------------------------------------- #
# Fast game rules used only during training (much quicker than rescanning the
# whole board after every move).
# --------------------------------------------------------------------------- #
_DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


def is_win_after_move(board: np.ndarray, cell: int, player: int, config: BoardConfig) -> bool:
    """Would ``player`` placing a piece on ``cell`` make ``config.win`` in a row?"""
    row, column = divmod(int(cell), config.columns)
    for row_step, column_step in _DIRECTIONS:
        count = 1
        for sign in (1, -1):
            r = row + row_step * sign
            c = column + column_step * sign
            while (
                0 <= r < config.rows
                and 0 <= c < config.columns
                and board[r * config.columns + c] == player
            ):
                count += 1
                r += row_step * sign
                c += column_step * sign
        if count >= config.win:
            return True
    return False


def _score_moves(
    network: MLP,
    board: np.ndarray,
    legal: np.ndarray,
    player: int,
    config: BoardConfig,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Score each legal move. Moves that end the game get their exact value."""
    encoded = candidate_afterstates(board, legal, player)
    values = network.forward(encoded)
    wins = np.array([is_win_after_move(board, cell, player, config) for cell in legal])
    if len(legal) == 1 and not wins[0]:
        values = np.zeros(1, dtype=np.float32)  # last square filled: draw
    values = np.where(wins, 1.0, values)
    return encoded, values, wins


def play_training_game(
    network: MLP,
    config: BoardConfig,
    epsilon: float,
    rng: np.random.Generator,
    random_player: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Play one exploratory self-play game. Returns (encoded afterstates, targets)."""
    board = np.zeros(config.cells, dtype=np.int8)
    player = 1
    states: List[np.ndarray] = []
    targets: List[float] = []
    waiting_for_target: Optional[int] = None

    while True:
        legal = np.flatnonzero(board == 0)
        encoded, values, wins = _score_moves(network, board, legal, player, config)
        best_value = float(values.max())

        # The opponent's previous position is worth minus our best reply.
        if waiting_for_target is not None:
            targets[waiting_for_target] = -best_value

        if player == random_player or rng.random() < epsilon:
            choice = int(rng.integers(len(legal)))
        else:
            best_choices = np.flatnonzero(values >= best_value - 1e-6)
            choice = int(rng.choice(best_choices))

        states.append(encoded[choice])
        targets.append(0.0)
        board[legal[choice]] = player

        if wins[choice]:
            targets[-1] = 1.0
            break
        if len(legal) == 1:
            targets[-1] = 0.0
            break

        waiting_for_target = len(states) - 1
        player = -player

    return np.array(states, dtype=np.float32), np.array(targets, dtype=np.float32)


def greedy_move(
    network: MLP,
    board: np.ndarray,
    player: int,
) -> int:
    """Pick the network's favourite move using the network alone."""
    legal = np.flatnonzero(board == 0)
    values = network.forward(candidate_afterstates(board, legal, player))
    return int(legal[int(np.argmax(values))])


def evaluate(
    network: MLP,
    config: BoardConfig,
    rng: np.random.Generator,
    games: int = 200,
) -> dict:
    """Play the greedy network against a random player and against itself."""
    results = {
        "as_x_vs_random": [0, 0, 0],  # wins, draws, losses
        "as_o_vs_random": [0, 0, 0],
    }
    for key, network_player in (("as_x_vs_random", 1), ("as_o_vs_random", -1)):
        for _ in range(games):
            winner = _play_match(network, config, rng, network_player)
            if winner == network_player:
                results[key][0] += 1
            elif winner == 0:
                results[key][1] += 1
            else:
                results[key][2] += 1
    results["self_play_winner"] = _play_match(network, config, rng, None)
    return results


def _play_match(
    network: MLP,
    config: BoardConfig,
    rng: np.random.Generator,
    network_player: Optional[int],
) -> int:
    """Return 1 if X wins, -1 if O wins, 0 for a draw.

    ``network_player`` is the side the network plays; the other side moves at
    random. ``None`` means the network plays both sides.
    """
    board = np.zeros(config.cells, dtype=np.int8)
    player = 1
    while True:
        legal = np.flatnonzero(board == 0)
        if network_player is None or player == network_player:
            cell = greedy_move(network, board, player)
        else:
            cell = int(rng.choice(legal))
        board[cell] = player
        if is_win_after_move(board, cell, player, config):
            return player
        if len(legal) == 1:
            return 0
        player = -player


def _format_record(record: Sequence[int]) -> str:
    wins, draws, losses = record
    return f"W {wins:>3} / D {draws:>3} / L {losses:>3}"


# --------------------------------------------------------------------------- #
# Training loop
# --------------------------------------------------------------------------- #
def train(
    rows: int,
    columns: int,
    win: int,
    games: int = 20_000,
    hidden_layers: Optional[Sequence[int]] = None,
    learning_rate: float = 1e-3,
    batch_size: int = 128,
    updates_per_game: int = 2,
    buffer_size: int = 50_000,
    start_epsilon: float = 0.5,
    end_epsilon: float = 0.05,
    random_opponent_fraction: float = 0.2,
    evaluate_every: int = 2_000,
    seed: int = 0,
    model_dir: str = MODEL_DIR,
    save: bool = True,
    verbose: bool = True,
) -> MLP:
    """Train a network for one board configuration and (optionally) save it."""
    if win > max(rows, columns):
        raise ValueError("Win length cannot be longer than the board")

    config = BoardConfig(rows, columns, win)
    rng = np.random.default_rng(seed)
    hidden = tuple(hidden_layers) if hidden_layers else default_hidden_layers(config.cells)
    network = MLP([2 * config.cells, *hidden, 1], seed=seed)
    permutations = symmetry_permutations(rows, columns)

    buffer_inputs = np.zeros((buffer_size, 2 * config.cells), dtype=np.float32)
    buffer_targets = np.zeros(buffer_size, dtype=np.float32)
    buffer_count = 0
    buffer_position = 0
    recent_losses: List[float] = []
    start_time = time.perf_counter()

    if verbose:
        print(
            f"Training {rows}x{columns} board, {win} in a row, "
            f"{games} games, layers {network.layer_sizes}"
        )

    for game_index in range(1, games + 1):
        progress = (game_index - 1) / max(games - 1, 1)
        epsilon = start_epsilon + (end_epsilon - start_epsilon) * progress
        random_player = None
        if rng.random() < random_opponent_fraction:
            random_player = int(rng.choice([1, -1]))

        states, targets = play_training_game(network, config, epsilon, rng, random_player)
        states = augment_with_symmetries(states, permutations)
        targets = np.tile(targets, len(permutations))

        for state, target in zip(states, targets):
            buffer_inputs[buffer_position] = state
            buffer_targets[buffer_position] = target
            buffer_position = (buffer_position + 1) % buffer_size
            buffer_count = min(buffer_count + 1, buffer_size)

        if buffer_count >= batch_size:
            for _ in range(updates_per_game):
                batch = rng.integers(0, buffer_count, batch_size)
                recent_losses.append(
                    network.train_step(buffer_inputs[batch], buffer_targets[batch], learning_rate)
                )

        if verbose and (game_index % evaluate_every == 0 or game_index == games):
            report = evaluate(network, config, rng)
            self_play = {1: "X wins", -1: "O wins", 0: "draw"}[report["self_play_winner"]]
            loss = np.mean(recent_losses) if recent_losses else float("nan")
            print(
                f"game {game_index:>6} | eps {epsilon:.2f} | loss {loss:.4f} | "
                f"as X vs random {_format_record(report['as_x_vs_random'])} | "
                f"as O vs random {_format_record(report['as_o_vs_random'])} | "
                f"self-play: {self_play} | {time.perf_counter() - start_time:.0f}s"
            )
            recent_losses.clear()

    if save:
        os.makedirs(model_dir, exist_ok=True)
        path = model_path(rows, columns, win, model_dir)
        network.save(path, rows=rows, columns=columns, win=win, games=games, seed=seed)
        if verbose:
            print(f"Saved model to {path}")

    return network


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Train the tic-tac-toe neural network.")
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--win", type=int, default=3, help="pieces in a row needed to win")
    parser.add_argument("--games", type=int, default=None, help="number of self-play games")
    parser.add_argument(
        "--hidden",
        type=int,
        nargs="+",
        default=None,
        help="hidden layer sizes, e.g. --hidden 256 128",
    )
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--model-dir", default=MODEL_DIR)
    parser.add_argument(
        "--preset",
        choices=["all"],
        help="train every board size in PRESETS instead of a single one",
    )
    args = parser.parse_args(argv)

    if args.preset == "all":
        jobs = PRESETS
    else:
        default_games = next(
            (
                preset_games
                for r, c, w, preset_games in PRESETS
                if (r, c, w) == (args.rows, args.columns, args.win)
            ),
            30_000,
        )
        jobs = [(args.rows, args.columns, args.win, args.games or default_games)]

    for rows, columns, win, games in jobs:
        train(
            rows,
            columns,
            win,
            games=games,
            hidden_layers=args.hidden,
            learning_rate=args.learning_rate,
            seed=args.seed,
            model_dir=args.model_dir,
        )


if __name__ == "__main__":
    main()
