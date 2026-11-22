from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from Tic_Tak_Toe.tic_tac_toe import O, X, TicTacToe

if TYPE_CHECKING:
    from stimulation import GameResult, GameStrategy


def _algorithm_name(strategy: GameStrategy) -> str:
    function = strategy.func if isinstance(strategy, partial) else strategy
    name = getattr(function, "__name__", type(function).__name__)
    keywords = strategy.keywords if isinstance(strategy, partial) else None
    max_depth = keywords.get("max_depth") if keywords else None
    if max_depth is not None:
        return f"{name}(max_depth={max_depth})"
    return name


def print_game_report(
    game_number: int,
    number_of_games: int,
    starting_player: str,
    game_result: GameResult,
    display_game: TicTacToe,
) -> None:
    print(
        f"\nGame {game_number}/{number_of_games} "
        f"(starting player: {starting_player})"
    )
    for move_number, move_record in enumerate(game_result.moves, start=1):
        print(
            f"Move {move_number}: {move_record.player} plays {move_record.move}"
        )
        display_game.display_board(move_record.state)

    if game_result.winner is None:
        print("Result: draw")
    else:
        print(f"Result: {game_result.winner} wins")
    print(
        f"X strategy time: {game_result.x_wall_clock_time:.4f}s wall-clock, "
        f"{game_result.x_cpu_time:.4f}s CPU"
    )
    print(
        f"O strategy time: {game_result.o_wall_clock_time:.4f}s wall-clock, "
        f"{game_result.o_cpu_time:.4f}s CPU"
    )


def print_summary(
    results: dict[str, int],
    number_of_games: int,
    x_strategy: GameStrategy,
    o_strategy: GameStrategy,
    total_x_wall_clock_time: float,
    total_o_wall_clock_time: float,
    total_x_cpu_time: float,
    total_o_cpu_time: float,
) -> None:
    x_win_rate = results[X] / number_of_games * 100
    o_win_rate = results[O] / number_of_games * 100
    overall_win_rate = (results[X] + results[O]) / number_of_games * 100
    draw_rate = results["draw"] / number_of_games * 100

    print("\nAlgorithms")
    print(f"X: {_algorithm_name(x_strategy)}")
    print(f"O: {_algorithm_name(o_strategy)}")
    print("\nFinal results")
    print(f"X wins: {results[X]} ({x_win_rate:.1f}%)")
    print(f"O wins: {results[O]} ({o_win_rate:.1f}%)")
    print(f"Overall win rate: {overall_win_rate:.1f}%")
    print(f"Draws: {results['draw']} ({draw_rate:.1f}%)")
    print(
        f"X strategy total: {total_x_wall_clock_time:.4f}s wall-clock, "
        f"{total_x_cpu_time:.4f}s CPU"
    )
    print(
        f"O strategy total: {total_o_wall_clock_time:.4f}s wall-clock, "
        f"{total_o_cpu_time:.4f}s CPU"
    )
    print(
        f"X strategy average per game: "
        f"{total_x_wall_clock_time / number_of_games:.4f}s wall-clock, "
        f"{total_x_cpu_time / number_of_games:.4f}s CPU"
    )
    print(
        f"O strategy average per game: "
        f"{total_o_wall_clock_time / number_of_games:.4f}s wall-clock, "
        f"{total_o_cpu_time / number_of_games:.4f}s CPU"
    )
