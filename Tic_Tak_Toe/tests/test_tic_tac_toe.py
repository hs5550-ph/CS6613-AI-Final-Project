import pytest

from Tic_Tak_Toe import tic_tac_toe
from Tic_Tak_Toe.tic_tac_toe import GameState, TicTacToe


@pytest.fixture
def game():
    return TicTacToe()


@pytest.fixture
def state():
    return GameState()


def test_insert_piece_places_x_and_o(game, state):
    game.insert_piece(state, 0, 1, tic_tac_toe.X)
    game.insert_piece(state, 2, 2, tic_tac_toe.O)

    assert state.board[0][1] == tic_tac_toe.X
    assert state.board[2][2] == tic_tac_toe.O


def test_game_states_have_independent_boards(game):
    first_state = GameState()
    second_state = GameState()
    game.insert_piece(first_state, 0, 0, tic_tac_toe.X)
    game.insert_piece(second_state, 2, 2, tic_tac_toe.O)

    assert first_state.board[0][0] == tic_tac_toe.X
    assert first_state.board[2][2] == tic_tac_toe.EMPTY
    assert second_state.board[0][0] == tic_tac_toe.EMPTY
    assert second_state.board[2][2] == tic_tac_toe.O
    assert (0, 0) not in game.actions(first_state)
    assert (0, 0) in game.actions(second_state)


def test_actions_returns_all_empty_board_positions(game, state):
    game.insert_piece(state, 0, 0, tic_tac_toe.X)

    actions = game.actions(state)

    assert len(actions) == 8
    assert (0, 0) not in actions
    assert all(state.board[row][column] == tic_tac_toe.EMPTY for row, column in actions)


def test_generate_random_move_returns_an_available_action(game, state):
    game.insert_piece(state, 0, 0, tic_tac_toe.X)

    move = game.generate_random_move(state)

    assert move in game.actions(state)


def test_generate_random_move_rejects_full_board(game, state):
    for row in range(state.rows):
        for column in range(state.columns):
            state.board[row][column] = tic_tac_toe.X

    with pytest.raises(ValueError, match="No available moves"):
        game.generate_random_move(state)


def test_insert_piece_rejects_out_of_range_position(game, state):
    with pytest.raises(IndexError):
        game.insert_piece(state, state.rows, 0, tic_tac_toe.X)


def test_insert_piece_rejects_invalid_piece(game, state):
    with pytest.raises(ValueError):
        game.insert_piece(state, 0, 0, "?")


def test_insert_piece_rejects_occupied_position(game, state):
    game.insert_piece(state, 1, 1, tic_tac_toe.X)

    with pytest.raises(ValueError):
        game.insert_piece(state, 1, 1, tic_tac_toe.O)


def test_is_win_detects_horizontal_win(game, state):
    for column in range(game.connecting_pieces_to_win):
        game.insert_piece(state, 1, column, tic_tac_toe.X)

    assert game.is_win(state)


def test_is_win_detects_vertical_win(game, state):
    for row in range(game.connecting_pieces_to_win):
        game.insert_piece(state, row, 1, tic_tac_toe.O)

    assert game.is_win(state)


def test_is_win_detects_diagonal_win(game, state):
    for index in range(game.connecting_pieces_to_win):
        game.insert_piece(state, index, index, tic_tac_toe.X)

    assert game.is_win(state)


def test_is_win_detects_anti_diagonal_win(game, state):
    for row in range(game.connecting_pieces_to_win):
        column = state.columns - 1 - row
        game.insert_piece(state, row, column, tic_tac_toe.O)

    assert game.is_win(state)


def test_utility_scores_wins_from_the_requested_player_perspective(game, state):
    for column in range(game.connecting_pieces_to_win):
        game.insert_piece(state, 1, column, tic_tac_toe.X)

    def mock_utility(current_state, current_player):
        winner = current_state.board[1][0]
        return 1.0 if current_player == winner else -1.0

    game_with_mock_utility = TicTacToe(utility_function=mock_utility)

    assert game_with_mock_utility.utility(state, tic_tac_toe.X) == 1.0
    assert game_with_mock_utility.utility(state, tic_tac_toe.O) == -1.0


def test_utility_scores_a_draw_as_zero(state):
    state.board[:] = [
        [tic_tac_toe.X, tic_tac_toe.O, tic_tac_toe.X],
        [tic_tac_toe.X, tic_tac_toe.O, tic_tac_toe.O],
        [tic_tac_toe.O, tic_tac_toe.X, tic_tac_toe.X],
    ]

    game = TicTacToe(utility_function=lambda _state, _player: 0.0)

    assert game.is_terminal(state)
    assert game.utility(state, tic_tac_toe.X) == 0.0
    assert game.utility(state, tic_tac_toe.O) == 0.0


def test_custom_utility_function_is_used(state):
    calls = []

    def custom_utility(current_state, player):
        calls.append((current_state, player))
        return 3.5

    game = TicTacToe(utility_function=custom_utility)

    assert game.utility(state, tic_tac_toe.O) == 3.5
    assert calls == [(state, tic_tac_toe.O)]


def test_utility_rejects_an_invalid_player(game, state):
    with pytest.raises(ValueError, match="Player must be X or O"):
        game.utility(state, "?")


def test_is_win_returns_false_without_a_connected_run(game, state):
    game.insert_piece(state, 0, 0, tic_tac_toe.X)
    game.insert_piece(state, 0, 1, tic_tac_toe.X)
    game.insert_piece(state, 1, 0, tic_tac_toe.O)

    assert not game.is_win(state)


def test_board_dimensions_and_win_length_are_configurable():
    game = TicTacToe(connecting_pieces_to_win=4)
    state = GameState(rows=5, columns=6)

    assert len(state.board) == 5
    assert all(len(row) == 6 for row in state.board)

    for column in range(game.connecting_pieces_to_win):
        game.insert_piece(state, 2, column, tic_tac_toe.X)
    assert game.is_win(state)

    state = GameState(rows=5, columns=6)
    for row in range(game.connecting_pieces_to_win):
        game.insert_piece(state, row, 3, tic_tac_toe.O)
    assert game.is_win(state)


def test_state_constructor_rejects_non_positive_board_dimensions():
    with pytest.raises(ValueError, match="must be positive"):
        GameState(rows=0)


def test_game_constructor_rejects_non_positive_win_length():
    with pytest.raises(ValueError, match="must be positive"):
        TicTacToe(connecting_pieces_to_win=0)


def test_is_terminal_returns_true_for_a_win(game, state):
    for column in range(game.connecting_pieces_to_win):
        game.insert_piece(state, 1, column, tic_tac_toe.X)

    assert game.is_terminal(state)


def test_is_terminal_returns_true_for_a_full_board_without_a_win(game, state):
    state.board[:] = [
        [tic_tac_toe.X, tic_tac_toe.O, tic_tac_toe.X],
        [tic_tac_toe.X, tic_tac_toe.O, tic_tac_toe.O],
        [tic_tac_toe.O, tic_tac_toe.X, tic_tac_toe.X],
    ]

    assert not game.is_win(state)
    assert game.is_terminal(state)


def test_is_terminal_returns_false_while_moves_remain(game, state):
    game.insert_piece(state, 0, 0, tic_tac_toe.X)

    assert not game.is_terminal(state)


def test_display_board_shows_grid_and_separators(game, state, capsys):
    game.insert_piece(state, 0, 0, tic_tac_toe.X)
    game.insert_piece(state, 1, 1, tic_tac_toe.O)

    game.display_board(state)

    assert capsys.readouterr().out == (
        "X |   |  \n"
        "---+---+---\n"
        "  | O |  \n"
        "---+---+---\n"
        "  |   |  \n"
    )
