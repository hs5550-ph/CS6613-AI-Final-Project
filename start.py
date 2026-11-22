from functools import partial

from Alpha_Beta_Pruning.alpha_beta_pruning import alpha_beta_search
from Stimulation.stimulation import GameStrategy, STARTING_PLAYER, run_stimulation

NUMBER_OF_GAMES = 10

def main() -> None:
    # TEST 1
    # Alpha-beta pruning vs Alpha-beta pruning with 3 * 3 board
    max_depth = 6
    number_of_rows = 3
    number_of_columns = 3
    connecting_pieces_to_win = 3
    x_strategy: GameStrategy = partial(alpha_beta_search, max_depth=max_depth)
    o_strategy: GameStrategy = partial(alpha_beta_search, max_depth=max_depth)
    run_stimulation(
        x_strategy,
        o_strategy,
        NUMBER_OF_GAMES,
        print_game=True,
        print_summary=True,
        number_of_rows=number_of_rows,
        number_of_columns=number_of_columns,
        connecting_pieces_to_win=connecting_pieces_to_win,
        starting_player=STARTING_PLAYER,
    )


if __name__ == "__main__":
    main()
