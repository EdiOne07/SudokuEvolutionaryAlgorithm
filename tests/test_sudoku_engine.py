import pytest
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