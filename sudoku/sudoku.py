class Sudoku:
    """A class to represent a Sudoku board."""
    board: list[list[int]]
    score: int

    def __init__(self, board: list[list[int]]):
        """Initializes a new instance of a Sudoku board.
        
            Parameters
            ----------
            board: list[list[int]]
                The sudoku board to use.
        """
        self.board = board
        self.score = 0

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
        return self.score
    
    def update_score(self):
        """Updates the current heuristic score of the board."""
        self.score = self.__heuristic_score()

    def __heuristic_score(self) -> int:
        '''
        Heuristic function that gives a score based on how many unique numbers are present on each row, column and 3x3 block
        WIll be further used in the evolutionary algorithm to determine how close to the ideal solution the board is
        '''
        score=0
        row_number=[]
        column_number=[]
        block_number=[]
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != 0:
                    row_number.append(self.board[i][j])
                if self.board[j][i] != 0:
                    column_number.append(self.board[j][i])
            score=score+len(set(row_number))+len(set(column_number))
            row_number.clear()
            column_number.clear()
        for box_row in range(0,9,3):
            for box_column in range(0,9,3):
                for i in range(3):
                    for j in range(3):
                        if self.board[box_row+i][box_column+j] != 0:
                            block_number.append(self.board[box_row+i][box_column+j])
                score=score+len(set(block_number))
                block_number.clear()
        print("Score calculated:", score)
        return score

    def visualize(self):
        """Pretty-print the sudoku board in the console with 3x3 blocks."""
        for i, row in enumerate(self.board):
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