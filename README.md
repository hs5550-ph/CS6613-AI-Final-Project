# Generic Tic-Tac-Toe AI

A two-dimensional Tic-Tac-Toe game with different AI algorithms.

## Creating a game and state

`TicTacToe` contains the general game rules. `GameState` contains the board and represents one particular game. 

```python
from Tic_Tak_Toe.tic_tac_toe import *

game = TicTacToe()
state1 = GameState()
state2 = GameState()

game.insert_piece(state1, 0, 0, X)
game.insert_piece(state2, 2, 2, O)

print(game.actions(state1))
game.display_board(state1)
game.display_board(state2)
```

## Module constants

```python
NUMBER_OF_ROWS = 3
NUMBER_OF_COLUMNS = 3
CONNECTING_PIECES_TO_WIN = 3
EMPTY = " "
X = "X"
O = "O"
```

## Game operations

- `actions(state)` returns all avilable moves left. Each move is represented by a tuple of two integers in the format of `(row, column)`.
- `generate_random_move(state)` returns a random available move. It raises
  `ValueError` if there are no available moves.
- `insert_piece(state, row, column, piece)` places `X` or `O` at a zero-based
  position in the state. It raises `IndexError` for an out-of-range position
  and `ValueError` for an invalid piece or an occupied position.
- `is_win(state, player)` returns `True` if the specified player has the
  required number of connected pieces horizontally, vertically, or diagonally.
- `is_terminal(state)` returns `True` when the state has a win or no legal
  actions remaining.
- `display_board(state)` prints the state's board.
- `utility_function(state, player)` return the score of utility for a particular player. 

## Utility function for alpha-beta pruning

Alpha-beta pruning needs a utility function that scores a state from the current
player's perspective. Provide a custom utility that accepts a `GameState` and the
current player, then pass it to `TicTacToe`:

```python
def utility(state, current_player):
    //Example utility function. Note that you need to implement your own utility function. 
    x_count = sum(row.count(X) for row in state.board)
    o_count = sum(row.count(O) for row in state.board)
    if current_player == X:
        return x_count - o_count
    return o_count - x_count


game = TicTacToe(utility_function=utility) 
utility = game.utility_fuction(state, tic_tac_toe.X)
```

## Alpha-beta pruning

`Alpha_Beta_Pruning.alpha_beta_pruning.alpha_beta_search` searches the game
tree and returns the best `(row, column)` move for the player to move. Its
optional `max_depth` parameter sets the search limit in plies and defaults to 6.

- `alpha_beta_search(game, state, tic_tac_toe.X)` run alpha beta pruning. 

```python
from Alpha_Beta_Pruning.alpha_beta_pruning import alpha_beta_search

move = alpha_beta_search(game, state, tic_tac_toe.X)
move = alpha_beta_search(game, state, tic_tac_toe.X, max_depth=4)
```

## Running the stimulation

Run the 10-game alpha-beta comparison with:

```bash
python3 start.py
```

`start.py` configures X and O strategies and calls `run_stimulation()`. Set
`max_depth` there to configure the alpha-beta search depth. The runner's
interface is:

```python
run_stimulation(
    x_strategy,
    o_strategy,
    number_of_games,
    print_game=True,
    print_summary=True,
)
```

`print_game` and `print_summary` independently control per-game reports and the
final summary. If both are `False`, the function produces no output.
`starting_player` and `utility` are optional keyword arguments.
`simulate_game()` remains a silent, single-game interface that returns a
`GameResult` with the winner and move/state history.
