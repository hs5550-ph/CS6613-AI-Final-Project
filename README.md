# Generic Tic-Tac-Toe AI

A configurable two-dimensional Tic-Tac-Toe game for experimentation with AI
algorithms.

## Creating a game and state

`TicTacToe` contains the general game rules. `GameState` contains the board and represents one particular game. 

```python
from Tic_Tak_Toe.tic_tac_toe import *

game = TicTacToe()
state = game.initial_state()

game.insert_piece(state, 0, 0, X)
game.insert_piece(state, 1, 1, O)
print(game.actions(state))
game.display_board(state)
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

- `actions(state)` returns all avilable positions left in the format of `(row, column)`.
- `generate_random_move(state)` returns a random available action. It raises
  `ValueError` if there are no available moves.
- `insert_piece(state, row, column, piece)` places `X` or `O` at a zero-based
  position in the state. It raises `IndexError` for an out-of-range position
  and `ValueError` for an invalid piece or an occupied position.
- `is_win(state)` returns `True` if either piece has the required number of
  connected pieces horizontally, vertically, or diagonally.
- `is_terminal(state)` returns `True` when the state has a win or no legal
  actions remaining.
- `display_board(state)` prints the state's board.
