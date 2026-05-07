import numpy as np
import random
def Inputpuzzle():
    # for i in range(3):
    #     a = list(map(int, input(f"Nhập dòng {i+1} của puzzle: ").split()))
    #     self.append(a)
    # return np.array(self)
    puzzle_matrix = np.random.permutation(9).reshape(3, 3)
    return puzzle_matrix
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
    return new_matrix
def main():
    puzzle = Inputpuzzle()
    blank = Find_blank(puzzle)
    row, col = blank
    print(puzzle)
    lst = get_move(row,col)
    print(lst)
    chosen_move = random.choice(lst)
    print("Nước đi đã chọn: ",chosen_move)
    new_puzzle = action(puzzle,chosen_move, row, col)
    print("Ma trận sau khi move: ",new_puzzle)
main()
