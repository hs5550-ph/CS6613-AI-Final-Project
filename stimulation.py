from collections.abc import Callable
from dataclasses import dataclass

from Tic_Tak_Toe.tic_tac_toe import O, X, GameState, Move, TicTacToe
from Alpha_Beta_Pruning.alpha_beta_pruning import result

GameStrategy = Callable[[TicTacToe, GameState, str], Move | None]
UtilityFunction = Callable[[GameState, str], float]
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

    while not game.is_terminal(state):
        game_strategy = x_strategy if current_player == X else o_strategy
        move = game_strategy(game, state, current_player)
        if move is None:
            raise RuntimeError(
                "Game strategy returned no move for a non-terminal state"
            )

        state = result(game, state, move, current_player)
        moves.append(MoveRecord(current_player, move, state))

        if game.is_win(state, current_player):
            return GameResult(current_player, tuple(moves))

        current_player = O if current_player == X else X

    return GameResult(None, tuple(moves))


