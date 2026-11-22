from time import perf_counter, process_time

from Alpha_Beta_Pruning.alpha_beta_pruning import alpha_beta_search
from Tic_Tak_Toe.tic_tac_toe import O, X
from stimulation import (
    GameStrategy,
    UtilityFunction,
    make_game,
    simulate_game,
    utility_function,
)
from summary import print_game_report, print_summary

NUMBER_OF_GAMES = 10
STARTING_PLAYER = X


def main() -> None:
    x_strategy: GameStrategy = alpha_beta_search
    o_strategy: GameStrategy = alpha_beta_search
    utility: UtilityFunction = utility_function
    display_game = make_game(utility)

    results = {X: 0, O: 0, "draw": 0}
    total_wall_clock_time = 0.0
    total_cpu_time = 0.0

    for game_number in range(1, NUMBER_OF_GAMES + 1):
        wall_clock_start = perf_counter()
        cpu_start = process_time()
        game_result = simulate_game(
            game_number,
            NUMBER_OF_GAMES,
            STARTING_PLAYER,
            x_strategy,
            o_strategy,
            utility,
        )
        game_wall_clock_time = perf_counter() - wall_clock_start
        game_cpu_time = process_time() - cpu_start
        total_wall_clock_time += game_wall_clock_time
        total_cpu_time += game_cpu_time

        if game_result.winner is None:
            results["draw"] += 1
        else:
            results[game_result.winner] += 1
        print_game_report(
            game_number,
            NUMBER_OF_GAMES,
            STARTING_PLAYER,
            game_result,
            display_game,
            game_wall_clock_time,
            game_cpu_time,
        )

    print_summary(
        results,
        NUMBER_OF_GAMES,
        x_strategy,
        o_strategy,
        total_wall_clock_time,
        total_cpu_time,
    )


if __name__ == "__main__":
    main()
