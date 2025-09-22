'''
Heuristic function that gives a score based on how many unique numbers are present on each row, column and 3x3 block
WIll be further used in the evolutionary algorithm to determine how close to the ideal solution the board is
'''
def heuristic_score(matrix):
    score=0
    row_number=[]
    column_number=[]
    block_number=[]
    # for i in range(9):
    #     for j in range(9):
    #         if matrix[i][j] != 0:
    #             row_number.append(matrix[i][j])
    #         if matrix[j][i] != 0:
    #             column_number.append(matrix[j][i])
    #     score=score+len(set(row_number))+len(set(column_number))
    #     row_number.clear()
    #     column_number.clear()
    # for box_row in range(0,9,3):
    #     for box_column in range(0,9,3):
    #         for i in range(3):
    #             for j in range(3):
    #                 if matrix[box_row+i][box_column+j] != 0:
    #                     block_number.append(matrix[box_row+i][box_column+j])
    #         score=score+len(set(block_number))
    #         block_number.clear()
    # return score

    for i in range(9):
        row_set = set()
        col_set = set() 
        block_set = set()
        
        for j in range(9):
            # Row processing
            if matrix[i][j] != 0:
                row_set.add(matrix[i][j])
            
            # Column processing
            if matrix[j][i] != 0:
                col_set.add(matrix[j][i])
            
            # Block processing
            block_row = (i // 3) * 3 + j // 3
            block_col = (i % 3) * 3 + j % 3
            if matrix[block_row][block_col] != 0:
                block_set.add(matrix[block_row][block_col])
        
        # Add all scores at once
        score += len(row_set) + len(col_set) + len(block_set)
    
    return score
        
