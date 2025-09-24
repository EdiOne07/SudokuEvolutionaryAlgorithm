import random
import time
from typing import Annotated


def print_sudoku(board):
    for row in board:
        print(" ".join([str(num) for num in row]))


class SudokuGA:
    def __init__(self, puzzle, population_size, elite_size, mutation_rate, max_generations):
        self.puzzle = puzzle
        self.population_size = population_size
        self.elite_size:Annotated[int, "keep the best parents"] = elite_size
        self.mutation_rate = mutation_rate
        self.max_generations = max_generations
        # get location of the given numbers conatin in the board
        self.given_indices = [(r, c) for r in range(9) for c in range(9) if self.puzzle[r][c] != 0]
        self.population = self._initialize_population()

    def solve(self):
        for generation in range(self.max_generations):
            # Calculate fitness for the entire population. list of (ind, fitness)
            pop_with_fitness = [(ind, self.calculate_fitness(ind)) for ind in self.population]
            pop_with_fitness.sort(key=lambda x: x[1])

            # Check for a solution
            if pop_with_fitness[0][1] == 0:
                print(f"Solution found in generation {generation}!")
                return pop_with_fitness[0][0]

            # Create the next generation
            next_generation = []

            # Elitism: carry over the best individuals
            elites = [val[0] for val in pop_with_fitness[:self.elite_size]]
            next_generation.extend(elites)

            # Generate the rest of the population
            parents = self._selection(pop_with_fitness)

            num_offspring = self.population_size - self.elite_size
            for i in range(0, num_offspring, 2):
                if i + 1 < len(parents):
                    parent1 = parents[i]
                    parent2 = parents[i + 1]

                    child1 = self._crossover(parent1, parent2)
                    child2 = self._crossover(parent2, parent1)

                    next_generation.append(self._mutate(child1))
                    if len(next_generation) < self.population_size:
                        next_generation.append(self._mutate(child2))

            self.population = next_generation
            print(f"Generation {generation}: Best Fitness = {pop_with_fitness[0][1]}")
            print("-" * 20)

        return None

    def _create_individual(self):
        individual = [list(row) for row in self.puzzle]
        for r in range(9):
            row = individual[r]
            givens_in_row = {val for val in row if val != 0}
            missing_numbers = list(set(range(1, 10)) - givens_in_row)
            random.shuffle(missing_numbers)

            for c in range(9):
                if individual[r][c] == 0:
                    individual[r][c] = missing_numbers.pop()
        return individual

    def _initialize_population(self):
        return [self._create_individual() for _ in range(self.population_size)]

    @staticmethod
    def _get_column(grid, c):
        return [grid[r][c] for r in range(9)]

    @staticmethod
    def _get_block(grid, r, c):
        block_r, block_c = r // 3 * 3, c // 3 * 3
        return [grid[i][j] for i in range(block_r, block_r + 3) for j in range(block_c, block_c + 3)]

    # fitness calculate the duplicate number in column and block
    def calculate_fitness(self, individual):
        violations = 0

        # Column violations
        for c in range(9):
            column = self._get_column(individual, c)
            violations += 9 - len(set(column))

        # Block violations
        for r in range(0, 9, 3):
            for c in range(0, 9, 3):
                block = self._get_block(individual, r, c)
                violations += 9 - len(set(block))

        return violations

    @staticmethod
    def _selection(population_with_fitness, tournament_size=3):
        selected = []
        for _ in range(len(population_with_fitness)):
            tournament = random.sample(population_with_fitness, tournament_size)
            winner = min(tournament, key=lambda x: x[1])  # Winner has the lowest fitness (violations)
            selected.append(winner)
        return selected

    @staticmethod
    def _crossover(parent1, parent2):
        child = []
        for r in range(9):
            if random.random() < 0.5:
                child.append(parent1[0][r])
            else:
                child.append(parent2[0][r])
        return child

    def _mutate(self, individual):
        mutated_individual = [list(row) for row in individual]
        for r in range(9):
            if random.random() < self.mutation_rate:
                # Find indices of non-given numbers in this row
                mutable_indices = [c for c in range(9) if (r, c) not in self.given_indices]
                if len(mutable_indices) >= 2:
                    idx1, idx2 = random.sample(mutable_indices, 2)
                    mutated_individual[r][idx1], mutated_individual[r][idx2] = \
                        mutated_individual[r][idx2], mutated_individual[r][idx1]
        return mutated_individual


if __name__ == "__main__":
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    POPULATION_SIZE = 5000
    ELITE_SIZE = 10
    MUTATION_RATE = 0.2
    MAX_GENERATIONS = 1000

    ga = SudokuGA(puzzle=puzzle,
                  population_size=POPULATION_SIZE,
                  elite_size=ELITE_SIZE,
                  mutation_rate=MUTATION_RATE,
                  max_generations=MAX_GENERATIONS)

    start_time = time.perf_counter()
    solution = ga.solve()
    end_time = time.perf_counter()

    if solution is None:
        print("Max generations reached. No solution found.")
    else:
        print("\nBest solution found:")
        print_sudoku(solution)
        print(f"\nFinal Fitness (violations): {ga.calculate_fitness(solution)}")
        print(f"\nTime spent: {end_time - start_time}s")
