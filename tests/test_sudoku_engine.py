import pytest

from heuristic import heuristic_score
from heuristic import HeuristicMatrix
from sudoku.engine import SudokuEngine
from sudoku.exceptions import InvalidNumberError, CellAlreadyFilledError

class TestSudokuEngine:
    """Tests core functionality of the sudoku engine class."""
    board = SudokuEngine(visualize_game=True, 
                        custom_board=[[0,0,7,1,5,4,3,9,6],
                            [9,6,5,3,2,7,1,4,8],
                            [3,4,1,6,8,9,7,5,2],
                            [5,9,3,4,6,8,2,7,1],
                            [4,7,2,5,1,3,6,8,9],
                            [6,1,8,9,7,2,4,3,5],
                            [7,8,6,2,3,5,9,1,4],
                            [1,5,4,7,9,6,8,2,3],
                            [2,3,9,8,4,1,5,6,7]])
    def test_invalid_number(self):
        with pytest.raises(InvalidNumberError):
            self.board.next(0,0,10)
    
    def test_place_duplicate_number(self):
        _, _, success = self.board.next(0,0,7)
        assert success == False

    def test_overwrite_existing_number(self):
        with pytest.raises(CellAlreadyFilledError):
            self.board.next(2,2,3)
    
    def test_game_finished(self):
        _, finished, _ = self.board.next(0,0,8)
        assert finished == False
        _, finished, _ = self.board.next(0,1,2)
        assert finished == True

class TestSudokuHeuristic:

    solved_board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]
    empty_board=[[0]*9 for i in range(9)]
    partial_valid = [
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
    conflict_board = [
        [5, 5, 0, 0, 7, 0, 0, 0, 0],  # two 5’s in same row → invalid
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    def test_solved_sudoku_score(self):
        Heuristic = HeuristicMatrix(self.solved_board)
        score=heuristic_score(self.solved_board)
        assert score==Heuristic.score
    def test_empty_sudoku_score(self):
        Heuristic = HeuristicMatrix(self.empty_board)
        score=heuristic_score(self.empty_board)
        assert score==Heuristic.score
    def test_partial_valid(self):
        Heuristic = HeuristicMatrix(self.partial_valid)
        score=heuristic_score(self.partial_valid)
        assert score==Heuristic.score
    def test_conflict_board(self):
        Heuristic = HeuristicMatrix(self.conflict_board)
        score=heuristic_score(self.conflict_board)
        assert score==Heuristic.score