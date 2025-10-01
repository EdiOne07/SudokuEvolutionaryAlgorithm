import random
import time
import logging
from typing import Annotated
import sudoku.boards as boards
import math
from sudoku_puzzle_generator import SudokuPuzzleGenerator


def print_sudoku(board, title="Sudoku Board"):
    """Pretty print a Sudoku board with nice formatting."""
    print(f"\n{title}")
    print("+=======+=======+=======+")
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
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


class SudokuGA:
    def __init__(self, puzzle, population_size, elite_size, mutation_rate, max_generations, puzzle_size):
        self.puzzle_size:Annotated[int, "this present the size of grid and has to be set to n^2 * n^2, that block can be sliced to n*n"] = puzzle_size
        self.block_size = int(math.sqrt(puzzle_size))
        self.puzzle = puzzle
        self.population_size = population_size
        self.elite_size:Annotated[int, "keep the best parents"] = elite_size
        self.mutation_rate = mutation_rate
        self.original_mutation_rate = mutation_rate  # Store original mutation rate
        self.max_generations = max_generations
        # get location of the given numbers conatin in the board
        self.given_indices = [(r, c) for r in range(self.puzzle_size) for c in range(self.puzzle_size) if self.puzzle[r][c] != 0]
        self.population = self._initialize_population()
        
        # Set up logging
        self.logger = logging.getLogger('SudokuGA')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_filename = f'sudoku_ga_log_{int(time.time())}.txt'
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
        
        self.logger.info(f"Starting Sudoku GA with parameters:")
        self.logger.info(f"Population size: {population_size}, Elite size: {elite_size}")
        self.logger.info(f"Initial mutation rate: {mutation_rate}, Max generations: {max_generations}")
        self.logger.info(f"Puzzle size: {puzzle_size}x{puzzle_size}")
        self.logger.info("-" * 50)
        
        # Adaptive mutation rate tracking
        self.stagnant_fitness = None  # The fitness value that's causing stagnation
        self.generations_stuck:Annotated[int, "this will count how many generations we've been stuck at this fitness"] = 0
        self.gen_stuck:Annotated[int, "this is a hyperparameter to adjust the generation stuck times"] = 50
        self.pop_stuck:Annotated[int, "this is a hyperparameter to adjust the population stuck times"] = 500
        self.mutation_increase:Annotated[float, "this is a hyperparameter to adjust the mutation increase rate"] = 0.01
        self.scale:Annotated[
            int, 
            "this is a hyperparameter to adjust the scale of current population should be keep to next generation\
            it always keep the worst individual\
            for instance,if scale is 2, then keep half of the population to next generation\
            "
            ] = 10

    def solve(self):
        best_fitness_overall = float('inf')
        best_individual_overall = None
        generations_without_improvement = 0
        
        for generation in range(self.max_generations):
            # Calculate fitness for the entire population. list of (ind, fitness)
            pop_with_fitness = [(ind, self.calculate_fitness(ind)) for ind in self.population]
            pop_with_fitness.sort(key=lambda x: x[1])
            
            current_best_fitness = pop_with_fitness[0][1]
            
            # # Track overall best fitness and individual
            if current_best_fitness < best_fitness_overall:
                best_fitness_overall = current_best_fitness
                best_individual_overall = [list(row) for row in pop_with_fitness[0][0]]  # Deep copy
                generations_without_improvement = 0
                # Reset stagnation tracking when we find improvement
                self.stagnant_fitness = current_best_fitness
                self.generations_stuck = 0
            else:
                generations_without_improvement += 1
                
                # Track stagnation for adaptive mutation
                if self.stagnant_fitness is None or self.stagnant_fitness != current_best_fitness:
                    # New fitness level, reset tracking
                    self.stagnant_fitness = current_best_fitness
                    self.generations_stuck = 1
                else:
                    # Same fitness as before, increment stagnation counter
                    self.generations_stuck += 1

            # Adaptive mutation rate adjustments
            if self.generations_stuck >= self.pop_stuck:
                # Keep some worst individuals from current generation using scale, then regenerate the rest
                self.logger.info(f"Generation {generation}: Population stuck for {self.generations_stuck} generations.")
                self.logger.info(f"Keeping worst {self.population_size // self.scale} individuals and regenerating the rest")
                
                # Keep worst individuals from current population
                worst_to_keep = self.population_size // self.scale
                worst_individuals = [val[0] for val in pop_with_fitness[-worst_to_keep:]]
                
                # Generate new individuals for the rest
                new_individuals = [self._create_individual() for _ in range(self.population_size - worst_to_keep)]
                
                # Combine worst kept individuals with new ones
                self.population = worst_individuals + new_individuals
                
                self.logger.info(f"Resetting mutation rate to {self.original_mutation_rate}")
                self.mutation_rate = self.original_mutation_rate
                self.stagnant_fitness = None
                self.generations_stuck = 0
                # Continue to next generation to evaluate the new population properly
                continue
            elif self.generations_stuck > 0 and self.generations_stuck % self.gen_stuck == 0:
                # Increase mutation rate every gen_stuck generations of stagnation
                old_mutation_rate = self.mutation_rate
                # for fixed mutation rate, it's better not to go above 0.3
                self.mutation_rate = min(0.3, self.mutation_rate + self.mutation_increase) 
                self.logger.info(f"Generation {generation}: Fitness stuck for {self.generations_stuck} generations.")
                self.logger.info(f"Increasing mutation rate from {old_mutation_rate:.2f} to {self.mutation_rate:.2f}")

            # Check for a solution
            if current_best_fitness == 0:
                self.logger.info(f"Solution found in generation {generation}!")
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
            self.logger.info(f"Generation {generation}: Best Fitness = {current_best_fitness}: Mutation Rate = {self.mutation_rate:.3f}")

        # If we reach here, max generations exceeded without finding solution
        self.logger.info(f"Maximum generations ({self.max_generations}) reached!")
        self.logger.info(f"Algorithm appears to be stuck at local minimum.")
        self.logger.info(f"Best fitness achieved: {best_fitness_overall} violations")
        self.logger.info(f"Generations without improvement: {generations_without_improvement}")
        print(f"\nMaximum generations ({self.max_generations}) reached!")
        print(f"Algorithm appears to be stuck at local minimum.")
        print(f"Best fitness achieved: {best_fitness_overall} violations")
        print(f"Generations without improvement: {generations_without_improvement}")
        
        # Show detailed violation information
        if best_individual_overall is not None:
            self.print_violation_details(best_individual_overall)
        
        return best_individual_overall

    def _create_individual(self):
        individual = [list(row) for row in self.puzzle]
        for r in range(self.puzzle_size):
            row = individual[r]
            givens_in_row = {val for val in row if val != 0}
            missing_numbers = list(set(range(1, self.puzzle_size + 1)) - givens_in_row)
            random.shuffle(missing_numbers)

            for c in range(self.puzzle_size):
                if individual[r][c] == 0:
                    individual[r][c] = missing_numbers.pop()
        return individual

    def _initialize_population(self):
        return [self._create_individual() for _ in range(self.population_size)]

    def _get_column(self, grid, c):
        return [grid[r][c] for r in range(self.puzzle_size)]

    def _get_block(self, grid, r, c):
        block_r, block_c = r // self.block_size * self.block_size, c // self.block_size * self.block_size
        return [grid[i][j] for i in range(block_r, block_r + self.block_size) for j in range(block_c, block_c + self.block_size)]

    # fitness calculate the duplicate number in column and block
    def calculate_fitness(self, individual, return_details=False):
        violations = 0
        violation_details = {'column_violations': [], 'block_violations': []}

        # Column violations
        for c in range(self.puzzle_size):
            column = self._get_column(individual, c)
            column_violations = self.puzzle_size - len(set(column))
            violations += column_violations
            
            if return_details and column_violations > 0:
                # Find duplicate numbers in this column
                seen = {}
                for r in range(self.puzzle_size):
                    num = individual[r][c]
                    if num in seen:
                        violation_details['column_violations'].append({
                            'column': c,
                            'duplicate_number': num,
                            'coordinates': seen[num] + [(r, c)]
                        })
                    else:
                        seen[num] = [(r, c)]

        # Block violations
        for block_r in range(0, self.puzzle_size, self.block_size):
            for block_c in range(0, self.puzzle_size, self.block_size):
                block = self._get_block(individual, block_r, block_c)
                block_violations = self.puzzle_size - len(set(block))
                violations += block_violations
                
                if return_details and block_violations > 0:
                    # Find duplicate numbers in this block
                    seen = {}
                    for i in range(self.block_size):
                        for j in range(self.block_size):
                            r, c = block_r + i, block_c + j
                            num = individual[r][c]
                            if num in seen:
                                violation_details['block_violations'].append({
                                    'block': f"({block_r//self.block_size},{block_c//self.block_size})",
                                    'duplicate_number': num,
                                    'coordinates': seen[num] + [(r, c)]
                                })
                            else:
                                seen[num] = [(r, c)]

        if return_details:
            return violations, violation_details
        return violations

    @staticmethod
    def _selection(population_with_fitness, tournament_size=2):
        selected = []
        for _ in range(len(population_with_fitness)):
            tournament = random.sample(population_with_fitness, tournament_size)
            winner = min(tournament, key=lambda x: x[1])  # Winner has the lowest fitness (violations)
            selected.append(winner)
        return selected

    def _crossover(self, parent1, parent2):
        child = []
        for r in range(self.puzzle_size):
            if random.random() < 0.5:
                child.append(parent1[0][r])
            else:
                child.append(parent2[0][r])
        return child

    def _mutate(self, individual):
        mutated_individual = [list(row) for row in individual]
        for r in range(self.puzzle_size):
            if random.random() < self.mutation_rate:
                # Find indices of non-given numbers in this row
                mutable_indices = [c for c in range(self.puzzle_size) if (r, c) not in self.given_indices]
                if len(mutable_indices) >= 2:
                    idx1, idx2 = random.sample(mutable_indices, 2)
                    mutated_individual[r][idx1], mutated_individual[r][idx2] = \
                        mutated_individual[r][idx2], mutated_individual[r][idx1]
        return mutated_individual

    def print_violation_details(self, individual):
        """Print detailed information about violations in the individual"""
        violations, details = self.calculate_fitness(individual, return_details=True)
        
        if violations == 0:
            print("No violations found!")
            return
            
        print(f"\nDetailed violation analysis (Total: {violations} violations):")
        print("=" * 60)
        
        # Column violations
        if details['column_violations']:
            print("\nCOLUMN VIOLATIONS:")
            for violation in details['column_violations']:
                coords_str = ', '.join([f"({r},{c})" for r, c in violation['coordinates']])
                print(f"  Column {violation['column']}: Number {violation['duplicate_number']} appears at coordinates: {coords_str}")
        
        # Block violations  
        if details['block_violations']:
            print("\nBLOCK VIOLATIONS:")
            for violation in details['block_violations']:
                coords_str = ', '.join([f"({r},{c})" for r, c in violation['coordinates']])
                print(f"  Block {violation['block']}: Number {violation['duplicate_number']} appears at coordinates: {coords_str}")


if __name__ == "__main__":
    # puzzle = boards.medium_board_2
    generator = SudokuPuzzleGenerator()
    puzzle, solution_original = generator.generate_puzzle(difficulty='medium')
    
    print_sudoku(puzzle, "Generated Sudoku Puzzle")
    print_sudoku(solution_original, "Generated Sudoku Solution")
    print("-" * 20)
    PUZZLE_SIZE = 9
    POPULATION_SIZE = 142
    ELITE_SIZE = 10
    MUTATION_RATE = 0.17 # the best mutation rate is 0.23 while we have to give some space for the adaptive mutation rate
    MAX_GENERATIONS = 100000

    ga = SudokuGA(puzzle=puzzle,
                  population_size=POPULATION_SIZE,
                  elite_size=ELITE_SIZE,
                  mutation_rate=MUTATION_RATE,
                  max_generations=MAX_GENERATIONS,
                  puzzle_size=PUZZLE_SIZE)

    start_time = time.perf_counter()
    solution = ga.solve()
    end_time = time.perf_counter()

    if solution is not None:
        final_fitness = ga.calculate_fitness(solution)
        if final_fitness == 0:
            print_sudoku(solution, "Perfect Solution Found!")
        else:
            print_sudoku(solution, f"Best Solution Found ({final_fitness} violations)")
        print(f"\nFinal Fitness (violations): {final_fitness}")
        
        # Show violation details if there are any violations
        if final_fitness > 0:
            ga.print_violation_details(solution)
    else:
        print("\nNo solution could be generated.")
    
    print(f"\nTime spent: {end_time - start_time}s")
