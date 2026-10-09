# Generic Tic-Tac-Toe AI

A Python implementation of a configurable two-dimensional Tic-Tac-Toe game for
experimentation with AI algorithms.

## Playing a game

Create a `TicTacToe` instance for each game. 
```python
from Tic_Tak_Toe.tic_tac_toe import TicTacToe, X, O

game = TicTacToe()
```
## Module constants

These constants are defined at module scope and can be imported directly:

```python
NUMBER_OF_ROWS = 3
NUMBER_OF_COLUMNS = 3
CONNECTING_PIECES_TO_WIN = 3
EMPTY = " "
X = "X"
O = "O"
CELL_SEPARATOR = " | "
ROW_SEPARATOR = "+"
```

## `TicTacToe` methods

- `generate_random_move()` returns a random `(row, column)` position that is
  empty on this game's board. It raises `ValueError` if the board is full.
- `insert_piece(row, column, piece)` places `X` or `O` at the zero-based
  position on this game's board. It raises `IndexError` for an out-of-range
  position and `ValueError` for an invalid piece or an occupied position.
- `is_win()` returns `True` if either piece has the required number of
  connected pieces horizontally, vertically, or diagonally on this board.
- `display_board()` prints this game's board.
