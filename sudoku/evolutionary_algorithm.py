import sudoku.boards as boards
from sudoku.sudoku import Sudoku
import random


class SudokuEvolutionaryAlgorithm:
    """A sudoku solver that uses an evolutionary algorithm to solve the puzzle."""
    _initial_board: Sudoku
    _population_size: int
    _mutation_rate: float
    _generations: int
    _population: list[Sudoku]

    def __init__(self, initial_board: Sudoku, population_size: int = 100, mutation_rate: float = 0.01):
        """Initializes the evolutionary algorithm class.
        
            Parameters
            ----------
            initial_board: list[list[int]]
                The initial sudoku game board to use.
            population_size: int
                The size of the population.
            mutation_rate: float
                The mutation rate.
        """
        self._initial_board = initial_board
        self._population_size = population_size
        self._mutation_rate = mutation_rate
        self._generations = 0

    def __initialize_population(self):
        """Creates the initial population for generation 0."""     
        for _ in range(self._population_size):
            randomly_filled_board = Sudoku(self._initial_board)
            for i in range(9):
                for j in range(9):
                    if randomly_filled_board[i][j] == 0:
                        randomly_filled_board[i][j] = random.randint(1, 9)

            self._population.append(randomly_filled_board)

    def __solution_found(self) -> bool:
        """Checks whether a solution has been found in the current population.

        Returns
        -------
        bool
            Whether a solution has been found.
        """
        for individual in self._population:
            if individual.check_goal_state():
                return True
        return False

    def solve(self) -> Sudoku:
        """Solves the sudoku puzzle using an evolutionary algorithm."""
        pass

if __name__ == "__main__":
    pass