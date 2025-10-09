import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sudoku_2.evolution import *
from generators.sudoku_puzzle_generator import SudokuPuzzleGenerator
import time
import glob
import re
import matplotlib.pyplot as plt
import numpy as np

class Analysis:
    def __init__(self):
        self.n_call = 100
        self.puzzle_size = 9
        self.population_size = 142
        self.elite_size = 10
        self.mutation_rate = 0.18
        self.max_generations = 100000
        self.difficulty:Annotated[
            str, 
            "this hyperparameter use to control the log file name and randomly difficulty for the board"
            ] = 'hard'

    # it's same with evolution main function
    def run(self):
        generator = SudokuPuzzleGenerator()
        for n in range(self.n_call):
            puzzle, solution = generator.generate_puzzle(difficulty=self.difficulty)
            print_sudoku(puzzle, "Generated Sudoku Puzzle")
            print_sudoku(solution, "Generated Sudoku Solution")
            print("-" * 50)
            ga = SudokuGA(puzzle=puzzle,
                  population_size=self.population_size,
                  elite_size=self.elite_size,
                  mutation_rate=self.mutation_rate,
                  max_generations=self.max_generations,
                  puzzle_size=self.puzzle_size,
                  difficulty=self.difficulty)
            start_time = time.perf_counter()
            solution = ga.solve()
            end_time = time.perf_counter()
            if solution is not None:
                final_fitness = ga.calculate_fitness(solution)
                if final_fitness == 0:
                    print_sudoku(solution, "Perfect Solution Found!")
                    print(f"Solution found in {end_time - start_time:.2f} seconds")
                else:
                    print_sudoku(solution, f"Best Solution Found ({final_fitness} violations)")
                    print(f"Solution found in {end_time - start_time:.2f} seconds")
            else:
                print(f"no solution and spent {end_time - start_time:.2f} seconds")
    
    def analyze_logs(self):
        logs_dir = 'logs'
        logs = glob.glob(os.path.join(logs_dir, 'sudoku_ga_log_*.txt'))
        for log in logs:
            with open(log, 'r') as f:
                print(f.read())
    
    def detailed_log_analysis(self):
        """
        Comprehensive analysis of genetic algorithm log files.
        Parses log data and extracts performance metrics.
        """
        logs_dir = 'logs'
        logs = glob.glob(os.path.join(logs_dir, f'sudoku_ga_log_{self.difficulty}.txt'))

        if not logs:
            print("No log files found!")
            return None
        
        all_results = []
        
        for log_file in logs:
            print(f"\n=== Analyzing {log_file} ===")
            
            with open(log_file, 'r') as f:
                content = f.read()
                
            # Parse log data (returns list of results)
            log_results = self._parse_log_content(content)
            
            if log_results:
                all_results.extend(log_results)
                print(f"Found {len(log_results)} solution records")
                self._print_batch_summary(log_results)
        
        if len(all_results) > 1:
            self._compare_multiple_runs(all_results)
        
        return all_results
    
    def _parse_log_content(self, content):
        """Parse log content and extract key metrics"""
        lines = content.strip().split('\n')
        
        results = []  # Store multiple results for multiple runs in same log
        current_run_data = {}  # Temporary storage for building a complete record
        
        for line in lines:
            # Skip separator lines
            if line.strip() == '-' * 50:
                continue
                
            # Look for successful solution lines
            solution_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - Solution found in generation (\d+)! \(Execution time: ([\d.]+)s\)', line)
            if solution_match:
                timestamp, generation, exec_time = solution_match.groups()
                data = {
                    'timestamp': timestamp,
                    'generation': int(generation),
                    'execution_time': float(exec_time),
                    'total_time': float(exec_time),
                    'violations': 0,  # Successful solutions have 0 violations
                    'success': True,
                    'stuck_at_local_minimum': False,
                    'generations_without_improvement': None,
                    'reason': 'solution_found'
                }
                results.append(data)
                current_run_data = {}  # Reset for next run
                continue
                
            # Look for maximum generations reached (failed runs)
            max_gen_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - Maximum generations \((\d+)\) reached! \(Execution time: ([\d.]+)s\)', line)
            if max_gen_match:
                timestamp, max_gen, exec_time = max_gen_match.groups()
                current_run_data.update({
                    'timestamp': timestamp,
                    'generation': int(max_gen),
                    'execution_time': float(exec_time),
                    'total_time': float(exec_time),
                    'success': False,
                    'reason': 'max_generations_reached'
                })
                continue
                
            # Look for local minimum detection
            if 'Algorithm appears to be stuck at local minimum' in line:
                current_run_data['stuck_at_local_minimum'] = True
                continue
                
            # Look for best fitness achieved
            fitness_match = re.search(r'Best fitness achieved: (\d+) violations?', line)
            if fitness_match:
                current_run_data['violations'] = int(fitness_match.group(1))
                continue
                
            # Look for generations without improvement
            no_improvement_match = re.search(r'Generations without improvement: (\d+)', line)
            if no_improvement_match:
                current_run_data['generations_without_improvement'] = int(no_improvement_match.group(1))
                # This is typically the last line of a failed run, so finalize the record
                if current_run_data:
                    # Set default values for any missing fields
                    current_run_data.setdefault('stuck_at_local_minimum', False)
                    current_run_data.setdefault('violations', None)
                    results.append(current_run_data.copy())
                    current_run_data = {}
                continue
        
        # Handle any remaining incomplete run data
        if current_run_data and 'generation' in current_run_data:
            current_run_data.setdefault('stuck_at_local_minimum', False)
            current_run_data.setdefault('violations', None)
            current_run_data.setdefault('generations_without_improvement', None)
            results.append(current_run_data)
        
        return results
    
    def _print_batch_summary(self, results):
        """Print summary for a batch of results"""
        if not results:
            return
            
        # Basic metrics
        generations = [r['generation'] for r in results]
        exec_times = [r['execution_time'] for r in results]
        
        # Success/failure analysis
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"Total runs: {len(results)}")
        print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
        print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
        
        print(f"Execution time range: {min(exec_times):.2f}s - {max(exec_times):.2f}s")
        print(f"Average generation: {np.mean(generations):.1f}")
        print(f"Average execution time: {np.mean(exec_times):.2f}s")
        
        if exec_times and generations:
            avg_gen_per_sec = np.mean([g/t for g, t in zip(generations, exec_times)])
            print(f"Average generations per second: {avg_gen_per_sec:.2f}")
        
        # Failed run analysis
        if failed:
            print(f"\n=== FAILED RUNS ANALYSIS ===")
            stuck_runs = [r for r in failed if r.get('stuck_at_local_minimum', False)]
            print(f"Runs stuck at local minimum: {len(stuck_runs)}")
            
            violations = [r['violations'] for r in failed if r.get('violations') is not None]
            if violations:
                print(f"Best fitness achieved in failed runs: {min(violations)} - {max(violations)} violations")
                print(f"Average violations in failed runs: {np.mean(violations):.1f}")
            
            no_improvement = [r['generations_without_improvement'] for r in failed if r.get('generations_without_improvement') is not None]
            if no_improvement:
                print(f"Generations without improvement: {min(no_improvement)} - {max(no_improvement)}")
                print(f"Average generations without improvement: {np.mean(no_improvement):.1f}")
        
        print("-" * 50)
    
    def _compare_multiple_runs(self, results):
        """Compare metrics across multiple runs"""
        print("\n=== COMPARISON ACROSS RUNS ===")
        
        generations = [r['generation'] for r in results if r['generation']]
        exec_times = [r['execution_time'] for r in results if r['execution_time']]
        violations = [r['violations'] for r in results if r['violations'] is not None]
        success_rate = sum(1 for r in results if r['success']) / len(results)
        
        # Separate successful and failed runs
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if generations:
            print(f"Generations - Avg: {np.mean(generations):.1f}, Min: {min(generations)}, Max: {max(generations)}")
        
        if exec_times:
            print(f"Execution Time - Avg: {np.mean(exec_times):.2f}s, Min: {min(exec_times):.2f}s, Max: {max(exec_times):.2f}s")
        
        if violations:
            print(f"Violations - Avg: {np.mean(violations):.1f}, Min: {min(violations)}, Max: {max(violations)}")
        
        print(f"Success Rate: {success_rate:.1%}")
        
        # Detailed failure analysis
        if failed:
            print(f"\n=== FAILURE ANALYSIS ===")
            print(f"Total failed runs: {len(failed)}")
            
            stuck_count = sum(1 for r in failed if r.get('stuck_at_local_minimum', False))
            if stuck_count > 0:
                print(f"Runs stuck at local minimum: {stuck_count} ({stuck_count/len(failed)*100:.1f}% of failures)")
            
            failed_violations = [r['violations'] for r in failed if r.get('violations') is not None]
            if failed_violations:
                print(f"Failed runs violations - Avg: {np.mean(failed_violations):.1f}, Min: {min(failed_violations)}, Max: {max(failed_violations)}")
            
            no_improvement_counts = [r['generations_without_improvement'] for r in failed if r.get('generations_without_improvement') is not None]
            if no_improvement_counts:
                print(f"Generations without improvement - Avg: {np.mean(no_improvement_counts):.1f}, Min: {min(no_improvement_counts)}, Max: {max(no_improvement_counts)}")
        
        # Success vs failure time comparison
        if successful and failed:
            success_times = [r['execution_time'] for r in successful if r['execution_time']]
            failed_times = [r['execution_time'] for r in failed if r['execution_time']]
            
            if success_times and failed_times:
                print(f"\n=== TIME COMPARISON ===")
                print(f"Successful runs - Avg time: {np.mean(success_times):.2f}s")
                print(f"Failed runs - Avg time: {np.mean(failed_times):.2f}s")
                print(f"Time difference: {np.mean(failed_times) - np.mean(success_times):.2f}s (failed runs take longer)")
    
    def visualize_performance(self):
        """Create visualization of execution time vs generation from logs"""
        logs_dir = 'logs'
        logs = glob.glob(os.path.join(logs_dir, 'sudoku_ga_log_*.txt'))
        
        if not logs:
            print("No log files found for visualization!")
            return
        
        all_results = []
        for log_file in logs:
            with open(log_file, 'r') as f:
                content = f.read()
            log_results = self._parse_log_content(content)
            if log_results:
                all_results.extend(log_results)
        
        if not all_results:
            print("No valid log data found!")
            return
        
        # Extract generation and execution time data
        generations = [r['generation'] for r in all_results if r['generation']]
        exec_times = [r['execution_time'] for r in all_results if r['execution_time']]
        
        if not (generations and exec_times):
            print("No generation and execution time data found!")
            return
        
        print(f"Plotting {len(generations)} data points")
        
        # Create single chart
        plt.figure(figsize=(10, 6))
        plt.scatter(generations, exec_times, alpha=0.7, s=50)
        plt.xlabel('Generation', fontsize=12)
        plt.ylabel('Execution Time (s)', fontsize=12)
        plt.title('Execution Time vs Generation', fontsize=14)
        plt.grid(True, alpha=0.3)
        
        # Add trend line if there are enough points
        if len(generations) > 1:
            z = np.polyfit(generations, exec_times, 1)
            p = np.poly1d(z)
            plt.plot(generations, p(generations), "r--", alpha=0.8, label=f'Trend line')
            plt.legend()
        
        plt.tight_layout()
        plt.savefig('generation_vs_execution_time.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Visualization saved as 'generation_vs_execution_time.png'")
    
    def visualize_performance_bars(self):
        """Create bar chart showing generation ranges vs execution time ranges"""
        logs_dir = 'logs'
        logs = glob.glob(os.path.join(logs_dir, f'sudoku_ga_log_{self.difficulty}.txt'))
        
        if not logs:
            print("No log files found for visualization!")
            return
        
        all_results = []
        for log_file in logs:
            with open(log_file, 'r') as f:
                content = f.read()
            log_results = self._parse_log_content(content)
            if log_results:
                all_results.extend(log_results)
        
        if not all_results:
            print("No valid log data found!")
            return
        
        # Extract data
        generations = [r['generation'] for r in all_results if r['generation']]
        exec_times = [r['execution_time'] for r in all_results if r['execution_time']]
        
        if not (generations and exec_times):
            print("No generation and execution time data found!")
            return
        
        # Define bins
        time_bins = [0, 0.5, 2, 20, float('inf')]
        time_labels = ['Quick (≤0.5s)', 'Medium (0.5-2s)', 'Slow (2-20s)', 'Very Slow (>20s)']
        
        gen_bins = [0, 50, 100, 500, 1000, max(generations) + 1]
        gen_labels = ['0-50', '50-100', '100-500', '500-1000', f'1000+']
        
        # Create a matrix to count combinations
        data_matrix = np.zeros((len(gen_labels), len(time_labels)))
        
        for gen, time in zip(generations, exec_times):
            # Find generation bin
            gen_idx = 0
            for i, threshold in enumerate(gen_bins[1:]):
                if gen < threshold:
                    gen_idx = i
                    break
            else:
                gen_idx = len(gen_labels) - 1
            
            # Find time bin
            time_idx = 0
            for i, threshold in enumerate(time_bins[1:]):
                if time < threshold:
                    time_idx = i
                    break
            else:
                time_idx = len(time_labels) - 1
            
            data_matrix[gen_idx, time_idx] += 1
        
        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(gen_labels))
        width = 0.2
        colors = ['#2E8B57', '#FFD700', '#FF6347', '#8B0000']  # Green, Gold, Tomato, Dark Red
        
        for i, (time_label, color) in enumerate(zip(time_labels, colors)):
            bars = ax.bar(x + i * width, data_matrix[:, i], width, 
                         label=time_label, color=color, alpha=0.8)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Generation Range', fontsize=12)
        ax.set_ylabel('Number of Solutions', fontsize=12)
        ax.set_title('Solution Distribution: Generation Range vs Execution Time', fontsize=14)
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(gen_labels)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add total count annotation
        total_solutions = len(generations)
        ax.text(0.02, 0.98, f'Total Solutions: {total_solutions}', 
                transform=ax.transAxes, fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                verticalalignment='top')
        
        plt.tight_layout()
        plt.savefig(f'generation_execution_time_bars_{self.difficulty}.png', dpi=300, bbox_inches='tight')
        plt.show()
        print(f"Bar chart saved as 'generation_execution_time_bars_{self.difficulty}.png'")
        
        # Print summary statistics
        print("\n=== PERFORMANCE DISTRIBUTION SUMMARY ===")
        for i, gen_label in enumerate(gen_labels):
            total_in_gen = sum(data_matrix[i, :])
            if total_in_gen > 0:
                print(f"\nGeneration {gen_label}: {int(total_in_gen)} solutions")
                for j, time_label in enumerate(time_labels):
                    count = int(data_matrix[i, j])
                    if count > 0:
                        percentage = (count / total_in_gen) * 100
                        print(f"  - {time_label}: {count} ({percentage:.1f}%)")
        
        print(f"\nOverall time distribution:")
        for j, time_label in enumerate(time_labels):
            total_in_time = sum(data_matrix[:, j])
            if total_in_time > 0:
                percentage = (total_in_time / total_solutions) * 100
                print(f"  - {time_label}: {int(total_in_time)} ({percentage:.1f}%)")


if __name__ == "__main__":
    analysis = Analysis()
    analysis.run()
    
    # print("=== DETAILED LOG ANALYSIS ===")
    # results = analysis.detailed_log_analysis()
    
    # if results:
    #     print("\n=== CREATING SCATTER PLOT ===")
    #     analysis.visualize_performance()
        
    #     print("\n=== CREATING BAR CHART ===")
    #     analysis.visualize_performance_bars()
