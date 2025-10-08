'''
Heuristic function that gives a score based on how many unique numbers are present on each row, column and 3x3 block
Will be further used in the evolutionary algorithm to determine how close to the ideal solution the board is
'''

class HeuristicMatrix:
    def __init__(self, matrix):
        self.matrix = matrix
        self.row_set=[set() for _ in range(9)]
        self.column_set=[set() for _ in range(9)]
        self.block_set=[set() for _ in range(9)]
        self.score=0
    def initialize(self):
        for i in range(9):
            for j in range(9):
                if self.matrix[i][j]!=0:
                    self.row_set[i].add(self.matrix[i][j])
                    self.column_set[j].add(self.matrix[i][j])
                    b = (i // 3) * 3 + (j // 3)
                    self.block_set[b].add(self.matrix[i][j])
        self.score+=sum(len(s) for s in self.row_set)+sum(len(s) for s in self.column_set)+ sum(len(s) for s in self.block_set)
    def update(self,i,j,new_value):
        old_value=self.matrix[i][j]
        if old_value==new_value:
            return self.score
        if old_value != 0:
            self.row_set[i].remove(old_value)
            self.column_set[j].remove(old_value)
            b = (i // 3) * 3 + (j // 3)
            self.block_set[b].remove(old_value)
        self.matrix[i][j]=new_value
        if new_value!=0:
            self.row_set[i].add(new_value)
            self.column_set[j].add(new_value)
            b = (i // 3) * 3 + (j // 3)
            self.block_set[b].add(new_value)
        self.score += sum(len(s) for s in self.row_set) + sum(len(s) for s in self.column_set) + sum(len(s) for s in self.block_set)
        print(self.score)
        return self.score