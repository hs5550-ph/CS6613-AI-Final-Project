import numpy as np
import pytest

from Tic_Tak_Toe.tic_tac_toe import EMPTY, O, X, GameState, TicTacToe
from Neural_Network.network import (
    MLP,
    augment_with_symmetries,
    candidate_afterstates,
    symmetry_permutations,
)
from Neural_Network.neural_network import neural_network_move, state_to_array
from Neural_Network.train import BoardConfig, is_win_after_move, model_path, train


def test_mlp_learns_a_simple_function():
    rng = np.random.default_rng(0)
    inputs = rng.integers(0, 2, (256, 4)).astype(np.float32)
    targets = np.where(inputs[:, 0] > inputs[:, 1], 0.8, -0.8)
    network = MLP([4, 16, 1], seed=0)

    first_loss = network.train_step(inputs, targets, learning_rate=1e-2)
    for _ in range(300):
        last_loss = network.train_step(inputs, targets, learning_rate=1e-2)

    assert last_loss < first_loss / 10


def test_mlp_save_and_load_give_same_predictions(tmp_path):
    network = MLP([18, 8, 1], seed=1)
    inputs = np.random.default_rng(1).random((5, 18)).astype(np.float32)
    path = tmp_path / "model.npz"

    network.save(str(path), rows=3, columns=3, win=3)
    loaded, metadata = MLP.load(str(path))

    np.testing.assert_allclose(loaded.forward(inputs), network.forward(inputs))
    assert metadata == {"rows": 3, "columns": 3, "win": 3}


@pytest.mark.parametrize("rows, columns, expected", [(3, 3, 8), (3, 4, 4)])
def test_symmetries_are_distinct_permutations(rows, columns, expected):
    permutations = symmetry_permutations(rows, columns)

    assert len(permutations) == expected
    assert len({tuple(p) for p in permutations}) == expected
    for permutation in permutations:
        assert sorted(permutation) == list(range(rows * columns))


def test_augmentation_keeps_piece_counts():
    board = np.array([1, -1, 0, 0, 1, 0, 0, 0, 0], dtype=np.int8)
    encoded = candidate_afterstates(board, [2], 1)

    augmented = augment_with_symmetries(encoded, symmetry_permutations(3, 3))

    assert augmented.shape == (8, 18)
    assert (augmented[:, :9].sum(axis=1) == 3).all()
    assert (augmented[:, 9:].sum(axis=1) == 1).all()


@pytest.mark.parametrize("rows, columns, win", [(3, 3, 3), (4, 5, 3), (5, 5, 4)])
def test_fast_win_check_matches_game_rules(rows, columns, win):
    rng = np.random.default_rng(rows * 100 + columns * 10 + win)
    game = TicTacToe(connecting_pieces_to_win=win)
    config = BoardConfig(rows, columns, win)

    for _ in range(200):
        board = rng.choice([1, -1, 0], rows * columns).astype(np.int8)
        empty = np.flatnonzero(board == 0)
        if len(empty) == 0:
            continue
        cell = int(rng.choice(empty))
        before = GameState(rows, columns)
        for index, value in enumerate(board):
            if value:
                before.board[index // columns][index % columns] = X if value == 1 else O
        already_won = game.is_win(before, X)
        board[cell] = 1
        after = GameState(rows, columns)
        for index, value in enumerate(board):
            if value:
                after.board[index // columns][index % columns] = X if value == 1 else O

        if not already_won:
            assert is_win_after_move(board, cell, 1, config) == game.is_win(after, X)


def test_state_to_array():
    state = GameState()
    state.board[0][0] = X
    state.board[2][1] = O

    assert state_to_array(state).tolist() == [1, 0, 0, 0, 0, 0, 0, -1, 0]


@pytest.fixture(scope="module")
def small_model_dir(tmp_path_factory):
    model_dir = tmp_path_factory.mktemp("models")
    train(3, 3, 3, games=3_000, model_dir=str(model_dir), verbose=False)
    return str(model_dir)


def test_training_saves_a_model(small_model_dir):
    _, metadata = MLP.load(model_path(3, 3, 3, small_model_dir))

    assert (metadata["rows"], metadata["columns"], metadata["win"]) == (3, 3, 3)


def test_move_is_legal_and_state_is_unchanged(small_model_dir):
    game = TicTacToe()
    state = GameState()
    state.board[1][1] = X
    original = [row[:] for row in state.board]

    move = neural_network_move(game, state, O, model_dir=small_model_dir)

    assert move in game.actions(state)
    assert state.board == original


def test_returns_none_for_finished_game(small_model_dir):
    game = TicTacToe()
    state = GameState()
    state.board[0] = [X, X, X]

    assert neural_network_move(game, state, O, model_dir=small_model_dir) is None


def test_takes_winning_move(small_model_dir):
    game = TicTacToe()
    state = GameState()
    state.board[0][:2] = [X, X]
    state.board[1][:2] = [O, O]

    assert neural_network_move(game, state, X, model_dir=small_model_dir) == (0, 2)


def test_missing_model_gives_helpful_error(tmp_path):
    game = TicTacToe(connecting_pieces_to_win=3)
    state = GameState(rows=6, columns=7)

    with pytest.raises(FileNotFoundError, match="python -m Neural_Network.train"):
        neural_network_move(game, state, X, model_dir=str(tmp_path))


def test_rejects_invalid_player(small_model_dir):
    with pytest.raises(ValueError):
        neural_network_move(TicTacToe(), GameState(), EMPTY, model_dir=small_model_dir)
