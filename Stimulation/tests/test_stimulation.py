from contextlib import redirect_stdout
from io import StringIO

import Stimulation.stimulation as stimulation
from Stimulation.stimulation import run_stimulation, utility_function


def first_available_move(game, state, _player):
    return game.actions(state)[0]


def test_run_stimulation_is_silent_when_print_summary_is_false():
    output = StringIO()

    with redirect_stdout(output):
        results = run_stimulation(
            first_available_move,
            first_available_move,
            number_of_games=1,
            print_game=False,
            print_summary=False,
            utility=utility_function,
        )

    assert output.getvalue() == ""
    assert sum(results.values()) == 1


def test_run_stimulation_prints_game_without_summary_when_requested():
    output = StringIO()

    with redirect_stdout(output):
        run_stimulation(
            first_available_move,
            first_available_move,
            number_of_games=1,
            print_game=True,
            print_summary=False,
            utility=utility_function,
        )

    report = output.getvalue()
    assert "Game 1/1" in report
    assert "Move 1:" in report
    assert "Final results" not in report


def test_run_stimulation_prints_summary_without_games_when_requested():
    output = StringIO()

    with redirect_stdout(output):
        run_stimulation(
            first_available_move,
            first_available_move,
            number_of_games=1,
            print_game=False,
            print_summary=True,
            utility=utility_function,
        )

    report = output.getvalue()
    assert "Game 1/1" not in report
    assert "Final results" in report


def test_run_stimulation_reports_x_and_o_strategy_times_separately(monkeypatch):
    wall_clock = iter(range(100))
    cpu_clock = iter(range(100))
    monkeypatch.setattr(stimulation, "perf_counter", lambda: next(wall_clock))
    monkeypatch.setattr(stimulation, "process_time", lambda: next(cpu_clock))
    output = StringIO()

    with redirect_stdout(output):
        run_stimulation(
            first_available_move,
            first_available_move,
            number_of_games=1,
            print_game=True,
            print_summary=True,
            utility=utility_function,
        )

    report = output.getvalue()
    assert "X strategy time: 4.0000s wall-clock, 4.0000s CPU" in report
    assert "O strategy time: 3.0000s wall-clock, 3.0000s CPU" in report
    assert "X strategy total: 4.0000s wall-clock, 4.0000s CPU" in report
    assert "O strategy total: 3.0000s wall-clock, 3.0000s CPU" in report


def test_run_stimulation_passes_configured_board_dimensions_to_strategies():
    observed_dimensions = []

    def tracking_strategy(game, state, _player):
        observed_dimensions.append((state.rows, state.columns))
        return game.actions(state)[0]

    run_stimulation(
        tracking_strategy,
        tracking_strategy,
        number_of_games=1,
        print_game=False,
        print_summary=False,
        number_of_rows=4,
        number_of_columns=5,
        utility=utility_function,
    )

    assert observed_dimensions
    assert set(observed_dimensions) == {(4, 5)}


def test_run_stimulation_passes_configured_win_length_to_strategies():
    observed_configurations = []

    def tracking_strategy(game, state, _player):
        observed_configurations.append(
            (state.rows, state.columns, game.connecting_pieces_to_win)
        )
        return game.actions(state)[0]

    run_stimulation(
        tracking_strategy,
        tracking_strategy,
        number_of_games=1,
        print_game=False,
        print_summary=False,
        number_of_rows=4,
        number_of_columns=5,
        connecting_pieces_to_win=2,
    )

    assert observed_configurations
    assert set(observed_configurations) == {(4, 5, 2)}
