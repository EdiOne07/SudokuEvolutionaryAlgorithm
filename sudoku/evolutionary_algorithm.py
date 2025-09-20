import sudoku.boards as boards
from sudoku.sudoku import Sudoku
import heuristic
import random


class SudokuEvolutionaryAlgorithm:
    """A sudoku solver that uses an evolutionary algorithm to solve the puzzle."""
    _initial_board: Sudoku
    _population_size: int
    _mutation_rate: int
    _generations: int
    _population: list[Sudoku]
    _solution: Sudoku

    def __init__(self, initial_board: Sudoku, population_size: int = 100, mutation_rate: int = 1):
        """Initializes the evolutionary algorithm class.
        
            Parameters
            ----------
            initial_board: list[list[int]]
                The initial sudoku game board to use.
            population_size: int
                The size of the population.
            mutation_rate: int
                The number of possible mutations on each child when generating the next generation.
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
            print(f"Solution found in generation {self._generations}!")
            return False

        # Selection
        # Top 20% of population creates 80% of next generation
        self._population.sort(key=lambda x: x.get_score(), reverse=True)
        top_parents = self._population[:int(self._population_size * 0.2)]
        
        next_generation = list[Sudoku]
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
        self._generations += 1
        print(f"Generation {self._generations} created.")
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
        child = Sudoku(self._initial_board)
        for row in range(9):
            for column in range(9):
                if self._initial_board[row][column] != 0:
                    continue
                if random.random() < 0.5:
                    child[row][column] = parent1[row][column]
                else:
                    child[row][column] = parent2[row][column]
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
        positions = list[tuple[int]]
        for mutation in range(self._mutation_rate):
            position = random.randint(0, 80)
            position_tuple = [position // 9, position % 9]
            if self._initial_board[position_tuple[0]][position_tuple[1]] == 0:
                positions.append(position_tuple)
            # Else don't mutate for now I guess?
        for position in positions:
            individual[position[0]][position[1]] = random.randint(1, 9)
        return individual

    def solve(self) -> Sudoku:
        """Solves the sudoku puzzle using an evolutionary algorithm."""
        pass

if __name__ == "__main__":
    pass