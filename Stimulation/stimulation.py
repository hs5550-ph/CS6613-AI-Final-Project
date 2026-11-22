from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter, process_time

from Tic_Tak_Toe.tic_tac_toe import O, X, GameState, Move, TicTacToe
from Alpha_Beta_Pruning.alpha_beta_pruning import result
from .summary import print_game_report, print_summary as print_summary_report

GameStrategy = Callable[[TicTacToe, GameState, str], Move | None]
UtilityFunction = Callable[[GameState, str], float]
STARTING_PLAYER = X
_UTILITY_EVALUATOR = TicTacToe()


@dataclass(frozen=True)
class MoveRecord:
    player: str
    move: Move
    state: GameState


@dataclass(frozen=True)
class GameResult:
    winner: str | None
    moves: tuple[MoveRecord, ...]
    x_wall_clock_time: float
    o_wall_clock_time: float
    x_cpu_time: float
    o_cpu_time: float


def utility_function(state: GameState, player: str) -> float:
    opponent = O if player == X else X
    if _UTILITY_EVALUATOR.is_win(state, player):
        return 1.0
    if _UTILITY_EVALUATOR.is_win(state, opponent):
        return -1.0
    return 0.0


def make_game(utility_function: UtilityFunction) -> TicTacToe:
    return TicTacToe(utility_function=utility_function)


def simulate_game(
    game_number: int,
    number_of_games: int,
    starting_player: str,
    x_strategy: GameStrategy,
    o_strategy: GameStrategy,
    utility: UtilityFunction,
) -> GameResult:
    if number_of_games < 1:
        raise ValueError("number_of_games must be positive")
    if not 1 <= game_number <= number_of_games:
        raise ValueError("game_number must be between 1 and number_of_games")
    if starting_player not in (X, O):
        raise ValueError("starting_player must be X or O")

    game = make_game(utility)
    state = GameState()
    current_player = starting_player
    moves: list[MoveRecord] = []
    x_wall_clock_time = 0.0
    o_wall_clock_time = 0.0
    x_cpu_time = 0.0
    o_cpu_time = 0.0

    while not game.is_terminal(state):
        game_strategy = x_strategy if current_player == X else o_strategy
        wall_clock_start = perf_counter()
        cpu_start = process_time()
        move = game_strategy(game, state, current_player)
        strategy_wall_clock_time = perf_counter() - wall_clock_start
        strategy_cpu_time = process_time() - cpu_start
        if current_player == X:
            x_wall_clock_time += strategy_wall_clock_time
            x_cpu_time += strategy_cpu_time
        else:
            o_wall_clock_time += strategy_wall_clock_time
            o_cpu_time += strategy_cpu_time

        if move is None:
            raise RuntimeError(
                "Game strategy returned no move for a non-terminal state"
            )

        state = result(game, state, move, current_player)
        moves.append(MoveRecord(current_player, move, state))

        if game.is_win(state, current_player):
            return GameResult(
                current_player,
                tuple(moves),
                x_wall_clock_time,
                o_wall_clock_time,
                x_cpu_time,
                o_cpu_time,
            )

        current_player = O if current_player == X else X

    return GameResult(
        None,
        tuple(moves),
        x_wall_clock_time,
        o_wall_clock_time,
        x_cpu_time,
        o_cpu_time,
    )


def run_stimulation(
    x_strategy: GameStrategy,
    o_strategy: GameStrategy,
    number_of_games: int,
    print_game: bool,
    print_summary: bool,
    starting_player: str = STARTING_PLAYER,
    utility: UtilityFunction = utility_function,
) -> dict[str, int]:
    if number_of_games < 1:
        raise ValueError("number_of_games must be positive")
    if starting_player not in (X, O):
        raise ValueError("starting_player must be X or O")

    display_game = make_game(utility)
    results = {X: 0, O: 0, "draw": 0}
    total_x_wall_clock_time = 0.0
    total_o_wall_clock_time = 0.0
    total_x_cpu_time = 0.0
    total_o_cpu_time = 0.0

    for game_number in range(1, number_of_games + 1):
        game_result = simulate_game(
            game_number,
            number_of_games,
            starting_player,
            x_strategy,
            o_strategy,
            utility,
        )
        total_x_wall_clock_time += game_result.x_wall_clock_time
        total_o_wall_clock_time += game_result.o_wall_clock_time
        total_x_cpu_time += game_result.x_cpu_time
        total_o_cpu_time += game_result.o_cpu_time

        if game_result.winner is None:
            results["draw"] += 1
        else:
            results[game_result.winner] += 1
        if print_game:
            print_game_report(
                game_number,
                number_of_games,
                starting_player,
                game_result,
                display_game,
            )

    if print_summary:
        print_summary_report(
            results,
            number_of_games,
            x_strategy,
            o_strategy,
            total_x_wall_clock_time,
            total_o_wall_clock_time,
            total_x_cpu_time,
            total_o_cpu_time,
        )

    return results


