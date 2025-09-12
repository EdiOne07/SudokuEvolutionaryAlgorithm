# my plans for this class (if something doesnt make sense just correct me):
# 1. general game logic (place number, check if game is finished, check if number is valid)
# 2. initializing random boards (todo: figure out how to randomly initialize solvable boards)
# 3. keep track of statistics (how many errors per game) 
#   3.1. if the agent tries to place a number in a position where a number already exists, its not an error but an exception.

class SudokuEngine:
    """A sudoku game engine that supports 9x9 boards."""
    _matrix = []
    _visualize_game = False
    _errors = 0

    def __init__(self, visualize_game = False):
        self._visualize_game = visualize_game
        self._matrix = [[0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0]]

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
            raise Exception(f"Provided number {number} is not in allowed range of 1-9!")
        current_num = self._matrix[row][column]
        if current_num != 0:
            raise Exception(f"Can't override existing value of {current_num} in row {row} column {column}!")
        self.__place_number(row, column, number)
        if self._visualize_game:
            self.__visualize()
        return (self._matrix, self.__check_goal_state(), True)
    
    def __place_number(self, row, column, number) -> bool:
        """Places the number if it is a valid placement, or otherwise increases the number of errors.
        
        Returns
        -------
        bool
            Whether the placement was successful."""
        # TODO: validate number (does there exist the same number in the same row, column, or 3x3 grid?) and afterwards return whether successful or not
        self._matrix[row][column] = number
    
    def __check_goal_state(self) -> bool:
        """Check whether the current state is a goal state.

        Returns
        -------
        bool
            Whether the current state is a goal state."""
        for i in range(9):
            for j in range(9):
                if self._matrix[i][j] == 0:
                    return False
        return True

    def __visualize(self):
        """Pretty-print the Sudoku board in the console with 3x3 blocks."""
        for i, row in enumerate(self._matrix):
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

if __name__ == '__main__':
    board = SudokuEngine(visualize_game=True)
    board.next(0,1,5)
    board.next(0,2,6)