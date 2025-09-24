import boards
from sudoku import Sudoku
import random
import copy
import time

class SudokuEvolutionaryAlgorithm:
    """A sudoku solver that uses an evolutionary algorithm to solve the puzzle."""
    _initial_sudoku: Sudoku
    _population_size: int
    _mutation_rate: int
    _generation: int
    _population: list[Sudoku]
    _solution: Sudoku

    def __init__(self, initial_sudoku: Sudoku, population_size: int = 100, mutation_rate: int = 1):
        """Initializes the evolutionary algorithm class.
        
            Parameters
            ----------
            initial_sudoku: list[list[int]]
                The initial sudoku game board to use.
            population_size: int
                The size of the population.
            mutation_rate: int
                The number of possible mutations on each child when generating the next generation.
        """
        self._initial_sudoku = initial_sudoku
        self._population_size = population_size
        self._mutation_rate = mutation_rate
        self._generation = 0
        self._solution = None
        self._population = []

    def __initialize_population(self):
        """Creates the initial population for generation 0."""     
        for _ in range(self._population_size):
            randomly_filled_sudoku = Sudoku(copy.deepcopy(self._initial_sudoku.board))
            for i in range(9):
                for j in range(9):
                    if randomly_filled_sudoku.board[i][j] == 0:
                        randomly_filled_sudoku.board[i][j] = random.randint(1, 9)

            randomly_filled_sudoku.heuristic_matrix.initialize()
            self._population.append(randomly_filled_sudoku)
        print("Initial population created.")

    def __solution_found(self) -> bool:
        """Checks whether a solution has been found in the current population.

        Returns
        -------
        bool
            Whether a solution has been found.
        """
        for individual in self._population:
            if individual.heuristic_matrix.score == 243:
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
            print(f"Solution found in generation {self._generation}!")
            return False

        # Selection
        # Top 20% of population creates 80% of next generation
        self._population.sort(key=lambda x: x.heuristic_matrix.score, reverse=True)
        top_parents = self._population[:int(self._population_size * 0.2)]
        
        next_generation = []
        for i in range(int(self._population_size * 0.8)):
            parent1 = random.choice(top_parents)
            parent2 = random.choice(top_parents)
            child = self.__crossover(parent1, parent2)
            child = self.__mutate(child)
            next_generation.append(child)
        
        # 20% of the all population creates 20% of the next generation
        for i in range(int(self._population_size * 0.2)):
            parent1 = random.choice(self._population)
            parent2 = random.choice(self._population)
            child = self.__crossover(parent1, parent2)
            child = self.__mutate(child)
            next_generation.append(child)
        
        self._population = next_generation
        self._generation += 1
        print(f"Generation {self._generation} created.")
        return True

    def __crossover(self, parent1: Sudoku, parent2: Sudoku) -> Sudoku:
        """Performs crossover between two parents to create a child.

        Parameters
        ----------
        parent1: Sudoku
            The first parent.
        parent2: Sudoku
            The second parent.

        Returns
        -------
        Sudoku
            The child created from the two parents.
        """
        child = Sudoku(copy.deepcopy(self._initial_sudoku.board))
        for row in range(9):
            for column in range(9):
                if self._initial_sudoku.board[row][column] != 0:
                    continue
                if random.random() < 0.5:
                    child.board[row][column] = parent1.board[row][column]
                else:
                    child.board[row][column] = parent2.board[row][column]
        child.heuristic_matrix.initialize()
        return child    

    def __mutate(self, individual: Sudoku) -> Sudoku:
        """Randomly mutates the number of tiles given by the mutation_rate parameter of 
        the evolutionary algorithm of the given Sudoku that is not given by the initial board.
        # TODO: There are many ways to go about mutation. We should test around with different implementations. 

        Parameters
        ----------
        individual: Sudoku
            The individual to mutate.
        """
        positions = []
        #     position = random.randint(0, 80)
        #     position_tuple = [position // 9, position % 9]
        #     if self._initial_sudoku.board[position_tuple[0]][position_tuple[1]] == 0:
        #         positions.append(position_tuple)
        #     # Else don't mutate for now I guess?
        # for position in positions:
        #     individual.board[position[0]][position[1]] = random.randint(1, 9)
        

        for mutation in range(self._mutation_rate):
            row = random.randint(0, 8)
            column = random.randint(0, 8)
            if self._initial_sudoku.board[row][column] == 0:
                current_number = individual.board[row][column]

                # Count the appearances of the current number
                row_count = individual.board[row].count(current_number)
                col_count = [individual.board[row][column] for row in range(9)].count(current_number)
                block_row = (row // 3) * 3
                block_col = (column // 3) * 3
                block_count = [
                    individual.board[r][c]
                    for r in range(block_row, block_row + 3)
                    for c in range(block_col, block_col + 3)
                ].count(current_number)    

                if row_count > 1 or col_count > 1 or block_count > 1:
                    # How to figure out which numbers are good candidates to mutate to?
                    individual.board[row][column] = random.randint(1, 9)
                    individual.heuristic_matrix.update(row, column, individual.board[row][column])

        return individual

    def solve(self) -> Sudoku:
        """Solves the sudoku puzzle using an evolutionary algorithm."""
        self.__initialize_population()
        while self.__create_next_generation():
            pass
        return self._solution

if __name__ == "__main__":
    initial_board = Sudoku(boards.get_random_board())
    evolutionary_algorithm = SudokuEvolutionaryAlgorithm(initial_board, population_size=100, mutation_rate=5)
    
    start_time = time.time()
    solution = evolutionary_algorithm.solve()
    end_time = time.time()

    print("Solution:")
    print(solution.visualize())
    print(f"The evolutionary algoirthm took {end_time - start_time:.2f} seconds to solve this puzzle.")