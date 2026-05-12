import numpy as np
import random
def Inputpuzzle():
    puzzle = np.random.permutation(9).reshape(3, 3)
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
    if(row < 2):
        valid_moves.append("DOWN")
    if(row > 0):
        valid_moves.append("UP")
    if(col < 2):
        valid_moves.append("RIGHT")
    if(col > 0):
        valid_moves.append("LEFT")
    return valid_moves

def action(puzzle,move,row,col):
    new_matrix = np.copy(puzzle)
    if(move=="DOWN"):
        new_row, new_col = row + 1, col
    if(move=="UP"):
        new_row, new_col = row - 1, col
    if(move=="LEFT"):
        new_row, new_col = row, col - 1
    if(move=="RIGHT"):
        new_row, new_col = row, col + 1
    new_matrix[row, col], new_matrix[new_row, new_col] = new_matrix[new_row, new_col], new_matrix[row, col]
    return new_matrix, new_row, new_col

def main():
    target_puzzle = np.array([[1, 2, 3],
                              [4, 5, 6],
                              [7, 8, 0]])
    
    puzzle = Inputpuzzle()
    blank = Find_blank(puzzle)
    row, col = blank
    print(puzzle)
    steps = 0
    explored_puzzles = set()
    explored_puzzles.add(tuple(puzzle.flatten()))
    while not np.array_equal(puzzle, target_puzzle):
        unseen_moves = []
        steps +=1
        valid_moves = get_move(row,col)
        for m in valid_moves:
            temp_p, _, _ = action(puzzle, m, row, col)
            state_tuple = tuple(temp_p.flatten())
            if state_tuple not in explored_puzzles:
                unseen_moves.append((m, state_tuple))
        
        if unseen_moves:
            move_chosen, state_tuple = random.choice(unseen_moves)
            puzzle, row, col = action(puzzle, move_chosen, row, col)
            explored_puzzles.add(tuple(puzzle.flatten()))
        else:
            if not np.array_equal(puzzle, target_puzzle):
                print("Không còn đường đi hợp lệ")
                return
            else:
                break
    print(f"Đã giải xong sau {steps} bước")
main()
