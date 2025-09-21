# my plans for this class (if something doesnt make sense just correct me):
# 1. general game logic (place number, check if game is finished, check if number is valid)
# 2. initializing random boards (todo: figure out how to randomly initialize solvable boards)
# 3. keep track of statistics (how many errors per game) 
#   3.1. if the agent tries to place a number in a position where a number already exists, its not an error but an exception.
#   3.2. maybe also remember errors per game for the last x games?

import sudoku.boards as boards
from sudoku.exceptions import InvalidNumberError, CellAlreadyFilledError

class SudokuEngine:
    # TODO: add function to reset board
    # TODO: use numpy arrays instead of matrixes?? do we want that or not?
    """A sudoku game engine that supports 9x9 boards."""
    _board = []
    _visualize_game = False
    _errors = 0

    def __init__(self, visualize_game = False, custom_board = None):
        """Initializes a new instance of this class.
        
            Parameters
            ----------
            difficulty: str
                TODO
            visualize_game: bool
                Whether to visualize the board in the console after every move.
            custom_board: list[list[int]]
                A custom sudoku board to use instead of a random one."""
        self._visualize_game = visualize_game
        if custom_board is not None:
            self._board = custom_board
        else:
            self._board = boards.get_random_board()

    def get_board(self) -> list[list[int]]:
        return self._board

    def next(self, row: int, column: int, number: int) -> tuple[list[list[int]], bool, bool]:
        """Handles the game logic.

            Parameters
            ----------
            row: int
                The row to place the number at. Has to be in range 0 <= row <= 8.
            column: int
                The column to place the number at. Has to be in range 0 <= column <= 8.
            number: int
                The number to place. Has to be in range 1 <= number <= 9.

            Returns
            -------
            list[list[int]]
                The sudoku matrix.
            bool
                Whether the current state is a goal state.
            bool
                Whether the placement was successful."""
        if number < 1 or number > 9:
            raise InvalidNumberError(f"Provided number {number} is not in allowed range of 1-9!")
        current_num = self._board[row][column]
        if current_num != 0:
            raise CellAlreadyFilledError(row, column, current_num)
        success = self.__place_number(row, column, number)
        if self._visualize_game:
            self.__visualize()
        return (self._board, self.__check_goal_state(), success)

    def __place_number(self, row, column, number) -> bool:
        """Places the number if it is a valid placement, or otherwise increases the number of errors.
        
        Returns
        -------
        bool
            Whether the placement was successful."""
        existing_numbers = set()
        # iterate all numbers in same row and same column
        for i in range(9):
            existing_numbers.add(self._board[row][i])
            existing_numbers.add(self._board[i][column])
        # iterate all numbers in same 3x3 cluster 
        row_start, row_end = row // 3 * 3, row // 3 * 3 + 2
        col_start, col_end = column // 3 * 3, column // 3 * 3 + 2 
        for i in range(row_start, row_end + 1):
            for j in range(col_start, col_end + 1):
                existing_numbers.add(self._board[i][j])
        # check if specified number already exists
        if number in existing_numbers:
            return False
        self._board[row][column] = number
        return True

    def __check_goal_state(self) -> bool:
        """Check whether the current state is a goal state.

        Returns
        -------
        bool
            Whether the current state is a goal state."""
        for i in range(9):
            for j in range(9):
                if self._board[i][j] == 0:
                    return False
        return True

    def __visualize(self):
        """Pretty-print the sudoku board in the console with 3x3 blocks."""
        for i, row in enumerate(self._board):
            if i % 3 == 0:
                print("+=======+=======+=======+")
            row_str = ""
            for j, num in enumerate(row):
                if j % 3 == 0:
                    row_str += "| "
                cell = str(num) if num != 0 else "."
                row_str += cell + " "
            row_str += "|"
            print(row_str)
        print("+=======+=======+=======+")

if __name__ == "__main__":
    engine = SudokuEngine()
    print(engine.get_board())