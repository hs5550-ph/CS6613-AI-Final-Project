import pytest

from Tic_Tak_Toe.tic_tac_toe import O, X, GameState, TicTacToe
from Alpha_Beta_Pruning.alpha_beta_pruning import alpha_beta_search, result


def make_game():
    game = TicTacToe()

    def utility(state, player):
        other_player = O if player == X else X
        if game.is_win(state, player):
            return 1.0
        if game.is_win(state, other_player):
            return -1.0
        return 0.0

    game.utility_function = utility
    return game


def test_alpha_beta_search_takes_a_winning_move_without_changing_state():
    game = make_game()
    state = GameState()
    state.board[0][:2] = [X, X]
    state.board[1][:2] = [O, O]
    original_board = [row[:] for row in state.board]

    move = alpha_beta_search(game, state, X)

    assert move == (0, 2)
    assert state.board == original_board


def test_alpha_beta_search_finds_winning_move_on_supplied_board():
    game = make_game()
    state = GameState()
    state.board[:] = [
        [X, X, O],
        [X, " ", O],
        [O, O, X],
    ]

    assert alpha_beta_search(game, state, X) == (1, 1)
    assert alpha_beta_search(game, state, O) == (1, 1)
    
def test_alpha_beta_search_finds_winning_move_on_supplied_board_2():
    game = make_game()
    state = GameState()
    state.board[:] = [
        [O, X, " "],
        [O, " ", O],
        [X, " ", X],
    ]

    assert alpha_beta_search(game, state, X) == (1, 1)
    assert alpha_beta_search(game, state, O) == (1, 1)


def test_alpha_beta_search_blocks_an_immediate_loss():
    game = make_game()
    state = GameState()
    state.board[0][:2] = [X, X]
    state.board[1][0] = O

    assert alpha_beta_search(game, state, O) == (0, 2)


def test_alpha_beta_search_returns_none_for_a_terminal_state():
    game = make_game()
    state = GameState()
    state.board[:] = [
        [X, O, X],
        [X, O, O],
        [O, X, X],
    ]

    assert game.is_terminal(state)
    assert alpha_beta_search(game, state, X) is None


def test_result_returns_the_state_after_the_move_without_mutating_input():
    game = make_game()
    state = GameState()

    next_state = result(game, state, (1, 2), X)

    assert next_state is not state
    assert next_state.board[1][2] == X
    assert state.board[1][2] == " "


def test_search_depth_bounds_the_search():
    game = make_game()
    state = GameState()
    evaluated_states = []
    original_utility = game.utility_function

    def tracking_utility(current_state, player):
        evaluated_states.append(current_state)
        return original_utility(current_state, player)

    game.utility_function = tracking_utility
    assert alpha_beta_search(game, state, X, max_depth=1) == (0, 0)
    assert len(evaluated_states) == 9
    assert all(not game.is_terminal(evaluated_state) for evaluated_state in evaluated_states)


def test_alpha_beta_search_rejects_non_positive_max_depth():
    game = make_game()
    state = GameState()

    with pytest.raises(ValueError, match="max_depth must be positive"):
        alpha_beta_search(game, state, X, max_depth=0)
