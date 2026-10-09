import pytest

from Tic_Tak_Toe import tic_tac_toe as game


@pytest.fixture(autouse=True)
def empty_board():
    original_board = [row[:] for row in game.board]
    for row in game.board:
        row[:] = [game.EMPTY] * game.COLUMNS

    yield

    game.board[:] = original_board


def test_insert_piece_places_x_and_o():
    game.insert_piece(0, 1, game.X)
    game.insert_piece(2, 2, game.O)

    assert game.board[0][1] == game.X
    assert game.board[2][2] == game.O


def test_generate_random_move_returns_an_empty_board_position():
    game.insert_piece(0, 0, game.X)

    row, column = game.generate_random_move()

    assert 0 <= row < game.ROWS
    assert 0 <= column < game.COLUMNS
    assert game.board[row][column] == game.EMPTY


def test_generate_random_move_rejects_full_board():
    for row in range(game.ROWS):
        for column in range(game.COLUMNS):
            game.board[row][column] = game.X

    with pytest.raises(ValueError, match="No available moves"):
        game.generate_random_move()


def test_insert_piece_rejects_out_of_range_position():
    with pytest.raises(IndexError):
        game.insert_piece(game.ROWS, 0, game.X)


def test_insert_piece_rejects_invalid_piece():
    with pytest.raises(ValueError):
        game.insert_piece(0, 0, "?")


def test_insert_piece_rejects_occupied_position():
    game.insert_piece(1, 1, game.X)

    with pytest.raises(ValueError):
        game.insert_piece(1, 1, game.O)


def test_is_win_detects_horizontal_win():
    for column in range(game.CONNECTING_PIECES_TO_WIN):
        game.insert_piece(1, column, game.X)

    assert game.is_win()


def test_is_win_detects_vertical_win():
    for row in range(game.CONNECTING_PIECES_TO_WIN):
        game.insert_piece(row, 1, game.O)

    assert game.is_win()


def test_is_win_detects_diagonal_win():
    for index in range(game.CONNECTING_PIECES_TO_WIN):
        game.insert_piece(index, index, game.X)

    assert game.is_win()


def test_is_win_detects_anti_diagonal_win():
    for row in range(game.CONNECTING_PIECES_TO_WIN):
        column = game.COLUMNS - 1 - row
        game.insert_piece(row, column, game.O)

    assert game.is_win()


def test_is_win_returns_false_without_a_connected_run():
    game.insert_piece(0, 0, game.X)
    game.insert_piece(0, 1, game.X)
    game.insert_piece(1, 0, game.O)

    assert not game.is_win()


def test_board_dimensions_and_win_length_are_configurable(monkeypatch):
    monkeypatch.setattr(game, "ROWS", 5)
    monkeypatch.setattr(game, "COLUMNS", 6)
    monkeypatch.setattr(game, "CONNECTING_PIECES_TO_WIN", 4)
    game.board[:] = [
        [game.EMPTY for _ in range(game.COLUMNS)] for _ in range(game.ROWS)
    ]

    assert len(game.board) == 5
    assert all(len(row) == 6 for row in game.board)

    for column in range(game.CONNECTING_PIECES_TO_WIN):
        game.insert_piece(2, column, game.X)
    assert game.is_win()

    game.board[:] = [
        [game.EMPTY for _ in range(game.COLUMNS)] for _ in range(game.ROWS)
    ]
    for row in range(game.CONNECTING_PIECES_TO_WIN):
        game.insert_piece(row, 3, game.O)
    assert game.is_win()


def test_display_board_shows_grid_and_separators(capsys):
    game.insert_piece(0, 0, game.X)
    game.insert_piece(1, 1, game.O)

    game.display_board()

    assert capsys.readouterr().out == (
        "X |   |  \n"
        "---+---+---\n"
        "  | O |  \n"
        "---+---+---\n"
        "  |   |  \n"
    )
