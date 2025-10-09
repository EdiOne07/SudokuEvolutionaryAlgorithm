# SudokuEvolutionaryAlgorithm
This project contains different implementations to solve sudoku puzzles of varying difficulty levels.
It includes two genetic algorithms and one depth-first search algorithm.

## Usage
Make sure you have Python 3.x installed.

Install the required packages using pip:
```
pip install -r requirements.txt
```

To run the first genetic algorithm, use:
```
python3 -m sudoku_1.algorithm
```

To run the second (main) genetic algorithm, use:
```
python3 -m sudoku_2.evolution
python3 -m sudoku_2.analysis
```

To run the DFS algorithm, use:
```
python3 -m search.dfs
python3 -m search.analysis
```

Folder search and sudoku_2 have analaysis.py files. Run these files to get detailed statistics over multiple runs (difficulty and number of runs can be set).
Run algorithm.py / dfs.py for individual run.

## Project Structure
- `sudoku_1`: Contains the first implementation of the genetic algorithm for solving Sudoku puzzles.
- `sudoku_2`: Contains the second implementation of the genetic algorithm for solving Sudoku puzzles. This implementation generally performs much better than the first one.
- `search`: Contains search algorithms for solving Sudoku puzzles.
- `generators`: Contains different Sudoku puzzle generators.
- `logs`: Contains log files generated during the execution of the algorithms.
- `Report`: Contains the project report in PDF format.