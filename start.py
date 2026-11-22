from functools import partial

from Alpha_Beta_Pruning.alpha_beta_pruning import alpha_beta_search
from stimulation import GameStrategy, STARTING_PLAYER, run_stimulation

NUMBER_OF_GAMES = 100

def main() -> None:
    # First test, 10 alpha-beta vs alpha-beta
    max_depth = 6
    x_strategy: GameStrategy = partial(alpha_beta_search, max_depth=max_depth)
    o_strategy: GameStrategy = partial(alpha_beta_search, max_depth=max_depth)
    run_stimulation(
        x_strategy,
        o_strategy,
        NUMBER_OF_GAMES,
        print_game=True,
        print_summary=True,
        starting_player=STARTING_PLAYER,
    )


if __name__ == "__main__":
    main()
