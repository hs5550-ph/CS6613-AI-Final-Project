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
ROWS = 3
COLUMNS = 3
CONNECTING_PIECES_TO_WIN = 3

## Tests

Install pytest if needed, then run the suite from the parent directory:

```bash
python -m pip install pytest
python -m pytest Tic_Tak_Toe/tests
```

The tests cover piece insertion, invalid moves, wins in each direction,
custom board dimensions, a four-piece win, and board display.
