'''
Heuristic function that gives a score based on how many unique numbers are present on each row, column and 3x3 block
WIll be further used in the evolutionary algorithm to determine how close to the ideal solution the board is
'''
def heuristic_score(matrix):
    score=0
    row_number=[]
    column_number=[]
    block_number=[]
    for i in range(9):
        for j in range(9):
            if matrix[i][j] != 0:
                row_number.append(matrix[i][j])
            if matrix[j][i] != 0:
                column_number.append(matrix[j][i])
        score=score+len(set(row_number))+len(set(column_number))
        row_number.clear()
        column_number.clear()
    for box_row in range(0,9,3):
        for box_column in range(0,9,3):
            for i in range(3):
                for j in range(3):
                    if matrix[box_row+i][box_column+j] != 0:
                        block_number.append(matrix[box_row+i][box_column+j])
            score=score+len(set(block_number))
            block_number.clear()
    return score