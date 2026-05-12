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
    target_puzzle = np.array([[1, 2, 3],
                              [4, 5, 6],
                              [7, 8, 0]])
    max_steps = 1000000
    steps = 0
    while not np.array_equal(puzzle, target_puzzle):
        blank = Find_blank(puzzle)
        row, col = blank
        lst = get_move(row, col)
        chosen_move = random.choice(lst)
        puzzle = action(puzzle, chosen_move, row, col)
        steps += 1

        if steps % 10000 == 0:
            print(f"Đã duyệt {steps} bước...")
            
        if steps > max_steps:
            print(f"\nĐã ngắt sau {max_steps} bước!")
            print("Nguyên nhân: Đi random quá lâu HOẶC ma trận ngẫu nhiên ban đầu bị vô nghiệm.")
            return


    print(f"Đã giải xong sau {steps} bước.")
    print("Ma trận đích:\n", puzzle)
main()
