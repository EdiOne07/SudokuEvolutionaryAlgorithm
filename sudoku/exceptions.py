class InvalidNumberError(Exception):
    """Raised when a provided number is not in the allowed range 1–9."""
    pass

class CellAlreadyFilledError(Exception):
    """Raised when trying to place a number in a non-empty cell."""
    def __init__(self, row, column, current_value):
        super().__init__(f"Can't override existing value {current_value} in row {row} column {column}!")
        self.row = row
        self.column = column
        self.current_value = current_value