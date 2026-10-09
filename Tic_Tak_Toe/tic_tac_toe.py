import random
from collections.abc import Callable

NUMBER_OF_ROWS = 3
NUMBER_OF_COLUMNS = 3
CONNECTING_PIECES_TO_WIN = 3
EMPTY = " "
X = "X"
O = "O"
CELL_SEPARATOR = " | "
ROW_SEPARATOR = "+"


class GameState:
    def __init__(
        self,
        rows: int = NUMBER_OF_ROWS,
        columns: int = NUMBER_OF_COLUMNS,
    ) -> None:
        if rows < 1 or columns < 1:
            raise ValueError("Board dimensions must be positive")

        self.rows = rows
        self.columns = columns
        self.board = [[EMPTY for _ in range(columns)] for _ in range(rows)]


class TicTacToe:
    def __init__(
        self,
        connecting_pieces_to_win: int = CONNECTING_PIECES_TO_WIN,
        utility_function: Callable[[GameState, str], float] | None = None,
    ) -> None:
        if connecting_pieces_to_win < 1:
            raise ValueError("Win length must be positive")

        self.connecting_pieces_to_win = connecting_pieces_to_win
        self.utility_function = utility_function

    def actions(self, state: GameState) -> list[tuple[int, int]]:
        return [
            (row_index, column_index)
            for row_index, row in enumerate(state.board)
            for column_index, piece in enumerate(row)
            if piece == EMPTY
        ]

    def generate_random_move(self, state: GameState) -> tuple[int, int]:
        available_moves = self.actions(state)
        if not available_moves:
            raise ValueError("No available moves")

        return random.choice(available_moves)

    def insert_piece(
        self,
        state: GameState,
        row: int,
        column: int,
        piece: str,
    ) -> None:
        if not 0 <= row < state.rows or not 0 <= column < state.columns:
            raise IndexError("Board position is out of range")
        if piece not in (X, O):
            raise ValueError("Piece must be X or O")
        if state.board[row][column] != EMPTY:
            raise ValueError("Board position is already occupied")

        state.board[row][column] = piece

    def _is_win_for_piece(self, state: GameState, target_piece: str) -> bool:
        directions = ((0, 1), (1, 0), (1, 1), (1, -1))

        for row in range(state.rows):
            for column in range(state.columns):
                piece = state.board[row][column]
                if piece != target_piece:
                    continue

                for row_step, column_step in directions:
                    end_row = row + (self.connecting_pieces_to_win - 1) * row_step
                    end_column = column + (
                        self.connecting_pieces_to_win - 1
                    ) * column_step
                    if not (
                        0 <= end_row < state.rows
                        and 0 <= end_column < state.columns
                    ):
                        continue

                    if all(
                        state.board[row + offset * row_step][
                            column + offset * column_step
                        ]
                        == piece
                        for offset in range(1, self.connecting_pieces_to_win)
                    ):
                        return True

        return False

    def is_win(self, state: GameState, player: str) -> bool:
        if player not in (X, O):
            raise ValueError("Player must be X or O")
        return self._is_win_for_piece(state, player)

    def utility(self, state: GameState, current_player: str) -> float:
        if current_player not in (X, O):
            raise ValueError("Player must be X or O")
        if self.utility_function is not None:
            return self.utility_function(state, current_player)
        else:
            raise NotImplementedError("Utility function is not implemented")
        

    def is_terminal(self, state: GameState) -> bool:
        return (
            self.is_win(state, X)
            or self.is_win(state, O)
            or not self.actions(state)
        )

    def display_board(self, state: GameState) -> None:
        for row_index, row in enumerate(state.board):
            print(CELL_SEPARATOR.join(row))
            if row_index < state.rows - 1:
                print(ROW_SEPARATOR.join("---" for _ in range(state.columns)))


if __name__ == "__main__":
    game = TicTacToe()
    game.display_board(GameState())
