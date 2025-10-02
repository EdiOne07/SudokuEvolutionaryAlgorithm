import numpy as np
import time
from typing import Dict, Tuple, List
from skopt import gp_minimize
from skopt.space import Integer, Real
from skopt.utils import use_named_args
import matplotlib.pyplot as plt
from evolution import SudokuGA
import sudoku.boards as boards


class SudokuBayesianOptimization:
    """
    how this works overview:
    - define a function: f(x) = GA performance, where x is the mutaion rate and population size, the performance is the best fitness achieved after like 10000 generations\
        Uses Gaussian Process models to predict performance, which can tells where the good regions probably are and where are uncertain.\
            Every time running GA is costly and noisy, GP models the function smoothly. account for uncertainty.
    - try a few random hyperparameters, like 100 population and 0.1 mutation rate
    - unsolved penalty is fitness * 100 + solving time, and if it's timetout, penalty is 1000
    - find the minimum of score that we got the best output, use that population size and mutation rate to solve the puzzle
    """
    
    def __init__(self, puzzle, puzzle_size: int = 9, max_generations: int = 5000, 
                 elite_size: int = 10, timeout: float = 300.0, difficulty: str = 'easy'):
        self.puzzle = puzzle
        self.puzzle_size = puzzle_size
        self.max_generations = max_generations
        self.elite_size = elite_size
        self.timeout = timeout
        self.optimization_history = []
        self.difficulty = difficulty
        
        # Define the search space, range of mutation rate is silimilar to evolution.py, or it will to random mutation
        self.dimensions = [
            Integer(low=50, high=1000, name='population_size'),
            Real(low=0.05, high=0.4, name='mutation_rate')
        ]
    
    def objective_function(self, params: List) -> float:
        """
        Objective function to minimize. Returns a score based on:
        - Time to solve (if solved)
        - Fitness achieved
        - Generations needed
        
        Parameters:
        -----------
        params : List
            [population_size, mutation_rate]
            
        Returns:
        --------
        float
            Score to minimize (lower is better)
        """
        population_size, mutation_rate = params
        population_size = int(population_size)
        
        print(f"\nTesting: Population={population_size}, Mutation Rate={mutation_rate:.4f}")
        
        try:
            # Create and run GA
            ga = SudokuGA(
                puzzle=self.puzzle,
                population_size=population_size,
                elite_size=self.elite_size,
                mutation_rate=mutation_rate,
                max_generations=self.max_generations,
                puzzle_size=self.puzzle_size,
                difficulty=self.difficulty
            )
            
            start_time = time.perf_counter()
            solution = ga.solve()
            end_time = time.perf_counter()
            
            solving_time = end_time - start_time
            
            if solution is not None:
                final_fitness = ga.calculate_fitness(solution)
            else:
                final_fitness = float('inf')
            
            # Calculate score based on multiple factors
            if final_fitness == 0:
                # Perfect solution found
                score = solving_time  # Minimize solving time for perfect solutions
                print(f"✓ SOLVED in {solving_time:.2f}s!")
            else:
                # Partial solution - penalize based on violations and time
                score = final_fitness * 100 + solving_time  # Heavy penalty for violations
                print(f"✗ Not solved. Violations: {final_fitness}, Time: {solving_time:.2f}s")
            
            # Store results for analysis
            self.optimization_history.append({
                'population_size': population_size,
                'mutation_rate': mutation_rate,
                'score': score,
                'solving_time': solving_time,
                'final_fitness': final_fitness,
                'solved': final_fitness == 0
            })
            
            # Timeout penalty
            if solving_time > self.timeout:
                print(f"Timeout reached ({self.timeout}s)")
                return score + 1000  # Heavy penalty for timeout
                
            return score
            
        except Exception as e:
            # For most of time it wont reach here, just for safety, if input is None type then rise exception
            print(f"Error during evaluation: {e}")
            return 10000
    
    def optimize(self, n_calls: int = 25, random_state: int = 42) -> Dict:
        """
        Run Bayesian optimization to find optimal hyperparameters.
        
        Parameters:
        -----------
        n_calls : int
            Number of optimization iterations
        random_state : int
            Random seed for reproducibility
            
        Returns:
        --------
        Dict
            Optimization results including best parameters
        """
        print("Starting Bayesian Optimization for Sudoku GA Hyperparameters")
        print("=" * 60)
        print(f"Search space:")
        print(f"  - Population size: {self.dimensions[0].low} to {self.dimensions[0].high}")
        print(f"  - Mutation rate: {self.dimensions[1].low:.3f} to {self.dimensions[1].high:.3f}")
        print(f"  - Number of optimization calls: {n_calls}")
        print(f"  - Max generations per run: {self.max_generations}")
        print(f"  - Timeout per run: {self.timeout}s")
        print()
        
        # Use named args decorator for cleaner interface
        @use_named_args(self.dimensions)
        def objective(**params):
            return self.objective_function([params['population_size'], params['mutation_rate']])
        
        # Run optimization
        start_optimization = time.perf_counter()
        result = gp_minimize(
            func=objective, # the function to minimize, it run the GA with given parameters and return the score
            dimensions=self.dimensions, # the search space
            n_calls=n_calls, # how many evaluations to run
            random_state=random_state,#  for reproducibility results
            #Expected Improvement, this tells the optimizer to pick the next parameter that are most likely\
            # to improve the current best score
            acq_func='EI',
            n_initial_points=10,  # start with 10 random parameter conbinations to get initial data
            noise=0.1  # tell the GP model that objective function is noisy, maybe 0.1 is a good value
        )
        end_optimization = time.perf_counter()
        
        # Extract best parameters
        best_population_size = int(result.x[0])
        best_mutation_rate = result.x[1]
        best_score = result.fun
        
        optimization_results = {
            'best_population_size': best_population_size,
            'best_mutation_rate': best_mutation_rate,
            'best_score': best_score,
            'optimization_time': end_optimization - start_optimization,
            'n_calls': n_calls,
            'all_results': result,
            'history': self.optimization_history
        }
        
        # Print results
        print("\n" + "=" * 60)
        print("BAYESIAN OPTIMIZATION COMPLETED")
        print("=" * 60)
        print(f"Best parameters found:")
        print(f"  - Population size: {best_population_size}")
        print(f"  - Mutation rate: {best_mutation_rate:.4f}")
        print(f"  - Best score: {best_score:.2f}")
        print(f"Total optimization time: {optimization_results['optimization_time']:.1f}s")
        
        # Show statistics about successful runs
        solved_runs = [h for h in self.optimization_history if h['solved']]
        if solved_runs:
            avg_solve_time = np.mean([r['solving_time'] for r in solved_runs])
            print(f"Successful solves: {len(solved_runs)}/{len(self.optimization_history)}")
            print(f"Average solving time for successful runs: {avg_solve_time:.2f}s")
        else:
            print("No runs successfully solved the puzzle completely")
        
        return optimization_results
    
    def plot_optimization_history(self, results: Dict, save_path: str = None):
        """
        Plot the optimization history and parameter relationships.
        
        Parameters:
        -----------
        results : Dict
            Results from optimize() method
        save_path : str
            Optional path to save the plot
        """
        history = results['history']
        if not history:
            print("No history to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Bayesian Optimization Results for Sudoku GA', fontsize=16)
        
        # Plot 1: Score over iterations
        scores = [h['score'] for h in history]
        iterations = range(1, len(scores) + 1)
        axes[0, 0].plot(iterations, scores, 'b-o', markersize=3)
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Score (lower is better)')
        axes[0, 0].set_title('Optimization Progress')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Highlight best score
        best_idx = np.argmin(scores)
        axes[0, 0].plot(best_idx + 1, scores[best_idx], 'ro', markersize=8, label=f'Best: {scores[best_idx]:.2f}')
        axes[0, 0].legend()
        
        # Plot 2: Population size vs Score
        pop_sizes = [h['population_size'] for h in history]
        colors = ['green' if h['solved'] else 'red' for h in history]
        axes[0, 1].scatter(pop_sizes, scores, c=colors, alpha=0.6)
        axes[0, 1].set_xlabel('Population Size')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].set_title('Population Size vs Performance')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Mutation rate vs Score
        mut_rates = [h['mutation_rate'] for h in history]
        axes[1, 0].scatter(mut_rates, scores, c=colors, alpha=0.6)
        axes[1, 0].set_xlabel('Mutation Rate')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].set_title('Mutation Rate vs Performance')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Parameter space exploration
        solved_mask = [h['solved'] for h in history]
        axes[1, 1].scatter(
            [h['population_size'] for h in history if not h['solved']], 
            [h['mutation_rate'] for h in history if not h['solved']], 
            c='red', alpha=0.6, label='Not solved', s=50
        )
        if any(solved_mask):
            axes[1, 1].scatter(
                [h['population_size'] for h in history if h['solved']], 
                [h['mutation_rate'] for h in history if h['solved']], 
                c='green', alpha=0.8, label='Solved', s=100, marker='s'
            )
        
        # Highlight best point
        best_result = history[best_idx]
        axes[1, 1].scatter(
            best_result['population_size'], 
            best_result['mutation_rate'], 
            c='blue', s=200, marker='*', 
            label=f'Best: Pop={best_result["population_size"]}, Mut={best_result["mutation_rate"]:.3f}',
            edgecolors='black', linewidth=2
        )
        
        axes[1, 1].set_xlabel('Population Size')
        axes[1, 1].set_ylabel('Mutation Rate')
        axes[1, 1].set_title('Parameter Space Exploration')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def test_best_parameters(self, results: Dict, num_runs: int = 5) -> Dict:
        """
        Test the best found parameters multiple times to validate performance.
        
        Parameters:
        -----------
        results : Dict
            Results from optimize() method
        num_runs : int
            Number of test runs
            
        Returns:
        --------
        Dict
            Test results statistics
        """
        print(f"\nTesting best parameters {num_runs} times...")
        print(f"Population size: {results['best_population_size']}")
        print(f"Mutation rate: {results['best_mutation_rate']:.4f}")
        print("-" * 40)
        
        test_results = []
        
        for run in range(num_runs):
            print(f"Test run {run + 1}/{num_runs}...")
            
            ga = SudokuGA(
                puzzle=self.puzzle,
                population_size=results['best_population_size'],
                elite_size=self.elite_size,
                mutation_rate=results['best_mutation_rate'],
                max_generations=self.max_generations,
                puzzle_size=self.puzzle_size
            )
            
            start_time = time.perf_counter()
            solution = ga.solve()
            end_time = time.perf_counter()
            
            solving_time = end_time - start_time
            final_fitness = ga.calculate_fitness(solution) if solution is not None else float('inf')
            
            test_results.append({
                'run': run + 1,
                'solved': final_fitness == 0,
                'solving_time': solving_time,
                'final_fitness': final_fitness
            })
            
            if final_fitness == 0:
                print(f"  ✓ Solved in {solving_time:.2f}s")
            else:
                print(f"  ✗ Not solved. Violations: {final_fitness}, Time: {solving_time:.2f}s")
        
        # Calculate statistics
        solved_runs = [r for r in test_results if r['solved']]
        success_rate = len(solved_runs) / num_runs * 100
        
        stats = {
            'success_rate': success_rate,
            'total_runs': num_runs,
            'successful_runs': len(solved_runs),
            'test_results': test_results
        }
        
        if solved_runs:
            solve_times = [r['solving_time'] for r in solved_runs]
            stats.update({
                'avg_solve_time': np.mean(solve_times),
                'min_solve_time': np.min(solve_times),
                'max_solve_time': np.max(solve_times),
                'std_solve_time': np.std(solve_times)
            })
        
        print("\n" + "=" * 40)
        print("TEST RESULTS SUMMARY")
        print("=" * 40)
        print(f"Success rate: {success_rate:.1f}% ({len(solved_runs)}/{num_runs})")
        
        if solved_runs:
            print(f"Average solve time: {stats['avg_solve_time']:.2f}s ± {stats['std_solve_time']:.2f}s")
            print(f"Fastest solve: {stats['min_solve_time']:.2f}s")
            print(f"Slowest solve: {stats['max_solve_time']:.2f}s")
        
        return stats


def run_optimization_example():
    """
    Example of how to use the Bayesian optimization for Sudoku GA.
    """
    
    'I wanna control variables so only use one board to get the best parameters'
    puzzle = boards.medium_board_2
    
    print("Sudoku Puzzle:")
    for row in puzzle:
        print(" ".join([str(num) if num != 0 else '.' for num in row]))
    print()
    
    # Initialize Bayesian optimization
    optimizer = SudokuBayesianOptimization(
        puzzle=puzzle,
        puzzle_size=9,
        max_generations=10000,
        elite_size=10,
        timeout=120.0
    )
    
    # Run optimization
    results = optimizer.optimize(n_calls=100, random_state=420)
    optimizer.plot_optimization_history(results, save_path='bayesian_optimization_results.png')
    
    # Test best parameters
    test_stats = optimizer.test_best_parameters(results, num_runs=3)
    
    return results, test_stats


if __name__ == "__main__":
    # Install required packages if not available
    try:
        import skopt
    except ImportError:
        print("Please install required packages:")
        print("pip install scikit-optimize matplotlib numpy pandas")
        exit(1)
    
    # Run the optimization example
    results, test_stats = run_optimization_example()
    
    print("\nOptimization completed successfully!")
    print(f"Recommended settings:")
    print(f"  - Population size: {results['best_population_size']}")
    print(f"  - Mutation rate: {results['best_mutation_rate']:.4f}")
