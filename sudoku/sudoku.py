import heuristic
class Sudoku:
    """A class to represent a Sudoku board."""
    _board: list[list[int]]
    _score: int

    def __init__(self, board: list[list[int]]):
        """Initializes a new instance of a Sudoku board.
        
            Parameters
            ----------
            board: list[list[int]]
                The sudoku board to use.
        """
        self._board = board
        self._score = heuristic.heuristic_score(board)

    def get_board(self) -> list[list[int]]:
        """Returns the current state of the board.
        
        Returns
        -------
        list[list[int]]
            The current state of the board.
        """
        return self._board
    
    def set_board(self, board: list[list[int]]):
        """Sets the current state of the board.
        
            Parameters
            ----------
            board: list[list[int]]
                The new state of the board.
        """
        self._board = board

    def check_goal_state(self) -> bool:
        """Check whether the current state is a goal state.

        Returns
        -------
        bool
            Whether the current state is a goal state."""
        
        # Check rows
        for row in self.board:
            if sum(row) != 45:
                return False
        
        # Check columns
        for j in range(9):
            column_sum = sum(self.board[i][j] for i in range(9))
            if column_sum != 45:
                return False
        
        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                box_sum = 0
                for i in range(3):
                    for j in range(3):
                        box_sum += self.board[box_row * 3 + i][box_col * 3 + j]
                if box_sum != 45:
                    return False
        
        return True
    
    def get_score(self) -> int:
        """Returns the current heuristic score of the board.
        
        Returns
        -------
        int
            The current heuristic score of the board.
        """
        return self._score
    
    def update_score(self):
        """Updates the current heuristic score of the board."""
        self._score = heuristic.heuristic_score(self._board)

    def visualize(self):
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