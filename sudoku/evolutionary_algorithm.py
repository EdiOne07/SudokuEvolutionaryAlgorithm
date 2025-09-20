import sudoku.boards as boards
from sudoku.sudoku import Sudoku
import heuristic
import random


class SudokuEvolutionaryAlgorithm:
    """A sudoku solver that uses an evolutionary algorithm to solve the puzzle."""
    _initial_board: Sudoku
    _population_size: int
    _mutation_rate: float
    _generations: int
    _population: list[Sudoku]
    _solution: Sudoku

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
        self._solution = None

    def __initialize_population(self):
        """Creates the initial population for generation 0."""     
        for _ in range(self._population_size):
            randomly_filled_board = Sudoku(self._initial_board)
            for i in range(9):
                for j in range(9):
                    if randomly_filled_board[i][j] == 0:
                        randomly_filled_board[i][j] = random.randint(1, 9)

            randomly_filled_board.update_score()
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
                self._solution = individual
                return True
        return False
    
    def __create_next_generation(self) -> bool:
        """Creates the next generation of the population.
        
        Returns
        -------
        bool
            Whether the next generation was created.
            If false is returned, a solution has been found.
        """
        if self.__solution_found():
            return False

        # Selection
        # Top 20% of population creates 80% of next generation
        # 20% of the all population creates 20% of the next generation
        self._population.sort(key=lambda x: x.get_score(), reverse=True)   
        
        return True           


    def solve(self) -> Sudoku:
        """Solves the sudoku puzzle using an evolutionary algorithm."""
        pass

if __name__ == "__main__":
    pass