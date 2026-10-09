import pytest

from Tic_Tak_Toe import tic_tac_toe
from Tic_Tak_Toe.tic_tac_toe import TicTacToe


@pytest.fixture
def game():
    return TicTacToe()


def test_insert_piece_places_x_and_o(game):
    game.insert_piece(0, 1, tic_tac_toe.X)
    game.insert_piece(2, 2, tic_tac_toe.O)

    assert game.board[0][1] == tic_tac_toe.X
    assert game.board[2][2] == tic_tac_toe.O


def test_game_objects_have_independent_boards():
    first_game = TicTacToe()
    second_game = TicTacToe()
    first_game.insert_piece(0, 0, tic_tac_toe.X)

    assert first_game.board[0][0] == tic_tac_toe.X
    assert second_game.board[0][0] == tic_tac_toe.EMPTY


def test_generate_random_move_returns_an_empty_board_position(game):
    game.insert_piece(0, 0, tic_tac_toe.X)

    row, column = game.generate_random_move()

    assert 0 <= row < game.rows
    assert 0 <= column < game.columns
    assert game.board[row][column] == tic_tac_toe.EMPTY


def test_generate_random_move_rejects_full_board(game):
    for row in range(game.rows):
        for column in range(game.columns):
            game.board[row][column] = tic_tac_toe.X

    with pytest.raises(ValueError, match="No available moves"):
        game.generate_random_move()


def test_insert_piece_rejects_out_of_range_position(game):
    with pytest.raises(IndexError):
        game.insert_piece(game.rows, 0, tic_tac_toe.X)


def test_insert_piece_rejects_invalid_piece(game):
    with pytest.raises(ValueError):
        game.insert_piece(0, 0, "?")


def test_insert_piece_rejects_occupied_position(game):
    game.insert_piece(1, 1, tic_tac_toe.X)

    with pytest.raises(ValueError):
        game.insert_piece(1, 1, tic_tac_toe.O)


def test_is_win_detects_horizontal_win(game):
    for column in range(game.connecting_pieces_to_win):
        game.insert_piece(1, column, tic_tac_toe.X)

    assert game.is_win()


def test_is_win_detects_vertical_win(game):
    for row in range(game.connecting_pieces_to_win):
        game.insert_piece(row, 1, tic_tac_toe.O)

    assert game.is_win()


def test_is_win_detects_diagonal_win(game):
    for index in range(game.connecting_pieces_to_win):
        game.insert_piece(index, index, tic_tac_toe.X)

    assert game.is_win()


def test_is_win_detects_anti_diagonal_win(game):
    for row in range(game.connecting_pieces_to_win):
        column = game.columns - 1 - row
        game.insert_piece(row, column, tic_tac_toe.O)

    assert game.is_win()


def test_is_win_returns_false_without_a_connected_run(game):
    game.insert_piece(0, 0, tic_tac_toe.X)
    game.insert_piece(0, 1, tic_tac_toe.X)
    game.insert_piece(1, 0, tic_tac_toe.O)

    assert not game.is_win()


def test_board_dimensions_and_win_length_are_configurable():
    game = TicTacToe(rows=5, columns=6, connecting_pieces_to_win=4)

    assert len(game.board) == 5
    assert all(len(row) == 6 for row in game.board)

    for column in range(game.connecting_pieces_to_win):
        game.insert_piece(2, column, tic_tac_toe.X)
    assert game.is_win()

    game = TicTacToe(rows=5, columns=6, connecting_pieces_to_win=4)
    for row in range(game.connecting_pieces_to_win):
        game.insert_piece(row, 3, tic_tac_toe.O)
    assert game.is_win()


def test_constructor_rejects_non_positive_board_dimensions():
    with pytest.raises(ValueError, match="must be positive"):
        TicTacToe(rows=0)


def test_display_board_shows_grid_and_separators(game, capsys):
    game.insert_piece(0, 0, tic_tac_toe.X)
    game.insert_piece(1, 1, tic_tac_toe.O)

    game.display_board()

    assert capsys.readouterr().out == (
        "X |   |  \n"
        "---+---+---\n"
        "  | O |  \n"
        "---+---+---\n"
        "  |   |  \n"
    )
