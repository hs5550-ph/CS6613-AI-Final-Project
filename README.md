# Generic Tic-Tac-Toe AI

A two-dimensional Tic-Tac-Toe game with different AI algorithms.

## Running a stimulation

The `start.py` runs the stimulation. Provide the implemented strategies and run it with:

```bash
python3 start.py
```

The interface is defined in `Stimulation/stimulation.py`:

```python
run_stimulation(
    x_strategy,
    o_strategy,
    number_of_games,
    print_game,
    print_summary,
    number_of_rows=3,
    number_of_columns=3,
    connecting_pieces_to_win=3,
    starting_player=X,
    utility=None,
)
```

`x_strategy` and `o_strategy` are move-selection algorithm we choose, for example alpha_beta pruning. 
`print_game` and `print_summary` independently control per-game output and the
final summary. The default utility scores a win as `1`, a loss as `-1`, and
other states as `0`, using the configured win length. Supply `utility` to use
a custom utility function. The function returns counts for X wins, O wins,
and draws.

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





## Neural network

`Neural_Network.neural_network.neural_network_move` picks a move with a trained
neural network and **no tree search**. It has the same signature as
`alpha_beta_search`, so it can be used as `x_strategy` or `o_strategy`.

How it picks a move: for every legal move it builds the resulting board, the
network scores each one from -1 (losing) to +1 (winning) for the player who
moved, and the highest-scoring move is played.

The network is a small multilayer perceptron written with NumPy
(`Neural_Network/network.py`). It is trained by self-play with temporal
difference learning (`Neural_Network/train.py`): each position is trained
toward minus the opponent's best reply score, and finished games give exact
targets (+1 win, 0 draw). Training data is multiplied by the board's
rotations and reflections.

Requires Python 3.10+ and NumPy (`pip install numpy`).

```python
from Neural_Network.neural_network import neural_network_move

run_stimulation(neural_network_move, alpha_beta_search, NUMBER_OF_GAMES, True, True)
```

Each board size and win length needs its own trained model, stored as
`Neural_Network/models/nn_<rows>x<columns>_win<win>.npz`. Models are included
for 3x3 (3 in a row), 4x4 (3 and 4 in a row) and 5x5 (4 in a row). To train
another one, run from the project root:

```bash
python -m Neural_Network.train --rows 6 --columns 6 --win 4 --games 50000
python -m Neural_Network.train --preset all   # retrain every included model
```

Training time is not counted in the simulation's timing, only the time to
choose moves.
