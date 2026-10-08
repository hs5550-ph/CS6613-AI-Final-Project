ROWS = 3
COLUMNS = 3
CONNECTING_PIECES_TO_WIN = 3
EMPTY = " "
X = "X"
O = "O"

board = [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]


def insert_piece(row: int, column: int, piece: str) -> None:
    if not 0 <= row < ROWS or not 0 <= column < COLUMNS:
        raise IndexError("Board position is out of range")
    if piece not in (X, O):
        raise ValueError("Piece must be X or O")
    if board[row][column] != EMPTY:
        raise ValueError("Board position is already occupied")

    board[row][column] = piece


def is_win() -> bool:
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))

    for row in range(ROWS):
        for column in range(COLUMNS):
            piece = board[row][column]
            if piece == EMPTY:
                continue

            for row_step, column_step in directions:
                end_row = row + (CONNECTING_PIECES_TO_WIN - 1) * row_step
                end_column = column + (CONNECTING_PIECES_TO_WIN - 1) * column_step
                if not (0 <= end_row < ROWS and 0 <= end_column < COLUMNS):
                    continue

                if all(
                    board[row + offset * row_step][column + offset * column_step]
                    == piece
                    for offset in range(1, CONNECTING_PIECES_TO_WIN)
                ):
                    return True

    return False


def display_board() -> None:
    for row_index, row in enumerate(board):
        print(" | ".join(row))
        if row_index < ROWS - 1:
            print("+".join("---" for _ in range(COLUMNS)))


if __name__ == "__main__":
    display_board()
