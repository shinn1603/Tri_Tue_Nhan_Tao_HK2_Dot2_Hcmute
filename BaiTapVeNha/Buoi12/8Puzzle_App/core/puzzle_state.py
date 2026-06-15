import numpy as np

class NODE:
    def __init__(self, state, parent, move_action, row, col):
        self.state = state 
        self.parent = parent
        self.move_action = move_action
        self.row = row
        self.col = col

def is_solvable(puzzle):
    flat_puzzle = [val for val in puzzle.flatten() if val != 0]
    inversions = 0
    for i in range(len(flat_puzzle)):
        for j in range(i + 1, len(flat_puzzle)):
            if flat_puzzle[i] > flat_puzzle[j]:
                inversions += 1
    return inversions % 2 == 0

def count_inversions(puzzle):
    flat = [val for val in puzzle.flatten() if val != 0]
    inversions = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] > flat[j]:
                inversions += 1
    return inversions

def check_solvable(start, target):
    return (count_inversions(start) % 2) == (count_inversions(target) % 2)

def Inputpuzzle():
    while True:
        puzzle = np.random.permutation(9).reshape(3, 3)
        if is_solvable(puzzle):
            return puzzle

def Find_blank(puzzle):
    result = np.where(puzzle == 0)
    if len(result[0]) > 0:
        row = result[0][0]
        col = result[1][0]
        return (row, col)
    return None

def get_move(row, col):
    valid_moves = []
    if(row < 2): valid_moves.append("DOWN")
    if(row > 0): valid_moves.append("UP")
    if(col < 2): valid_moves.append("RIGHT")
    if(col > 0): valid_moves.append("LEFT")
    return valid_moves

def action(puzzle, move, row, col):
    new_matrix = np.copy(puzzle)
    if(move=="DOWN"): new_row, new_col = row + 1, col
    if(move=="UP"): new_row, new_col = row - 1, col
    if(move=="LEFT"): new_row, new_col = row, col - 1
    if(move=="RIGHT"): new_row, new_col = row, col + 1
    new_matrix[row, col], new_matrix[new_row, new_col] = new_matrix[new_row, new_col], new_matrix[row, col]
    return new_matrix, new_row, new_col

def pathcost(new_puzzle, target_puzzle):
    cost = (target_puzzle != new_puzzle) & (new_puzzle != 0)
    return np.sum(cost)
