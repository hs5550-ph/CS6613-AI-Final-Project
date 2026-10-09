# Generic Tic-Tac-Toe AI

A configurable two-dimensional Tic-Tac-Toe game for experimentation with AI
algorithms.

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

- `actions(state)` returns all avilable moves left in the format of `(row, column)`.
- `generate_random_move(state)` returns a random available move. It raises
  `ValueError` if there are no available moves.
- `insert_piece(state, row, column, piece)` places `X` or `O` at a zero-based
  position in the state. It raises `IndexError` for an out-of-range position
  and `ValueError` for an invalid piece or an occupied position.
- `is_win(state)` returns `True` if either piece has the required number of
  connected pieces horizontally, vertically, or diagonally.
- `is_terminal(state)` returns `True` when the state has a win or no legal
  actions remaining.
- `display_board(state)` prints the state's board.
