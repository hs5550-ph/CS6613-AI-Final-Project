import random

NUMBER_OF_ROWS = 3
NUMBER_OF_COLUMNS = 3
CONNECTING_PIECES_TO_WIN = 3
EMPTY = " "
X = "X"
O = "O"
CELL_SEPARATOR = " | "
ROW_SEPARATOR = "+"


class TicTacToe:
    def __init__(
        self,
        rows: int = NUMBER_OF_ROWS,
        columns: int = NUMBER_OF_COLUMNS,
        connecting_pieces_to_win: int = CONNECTING_PIECES_TO_WIN,
    ) -> None:
        if rows < 1 or columns < 1 or connecting_pieces_to_win < 1:
            raise ValueError("Board dimensions and win length must be positive")

        self.rows = rows
        self.columns = columns
        self.connecting_pieces_to_win = connecting_pieces_to_win
        self.board = [[EMPTY for _ in range(columns)] for _ in range(rows)]

    def generate_random_move(self) -> tuple[int, int]:
        available_moves = [
            (row_index, column_index)
            for row_index, row in enumerate(self.board)
            for column_index, piece in enumerate(row)
            if piece == EMPTY
        ]
        if not available_moves:
            raise ValueError("No available moves")

        return random.choice(available_moves)

    def insert_piece(self, row: int, column: int, piece: str) -> None:
        if not 0 <= row < self.rows or not 0 <= column < self.columns:
            raise IndexError("Board position is out of range")
        if piece not in (X, O):
            raise ValueError("Piece must be X or O")
        if self.board[row][column] != EMPTY:
            raise ValueError("Board position is already occupied")

        self.board[row][column] = piece

    def is_win(self) -> bool:
        directions = ((0, 1), (1, 0), (1, 1), (1, -1))

        for row in range(self.rows):
            for column in range(self.columns):
                piece = self.board[row][column]
                if piece == EMPTY:
                    continue

                for row_step, column_step in directions:
                    end_row = row + (self.connecting_pieces_to_win - 1) * row_step
                    end_column = column + (
                        self.connecting_pieces_to_win - 1
                    ) * column_step
                    if not (
                        0 <= end_row < self.rows
                        and 0 <= end_column < self.columns
                    ):
                        continue

                    if all(
                        self.board[row + offset * row_step][
                            column + offset * column_step
                        ]
                        == piece
                        for offset in range(1, self.connecting_pieces_to_win)
                    ):
                        return True

        return False

    def display_board(self) -> None:
        for row_index, row in enumerate(self.board):
            print(CELL_SEPARATOR.join(row))
            if row_index < self.rows - 1:
                print(ROW_SEPARATOR.join("---" for _ in range(self.columns)))


if __name__ == "__main__":
    TicTacToe().display_board()
