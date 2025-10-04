"""
Sudoku Puzzle Generator

This module provides functionality to generate random, solvable 9x9 Sudoku puzzles
with configurable difficulty levels.

The generator ensures that:
1. All generated puzzles have exactly one unique solution
2. Puzzles are properly validated for solvability
3. Different difficulty levels are supported
4. Clean visualization is available
"""

import random
import copy
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from search import dfs


class SudokuPuzzleGenerator:
    """
    A comprehensive Sudoku puzzle generator that creates solvable puzzles with guaranteed unique solutions.
    """
    
    # Difficulty levels defined by number of clues (filled cells) remaining
    # clues are the number remaining in the puzzle if hard to understand what it means.
    DIFFICULTY_LEVELS = {
        'easy': (40, 50),      # 40-50 clues remaining
        'medium': (30, 39),    # 30-39 clues remaining  
        'hard': (25, 29),      # 25-29 clues remaining
    }
    
    def __init__(self, seed=None):
        """
        Initialize the puzzle generator.
        
        Parameters:
        -----------
        seed : int, optional
            Random seed for reproducible puzzle generation
        """
        if seed is not None:
            random.seed(seed)
    
    def generate_puzzle(self, difficulty='medium', max_attempts=100):
        """
        Generate a random solvable Sudoku puzzle.
        
        Parameters:
        -----------
        difficulty : str
            Difficulty level ('easy', 'medium', 'hard')
        max_attempts : int
            Maximum attempts to generate a valid puzzle
            
        Returns:
        --------
        tuple: (puzzle_board, solution_board) or (None, None) if generation fails
            puzzle_board: 9x9 list with the puzzle (0 for empty cells)
            solution_board: 9x9 list with the complete solution
        """
        if difficulty not in self.DIFFICULTY_LEVELS:
            raise ValueError(f"Invalid difficulty. Must be one of: {list(self.DIFFICULTY_LEVELS.keys())}")
        
        min_clues, max_clues = self.DIFFICULTY_LEVELS[difficulty]
        target_clues = random.randint(min_clues, max_clues)
        
        for _ in range(max_attempts):
            # Generate a complete solved board
            solution = self._generate_complete_solution()
            if solution is None:
                continue
            
            # Remove numbers to create puzzle while maintaining solvability
            puzzle = self._remove_numbers_strategically(solution, target_clues)
            if puzzle is None:
                continue
                
            # Verify the puzzle has exactly one solution
            if self._has_unique_solution(puzzle):
                return puzzle, solution
        
        print(f"Warning: Failed to generate puzzle after {max_attempts} attempts")
        return None, None
    
    def _generate_complete_solution(self):
        """
        Generate a complete, valid Sudoku solution using randomized solving.
        
        Returns:
        --------
        list: 9x9 solved board or None if generation fails
        """
        # init board
        board = [[0 for _ in range(9)] for _ in range(9)]
        
        # Use the existing DFS_random function to fill the board
        solution = dfs.DFS_random(board, 9)
        return solution
    
    def _remove_numbers_strategically(self, solution, target_clues):
        """
        Remove numbers from a complete solution to create a puzzle with target_clues remaining.
        Uses strategic removal to maintain solvability.
        
        Parameters:
        -----------
        solution : list
            Complete 9x9 solved board
        target_clues : int
            Number of clues to keep in the final puzzle
            
        Returns:
        --------
        list: Puzzle board or None if removal fails
        """
        puzzle = copy.deepcopy(solution)
        
        # Create list of all positions
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        removed_count = 0
        max_to_remove = 81 - target_clues
        
        for row, col in positions:
            if removed_count >= max_to_remove:
                break
                
            # Temporarily remove the number
            original_value = puzzle[row][col]
            puzzle[row][col] = 0
            
            # Check if puzzle still has a unique solution
            if self._has_unique_solution(puzzle):
                # Keep it removed
                removed_count += 1
            else:
                # Restore the number
                puzzle[row][col] = original_value
        
        # Verify we have the right number of clues, sometimes when trying to make hard puzzle like leave 25 cluus
        # at that point we dont have solution or have multiple solutions, while might 27 have one solution
        # so we need to allow small deviation, here we allow 2 deviations.
        clue_count = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)
        if abs(clue_count - target_clues) <= 2:
            return puzzle
        
        return None
    
    def _has_unique_solution(self, puzzle):
        """
        Check if a puzzle has exactly one unique solution.
        
        Parameters:
        -----------
        puzzle : list
            9x9 puzzle board to check
            
        Returns:
        --------
        bool: True if puzzle has exactly one solution
        """
        solutions = []
        puzzle_copy = copy.deepcopy(puzzle)
        
        # Find all solutions (stop after finding 2 to save time)
        if self._count_solutions(puzzle_copy, solutions, max_solutions=2):
            return len(solutions) == 1
        return False
    
    def _count_solutions(self, board, solutions, max_solutions=2):
        """
        Count the number of solutions for a given puzzle using backtracking.
        This is very similart to the DFS_random but count the number of solutions.
        
        Parameters:
        -----------
        board : list
            9x9 puzzle board
        solutions : list
            List to store found solutions
        max_solutions : int
            Maximum solutions to find before stopping
            
        Returns:
        --------
        bool: True if solving completed, False if max_solutions reached
        """
        # Find empty cell
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    # Try numbers 1-9
                    for num in range(1, 10):
                        if dfs.is_valid(board, i, j, num):
                            board[i][j] = num
                            
                            # Recursively solve
                            if not self._count_solutions(board, solutions, max_solutions):
                                return False
                            
                            # Backtrack
                            board[i][j] = 0
                            
                            # Stop if we've found enough solutions
                            if len(solutions) >= max_solutions:
                                return False
                    return True
        
        # Board is complete - found a solution
        solutions.append(copy.deepcopy(board))
        return len(solutions) < max_solutions
    
    def generate_multiple_puzzles(self, count=5, difficulty='medium'):
        """
        Generate multiple puzzles at once.
        
        Parameters:
        -----------
        count : int
            Number of puzzles to generate
        difficulty : str
            Difficulty level for all puzzles
            
        Returns:
        --------
        list: List of (puzzle, solution) tuples
        """
        puzzles = []
        for i in range(count):
            print(f"Generating puzzle {i+1}/{count}...")
            puzzle, solution = self.generate_puzzle(difficulty)
            if puzzle is not None:
                puzzles.append((puzzle, solution))
            else:
                print(f"Failed to generate puzzle {i+1}")
        
        return puzzles
    
    @staticmethod
    def visualize_puzzle(board, title="Sudoku Puzzle"):
        """
        Pretty print a Sudoku board.
        
        Parameters:
        -----------
        board : list
            9x9 board to display
        title : str
            Title to display above the board
        """
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
    
    @staticmethod
    def get_puzzle_stats(board):
        """
        Get statistics about a puzzle.
        
        Parameters:
        -----------
        board : list
            9x9 puzzle board
            
        Returns:
        --------
        dict: Statistics including clue count, difficulty estimate, etc.
        """
        clue_count = sum(1 for i in range(9) for j in range(9) if board[i][j] != 0)
        empty_count = 81 - clue_count
        
        # Estimate difficulty based on clue count
        difficulty = 'unknown'
        for diff, (min_clues, max_clues) in SudokuPuzzleGenerator.DIFFICULTY_LEVELS.items():
            if min_clues <= clue_count <= max_clues:
                difficulty = diff
                break
        
        return {
            'clues': clue_count,
            'empty_cells': empty_count,
            'estimated_difficulty': difficulty
        }


def main():
    """
    Demo function showing how to use the SudokuPuzzleGenerator.
    """
    print("=== Sudoku Puzzle Generator Demo ===\n")
    
    generator = SudokuPuzzleGenerator()
    
    # Generate puzzles of different difficulties
    difficulties = ['easy', 'medium', 'hard']
    
    for difficulty in difficulties:
        print(f"Generating {difficulty.upper()} puzzle...")
        puzzle, solution = generator.generate_puzzle(difficulty)
        
        if puzzle is not None:
            stats = generator.get_puzzle_stats(puzzle)
            print(f"Successfully generated {difficulty} puzzle with {stats['clues']} clues")
            
            # Show the puzzle
            generator.visualize_puzzle(puzzle, f"{difficulty.capitalize()} Puzzle")
            
            # Optionally show solution (commented out to avoid clutter)
            # generator.visualize_puzzle(solution, f"{difficulty.capitalize()} Solution")
            
            print(f"Stats: {stats}")
            print("-" * 50)
        else:
            print(f"Failed to generate {difficulty} puzzle")
    
    # Generate multiple medium puzzles
    print("\nGenerating 3 medium puzzles...")
    puzzles = generator.generate_multiple_puzzles(count=3, difficulty='medium')
    print(f"Successfully generated {len(puzzles)} puzzles")


if __name__ == "__main__":
    main()
