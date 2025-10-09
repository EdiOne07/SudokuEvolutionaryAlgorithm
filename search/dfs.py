import random
import time
import math

'''
how to solve:
It's a rule based algorithm, and using backtracking to solve the puzzle.
core function is DFS and is_valid
is_valid function validates whether placing the number num at position follows sudoku rules
DFS using backtracking:
1. Find first empty cell (0)
2. Try numbers 1-9 in that cell
3. For each number, use is_valid to check if it conflicts with existing numbers
4. If valid: place number and recursively solve rest
5. If invalid OR recursive call fails: backtrack (reset to 0) and try next number
6. If no numbers work: return False (dead end)
7. If all cells filled: return True (solved!)
'''

# this is use to check the specific number at position is valid
def is_valid_move(matrix, row, column, num):
    size=len(matrix)
    box_size=int(math.sqrt(size))
    if num in matrix[row]:
        return False
    
    if num in [matrix[i][column] for i in range(size)]:
        return False

    square_row, square_column = box_size * (row // box_size), box_size * (column // box_size)
    for i in range(square_row, square_row + box_size):
        for j in range(square_column, square_column + box_size):
            if matrix[i][j] == num:
                return False
    
    return True

# this is use to check the whole matrix is valid
def is_goal_state(matrix):
    # Check rows
    for row in matrix:
        if sum(row) != 45:
            return False
    
    # Check columns
    for j in range(9):
        column_sum = sum(matrix[i][j] for i in range(9))
        if column_sum != 45:
            return False
    
    # Check 3x3 boxes
    for box_row in range(3):
        for box_col in range(3):
            box_sum = 0
            for i in range(3):
                for j in range(3):
                    box_sum += matrix[box_row * 3 + i][box_col * 3 + j]
            if box_sum != 45:
                return False
    
    return True

'''
Recursively solve the sudoku puzzle
when current cell is empty, try to fill the cell with numbers 1-9
if the number is valid, recursively solve the rest of the puzzle
if the number is not valid, backtrack and try the next number
if all numbers are tried and no solution is found, return None
if all cells are filled, return True
'''
def DFS_random(matrix,size):
    for i in range(size):
        for j in range(size):
            if (matrix[i][j] == 0):
                nums=list(range(1,size+1))
                nums=random.sample(nums,len(nums))
                for num in nums:
                    if is_valid_move(matrix, i, j, num):
                        matrix[i][j] = num
                        
                        # Recursively solve puzzle
                        if DFS_random(matrix,size):
                            return matrix
                        
                        # Backtrack
                        matrix[i][j] = 0
                
                # If no number works, return None
                return None
    return matrix

def DFS(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if (matrix[i][j] == 0):
                for num in range(1, len(matrix)+1):
                    if is_valid_move(matrix, i, j, num):
                        matrix[i][j] = num

                        # Recursively solve puzzle
                        if DFS(matrix):
                            return True

                        # Backtrack
                        matrix[i][j] = 0
                return False
    return True

'''test the DFS function'''
if __name__ == "__main__":
    matrix = [
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
    
    print("Original matrix:")
    for row in matrix:
        print(row)

    if matrix is None:
        raise ValueError("Matrix is required")
    
    # check the row and column is 9*9
    if len(matrix) != 9 or any(len(row) != 9 for row in matrix):
        raise ValueError("Matrix must be 9x9, plz check your input")
    
    import copy
    filled_matrix = copy.deepcopy(matrix)
    
    start_time = time.time()
    success = DFS(filled_matrix)
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\nSudoku solved: {success}")
    print(f"Time taken: {elapsed_time:.6f} seconds")
    
    if success:
        print("\nFilled matrix:")
        for row in filled_matrix:
            print(row)
        print("\nIs filled matrix valid?", is_goal_state(filled_matrix))
    else:
        print("No solution found for this Sudoku puzzle")