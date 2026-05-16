import numpy as np
import random
from collections import deque
class NODE:
    def __init__(self, state, parent, move_action, row, col):
        self.state = state 
        self.parent = parent
        self.move_action = move_action
        self.row = row
        self.col = col

def PrintDetailWays(goal_node):
    path = []
    current = goal_node
    while current is not None:
        path.append(current)
        current = current.parent
    path = path[::-1]
    print(f"Đã hoàn thành với đường đi ngắn nhất: {len(path) - 1} bước")

    for i, node in enumerate(path):
        if node.move_action is None:
            print("Bước 0 trạng thái bắt đầu")
        else:
            print(f"Bước {i} trạng thái {node.move_action}")
        print(node.state)
        print("-"*20)

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
    print("Puzzle đầu vào\n")
    print(puzzle)
    steps = 0


    explored_puzzles = set()
    explored_puzzles.add(tuple(puzzle.flatten()))

    start_node = NODE(state=puzzle,parent=None,move_action=None,col=col, row=row)
    queue = deque()
    queue.append(start_node)


    while queue:
        cur_node = queue.pop()
        steps +=1


        if(np.array_equal(cur_node.state, target_puzzle)):
            PrintDetailWays(cur_node)
            return
        

        valid_moves = get_move(cur_node.row, cur_node.col)
        for move in valid_moves:
            new_puzzle, new_row, new_col = action(cur_node.state, move, cur_node.row, cur_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored_puzzles:
                explored_puzzles.add(state_tuple)
                child_node = NODE(
                    state=new_puzzle,
                    parent=cur_node,
                    move_action= move,
                    col=new_col,
                    row=new_row
                )
                queue.append(child_node)
    print(f"Đã duyệt qua {steps} trạng thái nhưng không có cách giải hợp lệ")
main()
