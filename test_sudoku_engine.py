import pytest
from sudoku_engine import *

class TestSudokuEngine:
    """Tests core functionality of the sudoku engine class."""
    board = SudokuEngine(visualize_game=True, 
                        custom_board=[[0,2,0,0,0,0,0,3,1],
                            [7,0,0,0,0,3,0,0,0],
                            [0,0,0,1,4,0,2,9,0],
                            [0,5,2,7,6,4,0,1,8],
                            [0,6,3,0,1,2,7,5,9],
                            [0,7,8,0,0,0,4,0,0],
                            [2,0,0,3,7,0,0,0,5],
                            [0,1,0,0,0,0,9,0,0],
                            [5,4,0,0,8,1,0,0,0]])

    def test_invalid_number(self):
        with pytest.raises(Exception):
            self.board.next(0,0,10)
    
    def test_place_duplicate_number(self):
        _, _, success = self.board.next(0,0,7)
        assert success == False

    def test_overwrite_existing_number(self):
        with pytest.raises(Exception):
            self.board.next(0,1,3)
    
    def test_errors(self):
        pass

    def test_game_finished(self):
        pass