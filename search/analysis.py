from typing import Annotated
from generators.sudoku_puzzle_generator import SudokuPuzzleGenerator
import time
from search import dfs
import logging
import os
import glob
import re
import numpy as np

class Analysis:
    def __init__(self):
        self.runs = 1000
        self.puzzle_size = 9
        self.difficulty:Annotated[
            str, 
            "this hyperparameter use to control the log file name and randomly difficulty for the board"
            ] = 'hard'
        
        # logging
        self.logger = logging.getLogger('SudokuDFS')
        self.logger.setLevel(logging.INFO)
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)
        log_filename = os.path.join(logs_dir, f'sudoku_dfs_log_{self.difficulty}.txt')
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
        
        self.logger.info("-" * 50)
    
    def run(self):
        generator = SudokuPuzzleGenerator()
        for _ in range(self.runs):
            puzzle, _ = generator.generate_puzzle(difficulty=self.difficulty)
            
            start_time = time.perf_counter()
            solved = dfs.DFS(puzzle)
            end_time = time.perf_counter()
            if solved:
                self.logger.info(f"Solution found in {end_time - start_time:.2f} seconds")
            else:
                self.logger.info(f"No solution found and spent {end_time - start_time:.2f} seconds")
    
    def _parse_log_content(self, content):
        """Parse log content and extract key metrics"""
        lines = content.strip().split('\n')
        
        results = []  # Store multiple results for multiple runs in same log
        
        for line in lines:
            # Skip separator lines
            if line.strip() == '-' * 50:
                continue

            solution_match = re.search(r'Solution found in\s+([0-9]+(?:\.[0-9]+)?)\s+seconds', line)
            if solution_match:
                exec_time = solution_match.group(1)
                results.append(exec_time)
                continue

        return results

    def detailed_log_analysis(self):
        """
        Comprehensive analysis of dfs log files.
        Parses log data and extracts performance metrics.
        """
        logs_dir = 'logs'
        logs = glob.glob(os.path.join(logs_dir, f'sudoku_dfs_log_{self.difficulty}.txt'))

        if not logs:
            print("No log files found!")
            return None
        
        for log_file in logs:
            print(f"\n=== Analyzing {log_file} ===")
            
            with open(log_file, 'r') as f:
                content = f.read()
                
            # Parse log data (returns list of results)
            log_results = self._parse_log_content(content)
            a = np.array(log_results, dtype=float)
            print("number of runs:", len(log_results))
            print("fastest time:", a.min())
            print("longest time:", a.max())
            print("median:", np.median(a)) 

if __name__ == "__main__":
    analysis = Analysis()
    #analysis.run()
    analysis.detailed_log_analysis()