# Generic Tic-Tac-Toe AI 

A Python implementation of a generic two-dimensional Tic-Tac-Toe game stimulation with different AI algorithms.

## Functions in tic_tac_toe.py

- `insert_piece(row, column, piece)` places `"X"` or `"O"` at the zero-based
  position. It raises `IndexError` for an out-of-range position and
  `ValueError` for an invalid piece or an occupied position.
- `is_win()` returns `True` if either piece has the required number of
  connected pieces horizontally, vertically, or diagonally.
- `display_board()` prints the current board.

## Constants in tic_tac_toe.py

```python
ROWS = 3
COLUMNS = 3
CONNECTING_PIECES_TO_WIN = 3
```